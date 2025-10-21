#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
from fastapi import Request, Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask, BackgroundTasks

from backend.app.admin.conf import admin_settings
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.model import User
from backend.app.admin.schema.token import GetLoginToken, GetNewToken
from backend.app.admin.schema.user import AuthLoginParam, AuthRegisterParam, RegisterUserParam, AuthResetPasswordParam, \
    SSORegisterUserParam, AuthSSOLoginParam
from backend.app.admin.service.login_log_service import LoginLogService
from backend.common.enums import LoginLogStatusType
from backend.common.exception import errors
from backend.common.response.response_code import CustomErrorCode
from backend.common.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token,
    jwt_decode,
    password_verify, get_hash_password,
)
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client
from backend.utils.timezone import timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import base64
from fastapi import HTTPException
from typing import Any
# 设置密钥，前端和后端需要一致


BLOCK_SIZE = AES.block_size

FRONTEND_SECRET_KEY_BASE64 = "G8ZyYyZ0Xf5x5f6uZrwf6ft4gD0pniYAkHp/Y6f4Pv4="

def get_aes_key():
    """
    获取与前端匹配的AES密钥
    CryptoJS.enc.Base64.parse()会将Base64字符串转换为WordArray
    我们需要模拟这一行为，确保密钥一致
    """
    # Base64解码前端密钥
    decoded_key = base64.b64decode(FRONTEND_SECRET_KEY_BASE64)
    # CryptoJS会将其视为UTF-8字符串处理，所以我们需要保持一致
    return decoded_key[:32]  # 确保密钥长度为32字节(AES-256)
# 解密函数
async def decrypt_data(encrypted_data: str, iv_base64: str) -> str:
    try:
        # 获取与前端匹配的密钥
        secret_key = get_aes_key()

        # 解码IV和密文
        iv = base64.b64decode(iv_base64.encode('utf-8'))
        ciphertext = base64.b64decode(encrypted_data.encode('utf-8'))

        # 使用AES-CBC模式解密
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

        return decrypted_data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Decryption failed: {str(e)}"
        )

# 加密token函数
# async def encrypt_for_cross_domain(token: str) -> dict:
#     try:
#         # 获取与前端匹配的密钥
#         secret_key = get_aes_key()
#
#         # 生成随机IV
#         iv = os.urandom(16)
#
#         # 使用AES-CBC模式加密
#         cipher = AES.new(secret_key, AES.MODE_CBC, iv)
#         padded_token = pad(token.encode('utf-8'), AES.block_size)
#         encrypted = cipher.encrypt(padded_token)
#
#         return {
#             "ciphertext": base64.b64encode(encrypted).decode('utf-8'),
#             "iv": base64.b64encode(iv).decode('utf-8')
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Encryption failed: {str(e)}"
#         )

async def encrypt_for_cross_domain(token: str) -> dict:
    try:
        # 获取与前端匹配的密钥 (32字节)
        secret_key = base64.b64decode("G8ZyYyZ0Xf5x5f6uZrwf6ft4gD0pniYAkHp/Y6f4Pv4=")
        if len(secret_key) > 32:  # 如果解码后长度超过32字节，截取前32字节
            secret_key = secret_key[:32]

        # 生成16字节的随机IV (128位)
        iv = os.urandom(16)

        # 使用AES-CBC模式加密
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        padded_token = pad(token.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_token)

        # 转换为与前端一致的格式
        encrypted_ciphertext = base64.b64encode(encrypted).decode('utf-8')
        iv_hex = iv.hex()  # 使用十六进制格式，与CryptoJS.enc.Hex.stringify(iv)一致

        return {
            "ciphertext": encrypted_ciphertext,  # Base64编码的密文
            "iv": iv_hex  # 十六进制编码的IV
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Encryption failed: {str(e)}"
        )

class AuthService:
    @staticmethod
    async def swagger_login(*, obj: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            current_user = await user_dao.get_by_username(db, obj.username)
            if not current_user:
                raise errors.NotFoundError(msg='账号或密码有误')
            elif not password_verify(f'{obj.password}{current_user.salt}', current_user.password):
                raise errors.AuthorizationError(msg='账号或密码有误')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            access_token = await create_access_token(str(current_user.id), current_user.is_multi_login)
            await user_dao.update_login_time(db, obj.username)
            return access_token.access_token, current_user

    @staticmethod
    async def login(
        *, request: Request, response: Response, obj: AuthLoginParam, background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        async with async_db_session.begin() as db:
            try:
                # 解密前端加密的字段
                obj.username = await decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.password = await decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.captcha = await decrypt_data(obj.captcha, obj.captcha_iv)  # 使用传来的 IV 和密文解密

                current_user = await user_dao.get_by_username(db, obj.username)
                if not current_user:
                    raise errors.NotFoundError(msg='账号或密码有误')
                user_uuid = current_user.uuid
                username = current_user.username
                if not password_verify(obj.password + current_user.salt, current_user.password):
                    raise errors.AuthorizationError(msg='账号或密码有误')
                elif not current_user.status:
                    raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
                current_user_id = current_user.id
                access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
                refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)
            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)
            except (errors.AuthorizationError, errors.CustomError) as e:
                task = BackgroundTask(
                    LoginLogService.create,
                    **dict(
                        db=db,
                        request=request,
                        user_uuid=user_uuid,
                        username=username,
                        login_time=timezone.now(),
                        status=LoginLogStatusType.fail.value,
                        msg=e.msg,
                    ),
                )
                raise errors.AuthorizationError(msg=e.msg, background=task)
            except Exception as e:
                raise e
            else:
                background_tasks.add_task(
                    LoginLogService.create,
                    **dict(
                        db=db,
                        request=request,
                        user_uuid=user_uuid,
                        username=username,
                        login_time=timezone.now(),
                        status=LoginLogStatusType.success.value,
                        msg='登录成功',
                    ),
                )
                await redis_client.delete(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                await user_dao.update_login_time(db, obj.username)
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                )
                await db.refresh(current_user)
                cross_domain_token = await encrypt_for_cross_domain(access_token.access_token)
                print("cross_domain_token", cross_domain_token)
                data = GetLoginToken(
                    access_token=access_token.access_token,
                    access_token_expire_time=access_token.access_token_expire_time,
                    user=current_user,  # type: ignore
                    cross_domain_token=cross_domain_token["ciphertext"],
                    cross_domain_iv=cross_domain_token["iv"]
                )
                return data

    @staticmethod
    async def sso_login(
            request: Request,
            response: Response,
            obj: AuthSSOLoginParam,
            background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        async with async_db_session.begin() as db:
            try:
                # 解密前端加密的用户名
                obj.username = decrypt_data(obj.username, obj.username_iv)

                # 获取用户信息
                current_user = await user_dao.get_by_username(db, obj.username)
                if not current_user:
                    raise errors.NotFoundError(msg='用户不存在')
                if not current_user.status:
                    raise errors.AuthorizationError(msg='用户已被锁定, 请联系系统管理员')

                # 生成令牌
                current_user_id = current_user.id
                access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
                refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)
            except errors.AuthorizationError as e:
                background_tasks.add_task(
                    LoginLogService.create,
                    db=db,
                    request=request,
                    user_uuid=current_user.uuid if current_user else None,
                    username=obj.username,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.fail.value,
                    msg=e.msg,
                )
                raise errors.AuthorizationError(msg=e.msg)
            except Exception as e:
                raise e
            else:
                # 记录登录日志
                background_tasks.add_task(
                    LoginLogService.create,
                    db=db,
                    request=request,
                    user_uuid=current_user.uuid,
                    username=current_user.username,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.success.value,
                    msg='SSO 登录成功',
                )

                # 设置 Refresh Token 到 Cookie
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                )

                # 更新用户登录时间
                await user_dao.update_login_time(db, obj.username)
                await db.refresh(current_user)

                # 返回登录凭证
                data = GetLoginToken(
                    access_token=access_token.access_token,
                    access_token_expire_time=access_token.access_token_expire_time,
                    user=current_user,  # type: ignore
                )
                return data

    @staticmethod
    async def register(
            *, request: Request, obj: AuthRegisterParam,
    ):
        async with async_db_session.begin() as db:
            try:
                obj.username = await decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.email =await decrypt_data(obj.email, obj.email_iv)
                obj.password = await decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.captcha = await decrypt_data(obj.captcha, obj.captcha_iv)  # 使用传来的 IV 和密文解密
                obj.nickname =await decrypt_data(obj.nickname, obj.nickname_iv)  # 使用传来的 IV 和密文解密

                if not obj.password:
                    raise errors.ForbiddenError(msg='密码为空')
                username = await user_dao.get_by_username(db, obj.username)
                if username:
                    raise errors.ForbiddenError(msg='用户已注册')
                obj.nickname = obj.nickname if obj.nickname else f'#{random.randrange(10000, 88888)}'
                # nickname = await user_dao.get_by_nickname(db, obj.nickname)
                # if nickname:
                #     raise errors.ForbiddenError(msg='昵称已注册')
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='邮箱已注册')
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
                obj_dict = obj.dict(exclude={"captcha"})
                user_param = RegisterUserParam(**obj_dict)
                await user_dao.create(db, user_param)

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)

    @staticmethod
    async def sso_register(
            request: Request,
            obj: SSORegisterUserParam,
    ):
        async with async_db_session.begin() as db:
            try:
                # 解密用户名和昵称
                obj.username = await decrypt_data(obj.username, obj.username_iv)
                obj.nickname = await decrypt_data(obj.nickname, obj.nickname_iv)

                # 设置密码与用户名相同
                obj.password = obj.username[-6:].zfill(6)

                # 设置邮箱为 username + @jxnu.edu.cn
                obj.email = f"{obj.username}@jxnu.edu.cn"
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='邮箱已注册')

                # 检查用户名是否已注册
                existing_user = await user_dao.get_by_username(db, obj.username)
                if existing_user:
                    raise errors.ForbiddenError(msg='用户已注册')
                # 构造注册用户参数（去掉验证码和邮箱的 IV 字段）
                obj_dict = obj.dict(exclude={"captcha", "captcha_iv", "email_iv"})
                obj_dict["password"] = obj.password
                obj_dict["email"] = obj.email
                user_param = RegisterUserParam(**obj_dict)

                # 创建用户
                await user_dao.create(db, user_param)

                return {"message": "注册成功"}

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: AuthResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            try:
                obj.username =await decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.email =await decrypt_data(obj.email, obj.email_iv)
                obj.password = await decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.captcha = await decrypt_data(obj.captcha, obj.captcha_iv)  # 使用传来的 IV 和密文解密
                    # 验证验证码
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)

                    # 检查密码
                if not obj.password:
                    raise errors.ForbiddenError(msg='密码为空')
                user = await user_dao.get_by_username(db, obj.username)
                if not user:
                    raise errors.ForbiddenError(msg='用户不存在')
                if not obj.email == user.email:
                    raise errors.ForbiddenError(msg='邮箱验证错误')

                    # 更新密码
                salt = user.salt
                hashed_password = get_hash_password(f'{obj.password}{salt}')  # 假设你需要哈希密码
                await user_dao.update_user_pwd(db, obj.username ,hashed_password)

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)



    @staticmethod
    async def new_token(*, request: Request, response: Response) -> GetNewToken:
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        if not refresh_token:
            raise errors.TokenError(msg='Refresh Token 丢失，请重新登录')
        try:
            user_id = jwt_decode(refresh_token)
        except Exception:
            raise errors.TokenError(msg='Refresh Token 无效')
        if request.user.id != user_id:
            raise errors.TokenError(msg='Refresh Token 无效')
        async with async_db_session() as db:
            current_user = await user_dao.get(db, user_id)
            if not current_user:
                raise errors.NotFoundError(msg='账号或密码有误')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            current_token = get_token(request)
            new_token = await create_new_token(
                sub=str(current_user.id),
                token=current_token,
                refresh_token=refresh_token,
                multi_login=current_user.is_multi_login,
            )
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=new_token.new_refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.f_utc(new_token.new_refresh_token_expire_time),
                httponly=True,
            )
            data = GetNewToken(
                access_token=new_token.new_access_token,
                access_token_expire_time=new_token.new_access_token_expire_time,
            )
            return data

    @staticmethod
    async def logout(*, request: Request, response: Response) -> None:
        token = get_token(request)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
        if request.user.is_multi_login:
            key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
            await redis_client.delete(key)
            if refresh_token:
                key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}'
                await redis_client.delete(key)
        else:
            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)
            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)


auth_service = AuthService()
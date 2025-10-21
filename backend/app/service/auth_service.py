#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import base64
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask, BackgroundTasks
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from app.conf import admin_settings
from app.crud.crud_user import user_dao
from app.model import User
from app.schema.token import GetLoginToken, GetNewToken
from app.schema.user_schema import AuthLoginParam, AuthRegisterParam, RegisterUserParam
# from app.admin.service.login_log_service import LoginLogService
from common.enums import LoginLogStatusType
from common.exception import errors

from common.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token,
    jwt_decode,
    password_verify,
)
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from utils.timezone import timezone


# 加密token函数，用于跨域认证
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
                raise errors.NotFoundError(msg='用户名或密码有误')
            elif not password_verify(f'{obj.password}{current_user.salt}', current_user.password):
                raise errors.AuthorizationError(msg='用户名或密码有误')
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
            current_user = await user_dao.get_by_username(db, obj.username)
            if not current_user:
                raise errors.NotFoundError(msg='用户名或密码有误')
            user_uuid = current_user.uuid
            username = current_user.username
            if not password_verify(obj.password + current_user.salt, current_user.password):
                raise errors.AuthorizationError(msg='用户名或密码有误')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{obj.captcha_id}')
            if not captcha_code:
                raise errors.AuthorizationError(msg='验证码失效，请重新获取')
            if captcha_code.lower() != obj.captcha.lower():
                raise errors.AuthorizationError(msg='验证码错误')
            current_user_id = current_user.id
            access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
            refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)

            # background_tasks.add_task(
            #     LoginLogService.create,
            #     **dict(
            #         db=db,
            #         request=request,
            #         user_uuid=user_uuid,
            #         username=username,
            #         login_time=timezone.now(),
            #         status=LoginLogStatusType.success.value,
            #         msg='登录成功',
            #     ),
            # )
            await redis_client.delete(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{obj.captcha_id}')
            await user_dao.update_login_time(db, obj.username)
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=refresh_token.refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                httponly=True,
            )
            await db.refresh(current_user)
            current_user = await user_dao.get_with_relation(db=db, user_uuid=current_user.uuid)
            
            # 生成跨域认证token
            cross_domain_token = await encrypt_for_cross_domain(access_token.access_token)
            print("cross_domain_token:",cross_domain_token)
            data = GetLoginToken(
                access_token=access_token.access_token,
                access_token_expire_time=access_token.access_token_expire_time,
                user=current_user,  # type: ignore
                cross_domain_token=cross_domain_token["ciphertext"],
                cross_domain_iv=cross_domain_token["iv"]
            )
            return data

    @staticmethod
    async def register(
            *, request: Request, obj: AuthRegisterParam,
    ):
        async with async_db_session.begin() as db:
            try:
                if not obj.password:
                    raise errors.ForbiddenError(msg='密码为空')
                username = await user_dao.get_by_username(db, obj.username)
                if username:
                    raise errors.ForbiddenError(msg='用户已注册')
                obj.nickname = obj.nickname if obj.nickname else f'#{random.randrange(10000, 88888)}'
                nickname = await user_dao.get_by_nickname(db, obj.nickname)
                if nickname:
                    raise errors.ForbiddenError(msg='昵称已注册')
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='邮箱已注册')
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{obj.captcha_id}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.AuthorizationError(msg='验证码错误')
                obj_dict = obj.dict(exclude={"captcha"})
                user_param = RegisterUserParam(**obj_dict)
                await redis_client.delete(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{obj.captcha_id}')
                await user_dao.create(db, user_param)

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
                raise errors.NotFoundError(msg='用户名或密码有误')
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
            # await redis_client.delete(key)
            if refresh_token:
                key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}'
                # await redis_client.delete(key)
        else:
            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:'
            # await redis_client.delete_prefix(key_prefix)
            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:'
            # await redis_client.delete_prefix(key_prefix)


auth_service = AuthService()

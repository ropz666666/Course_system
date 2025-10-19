#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBasicCredentials
from fastapi_limiter.depends import RateLimiter
from starlette.background import BackgroundTasks

from app.schema.user_schema import RegisterUserParam, AuthRegisterParam, AuthLoginParam
from app.schema.token import GetSwaggerToken
from app.service.auth_service import auth_service
from common.security.jwt import DependsJwtAuth

router = APIRouter()


@router.post('/login/swagger', summary='swagger 调试专用', description='用于快捷获取 token 进行 swagger 认证')
async def swagger_login(obj: Annotated[HTTPBasicCredentials, Depends()]):
    token, user = await auth_service.swagger_login(obj=obj)
    return GetSwaggerToken(access_token=token, user=user)  # type: ignore


@router.post(
    '/login',
    summary='用户登录',
    description='json 格式登录, 仅支持在第三方api工具调试, 例如: postman',
    dependencies=[],
)
async def user_login(
    request: Request, response: Response, obj: AuthLoginParam, background_tasks: BackgroundTasks
) :
    data = await auth_service.login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return data


@router.post(
    '/register',
    summary='注册用户',
    dependencies=[])
async def user_register(request: Request,obj: AuthRegisterParam
):
    obj.email = f"{obj.username}@example.com"
    await auth_service.register(request=request, obj=obj)
    return '注册成功'


@router.post('/token/new', summary='创建新 token', dependencies=[DependsJwtAuth])
async def create_new_token(request: Request, response: Response):
    data = await auth_service.new_token(request=request, response=response)
    return data


@router.post('/logout', summary='用户登出', dependencies=[DependsJwtAuth])
async def user_logout(request: Request, response: Response):
    await auth_service.logout(request=request, response=response)
    return '退出成功'

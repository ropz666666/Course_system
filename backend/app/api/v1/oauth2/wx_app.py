#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import httpx
from fastapi import APIRouter, HTTPException

from app.conf import admin_settings
from app.service.wx_oauth2_service import wx_oauth2_service
from common.exception.errors import RequestError
from common.schema import SchemaBase
router = APIRouter()


# 使用更规范的请求模型命名
class WxLoginRequest(SchemaBase):
    code: str


@router.post('/wx-auth', summary='微信小程序一键登录', response_description="授权成功返回用户凭证")
async def wechat_miniprogram_login(
    obj: WxLoginRequest
) :
    """
    微信小程序登录流程：
    1. 用临时code换取openid和session_key
    2. 后续应创建自己的用户会话（示例仅返回微信数据）
    """
    wx_api_url = admin_settings.OAuth2_WX_APP_URL

    # 构造请求参数（参数命名遵循微信官方文档）
    params_data = {
        "appid": admin_settings.OAuth2_WX_APPID,
        "secret":admin_settings.OAuth2_WX_SECRET,
        "js_code": obj.code,
        "grant_type": "authorization_code"
    }

    try:
        # 使用异步客户端请求微信接口
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(wx_api_url, params=params_data)
            response.raise_for_status()  # 自动处理4xx/5xx错误
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"微信接口请求失败: {str(e)}"
        )

    # 解析微信响应数据
    wx_data = response.json()
    # 处理微信返回的错误（微信接口规范）
    if "errcode" in wx_data and wx_data["errcode"] != 0:
        raise HTTPException(
            status_code=401,
            detail=f"微信认证失败: {wx_data.get('errmsg', '未知错误')}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user_uuid = wx_data.get('openid', None)
    if not user_uuid:
        raise RequestError(msg="微信认证失败")

    data = await wx_oauth2_service.create_with_login(
        user_uuid=user_uuid
    )
    return data


@router.get('/wx-auth/token', summary='微信小程序获取token', response_description="授权成功返回用户凭证")
async def wechat_miniprogram_token() :
    """
    微信小程序登录流程：
    1. 用临时code换取openid和session_key
    2. 后续应创建自己的用户会话（示例仅返回微信数据）
    """
    wx_api_url = admin_settings.OAuth2_WX_APP_TOKEN_URL

    # 构造请求参数（参数命名遵循微信官方文档）
    params_data = {
        "appid": admin_settings.OAuth2_WX_APPID,
        "secret":admin_settings.OAuth2_WX_SECRET,
        "grant_type": "authorization_code"
    }

    try:
        # 使用异步客户端请求微信接口
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(wx_api_url, params=params_data)
            response.raise_for_status()  # 自动处理4xx/5xx错误
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"微信接口请求失败: {str(e)}"
        )

    # 解析微信响应数据
    wx_data = response.json()
    # 处理微信返回的错误（微信接口规范）
    if "errcode" in wx_data and wx_data["errcode"] != 0:
        raise HTTPException(
            status_code=401,
            detail=f"微信认证失败: {wx_data.get('errmsg', '未知错误')}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return wx_data


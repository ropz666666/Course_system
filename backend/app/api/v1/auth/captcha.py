#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_captcha import img_captcha
from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter
from starlette.concurrency import run_in_threadpool

from app.conf import admin_settings
from database.db_redis import redis_client
import uuid

router = APIRouter()


@router.get(
    '',
    summary='获取登录验证码',
    dependencies=[],
)
async def get_captcha(request: Request):
    """
    此接口可能存在性能损耗，尽管是异步接口，但是验证码生成是IO密集型任务，使用线程池尽量减少性能损耗
    """
    img_type: str = 'base64'
    img, code = await run_in_threadpool(img_captcha, img_byte=img_type)
    captcha_id = str(uuid.uuid4())
    await redis_client.set(
        f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{captcha_id}', code, ex=admin_settings.CAPTCHA_LOGIN_EXPIRE_SECONDS
    )
    return {'captcha_id':captcha_id,'image_type': img_type, 'image': img}

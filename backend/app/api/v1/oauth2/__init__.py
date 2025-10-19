#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from app.api.v1.oauth2.wx_app import router as wx_router
from app.api.v1.oauth2.ai_jxnu import router as jxnu_router


router = APIRouter(prefix='/oauth2')

router.include_router(wx_router, prefix='/wx', tags=['Wx OAuth2'])
router.include_router(jxnu_router, prefix='/jxnu', tags=['Jxnu OAuth2'])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.sapper import router as sapper_router
from app.api.v1.file import router as file_router
from app.api.v1.oauth2 import router as oauth2_router
from app.api.v1.llm import router as llm_router
from app.api.v1.course import v1 as course_router


v1 = APIRouter()

v1.include_router(auth_router)
v1.include_router(file_router)
v1.include_router(sapper_router)
v1.include_router(oauth2_router)
v1.include_router(llm_router)
v1.include_router(course_router)


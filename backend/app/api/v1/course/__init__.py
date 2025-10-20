#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from app.api.v1.course.course import router as course_router
from app.api.v1.course.course_grade import router as grade_router
from app.api.v1.course.course_subject import router as subject_router
from app.api.v1.course.course_resource import router as course_resource_router
from app.api.v1.course.course_resource_preview import router as course_resource_preview_router
from app.api.v1.course.course_agent import router as course_agent_router

v1 = APIRouter()

v1.include_router(course_router, prefix='/courses', tags=['课程管理'])
v1.include_router(grade_router, prefix='/grades', tags=['年级管理'])
v1.include_router(subject_router, prefix='/subjects', tags=['科目管理'])
v1.include_router(course_resource_router, prefix='/course-resources', tags=['课程资源管理'])
v1.include_router(course_resource_preview_router, prefix='/course-resources', tags=['课程资源预览'])
v1.include_router(course_agent_router, prefix='/course-agents', tags=['课程智能体管理'])
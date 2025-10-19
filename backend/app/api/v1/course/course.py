#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema.course import (
    CreateCourseParam,
    UpdateCourseParam,
    GetCourseListDetails,
    GetCourseDetails,
    CourseTreeNode,
)
from app.service.course_service import CourseService
from common.pagination import DependsPagination, paging_data
from common.response.response_schema import ResponseModel, response_base
from common.response.response_code import CustomResponse
from common.security.jwt import DependsJwtAuth
from common.security.rbac import DependsRBAC
from database.db_mysql import CurrentSession

router = APIRouter()


@router.get('/tree', summary='获取课程树结构')
async def get_course_tree(
    db: CurrentSession,
) -> ResponseModel:
    """获取年级-科目-课程的树形结构"""
    data = await CourseService.get_course_tree(db=db)
    return response_base.success(data=data)


@router.get('', summary='获取课程列表', dependencies=[DependsPagination])
async def get_course_list(
    db: CurrentSession,
    grade_id: Annotated[int | None, Query(description='年级ID')] = None,
    subject_id: Annotated[int | None, Query(description='科目ID')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> ResponseModel:
    """获取课程列表"""
    # 构建查询对象而不是执行查询
    stmt = CourseService.get_list_query_by_grade_subject(
        grade_id=grade_id,
        subject_id=subject_id,
        status=status
    )
    page_data = await paging_data(db, stmt, GetCourseListDetails)
    return response_base.success(data=page_data)


@router.get(
    '/my', 
    summary='获取我的课程列表', 
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ]
)
async def get_my_course_list(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """获取当前用户（教师）的课程列表"""
    current_user = request.user
    # 构建查询对象而不是执行查询
    stmt = CourseService.get_teacher_courses_query(teacher_uuid=current_user.uuid)
    page_data = await paging_data(db, stmt, GetCourseListDetails)
    return response_base.success(data=page_data)


@router.get('/{course_id}', summary='获取课程详情')
async def get_course_detail(
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
) -> ResponseModel:
    """获取课程详情"""
    data = await CourseService.get_course_detail(db=db, course_id=course_id)
    if not data:
        return response_base.fail(res=CustomResponse(code=404, msg='课程不存在'))
    
    # 转换为正确的schema格式
    course_detail = GetCourseDetails.model_validate(data)
    return response_base.success(data=course_detail)


@router.post('', summary='创建课程', dependencies=[DependsJwtAuth])
async def create_course(
    request: Request,
    db: CurrentSession,
    obj: CreateCourseParam,
) -> ResponseModel:
    """创建课程"""
    current_user = request.user
   
    try:
        # 直接调用CourseService的create_course方法，它内部会检查年级和科目是否存在
        data = await CourseService.create_course(db=db, obj_in=obj, teacher_uuid=current_user.uuid)
        return response_base.success(data=data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=400, msg=str(e)))


@router.put('/{course_id}', summary='更新课程', dependencies=[DependsJwtAuth])
async def update_course(
    request: Request,
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
    obj: UpdateCourseParam,
) -> ResponseModel:
    """更新课程"""
    current_user = request.user
    
    # 检查课程是否存在
    course = await CourseService.get(db=db, course_id=course_id)
    if not course:
        return response_base.fail(res=CustomResponse(code=404, msg='课程不存在'))
    
    # 检查权限：只有课程创建者或管理员可以修改
    if course.teacher_uuid != current_user.uuid and not current_user.is_superuser:
        return response_base.fail(res=CustomResponse(code=403, msg='权限不足'))
    
    data = await CourseService.update(db=db, course_id=course_id, obj_in=obj)
    return response_base.success(data=data)


@router.delete('/{course_id}', summary='删除课程', dependencies=[DependsJwtAuth])
async def delete_course(
    request: Request,
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
) -> ResponseModel:
    """删除课程"""
    current_user = request.user
    
    # 检查课程是否存在
    course = await CourseService.get(db=db, course_id=course_id)
    if not course:
        return response_base.fail(res=CustomResponse(code=404, msg='课程不存在'))
    
    # 检查权限：只有课程创建者或管理员可以删除
    if course.teacher_uuid != current_user.uuid and not current_user.is_superuser:
        return response_base.fail(res=CustomResponse(code=403, msg='权限不足'))
    
    await CourseService.delete(db=db, course_id=course_id)
    return response_base.success()
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
    
    # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
    try:
        course_data = {
            "id": data.id,
            "uuid": data.uuid,
            "title": data.title,
            "description": data.description,
            "cover_image": data.cover_image,
            "grade_id": data.grade_id,
            "subject_id": data.subject_id,
            "teacher_uuid": data.teacher_uuid,
            "sort_order": data.sort_order,
            "status": data.status,
            "created_time": data.created_time.isoformat() if data.created_time else None,
            "updated_time": data.updated_time.isoformat() if data.updated_time else None,
            "grade": {
                "id": data.grade.id,
                "name": data.grade.name,
                "code": data.grade.code,
                "sort_order": data.grade.sort_order,
                "status": data.grade.status,
                "created_time": data.grade.created_time.isoformat() if data.grade.created_time else None,
                "updated_time": data.grade.updated_time.isoformat() if data.grade.updated_time else None
            } if data.grade else None,
            "subject": {
                "id": data.subject.id,
                "name": data.subject.name,
                "code": data.subject.code,
                "sort_order": data.subject.sort_order,
                "status": data.subject.status,
                "created_time": data.subject.created_time.isoformat() if data.subject.created_time else None,
                "updated_time": data.subject.updated_time.isoformat() if data.subject.updated_time else None
            } if data.subject else None,
            "teacher": {
                "uuid": data.teacher.uuid,
                "username": data.teacher.username,
                "nickname": data.teacher.nickname,
                "email": data.teacher.email,
                "phone": data.teacher.phone,
                "avatar": data.teacher.avatar,
                "is_superuser": data.teacher.is_superuser,
                "is_staff": data.teacher.is_staff,
                "status": data.teacher.status,
                "created_time": data.teacher.created_time.isoformat() if data.teacher.created_time else None,
                "updated_time": data.teacher.updated_time.isoformat() if data.teacher.updated_time else None
            } if data.teacher else None,
            "resources": []
        }
        
        # 手动处理resources字段，避免异步关系访问问题
        if data.resources:
            for resource in data.resources:
                resource_data = {
                    "id": resource.id,
                    "uuid": resource.uuid,
                    "title": resource.title,
                    "resource_type": resource.resource_type,
                    "course_id": resource.course_id,
                    "upload_user_uuid": resource.upload_user_uuid,
                    "description": resource.description,
                    "file_name": resource.file_name,
                    "file_path": resource.file_path,
                    "file_size": resource.file_size,
                    "file_type": resource.file_type,
                    "download_count": resource.download_count,
                    "status": resource.status,
                    "sort_order": resource.sort_order,
                    "created_time": resource.created_time.isoformat() if resource.created_time else None,
                    "updated_time": resource.updated_time.isoformat() if resource.updated_time else None,
                    "course": None,  # 避免循环引用
                    "uploader": None  # 避免异步访问问题
                }
                course_data["resources"].append(resource_data)
        
        return response_base.success(data=course_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f'获取课程详情失败: {str(e)}'))


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
        course_obj = await CourseService.create_course(db=db, obj_in=obj, teacher_uuid=current_user.uuid)
        
        # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
        course_data = {
            "id": course_obj.id,
            "uuid": course_obj.uuid,
            "title": course_obj.title,
            "description": course_obj.description,
            "cover_image": course_obj.cover_image,
            "grade_id": course_obj.grade_id,
            "subject_id": course_obj.subject_id,
            "teacher_uuid": course_obj.teacher_uuid,
            "sort_order": course_obj.sort_order,
            "status": course_obj.status,
            "created_time": course_obj.created_time,
            "updated_time": course_obj.updated_time,
            "grade": {
                "id": course_obj.grade.id,
                "name": course_obj.grade.name,
                "code": course_obj.grade.code,
                "sort_order": course_obj.grade.sort_order,
                "status": course_obj.grade.status,
                "created_time": course_obj.grade.created_time,
                "updated_time": course_obj.grade.updated_time
            } if course_obj.grade else None,
            "subject": {
                "id": course_obj.subject.id,
                "name": course_obj.subject.name,
                "code": course_obj.subject.code,
                "description": course_obj.subject.description,
                "sort_order": course_obj.subject.sort_order,
                "status": course_obj.subject.status,
                "created_time": course_obj.subject.created_time,
                "updated_time": course_obj.subject.updated_time
            } if course_obj.subject else None,
            "teacher": {
                "uuid": course_obj.teacher.uuid,
                "username": course_obj.teacher.username,
                "nickname": course_obj.teacher.nickname,
                "email": course_obj.teacher.email,
                "phone": course_obj.teacher.phone,
                "avatar": course_obj.teacher.avatar,
                "is_superuser": course_obj.teacher.is_superuser,
                "is_staff": course_obj.teacher.is_staff,
                "status": course_obj.teacher.status,
                "created_time": course_obj.teacher.created_time,
                "updated_time": course_obj.teacher.updated_time
            } if course_obj.teacher else None,
            "resources": []  # 新创建的课程没有资源
        }
        
        return response_base.success(data=course_data)
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
    
    try:
        # 检查课程是否存在
        course = await CourseService.get_course_detail(db=db, course_id=course_id)
        if not course:
            return response_base.fail(res=CustomResponse(code=404, msg='课程不存在'))
        
        # 检查权限：只有课程创建者或管理员可以修改
        if course.teacher_uuid != current_user.uuid and not current_user.is_superuser:
            return response_base.fail(res=CustomResponse(code=403, msg='权限不足'))
        
        # 更新课程
        updated_course = await CourseService.update_course(db=db, course_id=course_id, obj_in=obj)
        
        # 重新获取完整的课程信息，包含关联数据
        course_detail = await CourseService.get_course_detail(db=db, course_id=course_id)
        
        # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
        course_data = {
            "id": course_detail.id,
            "uuid": course_detail.uuid,
            "title": course_detail.title,
            "description": course_detail.description,
            "cover_image": course_detail.cover_image,
            "grade_id": course_detail.grade_id,
            "subject_id": course_detail.subject_id,
            "teacher_uuid": course_detail.teacher_uuid,
            "sort_order": course_detail.sort_order,
            "status": course_detail.status,
            "created_time": course_detail.created_time,
            "updated_time": course_detail.updated_time,
            "grade": {
                "id": course_detail.grade.id,
                "name": course_detail.grade.name,
                "code": course_detail.grade.code,
                "sort_order": course_detail.grade.sort_order,
                "status": course_detail.grade.status,
                "created_time": course_detail.grade.created_time,
                "updated_time": course_detail.grade.updated_time
            } if course_detail.grade else None,
            "subject": {
                "id": course_detail.subject.id,
                "name": course_detail.subject.name,
                "code": course_detail.subject.code,
                "description": course_detail.subject.description,
                "sort_order": course_detail.subject.sort_order,
                "status": course_detail.subject.status,
                "created_time": course_detail.subject.created_time,
                "updated_time": course_detail.subject.updated_time
            } if course_detail.subject else None,
            "teacher": {
                "uuid": course_detail.teacher.uuid,
                "username": course_detail.teacher.username,
                "nickname": course_detail.teacher.nickname,
                "email": course_detail.teacher.email,
                "phone": course_detail.teacher.phone,
                "avatar": course_detail.teacher.avatar,
                "is_superuser": course_detail.teacher.is_superuser,
                "is_staff": course_detail.teacher.is_staff,
                "status": course_detail.teacher.status,
                "created_time": course_detail.teacher.created_time,
                "updated_time": course_detail.teacher.updated_time
            } if course_detail.teacher else None,
            "resources": [
                {
                    "id": resource.id,
                    "uuid": resource.uuid,
                    "title": resource.title,
                    "description": resource.description,
                    "file_path": resource.file_path,
                    "file_size": resource.file_size,
                    "file_type": resource.file_type,
                    "status": resource.status,
                    "sort_order": resource.sort_order,
                    "created_time": resource.created_time,
                    "updated_time": resource.updated_time
                } for resource in course_detail.resources
            ] if course_detail.resources else []
        }
        
        return response_base.success(data=course_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=400, msg=str(e)))


@router.delete('/{course_id}', summary='删除课程', dependencies=[DependsJwtAuth])
async def delete_course(
    request: Request,
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
) -> ResponseModel:
    """删除课程"""
    current_user = request.user
    
    # 检查课程是否存在
    course = await CourseService.get_course_detail(db=db, course_id=course_id)
    if not course:
        return response_base.fail(res=CustomResponse(code=404, msg='课程不存在'))
    
    # 检查权限：只有课程创建者或管理员可以删除
    if course.teacher_uuid != current_user.uuid and not current_user.is_superuser:
        return response_base.fail(res=CustomResponse(code=403, msg='权限不足'))
    
    await CourseService.delete_course(db=db, course_id=course_id)
    return response_base.success()
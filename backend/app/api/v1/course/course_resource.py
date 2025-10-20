#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Query, Path, Request, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.course_resource_service import CourseResourceService
from app.schema.course_resource import (
    CreateCourseResourceParam,
    UpdateCourseResourceParam,
    GetCourseResourceListDetails,
    GetCourseResourceDetails
)
from common.pagination import DependsPagination, paging_data
from common.response.response_schema import ResponseModel, response_base
from common.response.response_code import CustomResponse
from common.security.jwt import DependsJwtAuth
from database.db_mysql import CurrentSession

router = APIRouter()


@router.get('', summary='获取课程资源列表', dependencies=[DependsPagination])
async def get_course_resource_list(
    db: CurrentSession,
    course_id: Annotated[int, Query(description='课程ID')],
    resource_type: Annotated[str | None, Query(description='资源类型')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> ResponseModel:
    """获取课程资源列表"""
    from fastapi_pagination.ext.sqlalchemy import paginate
    
    stmt = CourseResourceService.get_course_resources_query(
        course_id=course_id,
        resource_type=resource_type,
        status=status
    )
    
    # 直接使用paginate获取分页数据，避免Pydantic验证
    paginated_result = await paginate(db, stmt)
    
    # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
    try:
        items = []
        for resource in paginated_result.items:
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
                "course": {
                    "id": resource.course.id,
                    "uuid": resource.course.uuid,
                    "title": resource.course.title,
                    "description": resource.course.description,
                    "cover_image": resource.course.cover_image,
                    "grade_id": resource.course.grade_id,
                    "subject_id": resource.course.subject_id,
                    "teacher_uuid": resource.course.teacher_uuid,
                    "sort_order": resource.course.sort_order,
                    "status": resource.course.status,
                    "created_time": resource.course.created_time.isoformat() if resource.course.created_time else None,
                    "updated_time": resource.course.updated_time.isoformat() if resource.course.updated_time else None
                } if resource.course else None,
                "uploader": {
                    "uuid": resource.uploader.uuid,
                    "username": resource.uploader.username,
                    "nickname": resource.uploader.nickname,
                    "email": resource.uploader.email,
                    "phone": resource.uploader.phone,
                    "avatar": resource.uploader.avatar,
                    "is_superuser": resource.uploader.is_superuser,
                    "is_staff": resource.uploader.is_staff,
                    "status": resource.uploader.status,
                    "created_time": resource.uploader.created_time.isoformat() if resource.uploader.created_time else None,
                    "updated_time": resource.uploader.updated_time.isoformat() if resource.uploader.updated_time else None
                } if resource.uploader else None
            }
            items.append(resource_data)
        
        # 构建分页响应数据
        page_data = {
            "items": items,
            "total": paginated_result.total,
            "page": paginated_result.page,
            "size": paginated_result.size,
            "total_pages": paginated_result.total_pages,
            "links": paginated_result.links
        }
        
        return response_base.success(data=page_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f'获取课程资源列表失败: {str(e)}'))


@router.get('/{resource_id}', summary='获取课程资源详情')
async def get_course_resource_detail(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
) -> ResponseModel:
    """获取课程资源详情"""
    data = await CourseResourceService.get_resource_detail(db=db, resource_id=resource_id)
    if not data:
        return response_base.fail(res=CustomResponse(code=404, msg='资源不存在'))
    
    # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
    try:
        resource_data = {
            "id": data.id,
            "uuid": data.uuid,
            "title": data.title,
            "resource_type": data.resource_type,
            "course_id": data.course_id,
            "upload_user_uuid": data.upload_user_uuid,
            "description": data.description,
            "file_name": data.file_name,
            "file_path": data.file_path,
            "file_size": data.file_size,
            "file_type": data.file_type,
            "download_count": data.download_count,
            "status": data.status,
            "sort_order": data.sort_order,
            "created_time": data.created_time.isoformat() if data.created_time else None,
            "updated_time": data.updated_time.isoformat() if data.updated_time else None,
            "course": {
                "id": data.course.id,
                "uuid": data.course.uuid,
                "title": data.course.title,
                "description": data.course.description,
                "cover_image": data.course.cover_image,
                "grade_id": data.course.grade_id,
                "subject_id": data.course.subject_id,
                "teacher_uuid": data.course.teacher_uuid,
                "sort_order": data.course.sort_order,
                "status": data.course.status,
                "created_time": data.course.created_time.isoformat() if data.course.created_time else None,
                "updated_time": data.course.updated_time.isoformat() if data.course.updated_time else None
            } if data.course else None,
            "uploader": {
                "uuid": data.uploader.uuid,
                "username": data.uploader.username,
                "nickname": data.uploader.nickname,
                "email": data.uploader.email,
                "phone": data.uploader.phone,
                "avatar": data.uploader.avatar,
                "is_superuser": data.uploader.is_superuser,
                "is_staff": data.uploader.is_staff,
                "status": data.uploader.status,
                "created_time": data.uploader.created_time.isoformat() if data.uploader.created_time else None,
                "updated_time": data.uploader.updated_time.isoformat() if data.uploader.updated_time else None
            } if data.uploader else None
        }
        
        return response_base.success(data=resource_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f'获取资源详情失败: {str(e)}'))


@router.get('/uuid/{uuid}', summary='根据UUID获取课程资源详情')
async def get_course_resource_by_uuid(
    db: CurrentSession,
    uuid: Annotated[str, Path(description='资源UUID')]
) -> ResponseModel:
    """根据UUID获取课程资源详情"""
    data = await CourseResourceService.get_resource_by_uuid(db=db, uuid=uuid)
    if not data:
        return response_base.fail(res=CustomResponse(code=404, msg='资源不存在'))
    
    # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
    try:
        resource_data = {
            "id": data.id,
            "uuid": data.uuid,
            "title": data.title,
            "resource_type": data.resource_type,
            "course_id": data.course_id,
            "upload_user_uuid": data.upload_user_uuid,
            "description": data.description,
            "file_name": data.file_name,
            "file_path": data.file_path,
            "file_size": data.file_size,
            "file_type": data.file_type,
            "download_count": data.download_count,
            "status": data.status,
            "sort_order": data.sort_order,
            "created_time": data.created_time.isoformat() if data.created_time else None,
            "updated_time": data.updated_time.isoformat() if data.updated_time else None,
            "course": {
                "id": data.course.id,
                "uuid": data.course.uuid,
                "title": data.course.title,
                "description": data.course.description,
                "cover_image": data.course.cover_image,
                "grade_id": data.course.grade_id,
                "subject_id": data.course.subject_id,
                "teacher_uuid": data.course.teacher_uuid,
                "sort_order": data.course.sort_order,
                "status": data.course.status,
                "created_time": data.course.created_time.isoformat() if data.course.created_time else None,
                "updated_time": data.course.updated_time.isoformat() if data.course.updated_time else None
            } if data.course else None,
            "uploader": {
                "uuid": data.uploader.uuid,
                "username": data.uploader.username,
                "nickname": data.uploader.nickname,
                "email": data.uploader.email,
                "phone": data.uploader.phone,
                "avatar": data.uploader.avatar,
                "is_superuser": data.uploader.is_superuser,
                "is_staff": data.uploader.is_staff,
                "status": data.uploader.status,
                "created_time": data.uploader.created_time.isoformat() if data.uploader.created_time else None,
                "updated_time": data.uploader.updated_time.isoformat() if data.uploader.updated_time else None
            } if data.uploader else None
        }
        
        return response_base.success(data=resource_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f'获取资源详情失败: {str(e)}'))


@router.post('', summary='创建课程资源', dependencies=[DependsJwtAuth])
async def create_course_resource(
    request: Request,
    db: CurrentSession,
    title: Annotated[str, Form(description='资源标题')],
    resource_type: Annotated[str, Form(description='资源类型')],
    course_id: Annotated[int, Form(description='课程ID')],
    description: Annotated[str | None, Form(description='资源描述')] = None,
    sort_order: Annotated[int, Form(description='排序')] = 1,
    status: Annotated[int, Form(description='状态')] = 1,
    file: UploadFile = File(..., description='上传的文件')
) -> ResponseModel:
    """创建课程资源"""
    current_user = request.user
    
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 创建上传目录
        upload_dir = "static/uploads/course_resources"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_extension_with_dot = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension_with_dot}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # 获取文件信息
        file_type = file.content_type or 'application/octet-stream'
        
        # 构建创建参数
        from app.schema.course_resource import CreateCourseResourceParam
        obj_in = CreateCourseResourceParam(
            title=title,
            resource_type=resource_type,
            course_id=course_id,
            description=description,
            file_name=file.filename,
            file_path=f"/uploads/course_resources/{unique_filename}",  # 存储相对路径
            file_size=file_size,
            file_type=file_type,
            sort_order=sort_order,
            status=status
        )
        
        resource_obj = await CourseResourceService.create_resource(
            db=db, 
            obj_in=obj_in, 
            upload_user_uuid=current_user.uuid
        )
        
        # 手动构建响应数据，避免Pydantic验证时的异步关系访问问题
        resource_data = {
            "id": resource_obj.id,
            "uuid": resource_obj.uuid,
            "title": resource_obj.title,
            "resource_type": resource_obj.resource_type,
            "course_id": resource_obj.course_id,
            "upload_user_uuid": resource_obj.upload_user_uuid,
            "description": resource_obj.description,
            "file_name": resource_obj.file_name,
            "file_path": resource_obj.file_path,
            "file_size": resource_obj.file_size,
            "file_type": resource_obj.file_type,
            "download_count": resource_obj.download_count,
            "status": resource_obj.status,
            "sort_order": resource_obj.sort_order,
            "created_time": resource_obj.created_time.isoformat() if resource_obj.created_time else None,
            "updated_time": resource_obj.updated_time.isoformat() if resource_obj.updated_time else None
        }
        
        return response_base.success(data=resource_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=400, msg=str(e)))


@router.put('/{resource_id}', summary='更新课程资源')
async def update_course_resource(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')],
    obj_in: UpdateCourseResourceParam
) -> ResponseModel:
    """更新课程资源"""
    data = await CourseResourceService.update_resource(
        db=db,
        resource_id=resource_id,
        obj_in=obj_in
    )
    return response_base.success(data=GetCourseResourceDetails.from_orm(data))


@router.delete('/{resource_id}', summary='删除课程资源')
async def delete_course_resource(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
) -> ResponseModel:
    """删除课程资源"""
    await CourseResourceService.delete_resource(db=db, resource_id=resource_id)
    return response_base.success()


@router.get('/{resource_id}/download', summary='下载课程资源')
async def download_course_resource(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
):
    """下载课程资源"""
    import os
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    
    # 获取资源信息
    resource = await CourseResourceService.get_resource_detail(db=db, resource_id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    # 构建文件完整路径
    file_path = os.path.join("static", resource.file_path.lstrip("/"))
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 增加下载次数
    await CourseResourceService.increment_download_count(db=db, resource_id=resource_id)
    
    # 返回文件
    return FileResponse(
        path=file_path,
        filename=resource.file_name,
        media_type='application/octet-stream'
    )


@router.get('/user/{uploader_id}', summary='获取用户上传的资源列表', dependencies=[DependsPagination])
async def get_user_resources(
    db: CurrentSession,
    uploader_id: Annotated[str, Path(description='上传者ID')]
) -> ResponseModel:
    """获取用户上传的资源列表"""
    data = await CourseResourceService.get_user_resources(
        db=db,
        uploader_id=uploader_id
    )
    page_data = await paging_data(db, data, GetCourseResourceListDetails)
    return response_base.success(data=page_data)
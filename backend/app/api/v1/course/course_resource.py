#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Query, Path
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
    stmt = CourseResourceService.get_course_resources_query(
        course_id=course_id,
        resource_type=resource_type,
        status=status
    )
    page_data = await paging_data(db, stmt, GetCourseResourceListDetails)
    return response_base.success(data=page_data)


@router.get('/{resource_id}', summary='获取课程资源详情')
async def get_course_resource_detail(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
) -> ResponseModel:
    """获取课程资源详情"""
    data = await CourseResourceService.get_resource_detail(db=db, resource_id=resource_id)
    return response_base.success(data=GetCourseResourceDetails.from_orm(data))


@router.get('/uuid/{uuid}', summary='根据UUID获取课程资源详情')
async def get_course_resource_by_uuid(
    db: CurrentSession,
    uuid: Annotated[str, Path(description='资源UUID')]
) -> ResponseModel:
    """根据UUID获取课程资源详情"""
    data = await CourseResourceService.get_resource_by_uuid(db=db, uuid=uuid)
    return response_base.success(data=GetCourseResourceDetails.from_orm(data))


@router.post('', summary='创建课程资源')
async def create_course_resource(
    db: CurrentSession,
    obj_in: CreateCourseResourceParam
) -> ResponseModel:
    """创建课程资源"""
    data = await CourseResourceService.create_resource(db=db, obj_in=obj_in)
    return response_base.success(data=GetCourseResourceDetails.from_orm(data))


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


@router.post('/{resource_id}/download', summary='下载课程资源')
async def download_course_resource(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
) -> ResponseModel:
    """下载课程资源（增加下载次数）"""
    data = await CourseResourceService.download_resource(db=db, resource_id=resource_id)
    return response_base.success(data=GetCourseResourceDetails.from_orm(data))


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
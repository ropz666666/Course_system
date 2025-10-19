#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.course_subject_service import CourseSubjectService
from app.schema.course_subject import (
    CreateCourseSubjectParam,
    UpdateCourseSubjectParam,
    GetCourseSubjectListDetails
)
from common.pagination import DependsPagination, paging_data
from common.response.response_schema import ResponseModel, response_base
from common.response.response_code import CustomResponse
from database.db_mysql import CurrentSession

router = APIRouter()


@router.get('', summary='获取科目列表', dependencies=[DependsPagination])
async def get_subject_list(
    db: CurrentSession,
) -> ResponseModel:
    """获取科目列表"""
    stmt = CourseSubjectService.get_subject_list_query()
    page_data = await paging_data(db, stmt, GetCourseSubjectListDetails)
    return response_base.success(data=page_data)


@router.get('/{subject_id}', summary='获取科目详情')
async def get_subject_detail(
    db: CurrentSession,
    subject_id: Annotated[int, Path(description='科目ID')]
) -> ResponseModel:
    """获取科目详情"""
    data = await CourseSubjectService.get_subject_detail(db=db, subject_id=subject_id)
    return response_base.success(data=GetCourseSubjectListDetails.from_orm(data))


@router.post('', summary='创建科目')
async def create_subject(
    db: CurrentSession,
    obj_in: CreateCourseSubjectParam
) -> ResponseModel:
    """创建科目"""
    data = await CourseSubjectService.create_subject(db=db, obj_in=obj_in)
    return response_base.success(data=GetCourseSubjectListDetails.from_orm(data))


@router.put('/{subject_id}', summary='更新科目')
async def update_subject(
    db: CurrentSession,
    subject_id: Annotated[int, Path(description='科目ID')],
    obj_in: UpdateCourseSubjectParam
) -> ResponseModel:
    """更新科目"""
    data = await CourseSubjectService.update_subject(
        db=db,
        subject_id=subject_id,
        obj_in=obj_in
    )
    return response_base.success(data=GetCourseSubjectListDetails.from_orm(data))


@router.delete('/{subject_id}', summary='删除科目')
async def delete_subject(
    db: CurrentSession,
    subject_id: Annotated[int, Path(description='科目ID')]
) -> ResponseModel:
    """删除科目"""
    await CourseSubjectService.delete_subject(db=db, subject_id=subject_id)
    return response_base.success()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.course_grade_service import CourseGradeService
from app.schema.course_grade import (
    CreateCourseGradeParam,
    UpdateCourseGradeParam,
    GetCourseGradeListDetails
)
from common.pagination import DependsPagination, paging_data
from common.response.response_schema import ResponseModel, response_base
from common.response.response_code import CustomResponse
from database.db_mysql import CurrentSession

router = APIRouter()


@router.get('', summary='获取年级列表', dependencies=[DependsPagination])
async def get_grade_list(
    db: CurrentSession,
) -> ResponseModel:
    """获取年级列表"""
    stmt = CourseGradeService.get_grade_list_query()
    page_data = await paging_data(db, stmt, GetCourseGradeListDetails)
    return response_base.success(data=page_data)


@router.get('/{grade_id}', summary='获取年级详情')
async def get_grade_detail(
    db: CurrentSession,
    grade_id: Annotated[int, Path(description='年级ID')]
) -> ResponseModel:
    """获取年级详情"""
    data = await CourseGradeService.get_grade_detail(db=db, grade_id=grade_id)
    return response_base.success(data=GetCourseGradeListDetails.from_orm(data))


@router.post('', summary='创建年级')
async def create_grade(
    db: CurrentSession,
    obj_in: CreateCourseGradeParam
) -> ResponseModel:
    """创建年级"""
    data = await CourseGradeService.create_grade(db=db, obj_in=obj_in)
    return response_base.success(data=GetCourseGradeListDetails.from_orm(data))


@router.put('/{grade_id}', summary='更新年级')
async def update_grade(
    db: CurrentSession,
    grade_id: Annotated[int, Path(description='年级ID')],
    obj_in: UpdateCourseGradeParam
) -> ResponseModel:
    """更新年级"""
    data = await CourseGradeService.update_grade(
        db=db,
        grade_id=grade_id,
        obj_in=obj_in
    )
    return response_base.success(data=GetCourseGradeListDetails.from_orm(data))


@router.delete('/{grade_id}', summary='删除年级')
async def delete_grade(
    db: CurrentSession,
    grade_id: Annotated[int, Path(description='年级ID')]
) -> ResponseModel:
    """删除年级"""
    await CourseGradeService.delete_grade(db=db, grade_id=grade_id)
    return response_base.success()
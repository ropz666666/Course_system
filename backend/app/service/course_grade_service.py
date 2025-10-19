#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_course_grade import course_grade
from app.model.course.course_grade import CourseGrade
from app.schema.course_grade import CreateCourseGradeParam, UpdateCourseGradeParam
from common.exception import errors


class CourseGradeService:
    @staticmethod
    def get_grade_list_query(*, status: Optional[int] = None):
        """获取年级列表的查询对象"""
        return course_grade.get_list_query_by_status(status=status)

    @staticmethod
    async def get_grade_detail(db: AsyncSession, *, grade_id: int) -> Optional[CourseGrade]:
        """获取年级详情"""
        return await course_grade.get(db, id=grade_id)

    @staticmethod
    async def get_grade_list(
        db: AsyncSession,
        *,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseGrade]:
        """获取年级列表"""
        return await course_grade.get_list_by_status(
            db,
            status=status,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def create_grade(
        db: AsyncSession,
        *,
        obj_in: CreateCourseGradeParam
    ) -> CourseGrade:
        """创建年级"""
        # 检查编码是否已存在
        if await course_grade.check_code_exists(db, code=obj_in.code):
            raise errors.ForbiddenError(msg="年级编码已存在")
        
        # 创建年级
        grade_data = obj_in.dict()
        return await course_grade.create(db, obj_in=grade_data)

    @staticmethod
    async def update_grade(
        db: AsyncSession,
        *,
        grade_id: int,
        obj_in: UpdateCourseGradeParam
    ) -> CourseGrade:
        """更新年级"""
        # 获取年级
        grade_obj = await course_grade.get(db, id=grade_id)
        if not grade_obj:
            raise errors.NotFoundError(msg="年级不存在")
        
        # 如果更新编码，检查编码是否已存在
        if obj_in.code is not None and obj_in.code != grade_obj.code:
            if await course_grade.check_code_exists(db, code=obj_in.code, exclude_id=grade_id):
                raise errors.ForbiddenError(msg="年级编码已存在")
        
        # 更新年级
        update_data = obj_in.dict(exclude_unset=True)
        return await course_grade.update(db, db_obj=grade_obj, obj_in=update_data)

    @staticmethod
    async def delete_grade(db: AsyncSession, *, grade_id: int) -> bool:
        """删除年级"""
        grade_obj = await course_grade.get(db, id=grade_id)
        if not grade_obj:
            raise errors.NotFoundError(msg="年级不存在")
        
        # TODO: 检查是否有关联的课程，如果有则不允许删除
        
        await course_grade.remove(db, id=grade_id)
        return True
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_course_subject import course_subject
from app.model.course.course_subject import CourseSubject
from app.schema.course_subject import CreateCourseSubjectParam, UpdateCourseSubjectParam
from common.exception import errors


class CourseSubjectService:
    @staticmethod
    def get_subject_list_query(*, status: Optional[int] = None):
        """获取科目列表的查询对象"""
        return course_subject.get_list_query_by_status(status=status)

    @staticmethod
    async def get_subject_detail(db: AsyncSession, *, subject_id: int) -> Optional[CourseSubject]:
        """获取科目详情"""
        return await course_subject.get(db, id=subject_id)

    @staticmethod
    async def get_subject_list(
        db: AsyncSession,
        *,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseSubject]:
        """获取科目列表"""
        return await course_subject.get_list_by_status(
            db,
            status=status,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def create_subject(
        db: AsyncSession,
        *,
        obj_in: CreateCourseSubjectParam
    ) -> CourseSubject:
        """创建科目"""
        # 检查编码是否已存在
        if await course_subject.check_code_exists(db, code=obj_in.code):
            raise errors.ForbiddenError(msg="科目编码已存在")
        
        # 创建科目
        subject_data = obj_in.dict()
        return await course_subject.create(db, obj_in=subject_data)

    @staticmethod
    async def update_subject(
        db: AsyncSession,
        *,
        subject_id: int,
        obj_in: UpdateCourseSubjectParam
    ) -> CourseSubject:
        """更新科目"""
        # 获取科目
        subject_obj = await course_subject.get(db, id=subject_id)
        if not subject_obj:
            raise errors.NotFoundError(msg="科目不存在")
        
        # 如果更新编码，检查编码是否已存在
        if obj_in.code is not None and obj_in.code != subject_obj.code:
            if await course_subject.check_code_exists(db, code=obj_in.code, exclude_id=subject_id):
                raise errors.ForbiddenError(msg="科目编码已存在")
        
        # 更新科目
        update_data = obj_in.dict(exclude_unset=True)
        return await course_subject.update(db, db_obj=subject_obj, obj_in=update_data)

    @staticmethod
    async def delete_subject(db: AsyncSession, *, subject_id: int) -> bool:
        """删除科目"""
        subject_obj = await course_subject.get(db, id=subject_id)
        if not subject_obj:
            raise errors.NotFoundError(msg="科目不存在")
        
        # TODO: 检查是否有关联的课程，如果有则不允许删除
        
        await course_subject.remove(db, id=subject_id)
        return True
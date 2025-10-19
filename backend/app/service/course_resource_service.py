#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_course_resource import course_resource
from app.crud.crud_course import course
from app.model.course.course_resource import CourseResource
from app.schema.course_resource import CreateCourseResourceParam, UpdateCourseResourceParam
from common.exception import errors


class CourseResourceService:
    @staticmethod
    def get_course_resources_query(
        *,
        course_id: int,
        resource_type: Optional[str] = None,
        status: Optional[int] = None
    ):
        """获取课程资源列表的查询对象"""
        return course_resource.get_by_course_query(
            course_id=course_id,
            resource_type=resource_type,
            status=status
        )

    @staticmethod
    async def get_resource_detail(db: AsyncSession, *, resource_id: int) -> Optional[CourseResource]:
        """获取资源详情"""
        return await course_resource.get_by_id(db, id=resource_id)

    @staticmethod
    async def get_resource_by_uuid(db: AsyncSession, *, uuid: str) -> Optional[CourseResource]:
        """根据UUID获取资源详情"""
        return await course_resource.get_by_uuid(db, uuid=uuid)

    @staticmethod
    async def get_course_resources(
        db: AsyncSession,
        *,
        course_id: int,
        resource_type: Optional[str] = None,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseResource]:
        """获取课程资源列表"""
        return await course_resource.get_by_course(
            db,
            course_id=course_id,
            resource_type=resource_type,
            status=status,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def get_user_resources(
        db: AsyncSession,
        *,
        uploader_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseResource]:
        """获取用户上传的资源列表"""
        return await course_resource.get_by_uploader(
            db,
            uploader_id=uploader_id,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def create_resource(
        db: AsyncSession,
        *,
        obj_in: CreateCourseResourceParam
    ) -> CourseResource:
        """创建课程资源"""
        # 检查课程是否存在
        course_obj = await course.get(db, id=obj_in.course_id)
        if not course_obj:
            raise errors.NotFoundError(msg="课程不存在")
        
        # 创建资源
        resource_data = obj_in.dict()
        return await course_resource.create(db, obj_in=resource_data)

    @staticmethod
    async def update_resource(
        db: AsyncSession,
        *,
        resource_id: int,
        obj_in: UpdateCourseResourceParam
    ) -> CourseResource:
        """更新课程资源"""
        # 获取资源
        resource_obj = await course_resource.get(db, id=resource_id)
        if not resource_obj:
            raise errors.NotFoundError(msg="资源不存在")
        
        # 如果更新课程ID，检查课程是否存在
        if obj_in.course_id is not None:
            course_obj = await course.get(db, id=obj_in.course_id)
            if not course_obj:
                raise errors.NotFoundError(msg="课程不存在")
        
        # 更新资源
        update_data = obj_in.dict(exclude_unset=True)
        return await course_resource.update(db, db_obj=resource_obj, obj_in=update_data)

    @staticmethod
    async def delete_resource(db: AsyncSession, *, resource_id: int) -> bool:
        """删除课程资源"""
        resource_obj = await course_resource.get(db, id=resource_id)
        if not resource_obj:
            raise errors.NotFoundError(msg="资源不存在")
        
        await course_resource.remove(db, id=resource_id)
        return True

    @staticmethod
    async def download_resource(db: AsyncSession, *, resource_id: int) -> Optional[CourseResource]:
        """下载资源（增加下载次数）"""
        return await course_resource.increment_download_count(db, resource_id=resource_id)
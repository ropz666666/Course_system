#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional, Union, List

from sqlalchemy import select, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy_crud_plus import CRUDPlus

from app.model.course.course_resource import CourseResource


class CRUDCourseResource(CRUDPlus[CourseResource]):
    async def get_by_uuid(self, db: AsyncSession, *, uuid: str) -> Optional[CourseResource]:
        """根据UUID获取资源"""
        stmt = (
            select(CourseResource)
            .options(
                joinedload(CourseResource.course),
                joinedload(CourseResource.uploader)
            )
            .where(CourseResource.uuid == uuid)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_course_query(
        self,
        *,
        course_id: int,
        resource_type: Optional[str] = None,
        status: Optional[int] = None
    ):
        """根据课程ID获取资源列表的查询对象"""
        stmt = (
            select(CourseResource)
            .options(joinedload(CourseResource.uploader))
            .where(CourseResource.course_id == course_id)
        )
        
        conditions = []
        if resource_type is not None:
            conditions.append(CourseResource.resource_type == resource_type)
        if status is not None:
            conditions.append(CourseResource.status == status)
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.order_by(desc(CourseResource.created_time))
        return stmt

    async def get_by_course(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        resource_type: Optional[str] = None,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseResource]:
        """根据课程ID获取资源列表"""
        stmt = (
            select(CourseResource)
            .options(joinedload(CourseResource.uploader))
            .where(CourseResource.course_id == course_id)
        )
        
        conditions = []
        if resource_type is not None:
            conditions.append(CourseResource.resource_type == resource_type)
        if status is not None:
            conditions.append(CourseResource.status == status)
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.order_by(asc(CourseResource.sort_order), desc(CourseResource.created_time))
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_uploader(
        self, 
        db: AsyncSession, 
        *, 
        uploader_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CourseResource]:
        """获取用户上传的资源列表"""
        stmt = (
            select(CourseResource)
            .options(
                joinedload(CourseResource.course),
                joinedload(CourseResource.uploader)
            )
            .where(CourseResource.upload_user_uuid == uploader_id)
            .order_by(desc(CourseResource.created_time))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def increment_download_count(
        self,
        db: AsyncSession,
        *,
        resource_id: int
    ) -> Optional[CourseResource]:
        """增加下载次数"""
        resource = await self.get(db, id=resource_id)
        if resource:
            resource.download_count += 1
            await db.commit()
            await db.refresh(resource)
        return resource


course_resource = CRUDCourseResource(CourseResource)
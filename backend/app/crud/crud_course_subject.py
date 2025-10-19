#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional, Union, List

from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from app.model.course.course_subject import CourseSubject


class CRUDCourseSubject(CRUDPlus[CourseSubject]):
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[CourseSubject]:
        """根据ID获取科目"""
        stmt = select(CourseSubject).where(CourseSubject.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[CourseSubject]:
        """根据编码获取科目"""
        stmt = select(CourseSubject).where(CourseSubject.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def get_list_query_by_status(self, *, status: Optional[int] = None):
        """根据状态获取科目列表的查询对象"""
        stmt = select(CourseSubject)
        
        if status is not None:
            stmt = stmt.where(CourseSubject.status == status)
        
        stmt = stmt.order_by(asc(CourseSubject.sort_order))
        return stmt

    async def get_list_by_status(
        self, 
        db: AsyncSession, 
        *, 
        status: Optional[int] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CourseSubject]:
        """根据状态获取科目列表"""
        stmt = select(CourseSubject)
        
        if status is not None:
            stmt = stmt.where(CourseSubject.status == status)
        
        stmt = stmt.order_by(asc(CourseSubject.sort_order)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def check_code_exists(
        self,
        db: AsyncSession,
        *,
        code: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """检查编码是否已存在"""
        stmt = Select(CourseSubject).where(CourseSubject.code == code)
        if exclude_id:
            stmt = stmt.where(CourseSubject.id != exclude_id)
            
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None


course_subject = CRUDCourseSubject(CourseSubject)
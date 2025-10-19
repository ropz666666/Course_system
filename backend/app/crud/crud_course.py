#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional, Union, List

from sqlalchemy import Select, and_, or_, desc, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy_crud_plus import CRUDPlus

from app.model.course.course import Course


class CRUDCourse(CRUDPlus[Course]):
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[Course]:
        """根据ID获取课程详情，包含关联数据"""
        stmt = (
            select(Course)
            .options(
                joinedload(Course.grade),
                joinedload(Course.subject),
                joinedload(Course.teacher),
                selectinload(Course.resources),
            )
            .where(Course.id == id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def get_list_query_by_grade_subject(
        self,
        *,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        status: Optional[int] = None,
    ):
        """根据年级和科目构建课程查询对象，用于分页"""
        stmt = (
            select(Course)
            .options(
                joinedload(Course.grade),
                joinedload(Course.subject),
                joinedload(Course.teacher)
            )
        )
        
        filters = []
        if grade_id is not None:
            filters.append(Course.grade_id == grade_id)
        if subject_id is not None:
            filters.append(Course.subject_id == subject_id)
        if status is not None:
            filters.append(Course.status == status)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        return stmt

    async def get_by_grade_subject(
        self, 
        db: AsyncSession, 
        *, 
        grade_id: Optional[int] = None, 
        subject_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Course]:
        """根据年级和科目获取课程列表"""
        stmt = (
            select(Course)
            .options(
                joinedload(Course.grade),
                joinedload(Course.subject),
                joinedload(Course.teacher)
            )
        )
        
        filters = []
        if grade_id is not None:
            filters.append(Course.grade_id == grade_id)
        if subject_id is not None:
            filters.append(Course.subject_id == subject_id)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    def get_teacher_query(self, *, teacher_uuid: str):
        """获取教师课程的查询对象，用于分页"""
        stmt = (
            select(Course)
            .options(
                joinedload(Course.grade),
                joinedload(Course.subject),
                joinedload(Course.teacher)
            )
            .where(Course.teacher_uuid == teacher_uuid)
        )
        return stmt

    async def get_by_teacher(
        self, 
        db: AsyncSession, 
        *, 
        teacher_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Course]:
        """获取教师的课程列表"""
        stmt = (
            select(Course)
            .options(
                joinedload(Course.grade),
                joinedload(Course.subject),
                joinedload(Course.teacher)
            )
            .where(Course.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_with_relations(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any]
    ) -> Course:
        """创建课程"""
        db_obj = Course(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_with_relations(
        self,
        db: AsyncSession,
        *,
        db_obj: Course,
        obj_in: Union[Dict[str, Any], Course]
    ) -> Course:
        """更新课程"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
                
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


course = CRUDCourse(Course)
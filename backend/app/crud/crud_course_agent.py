#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from sqlalchemy_crud_plus import CRUDPlus
from app.model.course.course_agent import CourseAgent
from app.model.agent.agent_model import Agent
from app.model.course.course import Course


class CRUDCourseAgent(CRUDPlus[CourseAgent]):
    
    async def create_course_agent(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        agent_uuid: str,
        migrated_by: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> CourseAgent:
        """创建课程智能体"""
        # 检查智能体是否已经在该课程中
        existing = await self.get_by_course_and_agent(
            db=db, course_id=course_id, agent_uuid=agent_uuid
        )
        if existing:
            raise ValueError("该智能体已经在此课程中")
        
        # 如果没有提供标题和描述，从原智能体获取
        if not title or not description:
            agent_stmt = select(Agent).where(Agent.uuid == agent_uuid)
            agent_result = await db.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            if not agent:
                raise ValueError("智能体不存在")
            
            if not title:
                title = agent.name
            if not description:
                description = agent.description
        
        obj_in = {
            "course_id": course_id,
            "agent_uuid": agent_uuid,
            "migrated_by": migrated_by,
            "title": title,
            "description": description
        }
        
        db_obj = CourseAgent(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_course_and_agent(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        agent_uuid: str
    ) -> Optional[CourseAgent]:
        """根据课程ID和智能体UUID获取课程智能体"""
        stmt = select(CourseAgent).where(
            CourseAgent.course_id == course_id,
            CourseAgent.agent_uuid == agent_uuid
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_agents_by_course(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        status: Optional[int] = None
    ) -> List[CourseAgent]:
        """获取课程的所有智能体"""
        stmt = (
            select(CourseAgent)
            .options(
                joinedload(CourseAgent.agent),
                joinedload(CourseAgent.migrator)
            )
            .where(CourseAgent.course_id == course_id)
        )
        
        if status is not None:
            stmt = stmt.where(CourseAgent.status == status)
        
        stmt = stmt.order_by(CourseAgent.sort_order, CourseAgent.created_time)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def get_courses_by_agent(
        self,
        db: AsyncSession,
        *,
        agent_uuid: str,
        status: Optional[int] = None
    ) -> List[CourseAgent]:
        """获取智能体所在的所有课程"""
        stmt = (
            select(CourseAgent)
            .options(
                joinedload(CourseAgent.course),
                joinedload(CourseAgent.migrator)
            )
            .where(CourseAgent.agent_uuid == agent_uuid)
        )
        
        if status is not None:
            stmt = stmt.where(CourseAgent.status == status)
        
        stmt = stmt.order_by(CourseAgent.created_time.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def remove_agent_from_course(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        agent_uuid: str
    ) -> bool:
        """从课程中移除智能体"""
        course_agent = await self.get_by_course_and_agent(
            db=db, course_id=course_id, agent_uuid=agent_uuid
        )
        if not course_agent:
            return False
        
        await db.delete(course_agent)
        await db.commit()
        return True

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: CourseAgent,
        obj_in: Dict[str, Any]
    ) -> CourseAgent:
        """更新课程智能体信息"""
        # 使用基类的 update_model 方法更新数据
        await self.update_model(
            session=db,
            pk=db_obj.id,
            obj=obj_in,
            commit=True
        )
        
        # 刷新对象以获取最新数据
        await db.refresh(db_obj)
        return db_obj


course_agent = CRUDCourseAgent(CourseAgent)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_course_agent import course_agent
from app.crud.crud_course import course
from app.crud.crud_agent import agent_dao as agent_crud
from app.model.course.course_agent import CourseAgent
from app.schema.course_agent import MigrateAgentToCourseParam


class CourseAgentService:
    
    @staticmethod
    async def migrate_agent_to_course(
        db: AsyncSession,
        *,
        obj_in: MigrateAgentToCourseParam,
        migrated_by: str
    ) -> CourseAgent:
        """将智能体迁移到课程"""
        # 验证课程是否存在
        course_obj = await course.get(db=db, id=obj_in.course_id)
        if not course_obj:
            raise ValueError("课程不存在")
        
        # 验证智能体是否存在
        agent_obj = await agent_crud.get_by_uuid(db=db, uuid=obj_in.agent_uuid)
        if not agent_obj:
            raise ValueError("智能体不存在")
        
        # 创建课程智能体关联
        return await course_agent.create_course_agent(
            db=db,
            course_id=obj_in.course_id,
            agent_uuid=obj_in.agent_uuid,
            migrated_by=migrated_by,
            title=obj_in.title,
            description=obj_in.description
        )
    
    @staticmethod
    async def get_course_agents(
        db: AsyncSession,
        *,
        course_id: int,
        status: Optional[int] = None
    ) -> List[CourseAgent]:
        """获取课程的智能体列表"""
        return await course_agent.get_agents_by_course(
            db=db, course_id=course_id, status=status
        )
    
    @staticmethod
    async def get_agent_courses(
        db: AsyncSession,
        *,
        agent_uuid: str,
        status: Optional[int] = None
    ) -> List[CourseAgent]:
        """获取智能体所在的课程列表"""
        return await course_agent.get_courses_by_agent(
            db=db, agent_uuid=agent_uuid, status=status
        )
    
    @staticmethod
    async def remove_agent_from_course(
        db: AsyncSession,
        *,
        course_id: int,
        agent_uuid: str
    ) -> bool:
        """从课程中移除智能体"""
        return await course_agent.remove_agent_from_course(
            db=db, course_id=course_id, agent_uuid=agent_uuid
        )
    
    @staticmethod
    async def update_course_agent(
        db: AsyncSession,
        *,
        course_id: int,
        agent_uuid: str,
        obj_in: dict
    ) -> Optional[CourseAgent]:
        """更新课程智能体信息"""
        course_agent_obj = await course_agent.get_by_course_and_agent(
            db=db, course_id=course_id, agent_uuid=agent_uuid
        )
        if not course_agent_obj:
            return None
        
        return await course_agent.update(
            db=db, db_obj=course_agent_obj, obj_in=obj_in
        )
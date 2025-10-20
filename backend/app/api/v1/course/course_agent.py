#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.response.response_schema import ResponseModel, response_base
from common.response.response_code import CustomResponse
from database.db_mysql import CurrentSession
from common.security.jwt import DependsJwtAuth
from app.service.course_agent_service import CourseAgentService
from app.schema.course_agent import (
    MigrateAgentToCourseParam,
    GetCourseAgentListDetails,
    UpdateCourseAgentParam
)

router = APIRouter()


@router.post('/migrate', summary='将智能体迁移到课程', dependencies=[DependsJwtAuth])
async def migrate_agent_to_course(
    request: Request,
    db: CurrentSession,
    obj_in: MigrateAgentToCourseParam,
) -> ResponseModel:
    """将智能体迁移到课程"""
    current_user = request.user
    
    try:
        course_agent = await CourseAgentService.migrate_agent_to_course(
            db=db, obj_in=obj_in, migrated_by=current_user.uuid
        )
        
        # 手动构建响应数据
        response_data = {
            "id": course_agent.id,
            "uuid": course_agent.uuid,
            "course_id": course_agent.course_id,
            "agent_uuid": course_agent.agent_uuid,
            "migrated_by": course_agent.migrated_by,
            "title": course_agent.title,
            "description": course_agent.description,
            "sort_order": course_agent.sort_order,
            "status": course_agent.status,
            "created_time": course_agent.created_time,
            "updated_time": course_agent.updated_time
        }
        
        return response_base.success(data=response_data)
    except ValueError as e:
        return response_base.fail(res=CustomResponse(code=400, msg=str(e)))
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f"迁移失败: {str(e)}"))


@router.get('/course/{course_id}', summary='获取课程的智能体列表')
async def get_course_agents(
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
    status: Annotated[int | None, Query(description='状态筛选')] = None,
) -> ResponseModel:
    """获取课程的智能体列表"""
    try:
        agents = await CourseAgentService.get_course_agents(
            db=db, course_id=course_id, status=status
        )
        
        # 手动构建响应数据
        response_data = []
        for agent in agents:
            agent_data = {
                "id": agent.id,
                "uuid": agent.uuid,
                "course_id": agent.course_id,
                "agent_uuid": agent.agent_uuid,
                "migrated_by": agent.migrated_by,
                "title": agent.title,
                "description": agent.description,
                "sort_order": agent.sort_order,
                "status": agent.status,
                "created_time": agent.created_time,
                "updated_time": agent.updated_time,
                "agent": {
                    "uuid": agent.agent.uuid,
                    "name": agent.agent.name,
                    "description": agent.agent.description,
                    "cover_image": agent.agent.cover_image,
                    "type": agent.agent.type,
                    "status": agent.agent.status
                } if agent.agent else None,
                "migrator": {
                    "uuid": agent.migrator.uuid,
                    "username": agent.migrator.username,
                    "nickname": agent.migrator.nickname,
                    "avatar": agent.migrator.avatar
                } if agent.migrator else None
            }
            response_data.append(agent_data)
        
        return response_base.success(data=response_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f"获取失败: {str(e)}"))


@router.get('/agent/{agent_uuid}', summary='获取智能体所在的课程列表')
async def get_agent_courses(
    db: CurrentSession,
    agent_uuid: Annotated[str, Path(description='智能体UUID')],
    status: Annotated[int | None, Query(description='状态筛选')] = None,
) -> ResponseModel:
    """获取智能体所在的课程列表"""
    try:
        courses = await CourseAgentService.get_agent_courses(
            db=db, agent_uuid=agent_uuid, status=status
        )
        
        # 手动构建响应数据
        response_data = []
        for course_agent in courses:
            course_data = {
                "id": course_agent.id,
                "uuid": course_agent.uuid,
                "course_id": course_agent.course_id,
                "agent_uuid": course_agent.agent_uuid,
                "migrated_by": course_agent.migrated_by,
                "title": course_agent.title,
                "description": course_agent.description,
                "sort_order": course_agent.sort_order,
                "status": course_agent.status,
                "created_time": course_agent.created_time,
                "updated_time": course_agent.updated_time,
                "course": {
                    "id": course_agent.course.id,
                    "uuid": course_agent.course.uuid,
                    "title": course_agent.course.title,
                    "description": course_agent.course.description,
                    "cover_image": course_agent.course.cover_image,
                    "status": course_agent.course.status
                } if course_agent.course else None
            }
            response_data.append(course_data)
        
        return response_base.success(data=response_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f"获取失败: {str(e)}"))


@router.delete('/{course_id}/{agent_uuid}', summary='从课程中移除智能体', dependencies=[DependsJwtAuth])
async def remove_agent_from_course(
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
    agent_uuid: Annotated[str, Path(description='智能体UUID')],
) -> ResponseModel:
    """从课程中移除智能体"""
    try:
        success = await CourseAgentService.remove_agent_from_course(
            db=db, course_id=course_id, agent_uuid=agent_uuid
        )
        
        if success:
            return response_base.success(msg="移除成功")
        else:
            return response_base.fail(res=CustomResponse(code=404, msg="未找到该智能体"))
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f"移除失败: {str(e)}"))


@router.put('/{course_id}/{agent_uuid}', summary='更新课程智能体信息', dependencies=[DependsJwtAuth])
async def update_course_agent(
    db: CurrentSession,
    course_id: Annotated[int, Path(description='课程ID')],
    agent_uuid: Annotated[str, Path(description='智能体UUID')],
    obj_in: UpdateCourseAgentParam,
) -> ResponseModel:
    """更新课程智能体信息"""
    try:
        course_agent = await CourseAgentService.update_course_agent(
            db=db, 
            course_id=course_id, 
            agent_uuid=agent_uuid, 
            obj_in=obj_in.dict(exclude_unset=True)
        )
        
        if not course_agent:
            return response_base.fail(res=CustomResponse(code=404, msg="未找到该智能体"))
        
        # 手动构建响应数据
        response_data = {
            "id": course_agent.id,
            "uuid": course_agent.uuid,
            "course_id": course_agent.course_id,
            "agent_uuid": course_agent.agent_uuid,
            "migrated_by": course_agent.migrated_by,
            "title": course_agent.title,
            "description": course_agent.description,
            "sort_order": course_agent.sort_order,
            "status": course_agent.status,
            "created_time": course_agent.created_time,
            "updated_time": course_agent.updated_time
        }
        
        return response_base.success(data=response_data)
    except Exception as e:
        return response_base.fail(res=CustomResponse(code=500, msg=f"更新失败: {str(e)}"))
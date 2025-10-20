#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from common.schema import SchemaBase
from app.schema.agent_schema import AgentDetailSchema
from app.schema.user_schema import GetUserInfoNoRelationDetail


class CourseAgentSchemaBase(SchemaBase):
    """课程智能体基础Schema"""
    course_id: int = Field(..., description="课程ID")
    agent_uuid: str = Field(..., description="智能体UUID")
    title: Optional[str] = Field(None, description="在课程中显示的标题")
    description: Optional[str] = Field(None, description="在课程中显示的描述")
    sort_order: int = Field(1, description="排序")
    status: int = Field(1, description="状态(0停用 1正常)")


class CreateCourseAgentParam(BaseModel):
    """创建课程智能体参数"""
    course_id: int = Field(..., description="课程ID")
    agent_uuid: str = Field(..., description="智能体UUID")
    title: Optional[str] = Field(None, description="在课程中显示的标题")
    description: Optional[str] = Field(None, description="在课程中显示的描述")


class UpdateCourseAgentParam(BaseModel):
    """更新课程智能体参数"""
    title: Optional[str] = Field(None, description="在课程中显示的标题")
    description: Optional[str] = Field(None, description="在课程中显示的描述")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态(0停用 1正常)")


class GetCourseAgentListDetails(CourseAgentSchemaBase):
    """课程智能体列表详情"""
    id: int
    uuid: str
    migrated_by: str
    created_time: datetime
    updated_time: Optional[datetime] = None
    
    # 关联信息
    agent: Optional[AgentDetailSchema] = None
    migrator: Optional[GetUserInfoNoRelationDetail] = None


class GetCourseAgentDetails(GetCourseAgentListDetails):
    """课程智能体详情"""
    pass


class MigrateAgentToCourseParam(BaseModel):
    """智能体迁移到课程参数"""
    agent_uuid: str = Field(..., description="智能体UUID")
    course_id: int = Field(..., description="目标课程ID")
    title: Optional[str] = Field(None, description="在课程中显示的标题")
    description: Optional[str] = Field(None, description="在课程中显示的描述")
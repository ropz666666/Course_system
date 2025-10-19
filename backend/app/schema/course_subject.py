#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from common.schema import SchemaBase


class CourseSubjectSchemaBase(SchemaBase):
    name: str = Field(..., description="科目名称")
    code: str = Field(..., description="科目编码")
    description: Optional[str] = Field(None, description="科目描述")
    sort_order: int = Field(1, description="排序")
    status: int = Field(1, description="状态(0禁用 1启用)")


class CreateCourseSubjectParam(CourseSubjectSchemaBase):
    """创建科目参数"""
    pass


class UpdateCourseSubjectParam(BaseModel):
    """更新科目参数"""
    name: Optional[str] = Field(None, description="科目名称")
    code: Optional[str] = Field(None, description="科目编码")
    description: Optional[str] = Field(None, description="科目描述")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态(0禁用 1启用)")


class GetCourseSubjectListDetails(CourseSubjectSchemaBase):
    """科目列表详情"""
    id: int
    created_time: datetime
    updated_time: Optional[datetime] = None
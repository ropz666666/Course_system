#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from common.schema import SchemaBase


class CourseGradeSchemaBase(SchemaBase):
    name: str = Field(..., description="年级名称")
    code: str = Field(..., description="年级编码")
    sort_order: int = Field(1, description="排序")
    status: int = Field(1, description="状态(0禁用 1启用)")


class CreateCourseGradeParam(CourseGradeSchemaBase):
    """创建年级参数"""
    pass


class UpdateCourseGradeParam(BaseModel):
    """更新年级参数"""
    name: Optional[str] = Field(None, description="年级名称")
    code: Optional[str] = Field(None, description="年级编码")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态(0禁用 1启用)")


class GetCourseGradeListDetails(CourseGradeSchemaBase):
    """年级列表详情"""
    id: int
    created_time: datetime
    updated_time: Optional[datetime] = None
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from common.schema import SchemaBase


class CourseResourceSchemaBase(SchemaBase):
    title: str = Field(..., description="资源标题")
    resource_type: str = Field(..., description="资源类型(textbook教材 outline大纲 lesson_plan教案 ppt课件 video视频)")
    course_id: int = Field(..., description="课程ID")
    description: Optional[str] = Field(None, description="资源描述")
    file_name: Optional[str] = Field(None, description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_type: Optional[str] = Field(None, description="文件类型")
    sort_order: int = Field(1, description="排序")
    status: int = Field(1, description="状态(0禁用 1启用)")


class CreateCourseResourceParam(CourseResourceSchemaBase):
    """创建课程资源参数"""
    pass


class UpdateCourseResourceParam(BaseModel):
    """更新课程资源参数"""
    title: Optional[str] = Field(None, description="资源标题")
    resource_type: Optional[str] = Field(None, description="资源类型")
    course_id: Optional[int] = Field(None, description="课程ID")
    description: Optional[str] = Field(None, description="资源描述")
    file_name: Optional[str] = Field(None, description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_type: Optional[str] = Field(None, description="文件类型")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态(0禁用 1启用)")


class GetCourseResourceListDetails(CourseResourceSchemaBase):
    """课程资源列表详情"""
    id: int
    uuid: str
    upload_user_uuid: str
    download_count: int
    created_time: str
    updated_time: Optional[str] = None
    
    # 关联信息
    course: Optional[dict] = None
    uploader: Optional[dict] = None


class GetCourseResourceDetails(GetCourseResourceListDetails):
    """课程资源详情"""
    pass
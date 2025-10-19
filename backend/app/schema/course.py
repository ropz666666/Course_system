#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from common.schema import SchemaBase
from app.schema.course_grade import GetCourseGradeListDetails
from app.schema.course_subject import GetCourseSubjectListDetails
from app.schema.user_schema import GetUserInfoNoRelationDetail
from app.schema.course_resource import GetCourseResourceListDetails


class CourseSchemaBase(SchemaBase):
    title: str = Field(..., description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    cover_image: Optional[str] = Field(None, description="封面图片")
    grade_id: int = Field(..., description="年级ID")
    subject_id: int = Field(..., description="科目ID")
    sort_order: int = Field(0, description="排序")
    status: int = Field(1, description="状态(0禁用 1启用)")


class CreateCourseParam(CourseSchemaBase):
    """创建课程参数"""
    pass


class UpdateCourseParam(BaseModel):
    """更新课程参数"""
    title: Optional[str] = Field(None, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    cover_image: Optional[str] = Field(None, description="封面图片")
    grade_id: Optional[int] = Field(None, description="年级ID")
    subject_id: Optional[int] = Field(None, description="科目ID")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态(0禁用 1启用)")


class GetCourseListDetails(CourseSchemaBase):
    """课程列表详情"""
    id: int
    uuid: str
    teacher_uuid: str
    created_time: datetime
    updated_time: Optional[datetime] = None
    
    # 关联信息
    grade: Optional[GetCourseGradeListDetails] = None
    subject: Optional[GetCourseSubjectListDetails] = None
    teacher: Optional[GetUserInfoNoRelationDetail] = None


class GetCourseDetails(GetCourseListDetails):
    """课程详情"""
    resources: Optional[List[GetCourseResourceListDetails]] = None


class CourseTreeNode(BaseModel):
    """课程树节点"""
    id: int
    name: str
    type: str = Field(..., description="节点类型: grade/subject/course")
    children: Optional[List['CourseTreeNode']] = None
    course_count: Optional[int] = None


# 解决前向引用问题
CourseTreeNode.model_rebuild()
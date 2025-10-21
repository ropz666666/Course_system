#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_course import course
from app.crud.crud_course_grade import course_grade
from app.crud.crud_course_subject import course_subject
from app.model.course.course import Course
from app.schema.course import CreateCourseParam, UpdateCourseParam, CourseTreeNode
from common.exception import errors


class CourseService:
    @staticmethod
    async def get_course_detail(db: AsyncSession, *, course_id: int) -> Optional[Course]:
        """获取课程详情"""
        return await course.get_by_id(db, id=course_id)

    @staticmethod
    def get_list_query_by_grade_subject(
        *,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        status: Optional[int] = None,
    ):
        """根据年级和科目构建课程查询对象"""
        return course.get_list_query_by_grade_subject(
            grade_id=grade_id,
            subject_id=subject_id,
            status=status
        )

    @staticmethod
    async def get_list_by_grade_subject(
        db: AsyncSession,
        *,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:
        """根据年级和科目获取课程列表"""
        return await course.get_list_by_grade_subject(
            db,
            grade_id=grade_id,
            subject_id=subject_id,
            status=status,
            skip=skip,
            limit=limit
        )

    @staticmethod
    def get_teacher_courses_query(*, teacher_uuid: str):
        """获取教师课程的查询对象"""
        return course.get_teacher_query(teacher_uuid=teacher_uuid)

    @staticmethod
    async def get_teacher_courses(
        db: AsyncSession,
        *,
        teacher_uuid: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:
        """获取教师的课程列表"""
        return await course.get_by_teacher(
            db,
            teacher_uuid=teacher_uuid,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def get_course_tree(db: AsyncSession) -> List[CourseTreeNode]:
        """获取课程树结构"""
        # 获取所有启用的年级
        grades = await course_grade.get_list_by_status(db, status=1)
        
        tree_nodes = []
        for grade in grades:
            # 获取该年级下的所有启用科目
            subjects = await course_subject.get_list_by_status(db, status=1)
            
            subject_nodes = []
            for subject in subjects:
                # 获取该年级和科目下的课程数量
                courses = await course.get_by_grade_subject(
                    db,
                    grade_id=grade.id,
                    subject_id=subject.id
                )
                
                if courses:  # 只显示有课程的科目
                    subject_node = CourseTreeNode(
                        id=subject.id,
                        name=subject.name,
                        type='subject',
                        course_count=len(courses)
                    )
                    subject_nodes.append(subject_node)
            
            if subject_nodes:  # 只显示有科目的年级
                grade_node = CourseTreeNode(
                    id=grade.id,
                    name=grade.name,
                    type='grade',
                    children=subject_nodes
                )
                tree_nodes.append(grade_node)
        
        return tree_nodes

    @staticmethod
    async def create_course(
        db: AsyncSession,
        *,
        obj_in: CreateCourseParam,
        teacher_uuid: str
    ) -> Course:
        """创建课程"""
        # 检查年级是否存在
        grade_obj = await course_grade.get_by_id(db, id=obj_in.grade_id)
        if not grade_obj:
            raise errors.NotFoundError(msg="年级不存在")
        
        # 检查科目是否存在
        subject_obj = await course_subject.get_by_id(db, id=obj_in.subject_id)
        if not subject_obj:
            raise errors.NotFoundError(msg="科目不存在")
        
        #创建课程
        course_data = obj_in.model_dump()  # 使用model_dump()替代dict()以兼容Pydantic v2
        course_data['teacher_uuid'] = teacher_uuid  # 添加教师UUID
        return await course.create_with_relations(db, obj_in=course_data)

    @staticmethod
    async def update_course(
        db: AsyncSession,
        *,
        course_id: int,
        obj_in: UpdateCourseParam
    ) -> Course:
        """更新课程"""
        # 获取课程
        course_obj = await course.get(db, id=course_id)
        if not course_obj:
            raise errors.NotFoundError(msg="课程不存在")
        
        # 如果更新年级，检查年级是否存在
        if obj_in.grade_id is not None:
            grade_obj = await course_grade.get_by_id(db, id=obj_in.grade_id)
            if not grade_obj:
                raise errors.NotFoundError(msg="年级不存在")
        
        # 如果更新科目，检查科目是否存在
        if obj_in.subject_id is not None:
            subject_obj = await course_subject.get_by_id(db, id=obj_in.subject_id)
            if not subject_obj:
                raise errors.NotFoundError(msg="科目不存在")
        
        # 更新课程
        update_data = obj_in.dict(exclude_unset=True)
        return await course.update_with_relations(db, db_obj=course_obj, obj_in=update_data)

    @staticmethod
    async def delete_course(db: AsyncSession, *, course_id: int) -> bool:
        """删除课程"""
        course_obj = await course.get(db, id=course_id)
        if not course_obj:
            raise errors.NotFoundError(msg="课程不存在")
        
        await db.delete(course_obj)
        await db.commit()
        return True
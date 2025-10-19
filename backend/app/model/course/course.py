#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.model import Base, id_key
from database.db_mysql import uuid4_str


class Course(Base):
    """课程表"""

    __tablename__ = 'courses'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    
    # 必需字段（无默认值）
    title: Mapped[str] = mapped_column(String(255), comment='课程标题')
    grade_id: Mapped[int] = mapped_column(
        ForeignKey('course_grades.id', ondelete='CASCADE'),
        comment='年级ID'
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey('course_subjects.id', ondelete='CASCADE'),
        comment='科目ID'
    )
    teacher_uuid: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('user.uuid', ondelete='CASCADE'),
        comment='教师UUID'
    )
    
    # 可选字段（有默认值）
    description: Mapped[str | None] = mapped_column(Text, default=None, comment='课程描述')
    cover_image: Mapped[str | None] = mapped_column(String(500), default=None, comment='封面图片')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')
    sort_order: Mapped[int] = mapped_column(default=1, comment='排序')

    # 关系定义
    grade: Mapped['CourseGrade'] = relationship(  # noqa: F821
        init=False, back_populates='courses'
    )
    subject: Mapped['CourseSubject'] = relationship(  # noqa: F821
        init=False, back_populates='courses'
    )
    teacher: Mapped['User'] = relationship(  # noqa: F821
        init=False, foreign_keys=[teacher_uuid]
    )

    # 一对多关系：一个课程有多个资源和智能体
    resources: Mapped[list['CourseResource']] = relationship(  # noqa: F821
        init=False, back_populates='course', cascade='all, delete-orphan'
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.model import Base, id_key


class CourseSubject(Base):
    """科目表"""

    __tablename__ = 'course_subjects'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(50), comment='科目名称')
    code: Mapped[str] = mapped_column(String(20), unique=True, comment='科目编码')
    description: Mapped[str | None] = mapped_column(Text, default=None, comment='科目描述')
    sort_order: Mapped[int] = mapped_column(default=1, comment='排序')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # 一对多关系：一个科目有多个课程
    courses: Mapped[list['Course']] = relationship(  # noqa: F821
        init=False, back_populates='subject', cascade='all, delete-orphan'
    )
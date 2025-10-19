#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.model import Base, id_key


class CourseGrade(Base):
    """年级表"""

    __tablename__ = 'course_grades'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(50), comment='年级名称')
    code: Mapped[str] = mapped_column(String(20), unique=True, comment='年级编码')
    sort_order: Mapped[int] = mapped_column(default=1, comment='排序')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # 一对多关系：一个年级有多个课程
    courses: Mapped[list['Course']] = relationship(  # noqa: F821
        init=False, back_populates='grade', cascade='all, delete-orphan'
    )
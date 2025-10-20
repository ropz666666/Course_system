#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.model import Base, id_key
from database.db_mysql import uuid4_str


class CourseAgent(Base):
    """课程智能体表 - 存储迁移到课程中的智能体"""

    __tablename__ = 'course_agents'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    
    # 必需字段
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.id', ondelete='CASCADE'),
        comment='课程ID'
    )
    agent_uuid: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('agent.uuid', ondelete='CASCADE'),
        comment='智能体UUID'
    )
    migrated_by: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('user.uuid', ondelete='CASCADE'),
        comment='迁移操作者UUID'
    )
    
    # 可选字段
    title: Mapped[str | None] = mapped_column(String(255), default=None, comment='在课程中显示的标题')
    description: Mapped[str | None] = mapped_column(Text, default=None, comment='在课程中显示的描述')
    sort_order: Mapped[int] = mapped_column(default=1, comment='排序')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # 关系定义
    course: Mapped['Course'] = relationship(  # noqa: F821
        init=False, back_populates='agents'
    )
    agent: Mapped['Agent'] = relationship(  # noqa: F821
        init=False, foreign_keys=[agent_uuid]
    )
    migrator: Mapped['User'] = relationship(  # noqa: F821
        init=False, foreign_keys=[migrated_by]
    )
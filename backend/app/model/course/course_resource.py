#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.model import Base, id_key
from database.db_mysql import uuid4_str


class CourseResource(Base):
    """课程资源表"""

    __tablename__ = 'course_resources'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    
    # 必需字段（无默认值）
    title: Mapped[str] = mapped_column(String(255), comment='资源标题')
    resource_type: Mapped[str] = mapped_column(
        String(20), 
        comment='资源类型(textbook教材 outline大纲 lesson_plan教案 ppt课件 video视频)'
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.id', ondelete='CASCADE'),
        comment='课程ID'
    )
    upload_user_uuid: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('user.uuid', ondelete='CASCADE'),
        comment='上传用户UUID'
    )
    
    # 可选字段（有默认值）
    description: Mapped[str | None] = mapped_column(Text, default=None, comment='资源描述')
    file_name: Mapped[str | None] = mapped_column(String(255), default=None, comment='文件名')
    file_path: Mapped[str | None] = mapped_column(String(500), default=None, comment='文件路径')
    file_size: Mapped[int | None] = mapped_column(BigInteger, default=None, comment='文件大小(字节)')
    file_type: Mapped[str | None] = mapped_column(String(50), default=None, comment='文件类型')
    download_count: Mapped[int] = mapped_column(default=0, comment='下载次数')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')
    sort_order: Mapped[int] = mapped_column(default=1, comment='排序')

    # 关系定义
    course: Mapped['Course'] = relationship(  # noqa: F821
        init=False, back_populates='resources'
    )
    uploader: Mapped['User'] = relationship(  # noqa: F821
        init=False
    )
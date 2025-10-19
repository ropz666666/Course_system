from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from utils.timezone import timezone


class AgentVersion(Base):
    """智能体版本表"""
    __tablename__ = 'agent_version'

    id: Mapped[id_key] = mapped_column(init=False)
    agent_id: Mapped[int] = mapped_column(comment='所属智能体ID')
    version_number: Mapped[str] = mapped_column(String(20), comment='版本号')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='版本描述')
    release_notes: Mapped[Optional[str]] = mapped_column(Text, comment='发布说明')
    created_at: Mapped[datetime] = mapped_column(default_factory=timezone.now, comment='创建时间')

    # Relationships
    agent: Mapped['Agent'] = relationship(back_populates="versions")

    publishments: Mapped[List['AgentPublishment']] = relationship(
        back_populates="agent_version",
        cascade="all, delete-orphan"
    )

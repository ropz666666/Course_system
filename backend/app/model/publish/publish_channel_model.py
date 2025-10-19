from typing import List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class PublishChannel(Base):
    """发布渠道表"""
    __tablename__ = 'publish_channel'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(50), comment='渠道名称')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='渠道描述')
    is_active: Mapped[bool] = mapped_column(default=True, comment='是否激活')

    # Relationships
    publishments: Mapped[List['AgentPublishment']] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan", init=False
    )

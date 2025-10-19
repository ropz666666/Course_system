from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import JSON, Enum as SQLEnum, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class PublishStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    approved = "approved"
    rejected = "rejected"


class AgentPublishment(Base):
    __tablename__ = 'agent_publishment'

    # ---------- 无默认值的字段 ----------
    agent_uuid: Mapped[str] = mapped_column(ForeignKey('agent.uuid'), comment='智能体UUID')
    channel_uuid: Mapped[str] = mapped_column(ForeignKey('publish_channel.uuid'), comment='发布渠道UUID')
    published_by: Mapped[str] = mapped_column(comment='发布者ID')
    publish_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment='发布配置')

    # ---------- 有默认值的字段 ----------
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    status: Mapped[PublishStatus] = mapped_column(
        SQLEnum(PublishStatus),
        default=PublishStatus.pending,
        comment='发布状态'
    )

    # 关系字段
    agent: Mapped['Agent'] = relationship(back_populates="publishments", init=False)
    channel: Mapped['PublishChannel'] = relationship(back_populates="publishments", init=False)

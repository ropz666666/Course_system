from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class PublishStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


class PublishApproval(Base):
    """发布审批表"""
    __tablename__ = 'publish_approval'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    publishment_uuid: Mapped[int] = mapped_column(comment='发布记录ID')
    approver_uuid: Mapped[int] = mapped_column(comment='审批人ID')
    status: Mapped[PublishStatus] = mapped_column(
        SQLEnum(PublishStatus),
        default=PublishStatus.PENDING,
        comment='审批状态'
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, comment='审批意见', init=False)

    # Relationships
    publishment: Mapped['AgentPublishment'] = relationship(back_populates="approvals", init=False)

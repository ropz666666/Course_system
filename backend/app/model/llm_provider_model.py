from typing import Optional, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class LlmProvider(Base):
    """大模型提供商表"""
    __tablename__ = "llm_provider"
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    # 外键关系
    user_uuid: Mapped[str] = mapped_column(
        ForeignKey('user.uuid'),
        nullable=False,
        comment="用户UUID"
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, comment="提供商名称")  # 唯一约束
    api_key: Mapped[str] = mapped_column(String(255), comment="API密钥")
    api_url: Mapped[str] = mapped_column(String(512), comment="API地址")
    document_url: Mapped[Optional[str]] = mapped_column(String(512), comment="文档URL")
    llm_model_url: Mapped[Optional[str]] = mapped_column(String(512), comment="模型URL")
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # 关系定义
    models: Mapped[List["LlmModel"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
        init=False
    )


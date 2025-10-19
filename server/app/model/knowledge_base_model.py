from typing import List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str
from app.model import agent_knowledge_map


class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    user_uuid: Mapped[str] = mapped_column(ForeignKey('user.uuid'), nullable=False)
    name: Mapped[str] = mapped_column(String(32), comment='知识库名称')
    description: Mapped[str] = mapped_column(Text)
    embedding_model: Mapped[str] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255), default=None, comment='图像')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # Relationships
    agents: Mapped[List['Agent']] = relationship('Agent', secondary=agent_knowledge_map, back_populates='knowledge_bases', init=False)
    collections: Mapped[List['Collection']] = relationship("Collection", back_populates="knowledge_base", cascade="all, delete-orphan", init=False)
    graph_collections: Mapped[List['GraphCollection']] = relationship("GraphCollection", back_populates="knowledge_base", cascade="all, delete-orphan", init=False)
    user: Mapped['User'] = relationship('User', back_populates='knowledge_bases', init=False)

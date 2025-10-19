from typing import List

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class GraphCollection(Base):
    __tablename__ = 'graph_collection'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    knowledge_base_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_base.uuid'), nullable=False)
    name: Mapped[str] = mapped_column(String(32))
    entities: Mapped[str] = mapped_column(Text)
    relationships: Mapped[str] = mapped_column(String(32))
    communities: Mapped[str] = mapped_column(String(32))
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    knowledge_base: Mapped['KnowledgeBase'] = relationship('KnowledgeBase', back_populates='graph_collections', init=False)

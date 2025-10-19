from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class Conversation(Base):
    __tablename__ = 'conversation'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(32), comment='会话名称')
    chat_history: Mapped[str] = mapped_column(Text)
    chat_parameters: Mapped[str] = mapped_column(Text)
    short_memory: Mapped[str] = mapped_column(Text)
    long_memory: Mapped[str] = mapped_column(Text)
    user_uuid: Mapped[str] = mapped_column(ForeignKey('user.uuid'), nullable=False)
    user: Mapped['User'] = relationship("User", back_populates="conversations", init=False)
    agent_uuid: Mapped[str] = mapped_column(ForeignKey('agent.uuid'), nullable=False)
    knowledge_base_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_base.uuid'), nullable=False)
    collection_uuid: Mapped[str] = mapped_column(ForeignKey('collection.uuid'), nullable=False)
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常 2模拟器会话)')

    agent: Mapped['Agent'] = relationship("Agent", back_populates="conversations", init=False)
    knowledge_base: Mapped['KnowledgeBase'] = relationship("KnowledgeBase", init=False)
    collection: Mapped['Collection'] = relationship("Collection", init=False)


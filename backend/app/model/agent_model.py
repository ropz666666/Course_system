from typing import List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str
from app.model import agent_knowledge_map, agent_plugin_map, user_agent_map


class Agent(Base):
    """智能体表"""

    __tablename__ = 'agent'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    user_uuid: Mapped[str] = mapped_column(ForeignKey('user.uuid'), nullable=False)
    deploy_plugin_uuid: Mapped[str] = mapped_column(ForeignKey('plugin.uuid'))
    name: Mapped[str] = mapped_column(String(32), comment='智能体名称')
    description: Mapped[str] = mapped_column(Text)
    spl: Mapped[str] = mapped_column(Text)
    spl_form: Mapped[str] = mapped_column(Text)
    spl_chain: Mapped[str] = mapped_column(Text)
    welcome_info: Mapped[str] = mapped_column(Text)
    sample_query: Mapped[str] = mapped_column(Text)
    parameters: Mapped[str] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255), default=None, comment='图像')
    type: Mapped[int] = mapped_column(default=1, comment='智能体类型(0管理型 1功能型)')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # Relationships
    use_users: Mapped[List['Agent']] = relationship('User', secondary=user_agent_map, back_populates='add_agents', init=False)
    knowledge_bases: Mapped[List['KnowledgeBase']] = relationship('KnowledgeBase', secondary=agent_knowledge_map, back_populates='agents', init=False)
    plugins: Mapped[List['Plugin']] = relationship('Plugin', secondary=agent_plugin_map, back_populates='agents', init=False)
    deploy_plugin: Mapped['Plugin'] = relationship('Plugin', init=False)
    conversations: Mapped[List['Conversation']] = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan", init=False)
    user: Mapped['User'] = relationship('User', back_populates='agents', init=False)


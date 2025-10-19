from typing import List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str
from app.model import agent_plugin_map


class Plugin(Base):
    __tablename__ = 'plugin'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    user_uuid: Mapped[str] = mapped_column(ForeignKey('user.uuid'), nullable=False)
    name: Mapped[str] = mapped_column(String(32), comment='插件名称')
    description: Mapped[str] = mapped_column(Text)
    server_url: Mapped[str] = mapped_column(Text)
    header_info: Mapped[str] = mapped_column(Text)
    return_info: Mapped[str] = mapped_column(Text)
    api_parameter: Mapped[str] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255), default=None, comment='图像')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常) 工具类智能体状态(2停用 3正常)')

    # Relationships
    agents: Mapped[List['Agent']] = relationship('Agent', secondary=agent_plugin_map, back_populates='plugins', init=False)
    user: Mapped['User'] = relationship('User', back_populates='plugins', init=False)

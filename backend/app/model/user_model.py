from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model import user_agent_map
from common.model import Base, id_key
from database.db_mysql import uuid4_str
from utils.timezone import timezone


class User(Base):
    """用户表"""
    __tablename__ = 'user'
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment='用户名')
    nickname: Mapped[str] = mapped_column(String(20), unique=True, comment='昵称')
    password: Mapped[str | None] = mapped_column(String(255), comment='密码')
    salt: Mapped[str | None] = mapped_column(String(5), comment='加密盐')
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment='邮箱')
    is_superuser: Mapped[bool] = mapped_column(default=False, comment='超级权限(0否 1是)')
    is_staff: Mapped[bool] = mapped_column(default=False, comment='后台管理登陆(0否 1是)')
    status: Mapped[int] = mapped_column(default=1, comment='用户账号状态(0停用 1正常)')
    is_multi_login: Mapped[bool] = mapped_column(default=False, comment='是否重复登陆(0否 1是)')
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment='头像')
    phone: Mapped[str | None] = mapped_column(String(11), default=None, comment='手机号')
    join_time: Mapped[datetime] = mapped_column(init=False, default_factory=timezone.now, comment='注册时间')
    last_login_time: Mapped[datetime | None] = mapped_column(init=False, onupdate=timezone.now, comment='上次登录')

    # Relationships
    add_agents: Mapped[List['Agent']] = relationship('Agent', secondary=user_agent_map, back_populates='use_users', init=False)
    interactions: Mapped[List['UserAgentInteraction']] = relationship("UserAgentInteraction", back_populates="user",
                                                                      cascade="all, delete-orphan", init=False)
    agents: Mapped[List['Agent']] = relationship("Agent", back_populates="user", cascade="all, delete-orphan", init=False)
    conversations: Mapped[List['Conversation']] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan", init=False)
    knowledge_bases: Mapped[List['KnowledgeBase']] = relationship("KnowledgeBase", back_populates="user", cascade="all, delete-orphan", init=False)
    plugins: Mapped[List['Plugin']] = relationship("Plugin", back_populates="user", cascade="all, delete-orphan", init=False)

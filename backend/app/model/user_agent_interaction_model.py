from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, UniqueConstraint
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class UserAgentInteraction(Base):
    __tablename__ = "user_agent_interaction"
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)

    user_uuid: Mapped[str] = mapped_column(ForeignKey('user.uuid'), nullable=False)
    agent_uuid: Mapped[str] = mapped_column(ForeignKey('agent.uuid'), nullable=False)

    # 评分字段
    rating_value: Mapped[float] = mapped_column(Float)

    # 收藏字段
    is_favorite: Mapped[bool] = mapped_column(default=False, comment='是否收藏')

    # 使用记录字段
    usage_count: Mapped[int] = mapped_column(default=0, comment='使用次数')

    # 关系
    user: Mapped['User'] = relationship('User', back_populates='interactions', init=False)
    agent: Mapped['Agent'] = relationship('Agent', back_populates='interactions', init=False)

    # 正确的表参数定义
    __table_args__ = (
        UniqueConstraint('user_uuid', 'agent_uuid', name='uq_user_agent'),
        {'sqlite_autoincrement': True}
    )

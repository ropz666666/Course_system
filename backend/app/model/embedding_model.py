from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class Embedding(Base):
    __tablename__ = 'embedding'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    vector: Mapped[str] = mapped_column(Text, comment='实体嵌入向量')

    text_block_uuid: Mapped[str] = mapped_column(ForeignKey('text_block.uuid'), nullable=False, comment='关联的文本块ID')
    text_block: Mapped['TextBlock'] = relationship('TextBlock', back_populates='embedding', init=False)

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model import Base, id_key
from database.db_mysql import uuid4_str


class TextBlock(Base):
    __tablename__ = 'text_block'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    content: Mapped[str] = mapped_column(Text)
    collection_uuid: Mapped[str] = mapped_column(ForeignKey('collection.uuid'), nullable=False)

    collection: Mapped['Collection'] = relationship('Collection', back_populates='text_blocks', init=False)
    embedding: Mapped['Embedding'] = relationship('Embedding', back_populates='text_block', init=False, cascade="all, delete-orphan")

from datetime import datetime
from pydantic import model_validator

from app.schema.embedding_schema import EmbeddingDetailSchema
from common.schema import SchemaBase


# 基础的 TextBlock 信息结构
class TextBlockSchemaBase(SchemaBase):
    content: str


# TextBlock 列表信息结构
class TextBlockListSchema(TextBlockSchemaBase):
    id: int
    uuid: str
    collection_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


class TextBlockDetailSchema(TextBlockSchemaBase):
    id: int
    uuid: str
    collection_uuid: str
    similarity: float | None = None
    created_time: datetime
    updated_time: datetime | None = None

    embedding: EmbeddingDetailSchema | list | None = None

    @model_validator(mode='after')
    def handle(self):
        embedding = self.embedding
        if embedding is not None and type(embedding) is not list:
            self.embedding = embedding.vector

        return self


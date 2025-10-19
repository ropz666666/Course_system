import json
from datetime import datetime
from pydantic import Field, model_validator

from app.schema.embedding_schema import EmbeddingDetailSchema
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 TextBlock 信息结构
class TextBlockSchemaBase(SchemaBase):
    content: str


# 创建 TextBlock 参数
class CreateTextBlockParam(TextBlockSchemaBase):
    collection_uuid: str | None = None


# 更新 TextBlock 参数
class UpdateTextBlockParam(TextBlockSchemaBase):
    content: str | None = None


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
        if embedding is not None:
            self.embedding = embedding.vector

        return self


# 当前 TextBlock 信息详情
class GetTextBlockDetail(TextBlockDetailSchema):
    pass


# 当前 TextBlock 信息详情
class GetTextBlockList(TextBlockListSchema):
    pass

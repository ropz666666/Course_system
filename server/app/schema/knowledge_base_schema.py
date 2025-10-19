from datetime import datetime
from pydantic import Field
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 KnowledgeBase 信息结构
class KnowledgeBaseSchemaBase(SchemaBase):
    name: str
    description: str
    cover_image: str | None = None
    embedding_model: str
    status: int = Field(default=StatusType.enable.value)


# KnowledgeBase 详情信息结构
class KnowledgeBaseDetailSchema(KnowledgeBaseSchemaBase):
    id: int
    uuid: str
    user_uuid: str

    created_time: datetime
    updated_time: datetime | None = None

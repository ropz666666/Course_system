import json
from datetime import datetime
from pydantic import Field, model_validator

from app.schema.text_block_schema import TextBlockListSchema
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 Collection 信息结构
class CollectionSchemaBase(SchemaBase):
    name: str
    file_url: str
    processing_method: str
    training_mode: str
    status: int = Field(default=StatusType.enable.value)


class CollectionDetailSchema(CollectionSchemaBase):
    id: int
    uuid: str
    knowledge_base_uuid: str

    created_time: datetime
    updated_time: datetime | None = None



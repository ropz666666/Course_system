import json
from datetime import datetime
from pydantic import Field, model_validator

from app.schema.text_block_schema import TextBlockListSchema, TextBlockDetailSchema
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 Collection 信息结构
class CollectionSchemaBase(SchemaBase):
    name: str
    file_url: str
    processing_method: str
    training_mode: str
    status: int = Field(default=StatusType.enable.value)


# 创建 Collection 参数
class CreateCollectionParam(CollectionSchemaBase):
    knowledge_base_uuid: str | None = None
    processing_method: str = Field(default='markdown_chunking')
    training_mode: str = Field(default='direct_segment')


# 更新 Collection 参数
class UpdateCollectionParam(SchemaBase):
    name: str | None = None
    status: int | None = None


# Collection 列表信息结构
class CollectionListSchema(CollectionSchemaBase):
    id: int
    uuid: str
    knowledge_base_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


class CollectionDetailSchema(CollectionSchemaBase):
    id: int
    uuid: str
    knowledge_base_uuid: str

    created_time: datetime
    updated_time: datetime | None = None

    text_blocks: list[TextBlockListSchema]

    @model_validator(mode='after')
    def handle(self):
        return self


# 当前 Collection 信息详情
class GetCollectionWorkSpace(CollectionDetailSchema):
    text_blocks: list[TextBlockDetailSchema]


# 当前 Collection 信息详情
class GetCollectionDetail(CollectionDetailSchema):
    pass


# 当前 Collection 信息详情
class GetCollectionList(CollectionListSchema):
    pass

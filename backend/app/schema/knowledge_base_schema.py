import json
from datetime import datetime
from pydantic import Field, model_validator

from app.schema.graph_collection_schema import GraphCollectionListSchema, GetGraphCollectionWorkSpace
from app.schema.collection_schema import CollectionListSchema, CollectionDetailSchema, GetCollectionWorkSpace
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 KnowledgeBase 信息结构
class KnowledgeBaseSchemaBase(SchemaBase):
    name: str
    description: str
    cover_image: str | None = None
    embedding_model: str
    status: int = Field(default=StatusType.enable.value)


# 创建 KnowledgeBase 参数
class CreateKnowledgeBaseParam(KnowledgeBaseSchemaBase):
    user_uuid: str | None = None
    embedding_model: str | None = None

    @model_validator(mode='before')
    def check(cls, values):
        embedding_model = values.get('embedding_model')
        if embedding_model is None:
            values['embedding_model'] = "Dmeta-embedding-zh"

        return values


# 更新 KnowledgeBase 参数
class UpdateKnowledgeBaseParam(KnowledgeBaseSchemaBase):
    name: str | None = None
    description: str | None = None
    cover_image: str | None = None
    status: int | None = None
    embedding_model: str | None = None


# KnowledgeBase 列表信息结构
class KnowledgeBaseListSchema(KnowledgeBaseSchemaBase):
    id: int
    uuid: str
    user_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


# KnowledgeBase 详情信息结构
class KnowledgeBaseDetailSchema(KnowledgeBaseSchemaBase):
    id: int
    uuid: str
    user_uuid: str

    created_time: datetime
    updated_time: datetime | None = None

    collections: list[CollectionListSchema] | None = None
    graph_collections: list[GraphCollectionListSchema] | None = None


class GetKnowledgeBaseWorkSpace(KnowledgeBaseDetailSchema):
    collections: list[GetCollectionWorkSpace] | None = None
    graph_collections: list[GetGraphCollectionWorkSpace] | None = None


# 当前 KnowledgeBase 信息详情
class GetKnowledgeBaseDetail(KnowledgeBaseDetailSchema):
    pass


# 当前 KnowledgeBase 信息详情
class GetKnowledgeBaseList(KnowledgeBaseListSchema):
    pass

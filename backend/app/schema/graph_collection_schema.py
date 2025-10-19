import json
from datetime import datetime
from pydantic import model_validator
from common.schema import SchemaBase


# 基础的 GraphCollection 信息结构
class GraphCollectionSchemaBase(SchemaBase):
    name: str
    status: int


# 创建 GraphCollection 参数
class CreateGraphCollectionParam(GraphCollectionSchemaBase):
    knowledge_base_uuid: str | None = None
    entities: list | str | None = None
    relationships: list | str | None = None
    communities: list | str | None = None
    file_url: str

    @model_validator(mode='after')
    def handle(self):
        entities = self.entities
        if entities is not None:
            self.entities = json.dumps(entities)
        relationships = self.relationships
        if relationships is not None:
            self.relationships = json.dumps(relationships)
        communities = self.communities
        if communities is not None:
            self.communities = json.dumps(communities)

        return self


# 更新 GraphCollection 参数
class UpdateGraphCollectionParam(SchemaBase):
    name: str | None = None
    status: int | None = None


# GraphCollection 列表信息结构
class GraphCollectionListSchema(GraphCollectionSchemaBase):
    id: int
    uuid: str
    knowledge_base_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


class GraphCollectionDetailSchema(GraphCollectionSchemaBase):
    id: int
    uuid: str
    knowledge_base_uuid: str
    entities: list | str | None = None
    relationships: list | str | None = None
    communities: list | str | None = None

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='after')
    def handle(self):
        entities = self.entities
        if entities is not None:
            self.entities = json.loads(entities)
        relationships = self.relationships
        if relationships is not None:
            self.relationships = json.loads(relationships)
        communities = self.communities
        if communities is not None:
            self.communities = json.loads(communities)
        return self


# 当前 GraphCollection 信息详情
class GetGraphCollectionWorkSpace(GraphCollectionDetailSchema):
    pass


# 当前 GraphCollection 信息详情
class GetGraphCollectionDetail(GraphCollectionDetailSchema):
    pass


# 当前 GraphCollection 信息详情
class GetGraphCollectionList(GraphCollectionListSchema):
    pass

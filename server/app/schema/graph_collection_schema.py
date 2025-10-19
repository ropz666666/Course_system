import json
from datetime import datetime
from pydantic import model_validator
from common.schema import SchemaBase


# 基础的 GraphCollection 信息结构
class GraphCollectionSchemaBase(SchemaBase):
    name: str
    status: int


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
        if entities is not None and type(entities) is not list:
            self.entities = json.loads(entities)
        relationships = self.relationships
        if relationships is not None and type(relationships) is not list:
            self.relationships = json.loads(relationships)
        communities = self.communities
        if communities is not None and type(communities) is not list:
            self.communities = json.loads(communities)
        return self

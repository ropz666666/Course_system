import json
from datetime import datetime
from pydantic import model_validator
from common.schema import SchemaBase


# 基础的 Embedding 信息结构
class EmbeddingSchemaBase(SchemaBase):
    vector: str


# Embedding 详情信息结构
class EmbeddingDetailSchema(EmbeddingSchemaBase):
    id: int
    uuid: str
    text_block_uuid: str

    vector: str | list

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='after')
    def handle(self):
        vector = self.vector
        if vector:
            self.vector = json.loads(vector)
        else:
            self.vector = []

        return self

import json
from datetime import datetime
from pydantic import model_validator
from common.schema import SchemaBase


# 基础的 Embedding 信息结构
class EmbeddingSchemaBase(SchemaBase):
    vector: str


# 创建 Embedding 参数
class CreateEmbeddingParam(EmbeddingSchemaBase):
    text_block_uuid: str | None = None

    @model_validator(mode='before')
    def check(cls, values):
        vector = values.get('vector', [])
        if vector is not None:
            values['vector'] = json.dumps(vector)

        return values


# 更新 Embedding 参数
class UpdateEmbeddingParam(EmbeddingSchemaBase):
    vector: str | list

    @model_validator(mode='before')
    def check(cls, values):
        vector = values.get('vector', [])
        if vector is not None:
            values['vector'] = json.dumps(vector)

        return values


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


# Embedding 列表信息结构
class EmbeddingListSchema(EmbeddingSchemaBase):
    id: int
    uuid: str
    text_block_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


# 当前 Embedding 信息详情
class GetEmbeddingDetail(EmbeddingDetailSchema):
    pass


# 当前 Embedding 信息详情
class GetEmbeddingList(EmbeddingListSchema):
    pass

import json
from datetime import datetime
from pydantic import model_validator
from common.schema import SchemaBase


# 基础的 Conservation 信息结构
class ConservationSchemaBase(SchemaBase):
    name: str


# Conservation 详情信息结构
class ConservationDetailSchema(ConservationSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    agent_uuid: str
    knowledge_base_uuid: str
    collection_uuid: str
    chat_history: list
    chat_parameters: str | dict | None = None
    short_memory: str | None = None
    long_memory: str | None = None

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='before')
    def check(cls, values):
        chat_history = values.get("chat_history", [])
        new_chat_history = []
        if len(chat_history) > 0:
            for chat in chat_history[0:-1]:
                item_str = ""
                for item in chat.get("contents", []):
                    item_str += item.get("content")
                new_chat_history.append(item_str)
            values["chat_history"] = new_chat_history
        return values

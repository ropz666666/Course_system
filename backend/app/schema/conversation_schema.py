import json
from datetime import datetime
from pydantic import Field, model_validator
from common.schema import SchemaBase


# 基础的 Conversation 信息结构
class ConversationSchemaBase(SchemaBase):
    name: str
    status: int = Field(default=1)


# 创建 Conversation 参数
class CreateConversationParam(ConversationSchemaBase):
    agent_uuid: str = Field(..., description="关联的智能体 UUID")
    user_uuid: str = Field('', description="关联的用户 UUID")
    knowledge_base_uuid: str = Field('', description="关联的知识库 UUID")
    collection_uuid: str = Field('', description="关联的知识库 UUID")
    name: str | None = '新会话'
    chat_history: str | None = '[]'
    chat_parameters: str | None = '{}'
    short_memory: str | None = ''
    long_memory: str | None = ''

    @model_validator(mode='before')
    def check(cls, values):
        print(values)
        return values


# 更新 Conversation 参数
class UpdateConversationParam(ConversationSchemaBase):
    name: str | None = None
    status: int | None = None
    chat_history: str | None = None
    chat_parameters: str | None = None
    short_memory: str | None = None
    long_memory: str | None = None

    @model_validator(mode='before')
    def check(cls, values):
        chat_history = values.get('chat_history')
        if chat_history is not None:
            values['chat_history'] = json.dumps(chat_history, ensure_ascii=False)  # 设置默认值为空数组

        chat_parameters = values.get('chat_parameters')
        if chat_parameters is not None:
            values['chat_parameters'] = json.dumps(chat_parameters, ensure_ascii=False)  # 设置默认值为空数组

        return values


# Conversation 详情信息结构
class ConversationDetailSchema(ConversationSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    agent_uuid: str
    knowledge_base_uuid: str
    collection_uuid: str
    chat_history: str | list | None = None
    chat_parameters: str | dict | None = None
    short_memory: str | None = None
    long_memory: str | None = None

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='after')
    def handle(self):
        chat_history = self.chat_history
        if chat_history:
            self.chat_history = json.loads(chat_history)
        else:
            self.chat_history = []

        chat_parameters = self.chat_parameters
        if chat_parameters:
            self.chat_parameters = json.loads(chat_parameters)
        else:
            self.chat_parameters = {}

        return self


# Conversation 列表信息结构
class ConversationListSchema(ConversationSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    agent_uuid: str
    chat_history: str | list | None = None

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='after')
    def handle(self):
        chat_history = self.chat_history
        if chat_history:
            self.chat_history = json.loads(chat_history)
        else:
            self.chat_history = []

        return self


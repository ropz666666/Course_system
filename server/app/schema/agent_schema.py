import json
from datetime import datetime
from pydantic import Field
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 Agent 信息结构
class AgentSchemaBase(SchemaBase):
    name: str
    description: str
    cover_image: str
    type: int = Field(..., description="智能体类型(0管理型 1功能型)")
    short_memory: int = Field(description="短期记忆(0关闭 1开启)", default=0)
    long_memory: int = Field(description="长期记忆(0关闭 1开启)", default=0)
    suggestion: bool = Field(description="是否生成建议", default=False)
    status: int = Field(default=StatusType.enable.value)


# Agent 详情信息结构
class AgentDetailSchema(AgentSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    operator_uuid: str = ''
    spl: str | None = ''
    spl_form: str | list | None = '[]'
    spl_chain: str | dict | None = '{}'
    welcome_info: str | None = ''
    sample_query: str | list | None = '[]'
    parameters: str | dict | None = '{}'
    created_time: datetime
    updated_time: datetime | None = None

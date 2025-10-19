import json
from datetime import datetime
from typing import Dict, List

from pydantic import Field, model_validator
from common.dataclasses import SPLSection
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 AgentPublishment 信息结构
class AgentPublishmentSchemaBase(SchemaBase):
    uuid: str
    agent_uuid: str
    channel_uuid: str
    published_by: str
    publish_config: Dict | None = None
    # status: str = Field(default=StatusType.enable.value)


class PublishmentItem(SchemaBase):
    channel_uuid: str
    publish_config: Dict | None = None


# 创建 AgentPublishment 参数
class CreateAgentPublishmentParam(SchemaBase):
    agent_uuid: str
    published_by: str | None = None
    channels: list[PublishmentItem]


# 创建 AgentPublishment 参数
class AddAgentPublishmentSchema(SchemaBase):
    agent_uuid: str
    channel_uuid: str
    publish_config: dict | None = None
    published_by: str | None = None


# 更新 AgentPublishment 参数
class UpdateAgentPublishmentParam(AgentPublishmentSchemaBase):
    pass


# AgentPublishment 详情信息结构
class AgentPublishmentDetailSchema(AgentPublishmentSchemaBase):
    pass


# AgentPublishment 列表信息结构
class AgentPublishmentListSchema(AgentPublishmentSchemaBase):
    pass



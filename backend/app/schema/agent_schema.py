import json
from datetime import datetime
from typing import Dict, List

from pydantic import Field, model_validator
from common.dataclasses import SPLSection
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
    suggestion: bool = Field(default=False)
    output_chaining: bool = Field(default=True)
    status: int = Field(default=StatusType.enable.value)
    tags: str | list | None = None


# 创建 Agent 参数
class CreateAgentParam(AgentSchemaBase):
    user_uuid: str | None = None
    deploy_plugin_uuid: str | None = None
    welcome_info: str | None = None
    sample_query: str | None = None
    spl: str | None = None
    spl_form: str | list[SPLSection] | None = None
    spl_chain: str | dict | None = None
    parameters: str | dict | None = '{}'
    tags: list | None = '[]'

    @model_validator(mode='before')
    def check(cls, values):
        welcome_info = values.get('welcome_info')
        if welcome_info is None:
            values['welcome_info'] = "您可以输入任何问题"

        parameters = values.get('parameters')
        if parameters is None:
            parameters = {"Output1": {"type": "system", "value_type": "text", "fill_type": "cloze", "placeholder": "nihao1", "content": ""}, "UserRequest": {"type": "system", "value_type": "text", "fill_type": "select", "placeholder": "cdscsdc", "options": ["csdcs", "cdscs"], "content": "cdscs", "description": "csdcs"}, "Output3": {"type": "system", "value_type": "text", "fill_type": "cloze", "placeholder": "你好啊", "content": ""}, "Output2": {"type": "system", "value_type": "text", "fill_type": "cloze", "placeholder": "sasa", "content": ""}}
            values['parameters'] = json.dumps(parameters, ensure_ascii=False)

        sample_query = values.get('sample_query')
        if sample_query is None:
            values['sample_query'] = json.dumps([], ensure_ascii=False)  # 设置默认值为空数组

        spl = values.get('spl')
        if spl is None:
            values['spl'] = ''  # 设置默认值为空数组

        spl_form = values.get('spl_form')
        if spl_form is None:
            values['spl_form'] = json.dumps([], ensure_ascii=False)  # 设置默认值为空数组

        spl_chain = values.get('spl_chain')
        if spl_chain is None:
            values['spl_chain'] = json.dumps({}, ensure_ascii=False)  # 设置默认值为空数组

        # parameters = values.get('parameters')
        # if parameters is None:
        #     values['parameters'] = json.dumps({})  # 设置默认值为空数组

        return values


# 更新 Agent 参数
class UpdateAgentParam(AgentSchemaBase):
    name: str | None = None
    description: str | None = None
    deploy_plugin_uuid: str | None = None
    cover_image: str | None = None
    type: int | None = None
    status: int | None = None
    long_memory: int | None = None
    short_memory: int | None = None
    suggestion: bool | None = None
    output_chaining: bool | None = None
    welcome_info: str | None = None
    tags: str | None = None
    sample_query: str | list[str] | None = None
    spl: str | None = None
    spl_form: str | list[SPLSection] | None = None
    spl_chain: str | dict | None = None
    parameters: str | dict | None = None

    @model_validator(mode='before')
    def check(cls, values):
        sample_query = values.get('sample_query')
        if sample_query is not None:
            values['sample_query'] = json.dumps(sample_query, ensure_ascii=False)

        spl_form = values.get('spl_form')
        if spl_form is not None:
            values['spl_form'] = json.dumps(spl_form, ensure_ascii=False)

        spl_chain = values.get('spl_chain')
        if spl_chain is not None:
            values['spl_chain'] = json.dumps(spl_chain, ensure_ascii=False)

        parameters = values.get('parameters')
        if parameters is not None:
            values['parameters'] = json.dumps(parameters, ensure_ascii=False)

        tags = values.get('tags')
        if tags is not None:
            values['tags'] = json.dumps(tags, ensure_ascii=False)

        return values


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
    tags: str | list | None = []
    created_time: datetime
    updated_time: datetime | None = None


# Agent 列表信息结构
class AgentListSchema(AgentSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    welcome_info: str | None = ''
    sample_query: str | list | None = '[]'
    parameters: str | dict | None = '{}'

    created_time: datetime
    updated_time: datetime | None = None

    @model_validator(mode='after')
    def handle(self):
        sample_query = self.sample_query
        if sample_query is not None:
            self.sample_query = json.loads(sample_query)

        parameters = self.parameters
        if parameters is not None:
            self.parameters = json.loads(parameters)

        tags = self.tags
        if tags is not None:
            self.tags = json.loads(tags)
        elif tags is None:
            self.tags = []
        return self


# 给 Agent 添加插件参数
class AddAgentPluginParam(SchemaBase):
    plugin_uuids: list[str]


class PublishmentItem(SchemaBase):
    channel_uuid: str
    publish_config: Dict


class AgentPublishParam(SchemaBase):
    publishments: List[PublishmentItem]


# 给 Agent 添加知识库参数
class AddAgentKnowledgeBaseParam(SchemaBase):
    knowledge_base_uuids: list[str]


class QueryAgentParam(SchemaBase):
    conversation_uuid: str | None = None
    message: list
    stream: bool = True
    debug_unit: int | None = None

    @model_validator(mode='before')
    def check(cls, values):
        print(values)
        if type(values) == list or type(values) == dict:
            message = values.get('message')
            if message is not None and type(message) == str:
                values['message'] = [{'type': 'text', 'content': message}]
            return values
        return json.loads(values)

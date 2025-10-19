from pydantic import BaseModel,HttpUrl
from .data import TextData, GraphData
from pydantic import Field, model_validator
from .base import API, KnowledgeBase, Parameter
from .memory import AgentMemory, LongMemory, ShortMemory
from .chain import  Unit


class Conversation(BaseModel):
    name: str
    uuid: str
    agent_memory: AgentMemory | str | dict


class SplChain(BaseModel):
    global_params: list[Parameter]
    workflow: list[Unit]


class Agent(BaseModel):
    uuid: str
    name: str
    description: str
    type: int = Field(..., description="智能体类型(0管理型 1功能型)")
    spl_chain: SplChain| dict | list | None = '[]'
    parameter_base: list[Parameter] | dict | None = '{}'
    API_base: list[API] | None = None  # 与智能体相关联的插件
    knowledge_bases: list[KnowledgeBase] | None = None  # 与智能体相关联的知识库
    long_memory: LongMemory | str
    short_memory: ShortMemory | str
    suggestion: bool = False


class MagUnit:
    pass

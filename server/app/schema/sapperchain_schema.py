from pydantic import model_validator

from app.schema import GetAgentWorkSpace, ConservationDetailSchema
from common.schema import SchemaBase


class GenerateSplFormParam(SchemaBase):
    requirement: str


class GenerateSplChainParam(SchemaBase):
    agent_data: GetAgentWorkSpace


class GenerateAnswerParam(SchemaBase):
    agent_data: GetAgentWorkSpace
    conversation_data: ConservationDetailSchema | None = None
    query: list

    @model_validator(mode='before')
    def check(cls, values):
        return values


class GenerateAvatarParam(SchemaBase):
    requirement: str


class GenerateConversationNameParam(SchemaBase):
    query: str

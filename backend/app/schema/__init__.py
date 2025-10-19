from app.schema.conversation_schema import *
from app.schema.agent_schema import *
from app.schema.knowledge_base_schema import *
from app.schema.plugin_schema import *
from app.schema.embedding_schema import *
from app.schema.collection_schema import *
from app.schema.graph_collection_schema import *
from app.schema.text_block_schema import *
from app.schema.llm_provider_schema import *
from app.schema.publish import *
from app.schema.user_schema import *
from app.schema.interaction_schema import *


from typing import Optional, List
from pydantic import model_validator, Field
import json
from statistics import mean


class GetAgentDetail(AgentDetailSchema):
    emulator_conversation: Optional[ConversationListSchema] = None
    conversations: List[ConversationListSchema] = Field(default_factory=list)  # 当前用户的会话
    plugins: List[PluginDetailSchema] = Field(default_factory=list)
    knowledge_bases: List[KnowledgeBaseListSchema] = Field(default_factory=list)
    publishments: List[AgentPublishmentListSchema] = Field(default_factory=list)
    user: UserInfoSchemaBase  # 智能体创建者信息
    interactions: List[GetInteractionDetail] = Field(default_factory=list)  # 所有交互记录
    user_interaction: GetInteractionDetail = None

    # 所有用户的统计数据
    total_rating: Optional[float] = Field(None, description="所有用户的平均评分")
    rating_count: int = Field(0, description="所有评分次数")
    total_favorites: int = Field(0, description="总收藏次数")
    total_usage: int = Field(0, description="总使用次数")
    unique_users: int = Field(0, description="使用过的独立用户数")

    @model_validator(mode='after')
    def calculate_stats(self) -> 'GetAgentDetail':
        # 处理JSON字段
        for field in ['sample_query', 'spl_form', 'spl_chain', 'parameters']:
            if getattr(self, field) is not None:
                setattr(self, field, json.loads(getattr(self, field)))
        self.tags = json.loads(self.tags) if self.tags else []

        # 计算所有用户的交互数据
        if self.interactions:
            # 总使用次数
            self.total_usage = sum(i.usage_count for i in self.interactions)

            # 总收藏次数
            self.total_favorites = sum(1 for i in self.interactions if i.is_favorite)

            # 平均评分（排除未评分的记录）
            ratings = [i.rating_value for i in self.interactions if i.rating_value is not None]
            self.total_rating = mean(ratings) if ratings else None
            self.rating_count = len(ratings) if ratings else 0
            # 独立用户数
            self.unique_users = len({i.user_uuid for i in self.interactions})

            self.user_interaction = [i for i in self.interactions if i.user_uuid == self.operator_uuid].pop()

        # 处理当前用户的会话
        if self.conversations:
            self.emulator_conversation = next(
                (conv for conv in reversed(self.conversations) if conv.status == 2),
                None
            )
            self.conversations = [
                conv for conv in self.conversations
                if conv.user_uuid == self.operator_uuid and conv.status != 2
            ]

        return self


# 当前 Agent 信息详情
class GetAgentWorkSpace(AgentDetailSchema):
    plugins: list[PluginDetailSchema] | None = None  # 与智能体相关联的插件
    knowledge_bases: list[GetKnowledgeBaseWorkSpace] | None = None  # 与智能体相关联的知识库

    @model_validator(mode='after')
    def handle(self):
        sample_query = self.sample_query
        if sample_query is not None:
            self.sample_query = json.loads(sample_query)

        spl_form = self.spl_form
        if spl_form is not None:
            self.spl_form = json.loads(spl_form)

        spl_chain = self.spl_chain
        if spl_chain is not None:
            self.spl_chain = json.loads(spl_chain)

        parameters = self.parameters
        if parameters is not None:
            self.parameters = json.loads(parameters)

        # conversations = self.conversations
        # if conversations is not None:
        #     # 过滤出符合条件的会话（即user_uuid匹配的会话）
        #     self.conversations = [conversation for conversation in conversations if
        #                           conversation.user_uuid == self.user_uuid]
        return self


# 当前 Agent 信息详情
class GetAgentList(AgentListSchema):
    user: GetUserInfoNoRelationDetail | None = None
    interactions: List[GetInteractionDetail] = Field(default_factory=list)  # 所有交互记录
    # 所有用户的统计数据
    total_rating: Optional[float] = Field(None, description="所有用户的平均评分")
    rating_count: int = Field(0, description="所有评分次数")
    total_favorites: int = Field(0, description="总收藏次数")
    total_usage: int = Field(0, description="总使用次数")
    unique_users: int = Field(0, description="使用过的独立用户数")

    @model_validator(mode='after')
    def calculate_stats(self) -> 'GetAgentList':
        # 计算所有用户的交互数据
        if self.interactions:
            # 总使用次数
            self.total_usage = sum(i.usage_count for i in self.interactions)

            # 总收藏次数
            self.total_favorites = sum(1 for i in self.interactions if i.is_favorite)

            # 平均评分（排除未评分的记录）
            ratings = [i.rating_value for i in self.interactions if i.rating_value is not None]
            self.total_rating = mean(ratings) if ratings else None
            self.rating_count = len(ratings) if ratings else 0
            # 独立用户数
            self.unique_users = len({i.user_uuid for i in self.interactions})

        return self


class GetConversationDetail(ConversationDetailSchema):
    agent: AgentListSchema
    knowledge_base: KnowledgeBaseListSchema
    collection: CollectionListSchema


# 当前 Conversation 信息详情
class GetConversationList(ConversationListSchema):
    pass


class GetAgentPublishmentList(AgentListSchema):
    pass


class GetAgentPublishmentDetail(AgentListSchema):
    pass

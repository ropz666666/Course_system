from app.schema.conservation_schema import *
from app.schema.agent_schema import *
from app.schema.knowledge_base_schema import *
from app.schema.plugin_schema import *
from app.schema.embedding_schema import *
from app.schema.collection_schema import *
from app.schema.graph_collection_schema import *
from app.schema.text_block_schema import *


class GetTextCollectionWorkSpace(CollectionDetailSchema):
    text_blocks: list[TextBlockDetailSchema]


class GetKnowledgeBaseWorkSpace(KnowledgeBaseDetailSchema):
    text_collections: list[GetTextCollectionWorkSpace] | None = None
    graph_collections: list[GraphCollectionDetailSchema] | None = None


class GetPluginWorkSpace(PluginDetailSchema):
    pass


# 当前 Agent 信息详情
class GetAgentWorkSpace(AgentDetailSchema):
    plugins: list[GetPluginWorkSpace] | None = None  # 与智能体相关联的插件
    knowledge_bases: list[GetKnowledgeBaseWorkSpace] | None = None  # 与智能体相关联的知识库
    long_memory: dict | int | None = None
    short_memory: dict | int | None = None

    @model_validator(mode='before')
    def check(cls, values):
        # print(values)
        knowledge_bases = values.get("knowledge_bases", [])
        for knowledge_base in knowledge_bases:
            text_collections = knowledge_base.get("collections", [])
            knowledge_base["text_collections"] = text_collections
            del knowledge_base['collections']
        values["knowledge_bases"] = knowledge_bases
        return values

import json
from app.schema import GetAgentWorkSpace, ConservationDetailSchema
from sapperchain.config.sapper_config import SapperConfigurator
from sapperchain.functions.agent_initiator.core import AgentExecutor, AgentInitializer
from sapperchain.functions.agent_initiator.components.memory_manager import LongMemoryManager, ShortMemoryManager
from sapperchain.functions.agent_initiator.components.chain_initializer import ChainInitializer, ParamInitializer,UnitInitializer, \
     DataViewDefiner, DataStatementInitializer, APIStatementInitializer, ToolModelStatementInitializer, MagModelStatementInitializer
from sapperchain.functions.agent_initiator.components.chain_executor import ChainExecutor, UnitExecutor, \
    APIStatementExecutor, DataStatementExecutor, ToolModelStatementExecutor, MagModelStatementExecutor
from sapperchain.plugins.DataRetrievalPlugin import GraphDataRetriever, TextDataRetriever
from app.conf import admin_settings


def temporary_processing(agent_data: GetAgentWorkSpace, conversation_data: ConservationDetailSchema):
    parameters = []
    for knowledge_base in agent_data.knowledge_bases:
        for graph in knowledge_base.graph_collections:
            for entity in graph.entities:
                entity["attributes"] = json.loads(entity["attributes"])
                entity["community_ids"] = entity["communities"]
            for community in graph.communities:
                try:
                    community["attributes"] = {}
                except Exception as e:
                    a = 1
            for relationship in graph.relationships:
                relationship["attributes"] = json.loads(relationship["attributes"])
                relationship["triple_source"] = relationship["source"]
        if len(knowledge_base.graph_collections) != 0:
            for graph in knowledge_base.graph_collections:
                for relationship in graph.relationships:
                    relationship["attributes"] = "{}"
                    for entity in graph.entities:
                        if entity["uuid"] == relationship["source_entity_uuid"]:
                            relationship["source_entity"] = entity["name"]
                        if entity["uuid"] == relationship["target_entity_uuid"]:
                            relationship["target_entity"] = entity["name"]

    for param_id, param_value in agent_data.parameters.items():
        parameters.append({"uuid":param_id,"type":param_value.get("value_type", 'string'), "placeholder":f"${{{param_id}}}$",
                           "description":"des", "value":param_value.get("content", "")})

    agent_data.parameters = parameters

    if conversation_data is not None:
        if agent_data.long_memory == 1:
            agent_data.long_memory = {"preference": "preference", "knowledge_collections": [], "APIs": []}
        else:
            agent_data.long_memory = {"preference": "preference", "knowledge_collections": [], "APIs": []}

        if agent_data.short_memory == 1:
            agent_data.short_memory = {"chat_history": conversation_data.chat_history, "parameters": []}
        else:
            agent_data.short_memory = {"chat_history": [], "parameters": []}

    else:
        agent_data.long_memory = {"preference": "preference", "knowledge_collections": [], "APIs": []}
        agent_data.short_memory = {"chat_history": [], "parameters": []}
    return agent_data


class RunChain:
    def __init__(self, agent, agent_executor) -> None:
        self.agent = agent
        self.agent_executor = agent_executor

    @classmethod
    async def create(cls, openai_key, agent_data: GetAgentWorkSpace, conversation_data: ConservationDetailSchema = None):
        agent_data = temporary_processing(agent_data, conversation_data)
        config = {
            "model_config": {
                "api_key": openai_key
            },
            "retriever_config": {
                "embedding_model_path": admin_settings.EMBEDDING_MODEL_PATH,
                "extract_model_name": "gpt-4.1",
                "embedding_model_name": "Dmeta-embedding",
                "graph_level": None,
                "max_context_token": 8000
            }
        }
        sapper_configurator = SapperConfigurator()
        sapper_configurator.set_up_sapper(config)
        long_memory_manager = LongMemoryManager(agent_data.long_memory)
        short_memory_manager = ShortMemoryManager(agent_data.short_memory)
        agent_data = agent_data.to_dict()
        data_view_definer = DataViewDefiner()
        API_statement_initializer = APIStatementInitializer(agent_data["plugins"])
        data_statement_initializer = DataStatementInitializer(agent_data["knowledge_bases"], data_view_definer)
        tool_model_statement_initializer = ToolModelStatementInitializer(sapper_configurator.base_model_config)
        mag_model_statement_initializer = MagModelStatementInitializer(agent_data["plugins"],
                                                                       sapper_configurator.base_model_config)

        param_initializer = ParamInitializer(agent_data["parameters"])
        unit_initializer = UnitInitializer(API_statement_initializer, data_statement_initializer,
                                           tool_model_statement_initializer, mag_model_statement_initializer)
        graph_data_retriever = GraphDataRetriever()
        text_data_retriever = TextDataRetriever(sapper_configurator.retriever_config.embedding_model_path)
        API_statement_executor = APIStatementExecutor()
        data_statement_executor = DataStatementExecutor(text_data_retriever, graph_data_retriever)
        tool_model_statement_executor = ToolModelStatementExecutor()
        mag_model_statement_executor = MagModelStatementExecutor()
        unit_executor = UnitExecutor(short_memory_manager, API_statement_executor, data_statement_executor,
                                     tool_model_statement_executor, mag_model_statement_executor)
        chain_initializer = ChainInitializer(param_initializer, unit_initializer, )
        agent_initializer = AgentInitializer(chain_initializer)
        agent = await agent_initializer.init_agent(agent_data)

        chain_executor = ChainExecutor(unit_executor, long_memory_manager)
        agent_executor = AgentExecutor(chain_initializer, chain_executor)

        return cls(agent, agent_executor)

    async def run_chain(self, request):
        # try:
        parsed_data = {"Text": "", 'File_Path': [], "Image": None}
        # 遍历并处理每个元素
        for item in request:
            if item["type"] == "text":
                parsed_data["Text"] += item["content"] + " "
            elif item["type"] == "image":
                parsed_data['File_Path'].append(item["content"])
            elif item["type"] == "speech":
                parsed_data['File_Path'].append(item["content"])
            elif item["type"] == "txt":
                parsed_data['File_Path'].append(item["content"])
            elif item["type"] == "file":
                parsed_data['File_Path'].append(item["content"])
        mag_user_request = parsed_data["Text"]
        async for res in self.agent_executor.run_agent_to_answer(self.agent, user_request=mag_user_request, file_path_list=parsed_data['File_Path']):
            yield res
        # except Exception as e:
        #     yield json.dumps({"type": "error", "content": f"Something went wrong while running the agent. Please try again.{str(e)}"})

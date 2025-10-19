import re

from ....data_model.agent import SplChain, API,  KnowledgeBase
from ....data_model.data import DataView, TextData, GraphData
from ....data_model.unit import Statement
from ....data_model.chain import Unit
from ....data_model.statement import APIInput, ModelInput, DataInput, Tool
from ....base.initializer import BaseChainInitializer, BaseUnitInitializer, BaseParamInitializer, BaseStatementInitializer
from pydantic import validate_call
from ....utils.translate import chinese_to_pinyin_x
from ....data_model.base import Parameter
from ....utils.match import match_placeholder


class ChainInitializer(BaseChainInitializer):
    def __init__(self,param_initializer, unit_initializer):
        super(ChainInitializer, self).__init__()
        self.param_initializer = param_initializer
        self.unit_initializer = unit_initializer

    async def __init_unit(self, source_unit):
        return await self.unit_initializer.init_unit(source_unit)

    async def __init_global_params(self, source_param):
        return await self.param_initializer.init_param(source_param)

    async def init_chain(self, source_chain):
        workflow = []
        global_params = []
        for source_unit in source_chain["workflow"]:
            unit = await self.__init_unit(source_unit)
            workflow.append(unit)
        for source_param in source_chain["global_params"]:
            global_param = await self.__init_global_params(source_param)
            global_params.append(global_param)
        chain = SplChain(global_params=global_params, workflow=workflow)
        return chain


class ParamInitializer(BaseParamInitializer):
    def __init__(self, parameter_base):
        super(ParamInitializer, self).__init__()
        self.parameter_base = self.__instantiate_parameter_base(parameter_base)

    @validate_call
    def __instantiate_parameter_base(self, parameter_base:list[Parameter]):
        return parameter_base

    async def init_param(self, source_param):
        for param in self.parameter_base:
            if source_param == param.uuid:
                return param
            else:
                pass


class UnitInitializer(BaseUnitInitializer):
    def __init__(self,API_statement_initializer, data_statement_initializer, tool_model_statement_initializer, mag_model_statement_initializer):
        super(UnitInitializer, self).__init__()
        self.API_statement_initializer = API_statement_initializer
        self.data_statement_initializer = data_statement_initializer
        self.tool_model_statement_initializer = tool_model_statement_initializer
        self.mag_model_statement_initializer = mag_model_statement_initializer

    async def __extract_unit_input(self,statements):
       for statement in statements:
           if "model" in statement.type:
               return statement.input
       return statements[0].input

    async def init_unit(self, source_unit):
        statements = []
        for statement_type, source_statement in source_unit["functions"].items():
            if "data" in statement_type:
                statement = await self.data_statement_initializer.init_statement(source_statement)
                statements.append(statement)
            elif "API" in statement_type:
                statement = await self.API_statement_initializer.init_statement(source_statement)
                statements.append(statement)
            elif "tool_model" in statement_type:
                statement = await self.tool_model_statement_initializer.init_statement(source_statement)
                statements.append(statement)
            elif "mag_model" in statement_type:
                statement = await self.mag_model_statement_initializer.init_statement(source_statement)
                statements.append(statement)
            else:
                pass

        return Unit(name=source_unit["name"],input = await self.__extract_unit_input(statements), description=source_unit["description"], type=source_unit["type"], func_statements=statements)


class APIStatementInitializer(BaseStatementInitializer):
    def __init__(self, API_base):
        super(APIStatementInitializer, self).__init__()
        self.API_base = self.__instantiate_API_base(API_base)

    @validate_call
    def __instantiate_API_base(self, API_base: list[API]):
        return API_base

    async def init_statement(self, source_statement):
        API_ = next((api for api in self.API_base if api.uuid == source_statement["link_id"]), None)
        if API_ != None:
            input = APIInput(
                server_url=API_.server_url,
                api_parameter=source_statement["input"],
                parse_path=API_.parse_path,
                return_value_type=API_.return_value_type,
                content_type=API_.content_type,
                authorization=API_.authorization,
                stream=API_.stream
            )
            return Statement(name=API_.name, description=API_.description, type="API", input=input,output=source_statement["output"])


class DataStatementInitializer(BaseStatementInitializer):
    def __init__(self, data_base, data_view_definer):
        super(DataStatementInitializer, self).__init__()
        self.data_base = self.__instantiate_data_base(data_base)
        self.data_view_definer = data_view_definer

    @validate_call
    def __instantiate_data_base(self, data_base: list[KnowledgeBase]):
        return data_base

    async def init_statement(self, source_statement):
        data = next((api for api in self.data_base if api.uuid == source_statement["link_id"]), None)
        if data != None:
            # 这里需要修改，暂时先这样========================================
            data_view = DataView(text_view=None, graph_view=None)
            if data.text_collections != []:
                data_source = self.data_view_definer.def_text_view(data.text_collections)
                data_view.text_view = data_source
            else:
                data_source = self.data_view_definer.def_graph_view(data.graph_collections)
                data_view.graph_view = data_source
            data_input = DataInput(content_type="text", api_parameter=source_statement["input"], return_value_type="text", data_view=data_view)
            return Statement(name=data.name, description=data.description, type="data", input=data_input,output=source_statement["output"])


class ToolModelStatementInitializer(BaseStatementInitializer):
    def __init__(self, model):
        super(ToolModelStatementInitializer, self).__init__()
        self.model = model

    async def init_statement(self, source_statement):
        model = API(
            name="chat_bot",
            description="chat",
            uuid=self.model.uuid,
            server_url=self.model.server_url,
            api_parameter={"model": self.model.model,
                           "messages": [{"role": "system", "content": source_statement["model_prompt"]},
                                        {"role": "user", "content": source_statement["input"]}]},
            parse_path=self.model.tool_model_parse_path,
            content_type=self.model.content_type,
            authorization=self.model.authorization,
            stream=True
        )
        input = ModelInput(
            server_url=model.server_url,
            api_parameter=model.api_parameter,
            parse_path=model.parse_path,
            return_value_type=model.return_value_type,
            content_type=model.content_type,
            authorization=model.authorization,
            stream=model.stream
        )
        return Statement(name=model.name, description=model.description, type="tool_model", input=input, output=source_statement["output"])


class MagModelStatementInitializer(BaseStatementInitializer):
    def __init__(self,API_bases, model):
        super(MagModelStatementInitializer, self).__init__()
        self.model_tool = [self.__init_tool(API) for API in API_bases if self.__init_tool(API)]
        self.model = model

    @validate_call
    def __init_tool(self, API: API):
        api_keys = list(API.api_parameter.keys())
        if len(api_keys) > 0:
            input_schema = {
                "type": "object",
                "properties": {
                    f"{list(API.api_parameter.keys())[0]}": {"type": "string"},
                },
                "required": [list(API.api_parameter.keys())[0]]
            }
            tool_def = {
                "type": "function",
                "function": {
                    "name": re.sub(r'[^a-zA-Z]', '', chinese_to_pinyin_x(API.name))[:45],  # 只保留字母
                    "origin_name": API.name,
                    "description": API.description,  # 工具描述
                    "parameters": input_schema  # 工具输入模式
                }
            }

            tool = Tool(
                tool_def=tool_def,
                server_url=API.server_url,
                tool_parameter=API.api_parameter,
                parse_path=API.parse_path,
                return_value_type=API.return_value_type,
                content_type=API.content_type,
                authorization=API.authorization,
                stream=API.stream
            )

            return tool
        return None

    async def init_statement(self, source_statement):
        model = API(
            name="chat_bot",
            description="chat",
            uuid=self.model.uuid,
            server_url=self.model.server_url,
            api_parameter={"model": self.model.model,
                           "messages": [
                               {"role": "system", "content": source_statement["model_prompt"]},
                               {"role": "user", "content": source_statement["input"]}
                           ],
                           "tools": self.model_tool
                        },
            parse_path=self.model.mag_model_parse_path,
            content_type=self.model.content_type,
            authorization=self.model.authorization,
            stream=True
        )
        input = ModelInput(
            server_url=model.server_url,
            api_parameter=model.api_parameter,
            parse_path=model.parse_path,
            return_value_type=model.return_value_type,
            content_type=model.content_type,
            authorization=model.authorization,
            stream=model.stream
        )
        return Statement(name=model.name, description=model.description, type="mag_model", input=input,output=source_statement["output"])


class DataViewDefiner():
    def __init__(self):
        pass

    def def_text_view(self,data_base):
        temp_text_block = []
        for data in data_base:
            temp_text_block.extend(data.text_blocks)
        return TextData(text_blocks=temp_text_block)

    def def_graph_view(self, data_base):
        temp_entities = []
        temp_relationships = []
        temp_communities = []
        for data in data_base:
            temp_entities.extend(data.entities)
            temp_relationships.extend(data.relationships)
            temp_communities.extend(data.communities)
        return GraphData(entities=temp_entities, relationships=temp_relationships, communities=temp_communities)

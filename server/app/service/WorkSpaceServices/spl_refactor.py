from ..api_service import get_api_by_uuid
from ...common.AgentProperties import Chain, ExternalAPI, LongTerm_Memory, ShortTerm_Memory
from collections import deque
import json
from ..prompt_service import get_prompt_by_name
from ..agent_service import get_agent_by_uuid, edit_agent_by_uuid
from ..settings_service import get_settings_by_id
from ..user_service import get_user_by_uuid
from sqlalchemy.ext.asyncio import AsyncSession
from ...common.AgentType import ToolType
from ...common.AgentFunctionModuleBase.PromptRefactorModule import PromptRefactorer
from ...common.Tool import DecomposeUtility, ExternalAPIHandleUtility
class SPLRefactor:
    def __init__(self, agent, agent_uuid) -> None:
        self.agent = agent
        self.agent_uuid = agent_uuid

    @staticmethod
    async def get_settings_by_id(db: AsyncSession, id: int):
        return await get_settings_by_id(db, id)

    @staticmethod
    async def get_agent_by_uuid(db: AsyncSession, agent_uuid: str):
        agent = await get_agent_by_uuid(db, agent_uuid)
        return agent if agent else ''

    @staticmethod
    async def get_user_by_uuid(db: AsyncSession, user_uuid: str):
        user = await get_user_by_uuid(db, user_uuid)
        return user if user else ''

    @staticmethod
    async def get_api_by_uuid(db: AsyncSession, ebapi_uuid: str):
        api = await get_api_by_uuid(db, ebapi_uuid)
        return api if api else ''

    @staticmethod
    async def get_prompt(db: AsyncSession, name: str):
        prompt = await get_prompt_by_name(db, name)
        return prompt.prompt if prompt else ''

    @staticmethod
    async def update_agent(db: AsyncSession, agent_id: str, update_data: dict):
        return await edit_agent_by_uuid(db, agent_id, update_data)

    @classmethod
    async def create(cls, db: AsyncSession, agent_uuid):
        agentData = await cls.get_agent_by_uuid(db, agent_uuid)
        user = await cls.get_user_by_uuid(db, agentData.owner_uuid)
        API_Base = {}
        OpenAI_APIList = ['1', '2', '3', '4']
        for API_uuid in json.loads(agentData.api_call or "[]"):
            if API_uuid in OpenAI_APIList:
                API1 = ExternalAPI(API_Name="TextToImage",
                                      Description="The input is text, and the output is an image. (Generate images based on text.)",
                                      Server_Url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl?access_token=24.9a1ee895fc45b24e9a7db7a211e01544.2592000.1709556725.282335-43691480",
                                      Header_Info={'Content-Type': 'application/json'},
                                      Return_Info={"ReturnValue-Type": "Image_B64_Data",
                                            "Parse_Path": ["data", 0, "b64_image"]},
                                      API_Parameter={"model": "dall-e-3", "prompt": "{User_Request}", "n": 1,
                                                     "size": "1024x1024"})
                API2 = ExternalAPI(API_Name="ImageToText",
                                      Description="The elinput is an image, and the output is text. (Generate text based on images.)",
                                      Server_Url="https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large",
                                      Header_Info={"Content-Type": "application/octet-stream",
                                        "Authorization": "Bearer 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"},
                                      Return_Info={"ReturnValue-Type": "Text", "Parse_Path": [0, "generated_text"]},
                                      API_Parameter=None)
                if API_uuid == '1':
                    API_Base[API1.API_Name] = API1
                if API_uuid == '2':
                    API_Base[API2.API_Name] = API2
                continue
            APIData = await cls.get_api_by_uuid(db, API_uuid)
            if APIData == "":
                continue
            if APIData.api_parameter == "":
                parameter = None
            else:
                parameter = json.loads(APIData.api_parameter)
            API_Base[APIData.name] = ExternalAPI(API_Name=APIData.name,
                                           Description=APIData.description,
                                           Server_Url=APIData.server_url,
                                           Header_Info=json.loads(APIData.header_info),
                                           Return_Info=json.loads(APIData.return_info),
                                           API_Parameter=parameter)

        agentModel = ExternalAPI(API_Name="Chatbot",
                                    Description="",
                                    Server_Url="https://api.rcouyi.com/v1/chat/completions",
                                    Header_Info={'Content-Type': 'application/json',
                                                 "Authorization": f"Bearer {user.openai_key}"},
                                    Return_Info={"ReturnValue-Type": "Text",
                                                 "Parse_Path": ["choices", 0, "message", "content"]},
                                    API_Parameter={"model": json.loads(agentData.configure)['model'],
                                                   "messages": "{User_Request}"})
        agent = ToolType.ToolAgent(
              Model=agentModel,
              Name=agentData.name,
              Description="",
              Prompt=json.loads(agentData.spl_form),
              APIBase=API_Base,
              AIChain=Chain(deque(), deque()),
              LongTerm_Memory=LongTerm_Memory(),
              ShortTerm_Memory=ShortTerm_Memory(),
        )
        return cls(agent, agent_uuid)

    async def run_refactor(self, db):
        try:
            prompt_decomposer = DecomposeUtility(self.agent.APIBase, ExternalAPIHandleUtility(self.agent.Model))
            prompt_refactorer = PromptRefactorer(prompt_decomposer)
            async for response in prompt_refactorer.RefactorPrompt(self.agent.Prompt):
                # agent_data = {'spl': json.dumps(refactor_spl)}
                # await SPLRefactor.update_agent(db, self.agent_uuid, agent_data)
                yield response
        except Exception as e:
            yield json.dumps({'type': 'logInfo', 'content': "Error: Something went wrong while refactoring the form. Please review your changes and try again.\n"})
        yield "__END_OF_RESPONSE__"

import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any
import http.client
import httpx
from dotenv import load_dotenv
from xpinyin import Pinyin
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel

from common.Tool import ExternalAPIHandleUtility

TOOL_CHOOSE_PROMPT = '''
You are a helpful assistant with access to these tools:
{tools_description}
Choose the appropriate tool based on the user's question. 
If no tool is needed, reply directly.
IMPORTANT: When you need to use a tool, you must ONLY respond with the exact JSON object format below, nothing else:
{{
    "tool": "tool-name",
    "arguments": {{
        "argument-name": "value"
        }}
}}
After receiving a tool's response:
1. Keep responses concise but informative
2. Focus on the most relevant information
Please use only the tools that are explicitly defined above.
'''


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class ToolCall(BaseModel):
    name: str
    arguments: dict

class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self.api_key = "sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd"

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:

        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        return self.api_key


class Server:
    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.stdio_context: Any | None = None
        # self.session: ClientSession | None = None
        self.session:  None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection."""
        command = (
            shutil.which("npx")
            if self.config["command"] == "npx"
            else self.config["command"]
        )
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]}
            if self.config.get("env")
            else None,
        )
        try:

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()

            self.session = session
        except Exception as e:
            print(e)
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self,API_Base) -> list[Any]:

        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.session.list_tools()
        tools = []

        for tool in tools_response.tools:
            tools.append(Tool(tool.name, tool.description, tool.inputSchema))

        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> Any:

        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)

                return result

            except Exception as e:
                logging.info(e)
                attempt += 1
                logging.warning(
                    f"Error executing tool: {e}. Attempt {attempt} of {retries}."
                )
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")

class Tool:
    """Represents a tool with its properties and formatting."""

    def __init__(
        self, name: str, description: str, input_schema: dict[str, Any]
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:

        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = (
                    f"- {param_name}: {param_info.get('description', 'No description')}"
                )
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        return f"""
            Tool: {self.name}
            Description: {self.description}
            Arguments:
            {chr(10).join(args_desc)}
            """

class ToolArgument(BaseModel):
    content: dict

class ToolAnswer(BaseModel):
    tool_name: str
    tool_argument: ToolArgument

class Answer(BaseModel):
    IFTool: bool
    content: str | ToolAnswer

class LLMClient:
    """Manages communication with the LLM provider."""

    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.base_config = {
            "model": "gpt-4o",
            "temperature": 0.7,
            "top_p": 1,
            "stream": False,
            "stop": None,
        }
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.rcouyi.com/v1")
    def get_response(self, messages: list[dict[str, str]], **kwargs) -> str:

        payload = self.base_config
        payload["messages"] = messages
        if kwargs.get("tools") != None :
            payload["tools"] = kwargs["tools"]
        else:
            pass
        try:
            conn = http.client.HTTPSConnection("api.rcouyi.com")
            conn.request("POST", "/v1/chat/completions", json.dumps(payload), self.headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            a = 1
            return data

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logging.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logging.error(f"Status code: {status_code}")
                logging.error(f"Response details: {e.response.text}")

            return (
                f"I encountered an error: {error_message}. "
                "Please try again or rephrase your request."
            )
client = OpenAI(
        base_url="https://api.rcouyi.com/v1",
        api_key="sk-tQ8RTjMtsRn5Na5H82F0EeBb7e4946198d2e840a48BfBb90",
    )

async def stream_generate(message,tools):

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=message,
        stream=True,
        tools=tools
    )
    for chunk in stream:
        if len(chunk.choices) > 0:

            yield chunk.choices[0]


async def stream_text(text, delay=0.1):
    for char in text:
        yield char
        await asyncio.sleep(delay)


def split_string(input_str):
    return [word for word in input_str.split(' ') if word]


def split_json_objects(s):
    stack = []
    parts = []  # 存储分割后的JSON字符串
    start_index = 0  # 记录每个JSON对象的起始位置

    for i, char in enumerate(s):
        if char == '{':
            stack.append(char)  # 遇到左括号入栈
        elif char == '}':
            if stack:
                stack.pop()  # 遇到右括号出栈
            else:
                raise ValueError("多余的右括号 at index {}".format(i))

            # 栈空时表示一个完整JSON对象结束
            if not stack:
                parts.append(s[start_index:i + 1])
                start_index = i + 1  # 下一个对象起始位置

    # 最终检查栈是否为空
    if stack:
        raise ValueError("括号未闭合")

    return parts


def chinese_to_pinyin_x(text, tone=True, splitter=' '):
    """
    使用xpinyin库转换拼音
    :param text: 中文字符串
    :param tone: 是否带声调(默认True)
    :param splitter: 分隔符(默认空格)
    :return: 拼音字符串
    """
    p = Pinyin()
    if tone:
        return p.get_pinyin(text, splitter=splitter)
    else:
        return p.get_pinyin(text, splitter=splitter, tone_marks='numbers')



class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, llm_client: LLMClient) -> None:

        self.llm_client: LLMClient = llm_client

    async def process_llm_response(self, tool_call, API_base):
        tool_name = tool_call["name"]
        tool_arguments = tool_call["arguments"]
        print(f"Executing tool: {tool_name}")
        print(f"With arguments: {tool_arguments}")
        answer = "No tool"

        for API in API_base.values():
            if API.API_Name == tool_name:
                API_handler = ExternalAPIHandleUtility(API)
                API.API_Parameter = tool_arguments
                if "sapper" in str(API.Server_Url):
                    # print(f"api_parameter:{API.api_parameter}")

                    answer = API_handler.run_stream()
                    async for part in answer:
                        yield part
                else:
                    answer = API_handler.Run()
                    yield answer



    async def start(self, user_input, API_base):
        all_tools = []
        pingyi_to_eng = {}
        for API in API_base.values():
            pingyi_to_eng[chinese_to_pinyin_x(API.API_Name).replace(" ","")] = API.API_Name
            API.API_Name = chinese_to_pinyin_x(API.API_Name).replace(" ","")

            pingyi_to_eng[list(API.API_Parameter.keys())[0]] = API.API_Name
            input_schema = {
                        "type": "object",
                        "properties": {
                            f"{list(API.API_Parameter.keys())[0]}": {"type": "string"},
                        },
                        "required": [list(API.API_Parameter.keys())[0]]
                    }
            all_tools.append(Tool(API.API_Name, API.Description,input_schema))

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,  # 工具描述
                "parameters": tool.input_schema  # 工具输入模式
            }
        } for tool in all_tools]
        print("available_tools", available_tools)
        tools_description = "\n".join([tool.format_for_llm() for tool in all_tools])

        messages = [{"role": "system", "content": TOOL_CHOOSE_PROMPT.format(tools_description=tools_description)}]


        try:
            messages.append({"role": "user", "content": user_input})
            argument_text = ""
            tool_name = []
            ids = []
            finish_reason = None
            yield "[progress]: 正在进行问题分析..."
            async for res in stream_generate(messages, available_tools):
                if hasattr(res.delta, 'tool_calls') is not None:
                    if res.delta.tool_calls != None:
                        if res.delta.tool_calls[0].function.name != None:
                            tool_name.append(res.delta.tool_calls[0].function.name)

                            if res.delta.tool_calls[0].id!=None:
                                ids.append(res.delta.tool_calls[0].id)
                            else:
                                pass
                        elif res.delta.tool_calls[0].function.arguments:
                            argument_text += res.delta.tool_calls[0].function.arguments
                            if res.delta.tool_calls[0].id!=None:
                                ids.append(res.delta.tool_calls[0].id)
                            else:
                                pass
                    else:
                        if res.delta.content != None:
                            yield res.delta.content
                if hasattr(res, 'finish_reason'):
                    if res.finish_reason == None:
                        pass
                    else:
                        finish_reason = res.finish_reason
            print(tool_name)
            print(argument_text)
            print(ids)
            while True:
                if finish_reason == "stop":
                    break
                else:
                    structured_argument = split_json_objects(argument_text)
                    tool_calls = []
                    temp_mes = []
                    for index, tool in enumerate(tool_name):
                        yield "\n##### 已选中 " + pingyi_to_eng[tool] + "\n"


                        temp_mes.append(
                            {
                                'function': {
                                    'arguments': structured_argument[index],
                                    'name': tool
                                },
                                'id': ids[index],
                                'type': 'function'}
                        )


                        tool_calls.append({
                            "name": tool,
                            "arguments": json.loads(structured_argument[index]),
                            "id": ids[index]
                        })
                    messages.append(
                        {'role': 'assistant',
                         'content': None,
                         'refusal': None,
                         'tool_calls': temp_mes
                         }
                    )
                    print(f"finish_reason:{finish_reason}")
                    print(f"tool_calls:{tool_calls}")
                    if finish_reason == "tool_calls":
                        for tool_call in tool_calls:
                            yield "[progress]: 正在执行 "+ pingyi_to_eng[tool_call["name"]]
                            result = self.process_llm_response(tool_call, API_base)
                            yield "\n##### 以下是 " + pingyi_to_eng[tool_call["name"]] + " 的执行结果\n"
                            fina_res = ''
                            async for char in result:
                                fina_res+=char
                                yield char
                            messages.append({
                                "role": "tool",
                                "name": tool_call['name'],
                                "tool_call_id": tool_call['id'],
                                "content": f"tool result:{fina_res}",
                            })

                        print("messages",messages)
                        tool_name = []
                    async for res in stream_generate(messages, available_tools):
                        if hasattr(res.delta, 'tool_calls') is not None:
                            if res.delta.tool_calls != None:

                                if res.delta.tool_calls[0].function.name != None:
                                    tool_name.append(res.delta.tool_calls[0].function.name)
                                    print("second",tool_name)
                                    if res.delta.tool_calls[0].id != None:
                                        ids.append(res.delta.tool_calls[0].id)
                                    else:
                                        pass
                                elif res.delta.tool_calls[0].function.arguments:
                                    argument_text += res.delta.tool_calls[0].function.arguments
                                    if res.delta.tool_calls[0].id != None:
                                        ids.append(res.delta.tool_calls[0].id)
                                    else:
                                        pass
                            else:
                                if res.delta.content != None:
                                    yield res.delta.content
                        if hasattr(res, 'finish_reason'):
                            if res.finish_reason == None:
                                pass
                            else:
                                finish_reason = res.finish_reason

        except Exception as e:
            pass





async def init():
    config = Configuration()
    llm_client = LLMClient(config.llm_api_key)
    chat_session = ChatSession(llm_client)
    return chat_session

async def main(chat_session,user_request, API_base):
    """Initialize and run the chat session."""
    async for char in chat_session.start(user_request, API_base):
        yield char
        # logging.info(char)


# async def x():
#     chat_session = await init()
#     await main(chat_session)
# from fastapi.responses import StreamingResponse
# if __name__ == "__main__":
#     # chat_session = await init()
#     asyncio.run(x())

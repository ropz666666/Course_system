import importlib
import sys

from common.AgentProperties import ExternalAPI

project_root = "E:/virtual_teacher_server"  # 根据实际结构调整
sys.path.append(str(project_root))
import asyncio
import logging
import sys
from base_module.base import Prompt, CommonOutput,AI_WRITER_Output,AI_REVIEWER_Output
from model_module.function_moudle.llm_call.openai_ import ChatModel
from config import args
import mcp.types as types
from common.Tool import ExternalAPIHandleUtility
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from app.api.v1.custom_plugin_router import custom_image_to_text
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from mcp.server import Server, NotificationOptions
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from app.schema.plugin_schema import (
 ImageRequest, MarkdownConvertRequest
)

async def serve() -> Server:
    server = Server("agent_module_server")


    @server.list_tools()
    async def handle_list_tools(API_base) -> list[types.Tool]:
        tool_list = []

        for API in API_base:
            tool_list.append(
                types.Tool(
                    name=API.API_Name,
                    description=API.Description,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            f"{list(API.api_parameter.keys())[0]}": {"type": "string"},
                        },
                        "required": [list(API.api_parameter.keys())[0]]
                    }
                )
            )
        return tool_list

    @server.call_tool()
    async def handle_tool_call(name: str, arguments: dict | None, API_base) -> list[types.TextContent]:

        try:
            if not arguments:
                answer = "No tool"
                for API in API_base:
                    if API.API_Name == name:
                        API_handler = ExternalAPIHandleUtility(API)
                        if "sapper" in API.Server_Url:
                            answer = await API_handler.run_stream()
                        else:
                            answer = API_handler.Run()
                return [types.TextContent(type="text", text=f"{answer}")]

            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Tool call failed: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    return server


def main():
    try:
        async def _run():
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                server = await serve()
                await server.run(
                    read_stream, write_stream,
                    InitializationOptions(
                        server_name="agent_module_server",
                        server_version="0.1.0",
                        capabilities=server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        )
                    )
                )
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Server failed")
        sys.exit(1)


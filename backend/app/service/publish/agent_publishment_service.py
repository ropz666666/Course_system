from typing import Sequence
from uuid import uuid4

from fastapi import Request
from sqlalchemy import Select, Row, RowMapping

from app.conf import admin_settings
from app.crud.crud_agent import agent_dao
from app.crud.crud_plugin import plugin_dao
from app.model import AgentPublishment
from app.schema import AddAgentPublishmentSchema, UpdateAgentParam, CreatePluginParam
from app.schema import (
    CreateAgentPublishmentParam,
    UpdateAgentPublishmentParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from app.crud.crud_agent_publishment import agent_publishment_dao
from utils.sapper_server import send_async_request
from common.id_generation import generate_id


class AgentPublishmentService:
    @staticmethod
    async def add(*, request: Request, obj: CreateAgentPublishmentParam) -> None:
        for channel in obj.channels:
            publishment_obj = AddAgentPublishmentSchema(agent_uuid=obj.agent_uuid, channel_uuid=channel.channel_uuid,
                                                        published_by=obj.published_by)
            async with async_db_session.begin() as db:
                agent = await agent_dao.get_by_uuid(db=db, uuid=obj.agent_uuid)

            async with async_db_session.begin() as db:
                if channel.channel_uuid == 'a0c4c008-2201-11f0-a583-0250f2000002':
                    await agent_dao.update(db=db, agent_uuid=obj.agent_uuid, obj=UpdateAgentParam(status=2))
                elif channel.channel_uuid == 'a0c4bfaf-2201-11f0-a583-0250f2000002':
                    publishment_obj.publish_config = {
                        'Token': f"{generate_id(32)}",
                        'URL': f"https://sapperapi.jxselab.com/api/v1/sapper/agent/wechat/generate_answer/{obj.agent_uuid}",
                        'EncodingAESKey': f"{generate_id(43)}"}
                elif channel.channel_uuid == 'a0c43b23-2201-11f0-a583-0250f2000002':
                    obj = CreatePluginParam(
                        user_uuid=request.user.uuid,
                        name=agent.name,
                        description=agent.description,
                        server_url=f'{admin_settings.SAPPER_BACKEND_URL}sapper/agent/generate_answer/{agent.uuid}',
                        content_type='application/json',
                        authorization=request.headers.get('Authorization'),
                        return_value_type='Text',
                        parse_path=['current_unit', 'output', 'content'],
                        api_parameter={'message': '${UserRequest}$'},
                        status=3
                    )
                    plugin = await plugin_dao.create(db=db, obj=obj)

                    publishment_obj.publish_config = {
                        'plugin_uuid': plugin.uuid,
                        'Authorization': f"{request.headers.get('Authorization')}",
                        'URL': f'{admin_settings.SAPPER_BACKEND_URL}sapper/agent/generate_answer/{agent.uuid}',
                        'Example': f"""
import json
import httpx
from httpx import Timeout
import asyncio

authorization = '{request.headers.get('Authorization')}'
server_url = '{admin_settings.SAPPER_BACKEND_URL}sapper/agent/generate_answer/{agent.uuid}'

async def main():
    query = '你好'
    headers = {{
        "Content-Type": 'application/json',
        "Authorization": authorization
    }}
    data = {{
        "message": query
    }}
    async with httpx.AsyncClient(timeout=Timeout(60.0, read=360.0)) as client:
        async with client.stream("POST", server_url, headers=headers, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    payload = json.loads(line[6:])
                    result = payload
                    for key in ['current_unit', 'output', 'content']:
                        result = result.get(key, "")
                        if not result: break
                    if result: print(result, end="", flush=True)
                    if payload.get("choices") and payload["choices"][0].get("finish_reason") == "stop":
                        break

asyncio.run(main())
                        """
                    }
                    async with async_db_session.begin() as update_db:
                        await agent_dao.update(db=update_db, agent_uuid=agent.uuid,
                                               obj=UpdateAgentParam(deploy_plugin_uuid=plugin.uuid))

            async with async_db_session.begin() as db:
                await agent_publishment_dao.create(db, obj=publishment_obj)


    @staticmethod
    async def update(*, request: Request, agent_publishment_uuid: str, obj: UpdateAgentPublishmentParam) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            agent_publishment = await agent_publishment_dao.get_by_uuid(db, agent_publishment_uuid)
            if not agent_publishment:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能修改
            if not request.user.is_superuser and agent_publishment.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该会话")

            # 更新会话
            count = await agent_publishment_dao.update(db, agent_publishment_uuid, obj)
            return count

    @staticmethod
    async def update_status(*, request: Request, agent_publishment_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            agent_publishment = await agent_publishment_dao.get_by_uuid(db, agent_publishment_uuid)
            if not agent_publishment:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能修改
            if not request.user.is_superuser and agent_publishment.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该会话")

            # 更新会话状态
            count = await agent_publishment_dao.set_status(db, agent_publishment_uuid, status)
            return count

    @staticmethod
    async def delete(*, request: Request, agent_publishment_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            agent_publishment = await agent_publishment_dao.get_by_uuid(db, agent_publishment_uuid)

        if not agent_publishment:
            raise errors.NotFoundError(msg="会话不存在")

        if agent_publishment.channel_uuid == 'a0c4c008-2201-11f0-a583-0250f2000002':
            async with async_db_session.begin() as db:
                await agent_dao.update(db=db, agent_uuid=agent_publishment.agent_uuid, obj=UpdateAgentParam(status=1))
        elif agent_publishment.channel_uuid == 'a0c43b23-2201-11f0-a583-0250f2000002':
            if agent_publishment.publish_config.get('plugin_uuid', None) is not None:
                async with async_db_session.begin() as db:
                    await plugin_dao.delete(db, agent_publishment.publish_config.get('plugin_uuid', None))

        # 删除会话
        count = await agent_publishment_dao.delete(db, agent_publishment_uuid)
        return count

    @staticmethod
    async def get_agent_publishment(*, request: Request, agent_publishment_uuid: str) -> AgentPublishment:
        async with async_db_session() as db:
            # 获取会话并检查权限
            agent_publishment = await agent_publishment_dao.get_by_uuid(db, agent_publishment_uuid)
            if not agent_publishment:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能获取
            if not request.user.is_superuser and agent_publishment.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限查看该会话")

            return agent_publishment

    @staticmethod
    async def get_select(*, user_uuid: str = None, name: str = None, agent_uuid: str = None, status: int = None) -> Select:
        return await agent_publishment_dao.get_list(user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, agent_uuid: str = None) -> Sequence[
        Row[AgentPublishment] | RowMapping | AgentPublishment]:
        async with async_db_session() as db:
            return await agent_publishment_dao.get_all(db=db, user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    @staticmethod
    async def get_with_relation(*, request: Request, agent_publishment_uuid: str) -> AgentPublishment:
        """
        获取会话与相关信息（智能体等）
        """
        async with async_db_session() as db:
            agent_publishment = await agent_publishment_dao.get_with_relation(db, agent_publishment_uuid)
            if not agent_publishment:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能获取
            if not request.user.is_superuser and agent_publishment.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限查看该会话")

            return agent_publishment

    @staticmethod
    async def generate_name(*, query: str) -> str:
        data = {
            "query": query
        }
        url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-agent_publishment-name'
        headers = {
            "Content-Type": "application/json"
        }
        res = ''
        async for response in send_async_request(url, headers, data):
            res = response
        return res.get('content', "新会话")


agent_publishment_service = AgentPublishmentService()

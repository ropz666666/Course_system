import asyncio
import json
import time
from typing import List, Sequence, AsyncGenerator

from fastapi import Request, WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Select, Row, RowMapping

from app.crud.crud_conversation import conversation_dao
from app.crud.crud_interaction import interaction_dao
from app.model import Agent
from app.schema import (
    CreateAgentParam,
    UpdateAgentParam,
    AddAgentPluginParam,
    AddAgentKnowledgeBaseParam, GetAgentDetail, GetAgentList, GetAgentWorkSpace, ConversationDetailSchema
)
from common.exception import errors
from common.log import log
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_agent import agent_dao
from utils.sapper_server import send_async_request
from utils.serializers import select_as_dict
import json


class AgentService:
    @staticmethod
    async def add(*, obj: CreateAgentParam) -> Agent:
        async with async_db_session.begin() as db:
            # 创建智能体
            return await agent_dao.create(db, obj)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, description: str = None) -> Sequence[
        Row[Agent] | RowMapping | Agent]:
        async with async_db_session() as db:
            return await agent_dao.get_all(db=db, user_uuid=user_uuid, description=description, name=name)

    @staticmethod
    async def get_all_public(*, name: str = None, description: str = None) -> Sequence[
        Row[Agent] | RowMapping | Agent]:
        async with async_db_session() as db:
            return await agent_dao.get_all_public(db=db, description=description, name=name)

    @staticmethod
    async def update(*, request: Request, agent_uuid: str, obj: UpdateAgentParam) -> int:
        async with async_db_session.begin() as db:
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该智能体")

            # 更新智能体
            count = await agent_dao.update(db, agent_uuid, obj)
            return count

    @staticmethod
    async def update_status(*, request: Request, agent_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查智能体是否存在
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该智能体")

            # 更新智能体状态
            count = await agent_dao.set_status(db, agent_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def add_plugin(*, request: Request, agent_uuid: str, plugin_param: AddAgentPluginParam) -> int:
        async with async_db_session.begin() as db:
            # 检查插件是否存在
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该智能体")

            # 添加插件
            await agent_dao.reset_plugins(db, agent_uuid, plugin_param)
            return 1

    @staticmethod
    async def add_knowledge_base(*, request: Request, agent_uuid: str,
                                 knowledge_base_param: AddAgentKnowledgeBaseParam) -> int:
        async with async_db_session.begin() as db:
            # 检查知识库是否存在
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该智能体")

            # 添加知识库
            await agent_dao.reset_knowledge_bases(db, agent_uuid, knowledge_base_param)
            return 1

    @staticmethod
    async def delete(*, request: Request, agent_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查智能体是否存在
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：普通用户只能删除自己的智能体
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该智能体")

            # 删除智能体
            count = await agent_dao.delete(db, agent_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_agent(*, request: Request, agent_uuid: str) -> Agent:
        async with async_db_session() as db:
            agent = await agent_dao.get_by_uuid(db, agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该智能体")

            return agent

    @staticmethod
    async def get_select(*,user_uuid: str = None, name: str = None, description: str = None, tag: str = None, status: int = None) -> Select:
        return await agent_dao.get_list(user_uuid=user_uuid, name=name, description=description, status=status, tag=tag)

    @staticmethod
    async def get_with_relation(*, request: Request, agent_uuid: str, is_wx_auth: bool = False) -> Agent:
        """
        获取智能体与相关信息（插件、知识库等）
        """
        async with async_db_session() as db:
            agent = await agent_dao.get_with_relation(db, agent_uuid=agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not is_wx_auth and not request.user.is_superuser and agent.user_uuid != request.user.uuid and agent.status != 2:
                raise errors.ForbiddenError(msg="您没有权限获得该智能体")
            return agent

    @staticmethod
    async def generate_spl_form(*, request: Request, agent_uuid: str) -> str:
        async with async_db_session() as db:
            agent = await agent_dao.get_with_relation(db=db, agent_uuid=agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')
            agent_data = GetAgentWorkSpace(**select_as_dict(agent))
        data = {
            "requirement": agent_data.description
        }
        url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-spl-form'
        headers = {
            "Content-Type": "application/json"
        }
        spl_form = []
        async with async_db_session() as db:
            async for response in send_async_request(url, headers, data):
                spl_form.append(response)
                await agent_dao.update(db, agent_uuid=agent_uuid, obj=UpdateAgentParam(spl_form=spl_form))
                await db.commit()
                yield f'data: {json.dumps(response, ensure_ascii=False)}\n\n'
                await asyncio.sleep(0.1)
        yield f'[DONE]'

    @staticmethod
    async def generate_spl_chain(*, request: Request, agent_uuid: str) -> str:
        async with async_db_session() as db:
            agent = await agent_dao.get_with_relation(db=db, agent_uuid=agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')
            agent_data = GetAgentWorkSpace(**select_as_dict(agent))
        data = {
            "agent_data": jsonable_encoder(agent_data)
        }
        url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-spl-chain'
        headers = {
            "Content-Type": "application/json"
        }
        async with async_db_session() as db:
            async for response in send_async_request(url, headers, data):
                if response.get('type', None) == 'result':
                    spl_chain = response.get('content', [])
                    update_data = UpdateAgentParam(spl_chain=spl_chain)
                    await agent_dao.update(db, agent_uuid=agent_uuid, obj=update_data)
                    await db.commit()
                # 返回每个响应数据
                yield f'data: {json.dumps(response, ensure_ascii=False)}\n\n'
                await asyncio.sleep(0.1)
        yield f'[DONE]'

    @staticmethod
    async def generate_answer(
            *,
            agent_uuid: str,
            query: str,
            conversation_uuid: str = None,
            debug: bool = False,
            debug_unit: int = None
    ) -> AsyncGenerator[str, None]:
        """生成智能体回答（流式输出）"""
        try:
            # 1. 获取智能体和会话数据
            conversation_data = None
            async with async_db_session() as db:
                agent = await agent_dao.get_with_relation(db=db, agent_uuid=agent_uuid)
                if not agent:
                    raise errors.NotFoundError(msg='智能体不存在')
                agent_data = GetAgentWorkSpace(**select_as_dict(agent))

            if conversation_uuid:
                async with async_db_session() as db:
                    conversation = await conversation_dao.get_with_relation(db=db, conversation_uuid=conversation_uuid)
                    if not conversation:
                        raise errors.NotFoundError(msg='会话不存在')
                    conversation_data = ConversationDetailSchema(**select_as_dict(conversation))

            # 2. 调试模式处理
            if debug and debug_unit is not None:
                if not agent_data.spl_chain or "workflow" not in agent_data.spl_chain:
                    raise ValueError("智能体工作流配置无效")
                try:
                    workflow = agent_data.spl_chain["workflow"][debug_unit]
                    agent_data.spl_chain["workflow"] = [workflow]
                except IndexError:
                    raise ValueError(f"无效的调试单元索引: {debug_unit}")

            # 3. 准备请求数据
            request_data = {
                "agent_data": jsonable_encoder(agent_data),
                "query": query
            }

            if conversation_data:
                request_data["conversation_data"] = jsonable_encoder(conversation_data)

            # 4. 发送请求并流式返回
            url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-answer'
            headers = {"Content-Type": "application/json"}

            async for chunk in send_async_request(url, headers, request_data):
                try:
                    yield json.dumps(chunk, ensure_ascii=False)
                except json.JSONDecodeError:
                    log.warning(f"Invalid JSON chunk: {chunk}")
                    continue

        except errors.NotFoundError as e:
            log.error(f"Resource not found: {str(e)}")
            # raise
        except ValueError as e:
            log.error(f"Invalid debug configuration: {str(e)}")
            # raise errors.BadRequestError(msg=str(e))
        except Exception as e:
            log.error(f"Unexpected error in generate_answer: {str(e)}", exc_info=True)
            # raise errors.ServerError(msg="生成回答时发生错误")

    @staticmethod
    async def generate_avatar(*, requirement: str) -> str:
        data = {
            "requirement": requirement,
        }
        url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-avatar'
        headers = {
            "Content-Type": "application/json"
        }
        async for response in send_async_request(url, headers, data):
            yield json.dumps(response)

    @staticmethod
    async def download_agent(*, request: Request, agent_uuid: str):
        async with async_db_session() as db:
            agent = await agent_dao.get_with_relation(db=db, agent_uuid=agent_uuid)
            if not agent:
                raise errors.NotFoundError(msg='智能体不存在')

            # 权限检查：如果不是超级管理员，且不是自己的智能体，不能修改
            if not request.user.is_superuser and agent.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该智能体")

            agent_data = GetAgentWorkSpace(**select_as_dict(agent))

            return agent_data


agent_service = AgentService()

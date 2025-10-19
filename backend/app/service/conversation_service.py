import json
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, Row, RowMapping

from app.crud.crud_collection import collection_dao
from app.crud.crud_knowledge_base import knowledge_base_dao
from app.model import Conversation
from app.schema import CreateKnowledgeBaseParam, CreateCollectionParam
from app.schema.conversation_schema import (
    CreateConversationParam,
    UpdateConversationParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from app.crud.crud_conversation import conversation_dao
from utils.sapper_server import send_async_request


class ConversationService:
    @staticmethod
    async def add(*, request: Request, obj: CreateConversationParam) -> Conversation:
        async with async_db_session.begin() as db:
            # 关联的用户UUID和智能体UUID
            knowledge_base = await knowledge_base_dao.create(db=db, obj=CreateKnowledgeBaseParam(
                user_uuid=request.user.uuid,
                name=obj.name,
                description=obj.name,
                cover_image=obj.name,
                status=2
            ))

        async with async_db_session.begin() as db:
            # 关联的用户UUID和智能体UUID
            collection = await collection_dao.create(db=db, obj=CreateCollectionParam(
                knowledge_base_uuid=knowledge_base.uuid,
                name="聊天笔记",
                file_url="聊天笔记",
            ))

        async with async_db_session.begin() as db:
            obj.knowledge_base_uuid = knowledge_base.uuid
            obj.collection_uuid = collection.uuid
            obj.user_uuid = request.user.uuid
            # 创建会话
            new_conversation = await conversation_dao.create(db, obj)
            return new_conversation

    @staticmethod
    async def update(*, request: Request, conversation_uuid: str, obj: UpdateConversationParam) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            conversation = await conversation_dao.get_by_uuid(db, conversation_uuid)
            if not conversation:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能修改
            if not request.user.is_superuser and conversation.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该会话")

            # 更新会话
            count = await conversation_dao.update(db, conversation_uuid, obj)
            return count

    @staticmethod
    async def update_status(*, request: Request, conversation_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            conversation = await conversation_dao.get_by_uuid(db, conversation_uuid)
            if not conversation:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能修改
            if not request.user.is_superuser and conversation.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该会话")

            # 更新会话状态
            count = await conversation_dao.set_status(db, conversation_uuid, status)
            return count

    @staticmethod
    async def delete(*, request: Request, conversation_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 获取会话并检查权限
            conversation = await conversation_dao.get_by_uuid(db, conversation_uuid)
            if not conversation:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：普通用户只能删除自己的会话
            if not request.user.is_superuser and conversation.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该会话")

            # 删除会话
            count = await conversation_dao.delete(db, conversation_uuid)
            return count

    @staticmethod
    async def get_conversation(*, request: Request, conversation_uuid: str) -> Conversation:
        async with async_db_session() as db:
            # 获取会话并检查权限
            conversation = await conversation_dao.get_by_uuid(db, conversation_uuid)
            if not conversation:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能获取
            if not request.user.is_superuser and conversation.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限查看该会话")

            return conversation

    @staticmethod
    async def get_select(*, user_uuid: str = None, name: str = None, agent_uuid: str = None, status: int = None) -> Select:
        return await conversation_dao.get_list(user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, agent_uuid: str = None) -> Sequence[
        Row[Conversation] | RowMapping | Conversation]:
        async with async_db_session() as db:
            return await conversation_dao.get_all(db=db, user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    @staticmethod
    async def get_with_relation(*, request: Request, conversation_uuid: str) -> Conversation:
        """
        获取会话与相关信息（智能体等）
        """
        async with async_db_session() as db:
            conversation = await conversation_dao.get_with_relation(db, conversation_uuid)
            if not conversation:
                raise errors.NotFoundError(msg="会话不存在")

            # 权限检查：如果不是超级管理员，且不是自己的会话，不能获取
            if not request.user.is_superuser and conversation.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限查看该会话")

            return conversation

    @staticmethod
    async def generate_name(*, query: str) -> str:
        data = {
            "query": query
        }
        url = f'{settings.SAPPER_SERVER_URL}sapperchain/generate-conversation-name'
        headers = {
            "Content-Type": "application/json"
        }
        res = ''
        async for response in send_async_request(url, headers, data):
            res = response
        return res.get('content', "新会话")


conversation_service = ConversationService()

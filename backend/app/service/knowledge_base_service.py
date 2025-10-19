import json
import time
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, Row, RowMapping
from app.model import KnowledgeBase
from app.schema.knowledge_base_schema import (
    CreateKnowledgeBaseParam,
    UpdateKnowledgeBaseParam,
    GetKnowledgeBaseDetail
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_knowledge_base import knowledge_base_dao


class KnowledgeBaseService:
    @staticmethod
    async def add(*, obj: CreateKnowledgeBaseParam) -> KnowledgeBase:
        async with async_db_session.begin() as db:
            # 创建知识库
            return await knowledge_base_dao.create(db, obj)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, description: str = None) -> Sequence[
        Row[KnowledgeBase] | RowMapping | KnowledgeBase]:
        async with async_db_session() as db:
            return await knowledge_base_dao.get_all(db=db, user_uuid=user_uuid, description=description, name=name)

    @staticmethod
    async def update(*, request: Request, knowledge_base_uuid: str, obj: UpdateKnowledgeBaseParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识库
            knowledge_base = await knowledge_base_dao.get_by_uuid(db, knowledge_base_uuid)
            if not knowledge_base:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and knowledge_base.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该知识库")

            # 更新知识库
            count = await knowledge_base_dao.update(db, knowledge_base_uuid, obj)
            # await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_status(*, request: Request, knowledge_base_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查知识库是否存在
            knowledge_base = await knowledge_base_dao.get_by_uuid(db, knowledge_base_uuid)
            if not knowledge_base:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and knowledge_base.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该知识库")

            # 更新知识库状态
            count = await knowledge_base_dao.set_status(db, knowledge_base_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, knowledge_base_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查知识库是否存在
            knowledge_base = await knowledge_base_dao.get_by_uuid(db, knowledge_base_uuid)
            if not knowledge_base:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：普通用户只能删除自己的知识库
            if not request.user.is_superuser and knowledge_base.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该知识库")

            # 删除知识库
            count = await knowledge_base_dao.delete(db, knowledge_base_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_knowledge_base(*, request: Request, knowledge_base_uuid: str) -> KnowledgeBase:
        async with async_db_session() as db:
            knowledge_base = await knowledge_base_dao.get_by_uuid(db, knowledge_base_uuid)
            if not knowledge_base:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and knowledge_base.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该知识库")

            return knowledge_base

    @staticmethod
    async def get_select(*,user_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await knowledge_base_dao.get_list(user_uuid=user_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, knowledge_base_uuid: str) -> KnowledgeBase:
        """
        获取知识库与相关信息（知识库、知识库等）
        """
        async with async_db_session() as db:
            knowledge_base = await knowledge_base_dao.get_with_relation(db, knowledge_base_uuid=knowledge_base_uuid)
            if not knowledge_base:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and knowledge_base.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该知识库")
            return knowledge_base


knowledge_base_service = KnowledgeBaseService()

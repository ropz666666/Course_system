import json
import time
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, Row, RowMapping
from app.model import Interaction
from app.schema.interaction_schema import (
    CreateInteractionParam,
    UpdateInteractionParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_interaction import interaction_dao


class InteractionService:
    @staticmethod
    async def add(*, obj: CreateInteractionParam) -> Interaction:
        async with async_db_session.begin() as db:
            # 创建知识库
            return await interaction_dao.create(db, obj)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, description: str = None) -> Sequence[
        Row[Interaction] | RowMapping | Interaction]:
        async with async_db_session() as db:
            return await interaction_dao.get_all(db=db, user_uuid=user_uuid, description=description, name=name)

    @staticmethod
    async def update(*, request: Request, interaction_uuid: str, obj: UpdateInteractionParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识库
            interaction = await interaction_dao.get_by_uuid(db, interaction_uuid)
            if not interaction:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and interaction.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该知识库")

            # 更新知识库
            count = await interaction_dao.update(db, interaction_uuid, obj)
            # await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_by_agent_user(*, request: Request, agent_uuid: str, obj: UpdateInteractionParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识库
            interaction = await interaction_dao.get_by_agent_user(db, agent_uuid, user_uuid=request.user.uuid )
            if not interaction:
                raise errors.NotFoundError(msg='该interaction不存在')

            # 更新知识库
            count = await interaction_dao.update(db, interaction.uuid, obj)
            return count

    @staticmethod
    async def update_usage_count(*, request: Request, agent_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识库
            interaction = await interaction_dao.get_by_agent_user(db, agent_uuid, user_uuid=request.user.uuid)
            if not interaction:
                raise errors.NotFoundError(msg='该interaction不存在')

            # 更新知识库
            count = await interaction_dao.update(db, interaction.uuid, obj=UpdateInteractionParam(usage_count=interaction.usage_count + 1))
            return count

    @staticmethod
    async def update_status(*, request: Request, interaction_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查知识库是否存在
            interaction = await interaction_dao.get_by_uuid(db, interaction_uuid)
            if not interaction:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and interaction.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该知识库")

            # 更新知识库状态
            count = await interaction_dao.set_status(db, interaction_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, interaction_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查知识库是否存在
            interaction = await interaction_dao.get_by_uuid(db, interaction_uuid)
            if not interaction:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：普通用户只能删除自己的知识库
            if not request.user.is_superuser and interaction.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该知识库")

            # 删除知识库
            count = await interaction_dao.delete(db, interaction_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_interaction(*, request: Request, interaction_uuid: str) -> Interaction:
        async with async_db_session() as db:
            interaction = await interaction_dao.get_by_uuid(db, interaction_uuid)
            if not interaction:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and interaction.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该知识库")

            return interaction

    @staticmethod
    async def get_select(*,user_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await interaction_dao.get_list(user_uuid=user_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, interaction_uuid: str) -> Interaction:
        """
        获取知识库与相关信息（知识库、知识库等）
        """
        async with async_db_session() as db:
            interaction = await interaction_dao.get_with_relation(db, interaction_uuid=interaction_uuid)
            if not interaction:
                raise errors.NotFoundError(msg='知识库不存在')

            # 权限检查：如果不是超级管理员，且不是自己的知识库，不能修改
            if not request.user.is_superuser and interaction.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该知识库")
            return interaction


interaction_service = InteractionService()

import json
import time
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, Row, RowMapping
from app.model import Plugin
from app.schema.plugin_schema import (
    CreatePluginParam,
    UpdatePluginParam,
    GetPluginDetail
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_plugin import plugin_dao


class PluginService:
    @staticmethod
    async def add(*, obj: CreatePluginParam) -> Plugin:
        async with async_db_session.begin() as db:
            # 创建插件
            return await plugin_dao.create(db, obj)

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None, description: str = None) -> Sequence[
        Row[Plugin] | RowMapping | Plugin]:
        async with async_db_session() as db:
            return await plugin_dao.get_all(db=db, user_uuid=user_uuid, description=description, name=name)

    @staticmethod
    async def update(*, request: Request, plugin_uuid: str, obj: UpdatePluginParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的插件
            plugin = await plugin_dao.get_by_uuid(db, plugin_uuid)
            if not plugin:
                raise errors.NotFoundError(msg='插件不存在')

            # 权限检查：如果不是超级管理员，且不是自己的插件，不能修改
            if not request.user.is_superuser and plugin.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该插件")

            # 更新插件
            count = await plugin_dao.update(db, plugin_uuid, obj)
            # await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_status(*, request: Request, plugin_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查插件是否存在
            plugin = await plugin_dao.get_by_uuid(db, plugin_uuid)
            if not plugin:
                raise errors.NotFoundError(msg='插件不存在')

            # 权限检查：如果不是超级管理员，且不是自己的插件，不能修改
            if not request.user.is_superuser and plugin.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该插件")

            # 更新插件状态
            count = await plugin_dao.set_status(db, plugin_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, plugin_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查插件是否存在
            plugin = await plugin_dao.get_by_uuid(db, plugin_uuid)
            if not plugin:
                raise errors.NotFoundError(msg='插件不存在')

            # 权限检查：普通用户只能删除自己的插件
            if not request.user.is_superuser and plugin.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该插件")

            # 删除插件
            count = await plugin_dao.delete(db, plugin_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_plugin(*, request: Request, plugin_uuid: str) -> Plugin:
        async with async_db_session() as db:
            plugin = await plugin_dao.get_by_uuid(db, plugin_uuid)
            if not plugin:
                raise errors.NotFoundError(msg='插件不存在')

            # 权限检查：如果不是超级管理员，且不是自己的插件，不能修改
            if not request.user.is_superuser and plugin.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该插件")

            return plugin

    @staticmethod
    async def get_select(*,user_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await plugin_dao.get_list(user_uuid=user_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, plugin_uuid: str) -> Plugin:
        """
        获取插件与相关信息（插件、知识库等）
        """
        async with async_db_session() as db:
            plugin = await plugin_dao.get_with_relation(db, plugin_uuid=plugin_uuid)
            if not plugin:
                raise errors.NotFoundError(msg='插件不存在')

            # 权限检查：如果不是超级管理员，且不是自己的插件，不能修改
            if not request.user.is_superuser and plugin.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该插件")
            return plugin


plugin_service = PluginService()

import json
import time
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, RowMapping, Row
from app.model import GraphCollection
from app.schema.graph_collection_schema import (
    CreateGraphCollectionParam,
    UpdateGraphCollectionParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_graph_collection import graph_collection_dao


class GraphCollectionService:
    @staticmethod
    async def add(*, obj: CreateGraphCollectionParam) -> GraphCollection:
        async with async_db_session.begin() as db:
            # 创建知识集合
            return await graph_collection_dao.create(db, obj)

    @staticmethod
    async def get_all(*, knowledge_base_uuid: str = None, name: str = None) -> Sequence[
        Row[GraphCollection] | RowMapping | GraphCollection]:
        async with async_db_session() as db:
            return await graph_collection_dao.get_all(db=db, knowledge_base_uuid=knowledge_base_uuid, name=name)

    @staticmethod
    async def update(*, request: Request, graph_collection_uuid: str, obj: UpdateGraphCollectionParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识集合
            graph_collection = await graph_collection_dao.get_by_uuid(db, graph_collection_uuid)
            if not graph_collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 更新知识集合
            count = await graph_collection_dao.update(db, graph_collection_uuid, obj)
            return count

    @staticmethod
    async def update_status(*, request: Request, graph_collection_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查知识集合是否存在
            graph_collection = await graph_collection_dao.get_by_uuid(db, graph_collection_uuid)
            if not graph_collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 更新知识集合状态
            count = await graph_collection_dao.set_status(db, graph_collection_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, graph_collection_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查知识集合是否存在
            graph_collection = await graph_collection_dao.get_by_uuid(db, graph_collection_uuid)
            if not graph_collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 删除知识集合
            count = await graph_collection_dao.delete(db, graph_collection_uuid)
            return count

    @staticmethod
    async def get_graph_collection(*, request: Request, graph_collection_uuid: str) -> GraphCollection:
        async with async_db_session() as db:
            graph_collection = await graph_collection_dao.get_by_uuid(db, graph_collection_uuid)
            if not graph_collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            return graph_collection

    @staticmethod
    async def get_select(*, knowledge_base_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await graph_collection_dao.get_list(knowledge_base_uuid=knowledge_base_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, graph_collection_uuid: str) -> GraphCollection:
        """
        获取知识集合与相关信息（知识集合、知识集合等）
        """
        async with async_db_session() as db:
            graph_collection = await graph_collection_dao.get_with_relation(db, graph_collection_uuid=graph_collection_uuid)
            if not graph_collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            return graph_collection


graph_collection_service = GraphCollectionService()

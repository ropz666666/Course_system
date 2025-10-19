from typing import Sequence

from fastapi import Request
from sqlalchemy import Select, RowMapping, Row
from app.model import Collection
from app.schema.collection_schema import (
    CreateCollectionParam,
    UpdateCollectionParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_collection import collection_dao


class CollectionService:
    @staticmethod
    async def add(*, obj: CreateCollectionParam) -> Collection:
        async with async_db_session.begin() as db:
            # 创建知识集合
            return await collection_dao.create(db, obj)

    @staticmethod
    async def get_all(*, knowledge_base_uuid: str = None, name: str = None) -> Sequence[
        Row[Collection] | RowMapping | Collection]:
        async with async_db_session() as db:
            return await collection_dao.get_all(db=db, knowledge_base_uuid=knowledge_base_uuid, name=name)

    @staticmethod
    async def update(*, request: Request, collection_uuid: str, obj: UpdateCollectionParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的知识集合
            collection = await collection_dao.get_by_uuid(db, collection_uuid)
            if not collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 更新知识集合
            count = await collection_dao.update(db, collection_uuid, obj)
            return count

    @staticmethod
    async def update_status(*, request: Request, collection_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查知识集合是否存在
            collection = await collection_dao.get_by_uuid(db, collection_uuid)
            if not collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 更新知识集合状态
            count = await collection_dao.set_status(db, collection_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, collection_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查知识集合是否存在
            collection = await collection_dao.get_by_uuid(db, collection_uuid)
            if not collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            # 删除知识集合
            count = await collection_dao.delete(db, collection_uuid)
            return count

    @staticmethod
    async def get_collection(*, request: Request, collection_uuid: str) -> Collection:
        async with async_db_session() as db:
            collection = await collection_dao.get_by_uuid(db, collection_uuid)
            if not collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            return collection

    @staticmethod
    async def get_select(*, knowledge_base_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await collection_dao.get_list(knowledge_base_uuid=knowledge_base_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, collection_uuid: str) -> Collection:
        """
        获取知识集合与相关信息（知识集合、知识集合等）
        """
        async with async_db_session() as db:
            collection = await collection_dao.get_with_relation(db, collection_uuid=collection_uuid)
            if not collection:
                raise errors.NotFoundError(msg='知识集合不存在')

            return collection


collection_service = CollectionService()

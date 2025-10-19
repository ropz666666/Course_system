import json
import time
from typing import Sequence

from sqlalchemy import Select, RowMapping, Row
from fastapi import Request
from sqlalchemy import Select
from app.model import TextBlock
from app.schema.text_block_schema import (
    CreateTextBlockParam,
    UpdateTextBlockParam,
)
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_text_block import text_block_dao


class TextBlockService:
    @staticmethod
    async def add(*, obj: CreateTextBlockParam) -> TextBlock:
        async with async_db_session.begin() as db:
            # 创建文本块
            return await text_block_dao.create(db, obj)

    @staticmethod
    async def get_all(*, collection_uuid: str = None, content: str = None) -> Sequence[
        Row[TextBlock] | RowMapping | TextBlock]:
        async with async_db_session() as db:
            return await text_block_dao.get_all(db=db, collection_uuid=collection_uuid, content=content)

    @staticmethod
    async def update(*, request: Request, text_block_uuid: str, obj: UpdateTextBlockParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的文本块
            text_block = await text_block_dao.get_by_uuid(db, text_block_uuid)
            if not text_block:
                raise errors.NotFoundError(msg='文本块不存在')

            # 更新文本块
            count = await text_block_dao.update(db, text_block_uuid, obj)
            # await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_status(*, request: Request, text_block_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查文本块是否存在
            text_block = await text_block_dao.get_by_uuid(db, text_block_uuid)
            if not text_block:
                raise errors.NotFoundError(msg='文本块不存在')

            # 更新文本块状态
            count = await text_block_dao.set_status(db, text_block_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, text_block_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查文本块是否存在
            text_block = await text_block_dao.get_by_uuid(db, text_block_uuid)
            if not text_block:
                raise errors.NotFoundError(msg='文本块不存在')

            # 删除文本块
            count = await text_block_dao.delete(db, text_block_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_text_block(*, request: Request, text_block_uuid: str) -> TextBlock:
        async with async_db_session() as db:
            text_block = await text_block_dao.get_by_uuid(db, text_block_uuid)
            if not text_block:
                raise errors.NotFoundError(msg='文本块不存在')

            return text_block

    @staticmethod
    async def get_select(*, collection_uuid: str = None, content: str = None) -> Select:
        return await text_block_dao.get_list(collection_uuid=collection_uuid, content=content)

    @staticmethod
    async def get_with_relation(*, request: Request, text_block_uuid: str) -> TextBlock:
        """
        获取文本块与相关信息（文本块、文本块等）
        """
        async with async_db_session() as db:
            text_block = await text_block_dao.get_with_relation(db, text_block_uuid=text_block_uuid)
            if not text_block:
                raise errors.NotFoundError(msg='文本块不存在')

            return text_block


text_block_service = TextBlockService()

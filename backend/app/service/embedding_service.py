import json
import time

from fastapi import Request
from sqlalchemy import Select
from app.model import Embedding
from app.schema.embedding_schema import (
    CreateEmbeddingParam,
    UpdateEmbeddingParam,
    GetEmbeddingDetail
)
from app.schema.embedding_schema import CreateEmbeddingParam
from common.exception import errors
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client
from app.crud.crud_embedding import embedding_dao
import base64
import numpy as np


class EmbeddingService:
    @staticmethod
    async def encode_embedding(embedding: np.ndarray) -> str:
        return base64.b64encode(embedding.tobytes()).decode('utf-8')

    @staticmethod
    async def decode_embedding(encoded_embedding: str) -> np.ndarray:
        return np.frombuffer(base64.b64decode(encoded_embedding), dtype=np.float32)

    @staticmethod
    async def add(*, obj: CreateEmbeddingParam) -> Embedding:
        async with async_db_session.begin() as db:
            # 创建文本嵌入
            return await embedding_dao.create(db, obj)

    @staticmethod
    async def update(*, request: Request, embedding_uuid: str, obj: UpdateEmbeddingParam) -> int:
        async with async_db_session.begin() as db:
            # 检查权限：普通用户只能更新自己的文本嵌入
            embedding = await embedding_dao.get_by_uuid(db, embedding_uuid)
            if not embedding:
                raise errors.NotFoundError(msg='文本嵌入不存在')

            # 权限检查：如果不是超级管理员，且不是自己的文本嵌入，不能修改
            if not request.user.is_superuser and embedding.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该文本嵌入")

            # 更新文本嵌入
            count = await embedding_dao.update(db, embedding_uuid, obj)
            # await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_status(*, request: Request, embedding_uuid: str, status: bool) -> int:
        async with async_db_session.begin() as db:
            # 检查文本嵌入是否存在
            embedding = await embedding_dao.get_by_uuid(db, embedding_uuid)
            if not embedding:
                raise errors.NotFoundError(msg='文本嵌入不存在')

            # 权限检查：如果不是超级管理员，且不是自己的文本嵌入，不能修改
            if not request.user.is_superuser and embedding.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限修改该文本嵌入")

            # 更新文本嵌入状态
            count = await embedding_dao.set_status(db, embedding_uuid, status)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, embedding_uuid: str) -> int:
        async with async_db_session.begin() as db:
            # 检查文本嵌入是否存在
            embedding = await embedding_dao.get_by_uuid(db, embedding_uuid)
            if not embedding:
                raise errors.NotFoundError(msg='文本嵌入不存在')

            # 权限检查：普通用户只能删除自己的文本嵌入
            if not request.user.is_superuser and embedding.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限删除该文本嵌入")

            # 删除文本嵌入
            count = await embedding_dao.delete(db, embedding_uuid)
            # await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_embedding(*, request: Request, embedding_uuid: str) -> Embedding:
        async with async_db_session() as db:
            embedding = await embedding_dao.get_by_uuid(db, embedding_uuid)
            if not embedding:
                raise errors.NotFoundError(msg='文本嵌入不存在')

            # 权限检查：如果不是超级管理员，且不是自己的文本嵌入，不能修改
            if not request.user.is_superuser and embedding.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该文本嵌入")

            return embedding

    @staticmethod
    async def get_select(*, user_uuid: str = None, name: str = None, description: str = None, status: int = None) -> Select:
        return await embedding_dao.get_list(user_uuid=user_uuid, name=name, description=description, status=status)

    @staticmethod
    async def get_with_relation(*, request: Request, embedding_uuid: str) -> Embedding:
        """
        获取文本嵌入与相关信息（文本嵌入、文本嵌入等）
        """
        async with async_db_session() as db:
            embedding = await embedding_dao.get_with_relation(db, embedding_uuid=embedding_uuid)
            if not embedding:
                raise errors.NotFoundError(msg='文本嵌入不存在')

            # 权限检查：如果不是超级管理员，且不是自己的文本嵌入，不能修改
            if not request.user.is_superuser and embedding.user_uuid != request.user.uuid:
                raise errors.ForbiddenError(msg="您没有权限获得该文本嵌入")
            return embedding

    @staticmethod
    # 在循环中创建并提交单独的事务
    async def insert_embeddings(*, text_block_uuid: str, embed_result: list) -> None:
        async with async_db_session.begin() as db:
            for embed in embed_result:
                try:
                    # 使用独立的事务来插入每个嵌入记录，减少锁持有的时间
                    async with db.begin():
                        obj = CreateEmbeddingParam(
                            vectory=await embedding_service.encode_embedding(embed.text_embedding),
                            text_block_uuid=text_block_uuid
                        )
                        await embedding_service.add(obj=obj)
                except Exception as e:
                    print(f"Failed to insert embedding: {e}")


embedding_service = EmbeddingService()

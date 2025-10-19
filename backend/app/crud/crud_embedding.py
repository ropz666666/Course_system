from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Embedding
from app.schema.embedding_schema import (
    CreateEmbeddingParam,
    UpdateEmbeddingParam,
)


class CRUDEmbedding(CRUDPlus[Embedding]):
    async def get(self, db: AsyncSession, embedding_id: int) -> Embedding | None:
        """
        获取嵌入

        :param db:
        :param embedding_id:
        :return:
        """
        return await self.select_model(db, embedding_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Embedding | None:
        """
        通过 uuid 获取嵌入

        :param db:
        :param uuid:
        :return:
        """
        stmt = (
            select(self.model)
                .where(self.model.uuid == uuid)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj: CreateEmbeddingParam) -> Embedding:
        """
        创建嵌入

        :param db: 异步数据库会话
        :param obj: 创建嵌入的参数
        :return: 新创建的嵌入对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_embedding = self.model(**dict_obj)  # 使用字典数据创建新的嵌入实例
        db.add(new_embedding)  # 添加到数据库会话
        await db.commit()
        return new_embedding

    async def update(self, db: AsyncSession, embedding_uuid: str, obj: UpdateEmbeddingParam) -> int:
        """
        更新嵌入信息

        :param db:
        :param embedding_uuid:
        :param obj:
        :return:
        """
        embedding = await self.get_by_uuid(db, embedding_uuid)
        if not embedding:
            raise ValueError("Embedding not found")
        return await self.update_model(db, embedding.id, obj)

    async def set_status(self, db: AsyncSession, embedding_uuid: str, status: int) -> int:
        """
        更新嵌入信息

        :param db:
        :param embedding_uuid:
        :param status:
        :return:
        """
        embedding = await self.get_by_uuid(db, embedding_uuid)
        if not embedding:
            raise ValueError("Embedding not found")

        return await self.update_model(db, embedding.id, {'status': status})

    async def get_list(self, user_uuid: str = None, name: str = None, description: str = None,
                       status: int = None) -> Select:
        """
        获取嵌入列表

        :param user_uuid:
        :param name:
        :param description:
        :param status:
        :return:
        """
        stmt = (
            select(self.model)
            .order_by(desc(self.model.updated_time))
        )
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if description:
            where_list.append(self.model.description.like(f'%{description}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_with_relation(self, db: AsyncSession, embedding_uuid: str = None) -> Embedding:
        """
        获取嵌入列表

        :param db:
        :param embedding_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.embedding))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if embedding_uuid:
            where_list.append(self.model.uuid == embedding_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, embedding_uuid: str) -> int:
        """
        删除嵌入

        :param db:
        :param embedding_uuid:
        :return:
        """
        embedding = await self.get_by_uuid(db, embedding_uuid)
        if embedding:
            await db.delete(embedding)
            await db.commit()
        return 1


embedding_dao: CRUDEmbedding = CRUDEmbedding(Embedding)

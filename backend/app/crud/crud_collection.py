from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Collection
from app.schema.collection_schema import (
    CreateCollectionParam,
    UpdateCollectionParam,
)
from sqlalchemy import and_, desc, select, Row, RowMapping


class CRUDCollection(CRUDPlus[Collection]):
    async def get(self, db: AsyncSession, collection_id: int) -> Collection | None:
        """
        获取知识集合

        :param db:
        :param collection_id:
        :return:
        """
        return await self.select_model(db, collection_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Collection | None:
        """
        通过 uuid 获取知识集合

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

    async def create(self, db: AsyncSession, obj: CreateCollectionParam) -> Collection:
        """
        创建知识集合

        :param db: 异步数据库会话
        :param obj: 创建知识集合的参数
        :return: 新创建的知识集合对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_collection = self.model(**dict_obj)  # 使用字典数据创建新的知识集合实例
        db.add(new_collection)  # 添加到数据库会话
        await db.commit()
        return new_collection

    async def get_all(self, db: AsyncSession, knowledge_base_uuid: str = None, name: str = None) -> \
            Sequence[Row[Collection] | RowMapping | Collection]:
        """
        获取会话列表

        :param knowledge_base_uuid:
        :param db:
        :param name:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = []
        if knowledge_base_uuid:
            where_list.append(self.model.knowledge_base_uuid == knowledge_base_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, collection_uuid: str, obj: UpdateCollectionParam) -> int:
        """
        更新知识集合信息

        :param db:
        :param collection_uuid:
        :param obj:
        :return:
        """
        collection = await self.get_by_uuid(db, collection_uuid)
        if not collection:
            raise ValueError("Collection not found")
        return await self.update_model(db, collection.id, obj)

    async def set_status(self, db: AsyncSession, collection_uuid: str, status: int) -> int:
        """
        更新知识集合信息

        :param db:
        :param collection_uuid:
        :param status:
        :return:
        """
        collection = await self.get_by_uuid(db, collection_uuid)
        if not collection:
            raise ValueError("Collection not found")

        return await self.update_model(db, collection.id, {'status': status})

    async def get_list(self, knowledge_base_uuid: str = None, name: str = None, description: str = None,
                       status: int = None) -> Select:
        """
        获取知识集合列表

        :param knowledge_base_uuid:
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
        if knowledge_base_uuid:
            where_list.append(self.model.knowledge_base_uuid == knowledge_base_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if description:
            where_list.append(self.model.file_url.like(f'%{description}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_with_relation(self, db: AsyncSession, collection_uuid: str = None) -> Collection:
        """
        获取知识集合列表

        :param db:
        :param collection_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.text_blocks))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if collection_uuid:
            where_list.append(self.model.uuid == collection_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, collection_uuid: str) -> int:
        """
        删除知识集合

        :param db:
        :param collection_uuid:
        :return:
        """
        collection = await self.get_by_uuid(db, collection_uuid)
        if collection:
            await db.delete(collection)
            await db.commit()
        return 1


collection_dao: CRUDCollection = CRUDCollection(Collection)

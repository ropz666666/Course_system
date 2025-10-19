from typing import Sequence

from sqlalchemy import and_, desc, select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import KnowledgeBase
from app.schema.knowledge_base_schema import (
    CreateKnowledgeBaseParam,
    UpdateKnowledgeBaseParam,
)


class CRUDKnowledgeBase(CRUDPlus[KnowledgeBase]):
    async def get(self, db: AsyncSession, knowledge_base_id: int) -> KnowledgeBase | None:
        """
        获取知识库

        :param db:
        :param knowledge_base_id:
        :return:
        """
        return await self.select_model(db, knowledge_base_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> KnowledgeBase | None:
        """
        通过 uuid 获取知识库

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

    async def create(self, db: AsyncSession, obj: CreateKnowledgeBaseParam) -> KnowledgeBase:
        """
        创建知识库

        :param db: 异步数据库会话
        :param obj: 创建知识库的参数
        :return: 新创建的知识库对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_knowledge_base = self.model(**dict_obj)  # 使用字典数据创建新的知识库实例
        db.add(new_knowledge_base)  # 添加到数据库会话
        await db.commit()
        return new_knowledge_base

    async def update(self, db: AsyncSession, knowledge_base_uuid: str, obj: UpdateKnowledgeBaseParam) -> int:
        """
        更新知识库信息

        :param db:
        :param knowledge_base_uuid:
        :param obj:
        :return:
        """
        knowledge_base = await self.get_by_uuid(db, knowledge_base_uuid)
        if not knowledge_base:
            raise ValueError("KnowledgeBase not found")
        return await self.update_model(db, knowledge_base.id, obj)

    async def set_status(self, db: AsyncSession, knowledge_base_uuid: str, status: int) -> int:
        """
        更新知识库信息

        :param db:
        :param knowledge_base_uuid:
        :param status:
        :return:
        """
        knowledge_base = await self.get_by_uuid(db, knowledge_base_uuid)
        if not knowledge_base:
            raise ValueError("KnowledgeBase not found")

        return await self.update_model(db, knowledge_base.id, {'status': status})

    async def get_list(self, user_uuid: str = None, name: str = None, description: str = None,
                       status: int = None) -> Select:
        """
        获取知识库列表

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
        where_list = [self.model.status != 2]
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

    async def get_all(self, db: AsyncSession, user_uuid: str = None, description: str = None, name: str = None) -> \
            Sequence[Row[KnowledgeBase] | RowMapping | KnowledgeBase]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :param user_uuid:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = [self.model.status != 2]
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if description:
            where_list.append(self.model.description.like(f'%{description}%'))
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_with_relation(self, db: AsyncSession, knowledge_base_uuid: str = None) -> KnowledgeBase:
        """
        获取知识库列表

        :param db:
        :param knowledge_base_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.collections))
            .options(selectinload(self.model.graph_collections))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if knowledge_base_uuid:
            where_list.append(self.model.uuid == knowledge_base_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, knowledge_base_uuid: str) -> int:
        """
        删除知识库

        :param db:
        :param knowledge_base_uuid:
        :return:
        """
        knowledge_base = await self.get_by_uuid(db, knowledge_base_uuid)
        if knowledge_base:
            await db.delete(knowledge_base)
            await db.commit()
        return 1


knowledge_base_dao: CRUDKnowledgeBase = CRUDKnowledgeBase(KnowledgeBase)

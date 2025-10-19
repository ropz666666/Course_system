from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy_crud_plus import CRUDPlus
from app.model import GraphCollection
from app.schema.graph_collection_schema import (
    CreateGraphCollectionParam,
    UpdateGraphCollectionParam,
)
from sqlalchemy import and_, desc, select, Row, RowMapping


class CRUDGraphCollection(CRUDPlus[GraphCollection]):
    async def get(self, db: AsyncSession, graph_collection_id: int) -> GraphCollection | None:
        """
        获取知识集合

        :param db:
        :param graph_collection_id:
        :return:
        """
        return await self.select_model(db, graph_collection_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> GraphCollection | None:
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

    async def create(self, db: AsyncSession, obj: CreateGraphCollectionParam) -> GraphCollection:
        """
        创建知识集合

        :param db: 异步数据库会话
        :param obj: 创建知识集合的参数
        :return: 新创建的知识集合对象
        """
        # 将参数对象转换为字典
        dict_obj = obj.model_dump()

        # 移除 `file_url` 字段（如果存在）
        dict_obj.pop('file_url', None)

        # 使用字典数据创建新的知识集合实例
        new_graph_collection = self.model(**dict_obj)

        # 添加到数据库并提交
        db.add(new_graph_collection)
        await db.commit()

        return new_graph_collection

    async def get_all(self, db: AsyncSession, knowledge_base_uuid: str = None, name: str = None) -> \
            Sequence[Row[GraphCollection] | RowMapping | GraphCollection]:
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

    async def update(self, db: AsyncSession, graph_collection_uuid: str, obj: UpdateGraphCollectionParam) -> int:
        """
        更新知识集合信息

        :param db:
        :param graph_collection_uuid:
        :param obj:
        :return:
        """
        graph_collection = await self.get_by_uuid(db, graph_collection_uuid)
        if not graph_collection:
            raise ValueError("GraphCollection not found")
        return await self.update_model(db, graph_collection.id, obj)

    async def set_status(self, db: AsyncSession, graph_collection_uuid: str, status: int) -> int:
        """
        更新知识集合信息

        :param db:
        :param graph_collection_uuid:
        :param status:
        :return:
        """
        graph_collection = await self.get_by_uuid(db, graph_collection_uuid)
        if not graph_collection:
            raise ValueError("GraphCollection not found")

        return await self.update_model(db, graph_collection.id, {'status': status})

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
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_with_relation(self, db: AsyncSession, graph_collection_uuid: str = None) -> GraphCollection:
        """
        获取知识集合列表

        :param db:
        :param graph_collection_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if graph_collection_uuid:
            where_list.append(self.model.uuid == graph_collection_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, graph_collection_uuid: str) -> int:
        """
        删除知识集合

        :param db:
        :param graph_collection_uuid:
        :return:
        """
        graph_collection = await self.get_by_uuid(db, graph_collection_uuid)
        if graph_collection:
            await db.delete(graph_collection)
            await db.commit()
        return 1


graph_collection_dao: CRUDGraphCollection = CRUDGraphCollection(GraphCollection)

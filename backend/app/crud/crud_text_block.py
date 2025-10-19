from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import TextBlock
from app.schema.text_block_schema import (
    CreateTextBlockParam,
    UpdateTextBlockParam,
)
from sqlalchemy import and_, desc, select, Row, RowMapping


class CRUDTextBlock(CRUDPlus[TextBlock]):
    async def get(self, db: AsyncSession, text_block_id: int) -> TextBlock | None:
        """
        获取知识集合

        :param db:
        :param text_block_id:
        :return:
        """
        return await self.select_model(db, text_block_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> TextBlock | None:
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

    async def create(self, db: AsyncSession, obj: CreateTextBlockParam) -> TextBlock:
        """
        创建知识集合

        :param db: 异步数据库会话
        :param obj: 创建知识集合的参数
        :return: 新创建的知识集合对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_text_block = self.model(**dict_obj)  # 使用字典数据创建新的知识集合实例
        db.add(new_text_block)  # 添加到数据库会话
        await db.commit()
        return new_text_block

    async def get_all(self, db: AsyncSession, collection_uuid: str = None, content: str = None) -> \
            Sequence[Row[TextBlock] | RowMapping | TextBlock]:
        """
        获取会话列表

        :param collection_uuid:
        :param db:
        :param content:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = []
        if collection_uuid:
            where_list.append(self.model.collection_uuid == collection_uuid)
        if content:
            where_list.append(self.model.content.like(f'%{content}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, text_block_uuid: str, obj: UpdateTextBlockParam) -> int:
        """
        更新知识集合信息

        :param db:
        :param text_block_uuid:
        :param obj:
        :return:
        """
        text_block = await self.get_by_uuid(db, text_block_uuid)
        if not text_block:
            raise ValueError("TextBlock not found")
        return await self.update_model(db, text_block.id, obj)

    async def set_status(self, db: AsyncSession, text_block_uuid: str, status: int) -> int:
        """
        更新知识集合信息

        :param db:
        :param text_block_uuid:
        :param status:
        :return:
        """
        text_block = await self.get_by_uuid(db, text_block_uuid)
        if not text_block:
            raise ValueError("TextBlock not found")

        return await self.update_model(db, text_block.id, {'status': status})

    async def get_list(self, collection_uuid: str = None, content: str = None) -> Select:
        """
        获取知识集合列表

        :param collection_uuid:
        :param content:
        :return:
        """
        stmt = (
            select(self.model)
            .order_by(desc(self.model.updated_time))
        )
        where_list = []
        if collection_uuid:
            where_list.append(self.model.collection_uuid == collection_uuid)
        if content:
            where_list.append(self.model.content.like(f'%{content}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_with_relation(self, db: AsyncSession, text_block_uuid: str = None) -> TextBlock:
        """
        获取知识集合列表

        :param db:
        :param text_block_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.embedding))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if text_block_uuid:
            where_list.append(self.model.uuid == text_block_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, text_block_uuid: str) -> int:
        """
        删除知识集合

        :param db:
        :param text_block_uuid:
        :return:
        """
        text_block = await self.get_by_uuid(db, text_block_uuid)
        if text_block:
            await db.delete(text_block)
            await db.commit()
        return 1


text_block_dao: CRUDTextBlock = CRUDTextBlock(TextBlock)

from typing import Any, Sequence

from sqlalchemy import and_, desc, select, Select, ScalarResult, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Conversation
from app.schema.conversation_schema import CreateConversationParam, UpdateConversationParam


class CRUDConversation(CRUDPlus[Conversation]):
    async def get(self, db: AsyncSession, conversation_id: int) -> Conversation | None:
        """
        获取会话

        :param db:
        :param conversation_id:
        :return:
        """
        return await self.select_model(db, conversation_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Conversation | None:
        """
        通过 uuid 获取会话

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

    async def create(self, db: AsyncSession, obj: CreateConversationParam) -> Conversation:
        """
        创建会话

        :param db:
        :param obj:
        :return:
        """
        dict_obj = obj.model_dump()
        new_conversation = self.model(**dict_obj)
        db.add(new_conversation)
        await db.commit()
        return new_conversation

    async def update(self, db: AsyncSession, conversation_uuid: str, obj: UpdateConversationParam) -> int:
        """
        更新会话信息

        :param db:
        :param conversation_uuid:
        :param obj:
        :return:
        """
        conversation = await self.get_by_uuid(db, conversation_uuid)
        if not conversation:
            raise ValueError("Conversation not found")
        return await self.update_model(db, conversation.id, obj, commit=True)

    async def set_status(self, db: AsyncSession, conversation_uuid: str, status: int) -> int:
        """
        更新会话状态

        :param db:
        :param conversation_uuid:
        :param status:
        :return:
        """
        conversation = await self.get_by_uuid(db, conversation_uuid)
        if not conversation:
            raise ValueError("Conversation not found")
        return await self.update_model(db, conversation.id, {'status': status})

    async def get_list(self, user_uuid: str = None, agent_uuid: str = None, name: str = None) -> Select:
        """
        获取会话列表

        :param name:
        :param user_uuid:
        :param agent_uuid:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if agent_uuid:
            where_list.append(self.model.agent_uuid == agent_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_all(self, db: AsyncSession, user_uuid: str = None, agent_uuid: str = None, name: str = None) -> \
            Sequence[Row[Conversation] | RowMapping | Conversation]:
        """
        获取会话列表

        :param db:
        :param name:
        :param user_uuid:
        :param agent_uuid:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if agent_uuid:
            where_list.append(self.model.agent_uuid == agent_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_with_relation(self, db: AsyncSession, conversation_uuid: str = None) -> Conversation:
        """
        获取会话与相关的用户和智能体信息

        :param db:
        :param conversation_uuid:
        :return:
        """
        stmt = select(self.model).options(
            selectinload(self.model.user),
            selectinload(self.model.agent),
            selectinload(self.model.knowledge_base),
            selectinload(self.model.collection)
        )
        where_list = []
        if conversation_uuid:
            where_list.append(self.model.uuid == conversation_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, conversation_uuid: str) -> int:
        """
        删除会话

        :param db:
        :param conversation_uuid:
        :return:
        """
        conversation = await self.get_by_uuid(db, conversation_uuid)
        if conversation:
            await db.delete(conversation)
            await db.commit()
        return 1


conversation_dao: CRUDConversation = CRUDConversation(Conversation)

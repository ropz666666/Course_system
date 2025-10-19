from typing import Sequence

from sqlalchemy import and_, desc, select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import AgentPublishment, Collection, TextBlock
from app.schema import (
    CreateAgentPublishmentParam,
    UpdateAgentPublishmentParam,
)
from app.model import Plugin, KnowledgeBase
from common.exception import errors


class CRUDAgentPublishment(CRUDPlus[AgentPublishment]):
    async def get(self, db: AsyncSession, agent_publishment_id: int) -> AgentPublishment | None:
        """
        获取智能体

        :param db:
        :param agent_publishment_id:
        :return:
        """
        return await self.select_model(db, agent_publishment_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> AgentPublishment | None:
        """
        通过 uuid 获取智能体

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

    async def create(self, db: AsyncSession, obj: CreateAgentPublishmentParam) -> AgentPublishment:
        """
        创建智能体

        :param db: 异步数据库会话
        :param obj: 创建智能体的参数
        :return: 新创建的智能体对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_agent_publishment = self.model(**dict_obj)  # 使用字典数据创建新的智能体实例
        db.add(new_agent_publishment)  # 添加到数据库会话
        await db.commit()
        return new_agent_publishment

    async def get_all(self, db: AsyncSession, user_uuid: str = None, description: str = None, name: str = None) -> \
            Sequence[Row[AgentPublishment] | RowMapping | AgentPublishment]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :param user_uuid:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        where_list = []
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

    async def get_all_public(self, db: AsyncSession,description: str = None, name: str = None) -> \
            Sequence[Row[AgentPublishment] | RowMapping | AgentPublishment]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.id))
        where_list = [self.model.status == 2]
        if description:
            where_list.append(self.model.description.like(f'%{description}%'))
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, agent_publishment_uuid: str, obj: UpdateAgentPublishmentParam) -> int:
        """
        更新智能体信息

        :param db:
        :param agent_publishment_uuid:
        :param obj:
        :return:
        """
        agent_publishment = await self.get_by_uuid(db, agent_publishment_uuid)
        if not agent_publishment:
            raise ValueError("AgentPublishment not found")
        return await self.update_model(db, agent_publishment.id, obj)

    async def set_status(self, db: AsyncSession, agent_publishment_uuid: str, status: int) -> int:
        """
        更新智能体信息

        :param db:
        :param agent_publishment_uuid:
        :param status:
        :return:
        """
        agent_publishment = await self.get_by_uuid(db, agent_publishment_uuid)
        if not agent_publishment:
            raise ValueError("AgentPublishment not found")

        return await self.update_model(db, agent_publishment.id, {'status': status})


    async def get_with_relation(self, db: AsyncSession, agent_publishment_uuid: str = None) -> AgentPublishment:
        """
        获取智能体列表

        :param db:
        :param agent_publishment_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.plugins))
            .options(
                selectinload(self.model.knowledge_bases)
                .options(
                    selectinload(KnowledgeBase.collections)
                    .options(
                        selectinload(Collection.text_blocks)
                        .options(selectinload(TextBlock.embedding))
                    )
                )
                .options(selectinload(KnowledgeBase.graph_collections))
            )
            .options(selectinload(self.model.conversations))
            .options(selectinload(self.model.deploy_plugin))
            .options(selectinload(self.model.publishments))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if agent_publishment_uuid:
            where_list.append(self.model.uuid == agent_publishment_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, agent_publishment_uuid: str) -> int:
        """
        删除智能体

        :param db:
        :param agent_publishment_uuid:
        :return:
        """
        agent_publishment = await self.get_by_uuid(db, agent_publishment_uuid)
        if agent_publishment:
            await db.delete(agent_publishment)
            await db.commit()
        return 1


agent_publishment_dao: CRUDAgentPublishment = CRUDAgentPublishment(AgentPublishment)

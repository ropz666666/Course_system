from typing import Sequence

from sqlalchemy import and_, desc, select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Interaction
from app.schema.interaction_schema import (
    CreateInteractionParam,
    UpdateInteractionParam,
)


class CRUDInteraction(CRUDPlus[Interaction]):
    async def get(self, db: AsyncSession, interaction_id: int) -> Interaction | None:
        """
        获取知识库

        :param db:
        :param interaction_id:
        :return:
        """
        return await self.select_model(db, interaction_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Interaction | None:
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

    async def get_by_agent_user(self, db: AsyncSession, agent_uuid: str, user_uuid: str) -> Interaction | None:
        """
        通过 uuid 获取知识库

        :param db:
        :param uuid:
        :return:
        """
        stmt = (
            select(self.model)
                .where(self.model.user_uuid == user_uuid)
                .where(self.model.agent_uuid == agent_uuid)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj: CreateInteractionParam) -> Interaction:
        """
        创建知识库

        :param db: 异步数据库会话
        :param obj: 创建知识库的参数
        :return: 新创建的知识库对象
        """
        dict_obj = obj.model_dump()
        new_interaction = self.model(**dict_obj)
        db.add(new_interaction)
        await db.commit()
        return new_interaction

    async def update(self, db: AsyncSession, interaction_uuid: str, obj: UpdateInteractionParam) -> int:
        """
        更新知识库信息

        :param db:
        :param interaction_uuid:
        :param obj:
        :return:
        """
        interaction = await self.get_by_uuid(db, interaction_uuid)
        if not interaction:
            raise ValueError("Interaction not found")
        print("crud", obj)
        return await self.update_model(db, interaction.id, obj)

    async def set_status(self, db: AsyncSession, interaction_uuid: str, status: int) -> int:
        """
        更新知识库信息

        :param db:
        :param interaction_uuid:
        :param status:
        :return:
        """
        interaction = await self.get_by_uuid(db, interaction_uuid)
        if not interaction:
            raise ValueError("Interaction not found")

        return await self.update_model(db, interaction.id, {'status': status})

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
            Sequence[Row[Interaction] | RowMapping | Interaction]:
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

    async def get_with_relation(self, db: AsyncSession, interaction_uuid: str = None) -> Interaction:
        """
        获取知识库列表

        :param db:
        :param interaction_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.collections))
            .options(selectinload(self.model.graph_collections))
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if interaction_uuid:
            where_list.append(self.model.uuid == interaction_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, interaction_uuid: str) -> int:
        """
        删除知识库

        :param db:
        :param interaction_uuid:
        :return:
        """
        interaction = await self.get_by_uuid(db, interaction_uuid)
        if interaction:
            await db.delete(interaction)
            await db.commit()
        return 1


interaction_dao: CRUDInteraction = CRUDInteraction(Interaction)

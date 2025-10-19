from typing import Sequence

from sqlalchemy import and_, desc, select, RowMapping, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Plugin
from app.schema.plugin_schema import (
    CreatePluginParam,
    UpdatePluginParam,
)


class CRUDPlugin(CRUDPlus[Plugin]):
    async def get(self, db: AsyncSession, plugin_id: int) -> Plugin | None:
        """
        获取插件

        :param db:
        :param plugin_id:
        :return:
        """
        return await self.select_model(db, plugin_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Plugin | None:
        """
        通过 uuid 获取插件

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

    async def create(self, db: AsyncSession, obj: CreatePluginParam) -> Plugin:
        """
        创建插件

        :param db: 异步数据库会话
        :param obj: 创建插件的参数
        :return: 新创建的插件对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_plugin = self.model(**dict_obj)  # 使用字典数据创建新的插件实例
        db.add(new_plugin)  # 添加到数据库会话
        await db.commit()
        return new_plugin

    async def update(self, db: AsyncSession, plugin_uuid: str, obj: UpdatePluginParam) -> int:
        """
        更新插件信息

        :param db:
        :param plugin_uuid:
        :param obj:
        :return:
        """
        plugin = await self.get_by_uuid(db, plugin_uuid)
        if not plugin:
            raise ValueError("Plugin not found")
        return await self.update_model(db, plugin.id, obj)

    async def set_status(self, db: AsyncSession, plugin_uuid: str, status: int) -> int:
        """
        更新插件信息

        :param db:
        :param plugin_uuid:
        :param status:
        :return:
        """
        plugin = await self.get_by_uuid(db, plugin_uuid)
        if not plugin:
            raise ValueError("Plugin not found")

        return await self.update_model(db, plugin.id, {'status': status})

    async def get_list(self, user_uuid: str = None, name: str = None, description: str = None,
                       status: int = None) -> Select:
        """
        获取插件列表

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
        # 只获取从 plugin base 创建的插件
        # where_list = [self.model.status.in_([0, 1])]
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

    async def get_all(self, db: AsyncSession, user_uuid: str = None, description: str = None, name: str = None) -> \
            Sequence[Row[Plugin] | RowMapping | Plugin]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :param user_uuid:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.uuid))
        # 只获取从 plugin base 创建的插件
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

    async def get_with_relation(self, db: AsyncSession, plugin_uuid: str = None) -> Plugin:
        """
        获取插件列表

        :param db:
        :param plugin_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if plugin_uuid:
            where_list.append(self.model.uuid == plugin_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, plugin_uuid: str) -> int:
        """
        删除插件

        :param db:
        :param plugin_uuid:
        :return:
        """
        plugin = await self.get_by_uuid(db, plugin_uuid)
        if plugin:
            await db.delete(plugin)
            await db.commit()
        return 1


plugin_dao: CRUDPlugin = CRUDPlugin(Plugin)

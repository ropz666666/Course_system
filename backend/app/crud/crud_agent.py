from typing import Sequence

from sqlalchemy import and_, desc, select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus
from app.model import Agent, Collection, TextBlock, AgentPublishment
from app.schema.agent_schema import (
    CreateAgentParam,
    UpdateAgentParam,
    AddAgentPluginParam,
    AddAgentKnowledgeBaseParam,
)
from app.model import Plugin, KnowledgeBase
from common.exception import errors


class CRUDAgent(CRUDPlus[Agent]):
    async def get(self, db: AsyncSession, agent_id: int) -> Agent | None:
        """
        获取智能体

        :param db:
        :param agent_id:
        :return:
        """
        return await self.select_model(db, agent_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Agent | None:
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

    async def create(self, db: AsyncSession, obj: CreateAgentParam) -> Agent:
        """
        创建智能体

        :param db: 异步数据库会话
        :param obj: 创建智能体的参数
        :return: 新创建的智能体对象
        """
        dict_obj = obj.model_dump()  # 获取参数的字典数据
        new_agent = self.model(**dict_obj)  # 使用字典数据创建新的智能体实例
        db.add(new_agent)  # 添加到数据库会话
        await db.commit()
        return new_agent

    async def get_all(self, db: AsyncSession, user_uuid: str = None, description: str = None, name: str = None) -> \
            Sequence[Row[Agent] | RowMapping | Agent]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :param user_uuid:
        :return:
        """
        stmt = select(self.model).options(selectinload(self.model.user)).order_by(desc(self.model.uuid))
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
            Sequence[Row[Agent] | RowMapping | Agent]:
        """
        获取会话列表

        :param description:
        :param db:
        :param name:
        :return:
        """
        stmt = select(self.model).options(selectinload(self.model.user)).order_by(desc(self.model.id))
        where_list = [self.model.status == 2]
        if description:
            where_list.append(self.model.description.like(f'%{description}%'))
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, agent_uuid: str, obj: UpdateAgentParam) -> int:
        """
        更新智能体信息

        :param db:
        :param agent_uuid:
        :param obj:
        :return:
        """
        agent = await self.get_by_uuid(db, agent_uuid)
        if not agent:
            raise ValueError("Agent not found")
        return await self.update_model(db, agent.id, obj)

    async def set_status(self, db: AsyncSession, agent_uuid: str, status: int) -> int:
        """
        更新智能体信息

        :param db:
        :param agent_uuid:
        :param status:
        :return:
        """
        agent = await self.get_by_uuid(db, agent_uuid)
        if not agent:
            raise ValueError("Agent not found")

        return await self.update_model(db, agent.id, {'status': status})

    async def add_plugin(self, db: AsyncSession, agent_uuid: str, plugin_param: AddAgentPluginParam) -> Agent:
        """
        给智能体添加插件

        :param db:
        :param agent_uuid:
        :param plugin_param:
        :return:
        """
        agent = await self.get_by_uuid(db, agent_uuid)
        if not agent:
            raise ValueError("Agent not found")

        plugin = await db.execute(select(Plugin).where(Plugin.uuid == plugin_param.plugin_uuids))
        plugin = plugin.scalars().first()
        if plugin:
            agent.plugins.append(plugin)
            await db.commit()
            await db.refresh(agent)
        return agent

    async def add_knowledge_base(self, db: AsyncSession, agent_uuid: str,
                                 knowledge_base_param: AddAgentKnowledgeBaseParam) -> Agent:
        """
        给智能体添加知识库

        :param db:
        :param agent_uuid:
        :param knowledge_base_param:
        :return:
        """
        agent = await self.get_by_uuid(db, agent_uuid)
        if not agent:
            raise ValueError("Agent not found")

        knowledge_base = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.uuid == knowledge_base_param.knowledge_base_uuid))
        knowledge_base = knowledge_base.scalars().first()
        if knowledge_base:
            agent.knowledge_bases.append(knowledge_base)
            await db.commit()
            await db.refresh(agent)
        return agent

    async def reset_plugins(self, db: AsyncSession, agent_uuid: str, plugin_param: AddAgentPluginParam) -> Agent:
        """
        给智能体重置插件

        :param db:
        :param agent_uuid:
        :param plugin_param:
        :return:
        """
        # 获取智能体对象
        agent = await self.get_with_relation(db, agent_uuid)
        if not agent:
            raise errors.NotFoundError(msg="智能体不存在")

        # 获取插件
        stmt = select(Plugin).where(Plugin.uuid.in_(plugin_param.plugin_uuids))  # 创建查询语句
        result = await db.execute(stmt)  # 异步执行查询
        plugins = result.scalars().all()  # 将查询结果转为插件列表

        if not plugins:
            plugins = []

        # 更新 agent 的插件列表
        agent.plugins = plugins
        await db.commit()  # 提交事务
        return agent

    async def reset_knowledge_bases(self, db: AsyncSession, agent_uuid: str,
                                 knowledge_base_param: AddAgentKnowledgeBaseParam) -> Agent:
        """
        给智能体添加知识库

        :param db:
        :param agent_uuid:
        :param knowledge_base_param:
        :return:
        """
        agent = await self.get_with_relation(db, agent_uuid)
        if not agent:
            raise ValueError("Agent not found")

        # 获取插件
        stmt = select(KnowledgeBase).where(KnowledgeBase.uuid.in_(knowledge_base_param.knowledge_base_uuids))  # 创建查询语句
        result = await db.execute(stmt)  # 异步执行查询
        knowledge_bases = result.scalars().all()  # 将查询结果转为插件列表

        if not knowledge_bases:
            knowledge_bases = []
            # raise errors.NotFoundError(msg="没有找到对应的知识库")

        # 更新 agent 的插件列表
        agent.knowledge_bases = knowledge_bases
        return agent

    async def get_list(self, user_uuid: str = None, name: str = None, description: str = None, tag: str = None,
                       status: int = None) -> Select:
        """
        获取智能体列表

        :param user_uuid:
        :param name:
        :param description:
        :param status:
        :return:
        """
        stmt = (
            select(self.model).options(selectinload(self.model.user))
                .options(selectinload(self.model.interactions))
            .order_by(desc(self.model.updated_time))
        )
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if description:
            where_list.append(self.model.description.like(f'%{description}%'))
        if tag:
            where_list.append(self.model.tags.like(f'%{tag}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_with_relation(self, db: AsyncSession, agent_uuid: str = None) -> Agent:
        """
        获取智能体列表

        :param db:
        :param agent_uuid:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.user))
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
            .options(selectinload(self.model.interactions))
            .options(
                selectinload(self.model.publishments)
                .options(
                    selectinload(AgentPublishment.channel)
                )
            )
            .order_by(desc(self.model.updated_time))
        )

        where_list = []
        if agent_uuid:
            where_list.append(self.model.uuid == agent_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, agent_uuid: str) -> int:
        """
        删除智能体

        :param db:
        :param agent_uuid:
        :return:
        """
        agent = await self.get_by_uuid(db, agent_uuid)
        if agent:
            await db.delete(agent)
            await db.commit()
        return 1


agent_dao: CRUDAgent = CRUDAgent(Agent)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_captcha import text_captcha
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy.orm import selectinload
from app.model import User, Agent
from app.schema.user_schema import (
    AddUserParam,
    AvatarParam,
    RegisterUserParam,
    UpdateUserParam, UserAgentParam,
)
from common.exception import errors
from common.security.jwt import get_hash_password
from utils.timezone import timezone


class CRUDUser(CRUDPlus[User]):
    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        """
        获取用户

        :param db:
        :param user_id:
        :return:
        """
        return await self.select_model(db, user_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        通过 username 获取用户

        :param db: 异步数据库会话
        :param username: 用户名
        :return: 返回找到的用户，或者 None
        """
        stmt = (
            select(self.model)
        )
        filters = []

        if username:
            filters.append(self.model.username == username)
        user = await db.execute(stmt.where(*filters))
        return user.scalars().first()

    async def get_by_nickname(self, db: AsyncSession, nickname: str) -> User | None:
        """
        通过 nickname 获取用户

        :param db:
        :param nickname:
        :return:
        """
        return await self.select_model_by_column(db, nickname=nickname)

    async def update_login_time(self, db: AsyncSession, username: str) -> int:
        """
        更新用户登录时间

        :param db:
        :param username:
        :return:
        """
        return await self.update_model_by_column(db, {'last_login_time': timezone.now()}, username=username)

    async def create(self, db: AsyncSession, obj: RegisterUserParam, *, social: bool = False) -> None:
        """
        创建用户

        :param db:
        :param obj:
        :param social: 社交用户，适配 oauth 2.0
        :return:
        """
        if not social:
            salt = text_captcha(5)
            obj.password = get_hash_password(f'{obj.password}{salt}')
            dict_obj = obj.model_dump()
            dict_obj.update({'is_staff': True, 'salt': salt})
        else:
            dict_obj = obj.model_dump()
            dict_obj.update({'is_staff': True, 'salt': None})
        print(dict_obj)
        new_user = self.model(**dict_obj)
        db.add(new_user)
        await db.commit()

    async def add(self, db: AsyncSession, obj: AddUserParam) -> None:
        """
        后台添加用户

        :param db:
        :param obj:
        :return:
        """
        salt = text_captcha(5)
        obj.password = get_hash_password(f'{obj.password}{salt}')
        dict_obj = obj.model_dump(exclude={'roles', 'depts'})
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)

        db.add(new_user)

    async def update_userinfo(self, db: AsyncSession, input_user: int, obj: UpdateUserParam) -> int:
        """
        更新用户信息

        :param db:
        :param input_user:
        :param obj:
        :return:
        """
        return await self.update_model(db, input_user, obj)

    async def update_avatar(self, db: AsyncSession, input_user: int, avatar: AvatarParam) -> int:
        """
        更新用户头像

        :param db:
        :param input_user:
        :param avatar:
        :return:
        """
        return await self.update_model(db, input_user, {'avatar': avatar.url})

    async def delete(self, db: AsyncSession, user_id: int) -> int:
        """
        删除用户

        :param db:
        :param user_id:
        :return:
        """
        return await self.delete_model(db, user_id)

    async def check_email(self, db: AsyncSession, email: str) -> User | None:
        """
        检查邮箱是否存在

        :param db:
        :param email:
        :return:
        """
        return await self.select_model_by_column(db, email=email)

    async def reset_password(self, db: AsyncSession, pk: int, new_pwd: str) -> int:
        """
        重置用户密码

        :param db:
        :param pk:
        :param new_pwd:
        :return:
        """
        return await self.update_model(db, pk, {'password': new_pwd})

    async def get_list(self, dept: int = None, username: str = None, phone: str = None, status: int = None) -> Select:
        """
        获取用户列表

        :param dept:
        :param username:
        :param phone:
        :param status:
        :return:
        """
        stmt = (
            select(self.model)
                .order_by(desc(self.model.join_time))
        )
        where_list = []
        if username:
            where_list.append(self.model.username.like(f'%{username}%'))
        if phone:
            where_list.append(self.model.phone.like(f'%{phone}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_super(self, db: AsyncSession, user_id: int) -> bool:
        """
        获取用户超级管理员状态

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        return user.is_superuser

    async def get_staff(self, db: AsyncSession, user_id: int) -> bool:
        """
        获取用户后台登录状态

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        return user.is_staff

    async def get_status(self, db: AsyncSession, user_id: int) -> int:
        """
        获取用户状态

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        return user.status

    async def get_multi_login(self, db: AsyncSession, user_id: int) -> bool:
        """
        获取用户多点登录状态

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        return user.is_multi_login

    async def set_super(self, db: AsyncSession, user_id: int, _super: bool) -> int:
        """
        设置用户超级管理员

        :param db:
        :param user_id:
        :param _super:
        :return:
        """
        return await self.update_model(db, user_id, {'is_superuser': _super})

    async def set_staff(self, db: AsyncSession, user_id: int, staff: bool) -> int:
        """
        设置用户后台登录

        :param db:
        :param user_id:
        :param staff:
        :return:
        """
        return await self.update_model(db, user_id, {'is_staff': staff})

    async def set_status(self, db: AsyncSession, user_id: int, status: bool) -> int:
        """
        设置用户状态

        :param db:
        :param user_id:
        :param status:
        :return:
        """
        return await self.update_model(db, user_id, {'status': status})

    async def set_multi_login(self, db: AsyncSession, user_id: int, multi_login: bool) -> int:
        """
        设置用户多点登录

        :param db:
        :param user_id:
        :param multi_login:
        :return:
        """
        return await self.update_model(db, user_id, {'is_multi_login': multi_login})

    async def get_with_relation(self, db: AsyncSession, *, user_id: int = None, username: str = None,
                                user_uuid: str = None) -> User | None:
        """
        获取用户和（部门，角色，菜单）

        :param db:
        :param user_id:
        :param username:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.agents))
            .options(selectinload(self.model.plugins))
            .options(selectinload(self.model.conversations))
            .options(selectinload(self.model.knowledge_bases))
            .options(selectinload(self.model.add_agents))
            .order_by(desc(self.model.updated_time))
        )
        filters = []
        if user_id:
            filters.append(self.model.id == user_id)
        if username:
            filters.append(self.model.username == username)
        if user_uuid:
            filters.append(self.model.uuid == user_uuid)
        if filters:
            stmt = stmt.where(*filters)

        user = await db.execute(stmt)

        return user.scalars().first()

    async def reset_agents(self, db: AsyncSession, user_uuid: str, agent_param: UserAgentParam) -> User | None:
        """
        获取用户和（部门，角色，菜单）

        :param db:
        :param user_uuid:
        :param agent_param:
        :return:
        """
        user = await self.get_with_relation(db, user_uuid=user_uuid)
        if not user:
            raise errors.NotFoundError(msg="用户不存在")

        # 获取智能体
        stmt = select(Agent).where(Agent.uuid.in_(agent_param.agent_uuids))  # 创建查询语句
        result = await db.execute(stmt)  # 异步执行查询
        agents = result.scalars().all()  # 将查询结果转为插件列表

        if not agents:
            agents = []

        # 更新 agent 的插件列表
        user.add_agents = agents
        await db.commit()  # 提交事务

        return user

    async def add_agents(self, db: AsyncSession, user_uuid: str, agent_param: UserAgentParam) -> User:
        """
        获取用户并为其添加智能体

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :param agent_param: 包含智能体 UUID 列表的参数
        :return: 更新后的用户对象
        :raises errors.NotFoundError: 如果用户不存在
        """
        # 获取用户及其关联的智能体
        user = await self.get_with_relation(db, user_uuid=user_uuid)
        if not user:
            raise errors.NotFoundError(msg="用户不存在")

        # 获取用户已关联的智能体 UUID 列表
        exit_agent = [agent.uuid for agent in user.add_agents] + [agent.uuid for agent in user.agents]

        # 查询需要添加的智能体，排除已关联的智能体
        stmt = select(Agent).where(
            and_(
                Agent.uuid.in_(agent_param.agent_uuids),
                Agent.uuid.not_in(exit_agent)
            )
        )
        result = await db.execute(stmt)
        agents = result.scalars().all()

        # 如果没有需要添加的智能体，直接返回用户
        if not agents:
            return user

        # 将智能体添加到用户的 add_agents 列表
        user.add_agents.extend(agents)

        # 提交事务
        await db.commit()

        return user

    async def delete_agents(self, db: AsyncSession, user_uuid: str, agent_param: UserAgentParam) -> User:
        """
        获取用户并删除其关联的智能体

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :param agent_param: 包含智能体 UUID 列表的参数
        :return: 更新后的用户对象
        :raises errors.NotFoundError: 如果用户不存在
        """
        # 获取用户及其关联的智能体
        user = await self.get_with_relation(db, user_uuid=user_uuid)
        if not user:
            raise errors.NotFoundError(msg="用户不存在")

        # 获取用户已关联的智能体 UUID 列表
        existing_agents = [agent.uuid for agent in user.add_agents] + [agent.uuid for agent in user.agents]

        # 过滤出需要删除的智能体 UUID（确保它们存在于用户的关联列表中）
        agents_to_delete_uuids = [uuid for uuid in agent_param.agent_uuids if uuid in existing_agents]

        if not agents_to_delete_uuids:
            # 如果没有需要删除的智能体，直接返回用户
            return user

        # 从用户的 add_agents 和 agents 列表中移除需要删除的智能体
        user.add_agents = [agent for agent in user.add_agents if agent.uuid not in agents_to_delete_uuids]
        user.agents = [agent for agent in user.agents if agent.uuid not in agents_to_delete_uuids]

        # 提交事务
        await db.commit()

        return user


user_dao: CRUDUser = CRUDUser(User)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl, model_validator

from app.schema import AgentListSchema, KnowledgeBaseListSchema, ConversationListSchema, PluginListSchema
from common.enums import StatusType
from common.schema import CustomPhoneNumber, SchemaBase


class AuthSchemaBase(SchemaBase):
    username: str
    password: str | None


class AuthLoginParam(AuthSchemaBase):
    captcha: str
    captcha_id: str


class RegisterUserParam(AuthSchemaBase):
    nickname: str | None = None
    email: EmailStr = Field('user@example.com', examples=['user@example.com'])


class AuthRegisterParam(RegisterUserParam):
    captcha: str
    captcha_id: str

    @model_validator(mode='before')
    def check(cls, values):
        print(values)
        return values


class AddUserParam(AuthSchemaBase):
    nickname: str | None = None
    email: EmailStr = Field(..., examples=['user@example.com'])


class UserInfoSchemaBase(SchemaBase):
    username: str
    nickname: str
    email: EmailStr = Field(..., examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None


class UpdateUserParam(SchemaBase):
    username: str | None = None
    avatar: str | None = None
    nickname: str | None = None
    email: EmailStr | None = Field(None, examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None


class AvatarParam(SchemaBase):
    url: HttpUrl = Field(..., description='头像 http 地址')


class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: str
    avatar: str | None = None
    status: StatusType = Field(default=StatusType.enable)
    is_superuser: bool
    is_staff: bool
    is_multi_login: bool
    join_time: datetime = None
    last_login_time: datetime | None = None


class GetUserInfoListDetails(GetUserInfoNoRelationDetail):
    pass


class GetCurrentUserInfoDetail(GetUserInfoListDetails):
    add_agents: list[AgentListSchema]
    agents: list[AgentListSchema]
    knowledge_bases: list[KnowledgeBaseListSchema]
    conversations: list[ConversationListSchema]
    plugins: list[PluginListSchema]


class CurrentUserIns(GetUserInfoListDetails):
    pass


class ResetPasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str


# 给 用户 添加智能体参数
class UserAgentParam(SchemaBase):
    agent_uuids: list[str]

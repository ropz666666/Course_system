#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from app.schema.user_schema import GetUserInfoNoRelationDetail, GetUserInfoListDetails, GetCurrentUserInfoDetail
from common.schema import SchemaBase


class GetSwaggerToken(SchemaBase):
    access_token: str
    token_type: str = 'Bearer'
    user: GetCurrentUserInfoDetail


class AccessTokenBase(SchemaBase):
    access_token: str
    access_token_type: str = 'Bearer'
    access_token_expire_time: datetime


class GetNewToken(AccessTokenBase):
    pass


class GetLoginToken(AccessTokenBase):
    user: GetCurrentUserInfoDetail
    cross_domain_token: str | None = None
    cross_domain_iv: str | None = None


class GetRegisterToken(AccessTokenBase):
    pass

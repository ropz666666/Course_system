#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema import (
    CreateAgentPublishmentParam,
    UpdateAgentPublishmentParam,
    GetAgentPublishmentList,
    GetAgentPublishmentDetail
)
from app.service import agent_publishment_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession
from utils.serializers import select_as_dict

router = APIRouter()


@router.post('', summary='创建智能体发布', dependencies=[DependsJwtAuth])
async def create_agent_publishment(request: Request, obj: CreateAgentPublishmentParam):
    obj.published_by = request.user.uuid
    await agent_publishment_service.add(request=request, obj=obj)
    return ''


@router.put('/{agent_publishment_uuid}', summary='更新智能体发布信息', dependencies=[DependsJwtAuth])
async def update_agent_publishment(request: Request, agent_publishment_uuid: Annotated[str, Path(...)],
                              obj: UpdateAgentPublishmentParam) :
    count = await agent_publishment_service.update(request=request, agent_publishment_uuid=agent_publishment_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{agent_publishment_uuid}/status', summary='修改智能体发布状态', dependencies=[DependsJwtAuth])
async def update_agent_publishment_status(request: Request, agent_publishment_uuid: Annotated[str, Path(...)],
                                     status: Annotated[bool, Query()]) :
    count = await agent_publishment_service.update_status(request=request, agent_publishment_uuid=agent_publishment_uuid,
                                                     status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/all', summary='查看智能体发布信息', dependencies=[DependsJwtAuth])
async def get_all_agent_publishments(
    request: Request,
    agent_uuid: Annotated[str | None, Query()] = None,
    user_uuid: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
) :
    # 获取所有智能体发布
    agent_publishments = await agent_publishment_service.get_all(user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    # 过滤出和当前用户相关的智能体发布
    filtered_agent_publishments = [
        agent_publishment for agent_publishment in agent_publishments
        if agent_publishment.user_uuid == request.user.uuid and agent_publishment.status != 2
    ]

    # 转换为响应所需的格式
    data = [GetAgentPublishmentList(**select_as_dict(agent_publishment)) for agent_publishment in filtered_agent_publishments]
    return data


@router.get('/{agent_publishment_uuid}', summary='查看智能体发布信息', dependencies=[DependsJwtAuth])
async def get_agent_publishment_info(request: Request, agent_publishment_uuid: Annotated[str, Path(...)]) :
    current_agent_publishment = await agent_publishment_service.get_with_relation(request=request,
                                                                        agent_publishment_uuid=agent_publishment_uuid)
    data = GetAgentPublishmentDetail(**select_as_dict(current_agent_publishment))
    return data


@router.get(
    '',
    summary='分页获取所有智能体发布',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_agent_publishments(
        request: Request,
        db: CurrentSession,
        name: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,
):
    agent_publishment_select = await agent_publishment_service.get_select(user_uuid=request.user.uuid, name=name, status=status)
    page_data = await paging_data(db, agent_publishment_select, GetAgentPublishmentList)
    # 过滤出和当前用户相关的智能体发布
    filtered_page_data = [
        agent_publishment for agent_publishment in page_data.get("items", [])
        if agent_publishment['status'] != 2
    ]
    page_data['items'] = filtered_page_data
    return page_data


@router.delete(
    path='/{agent_publishment_uuid}',
    summary='删除智能体发布',
    description='删除后智能体发布将从数据库中删除',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:agent_publishment:del'))],
)
async def delete_agent_publishment(request: Request, agent_publishment_uuid: Annotated[str, Path(...)]) :
    count = await agent_publishment_service.delete(request=request, agent_publishment_uuid=agent_publishment_uuid)
    if count > 0:
        return ''
    raise RequestError

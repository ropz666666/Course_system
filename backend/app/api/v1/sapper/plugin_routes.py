#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema.plugin_schema import (
    CreatePluginParam,
    UpdatePluginParam,
    GetPluginList, GetPluginDetail
)
from app.service.plugin_service import plugin_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession
from utils.serializers import select_as_dict
router = APIRouter()


@router.get('/all', summary='查看会话信息', dependencies=[DependsJwtAuth])
async def get_all_plugins(
    request: Request,
    description: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    plugins = await plugin_service.get_all(user_uuid=request.user.uuid, description=description, name=name)

    # 转换为响应所需的格式
    data = [GetPluginDetail(**select_as_dict(plugin)) for plugin in plugins]
    return data


@router.post('', summary='添加插件', dependencies=[DependsJwtAuth])
async def add_plugin(request: Request, obj: CreatePluginParam) :
    obj.user_uuid = request.user.uuid
    plugin = await plugin_service.add(obj=obj)
    return ''


@router.put('/{plugin_uuid}', summary='更新插件信息', dependencies=[DependsJwtAuth])
async def update_plugin(request: Request, plugin_uuid: Annotated[str, Path(...)], obj: UpdatePluginParam) :
    count = await plugin_service.update(request=request, plugin_uuid=plugin_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{plugin_uuid}/status', summary='修改插件状态', dependencies=[DependsJwtAuth])
async def update_plugin_status(request: Request, plugin_uuid: Annotated[str, Path(...)], status: Annotated[bool, Query()]) :
    count = await plugin_service.update_status(request=request, plugin_uuid=plugin_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/{plugin_uuid}', summary='查看插件信息', dependencies=[DependsJwtAuth])
async def get_plugin_info(request: Request, plugin_uuid: Annotated[str, Path(...)]) :
    current_plugin = await plugin_service.get_with_relation(request=request, plugin_uuid=plugin_uuid)
    data = GetPluginDetail(**select_as_dict(current_plugin))
    return data


@router.get(
    '',
    summary='分页获取所有插件',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_plugins(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
):
    plugin_select = await plugin_service.get_select(user_uuid=request.user.uuid, name=name, description=description, status=1)
    page_data = await paging_data(db, plugin_select, GetPluginList)
    return page_data


@router.delete(
    path='/{plugin_uuid}',
    summary='删除插件',
    description='删除后插件将从数据库中删除',
    dependencies=[Depends(RequestPermission('sys:plugin:del'))],
)
async def delete_plugin(request: Request, plugin_uuid: Annotated[str, Path(...)]) :
    count = await plugin_service.delete(request=request, plugin_uuid=plugin_uuid)
    if count > 0:
        return ''
    raise RequestError

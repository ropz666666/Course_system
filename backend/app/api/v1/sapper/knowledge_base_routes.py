#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema.knowledge_base_schema import (
    CreateKnowledgeBaseParam,
    UpdateKnowledgeBaseParam,
    GetKnowledgeBaseList, GetKnowledgeBaseDetail
)
from app.service.knowledge_base_service import knowledge_base_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession
from utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看知识库信息', dependencies=[DependsJwtAuth])
async def get_all_knowledge_bases(
    request: Request,
    description: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    knowledgeBases = await knowledge_base_service.get_all(user_uuid=request.user.uuid, description=description, name=name)

    # 转换为响应所需的格式
    data = [GetKnowledgeBaseList(**select_as_dict(knowledgeBase)) for knowledgeBase in knowledgeBases]
    return data


@router.post('', summary='添加知识库', dependencies=[DependsJwtAuth])
async def add_knowledge_base(request: Request, obj: CreateKnowledgeBaseParam) :
    obj.user_uuid = request.user.uuid
    knowledge_base = await knowledge_base_service.add(obj=obj)
    return ''


@router.put('/{knowledge_base_uuid}', summary='更新知识库信息', dependencies=[DependsJwtAuth])
async def update_knowledge_base(request: Request, knowledge_base_uuid: Annotated[str, Path(...)], obj: UpdateKnowledgeBaseParam) :
    count = await knowledge_base_service.update(request=request, knowledge_base_uuid=knowledge_base_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{knowledge_base_uuid}/status', summary='修改知识库状态', dependencies=[DependsJwtAuth])
async def update_knowledge_base_status(request: Request, knowledge_base_uuid: Annotated[str, Path(...)], status: Annotated[bool, Query()]) :
    count = await knowledge_base_service.update_status(request=request, knowledge_base_uuid=knowledge_base_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/{knowledge_base_uuid}', summary='查看知识库信息', dependencies=[DependsJwtAuth])
async def get_knowledge_base_info(request: Request, knowledge_base_uuid: Annotated[str, Path(...)]) :
    current_knowledge_base = await knowledge_base_service.get_with_relation(request=request, knowledge_base_uuid=knowledge_base_uuid)
    data = GetKnowledgeBaseDetail(**select_as_dict(current_knowledge_base))
    return data


@router.get(
    '',
    summary='分页获取所有知识库',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_knowledge_bases(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
):
    knowledge_base_select = await knowledge_base_service.get_select(user_uuid=request.user.uuid, name=name, description=description, status=status)
    page_data = await paging_data(db, knowledge_base_select, GetKnowledgeBaseList)
    return page_data


@router.delete(
    path='/{knowledge_base_uuid}',
    summary='删除知识库',
    description='删除后知识库将从数据库中删除',
    dependencies=[Depends(RequestPermission('sys:knowledge_base:del'))],
)
async def delete_knowledge_base(request: Request, knowledge_base_uuid: Annotated[str, Path(...)]) :
    count = await knowledge_base_service.delete(request=request, knowledge_base_uuid=knowledge_base_uuid)  # no need for request here
    if count > 0:
        return ''
    raise RequestError

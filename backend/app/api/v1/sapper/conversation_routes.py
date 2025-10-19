#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema import (
    CreateConversationParam,
    UpdateConversationParam,
    GetConversationList,
    GetConversationDetail, CreateKnowledgeBaseParam,
)
from app.service.conversation_service import conversation_service
from app.service.knowledge_base_service import knowledge_base_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession
from utils.serializers import select_as_dict

router = APIRouter()


@router.post('', summary='创建会话', dependencies=[DependsJwtAuth])
async def create_conversation(request: Request, obj: CreateConversationParam):
    conversation = await conversation_service.add(request=request, obj=obj)
    conversation_data = GetConversationList(**select_as_dict(conversation))
    return conversation_data


@router.put('/{conversation_uuid}', summary='更新会话信息', dependencies=[DependsJwtAuth])
async def update_conversation(request: Request, conversation_uuid: Annotated[str, Path(...)],
                              obj: UpdateConversationParam) :
    count = await conversation_service.update(request=request, conversation_uuid=conversation_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{conversation_uuid}/status', summary='修改会话状态', dependencies=[DependsJwtAuth])
async def update_conversation_status(request: Request, conversation_uuid: Annotated[str, Path(...)],
                                     status: Annotated[bool, Query()]) :
    count = await conversation_service.update_status(request=request, conversation_uuid=conversation_uuid,
                                                     status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/all', summary='查看会话信息', dependencies=[DependsJwtAuth])
async def get_all_conversations(
    request: Request,
    agent_uuid: Annotated[str | None, Query()] = None,
    user_uuid: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    conversations = await conversation_service.get_all(user_uuid=user_uuid, agent_uuid=agent_uuid, name=name)

    # 过滤出和当前用户相关的会话
    filtered_conversations = [
        conversation for conversation in conversations
        if conversation.user_uuid == request.user.uuid and conversation.status != 2
    ]

    # 转换为响应所需的格式
    data = [GetConversationList(**select_as_dict(conversation)) for conversation in filtered_conversations]
    return data


@router.get('/{conversation_uuid}', summary='查看会话信息', dependencies=[DependsJwtAuth])
async def get_conversation_info(request: Request, conversation_uuid: Annotated[str, Path(...)]) :
    current_conversation = await conversation_service.get_with_relation(request=request,
                                                                        conversation_uuid=conversation_uuid)
    data = GetConversationDetail(**select_as_dict(current_conversation))
    return data


@router.get(
    '',
    summary='分页获取所有会话',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_conversations(
        request: Request,
        db: CurrentSession,
        name: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,
):
    conversation_select = await conversation_service.get_select(user_uuid=request.user.uuid, name=name, status=status)
    page_data = await paging_data(db, conversation_select, GetConversationList)
    # 过滤出和当前用户相关的会话
    filtered_page_data = [
        conversation for conversation in page_data.get("items", [])
        if conversation['status'] != 2
    ]
    page_data['items'] = filtered_page_data
    return page_data


@router.delete(
    path='/{conversation_uuid}',
    summary='删除会话',
    description='删除后会话将从数据库中删除',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:conversation:del'))],
)
async def delete_conversation(request: Request, conversation_uuid: Annotated[str, Path(...)]) :
    count = await conversation_service.delete(request=request, conversation_uuid=conversation_uuid)
    if count > 0:
        return ''
    raise RequestError

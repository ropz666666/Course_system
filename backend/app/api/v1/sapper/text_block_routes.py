#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
import re
from fastapi import APIRouter, Depends, Path, Query, Request

from app.schema.text_block_schema import (
    UpdateTextBlockParam,
    GetTextBlockList, GetTextBlockDetail
)
from app.schema.embedding_schema import CreateEmbeddingParam, UpdateEmbeddingParam
from app.schema.text_block_schema import CreateTextBlockParam
from app.service.embedding_service import embedding_service
from app.service.text_block_service import text_block_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from core.conf import settings
from database.db_mysql import CurrentSession
from utils.sapper_server import send_async_rag_request, send_async_embed_request
from utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看集合下所有文本块', dependencies=[DependsJwtAuth])
async def get_all_text_blocks(
        request: Request,
        collection_uuid: Annotated[str | None, Query()] = None,
        content: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    agents = await text_block_service.get_all(collection_uuid=collection_uuid, content=content)
    # 转换为响应所需的格式
    data = [GetTextBlockList(**select_as_dict(agent)) for agent in agents]
    return data


@router.post('', summary='添加文本块', dependencies=[DependsJwtAuth])
async def add_text_block(request: Request, obj: CreateTextBlockParam) :
    text_block = await text_block_service.add(obj=obj)
    url = f'{settings.SAPPER_SERVER_URL}sapperrag/content-embedding'
    headers = {"Accept": "application/json"}

    # Process embeddings
    embed_result = await send_async_embed_request(url, headers, obj.content)
    await embedding_service.add(
        obj=CreateEmbeddingParam(
            vector=embed_result['embed_result'][0]['text_embedding'],
            text_block_uuid=text_block.uuid
        )
    )
    text_block_data = GetTextBlockList(**select_as_dict(text_block))
    return text_block_data


@router.put('/{text_block_uuid}', summary='更新文本块信息', dependencies=[DependsJwtAuth])
async def update_text_block(request: Request, text_block_uuid: Annotated[str, Path(...)], obj: UpdateTextBlockParam) :
    count = await text_block_service.update(request=request, text_block_uuid=text_block_uuid, obj=obj)
    url = f'{settings.SAPPER_SERVER_URL}sapperrag/content-embedding'
    headers = {"Accept": "application/json"}
    text_block = await text_block_service.get_with_relation(request=request, text_block_uuid=text_block_uuid)
    # Process embeddings
    embed_result = await send_async_embed_request(url, headers, obj.content)
    await embedding_service.update(
        request=request,
        embedding_uuid=text_block.embedding.uuid,
        obj=UpdateEmbeddingParam(
            vector=embed_result['embed_result'][0]['text_embedding'],
        )
    )
    if count > 0:
        return ''
    raise RequestError


@router.put('/{text_block_uuid}/status', summary='修改文本块状态', dependencies=[DependsJwtAuth])
async def update_text_block_status(request: Request, text_block_uuid: Annotated[str, Path(...)], status: Annotated[bool, Query()]) :
    count = await text_block_service.update_status(request=request, text_block_uuid=text_block_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/{text_block_uuid}', summary='查看文本块信息', dependencies=[DependsJwtAuth])
async def get_text_block_info(request: Request, text_block_uuid: Annotated[str, Path(...)]) :
    current_text_block = await text_block_service.get_with_relation(request=request, text_block_uuid=text_block_uuid)
    data = GetTextBlockDetail(**select_as_dict(current_text_block))
    return data


@router.get(
    '',
    summary='分页获取所有文本块',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_text_blocks(
    request: Request,
    db: CurrentSession,
    content: Annotated[str | None, Query()] = None,
    collection_uuid: Annotated[str | None, Query()] = None,
):
    print(collection_uuid, "collection_uuid")
    text_block_select = await text_block_service.get_select(collection_uuid=collection_uuid, content=content)
    page_data = await paging_data(db, text_block_select, GetTextBlockList)
    return page_data


@router.delete(
    path='/{text_block_uuid}',
    summary='删除文本块',
    description='删除后文本块将从数据库中删除',
    dependencies=[Depends(RequestPermission('sys:text_block:del'))],
)
async def delete_text_block(request: Request, text_block_uuid: Annotated[str, Path(...)]) :
    count = await text_block_service.delete(request=request, text_block_uuid=text_block_uuid)  # no need for request here
    if count > 0:
        return ''
    raise RequestError

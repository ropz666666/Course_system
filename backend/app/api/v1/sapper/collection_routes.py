#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request, UploadFile
from fastapi import BackgroundTasks
from app.schema.collection_schema import (
    CreateCollectionParam,
    UpdateCollectionParam,
    GetCollectionList, GetCollectionDetail
)
from app.schema.embedding_schema import CreateEmbeddingParam
from app.schema.text_block_schema import CreateTextBlockParam
from app.service.embedding_service import embedding_service
from app.service.collection_service import collection_service
from app.service.text_block_service import text_block_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from core.conf import settings
from database.db_mysql import CurrentSession, get_db
from utils.sapper_server import send_async_rag_request
from utils.serializers import select_as_dict
from common.log import log
router = APIRouter()


@router.get('/all', summary='查看知识库下所有集合', dependencies=[DependsJwtAuth])
async def get_all_collections(
        request: Request,
        knowledge_base_uuid: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    agents = await collection_service.get_all(knowledge_base_uuid=knowledge_base_uuid)

    # 转换为响应所需的格式
    data = [GetCollectionList(**select_as_dict(agent)) for agent in agents]
    return data


@router.post('', summary='添加知识集合', dependencies=[DependsJwtAuth])
async def add_collection(
        request: Request,
        obj: CreateCollectionParam,
        background_tasks: BackgroundTasks
):
    obj.status = 2  # Set status to "processing"
    collection = await collection_service.add(obj=obj)

    # Add the embedding task to background tasks
    background_tasks.add_task(
        process_collection_embedding,
        collection.uuid,
        obj.file_url
    )

    return GetCollectionList(**select_as_dict(collection))


async def process_collection_embedding(collection_uuid: str, file_url: str):
    """Background task for processing collection embeddings"""
    try:
        log.info(f"Starting embedding process for collection {collection_uuid}")
    
        url = f'{settings.SAPPER_SERVER_URL}sapperrag/embedding'
        headers = {"Accept": "application/json"}
        data = {
            "file_url": file_url
        }
        # Process embeddings
        embed_result = await send_async_rag_request(url, headers, data)
    
        # Use a transaction for all database operations
        for embed in embed_result.get('embed_result', []):
            text_block_data = await text_block_service.add(
                obj=CreateTextBlockParam(
                    collection_uuid=collection_uuid,
                    content=embed.get('text', '')
                )
            )
    
            await embedding_service.add(
                obj=CreateEmbeddingParam(
                    vector=embed.get('text_embedding', []),
                    text_block_uuid=text_block_data.uuid
                )
            )
    
        # Update collection status to "completed"
        await collection_service.update(
            request=None,
            collection_uuid=collection_uuid,
            obj=UpdateCollectionParam(status=1)
        )
    
        log.info(f"Successfully processed embeddings for collection {collection_uuid}")
    except Exception as e:
        log.error(f"Error processing embeddings for collection {collection_uuid}: {str(e)}")

        # Update collection status to "failed"
        await collection_service.update(
            request=None,
            collection_uuid=collection_uuid,
            obj=UpdateCollectionParam(status=3)  # Assuming 3 means "failed"
        )

        # Re-raise if you want the error to be visible in logs
        raise


@router.put('/{collection_uuid}', summary='更新知识集合信息', dependencies=[DependsJwtAuth])
async def update_collection(request: Request, collection_uuid: Annotated[str, Path(...)], obj: UpdateCollectionParam) :
    count = await collection_service.update(request=request, collection_uuid=collection_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{collection_uuid}/status', summary='修改知识集合状态', dependencies=[DependsJwtAuth])
async def update_collection_status(request: Request, collection_uuid: Annotated[str, Path(...)], status: Annotated[bool, Query()]) :
    count = await collection_service.update_status(request=request, collection_uuid=collection_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/{collection_uuid}', summary='查看知识集合信息', dependencies=[DependsJwtAuth])
async def get_collection_info(request: Request, collection_uuid: Annotated[str, Path(...)]) :
    current_collection = await collection_service.get_with_relation(request=request, collection_uuid=collection_uuid)
    data = GetCollectionDetail(**select_as_dict(current_collection))
    return data


@router.get(
    '',
    summary='分页获取所有知识集合',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_collections(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    knowledge_base_uuid: Annotated[str | None, Query()] = None,
):
    collection_select = await collection_service.get_select(knowledge_base_uuid=knowledge_base_uuid, name=name, description=description, status=status)
    page_data = await paging_data(db, collection_select, GetCollectionList)
    return page_data


@router.delete(
    path='/{collection_uuid}',
    summary='删除知识集合',
    description='删除后知识集合将从数据库中删除',
    dependencies=[Depends(RequestPermission('sys:collection:del'))],
)
async def delete_collection(request: Request, collection_uuid: Annotated[str, Path(...)]) :
    count = await collection_service.delete(request=request, collection_uuid=collection_uuid)  # no need for request here
    if count > 0:
        return ''
    raise RequestError

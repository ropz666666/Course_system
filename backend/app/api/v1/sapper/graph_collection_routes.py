#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from app.schema.graph_collection_schema import (
    CreateGraphCollectionParam,
    UpdateGraphCollectionParam,
    GetGraphCollectionList, GetGraphCollectionDetail
)
from app.service.graph_collection_service import graph_collection_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession
from utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看知识库下所有集合', dependencies=[DependsJwtAuth])
async def get_all_graph_collections(
        request: Request,
        knowledge_base_uuid: Annotated[str | None, Query()] = None,
) :
    # 获取所有会话
    agents = await graph_collection_service.get_all(knowledge_base_uuid=knowledge_base_uuid)

    # 转换为响应所需的格式
    data = [GetGraphCollectionList(**select_as_dict(agent)) for agent in agents]
    return data


@router.post('', summary='添加知识集合', dependencies=[DependsJwtAuth])
async def add_graph_collection(request: Request, obj: CreateGraphCollectionParam) :
    file_url = obj.file_url
    if file_url is not None:
        try:
            # 读取 JSON 文件
            with open(file_url, 'r', encoding='utf-8') as file:
                json_data = json.load(file)  # 直接解析 JSON 文件内容

            # 确保 JSON 数据是一个字典，并且包含所需的字段
            if isinstance(json_data, dict):
                entities = json_data.get('entities', '[]')
                relationships = json_data.get('relationships', '[]')
                communities = json_data.get('communities', '[]')
                obj.entities = entities
                obj.relationships = relationships
                obj.communities = communities
            else:
                raise RequestError(msg="Invalid JSON format: expected a dictionary")

        except Exception as e:
            raise RequestError(msg=f"Failed to read JSON file: {str(e)}")

    # 继续处理逻辑
    graph_collection = await graph_collection_service.add(obj=obj)
    graph_collection_data = GetGraphCollectionList(**select_as_dict(graph_collection))
    return graph_collection_data


@router.put('/{graph_collection_uuid}', summary='更新知识集合信息', dependencies=[DependsJwtAuth])
async def update_graph_collection(request: Request, graph_collection_uuid: Annotated[str, Path(...)], obj: UpdateGraphCollectionParam) :
    count = await graph_collection_service.update(request=request, graph_collection_uuid=graph_collection_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{graph_collection_uuid}/status', summary='修改知识集合状态', dependencies=[DependsJwtAuth])
async def update_graph_collection_status(request: Request, graph_collection_uuid: Annotated[str, Path(...)], status: Annotated[bool, Query()]) :
    count = await graph_collection_service.update_status(request=request, graph_collection_uuid=graph_collection_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.get('/{graph_collection_uuid}', summary='查看知识集合信息', dependencies=[DependsJwtAuth])
async def get_graph_collection_info(request: Request, graph_collection_uuid: Annotated[str, Path(...)]) :
    current_graph_collection = await graph_collection_service.get_with_relation(request=request, graph_collection_uuid=graph_collection_uuid)
    data = GetGraphCollectionDetail(**select_as_dict(current_graph_collection))
    return data


@router.get(
    '',
    summary='分页获取所有知识集合',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_graph_collections(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    knowledge_base_uuid: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
):
    graph_collection_select = await graph_collection_service.get_select(knowledge_base_uuid=knowledge_base_uuid, name=name, description=description, status=status)
    page_data = await paging_data(db, graph_collection_select, GetGraphCollectionList)
    return page_data


@router.delete(
    path='/{graph_collection_uuid}',
    summary='删除知识集合',
    description='删除后知识集合将从数据库中删除',
    dependencies=[Depends(RequestPermission('sys:graph_collection:del'))],
)
async def delete_graph_collection(request: Request, graph_collection_uuid: Annotated[str, Path(...)]) :
    count = await graph_collection_service.delete(request=request, graph_collection_uuid=graph_collection_uuid)  # no need for request here
    if count > 0:
        return ''
    raise RequestError

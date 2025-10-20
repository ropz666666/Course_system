#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated
import os
import mimetypes

from fastapi import APIRouter, Path, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.course_resource_service import CourseResourceService
from database.db_mysql import CurrentSession

router = APIRouter()


@router.get('/{resource_id}/preview', summary='预览课程资源')
async def preview_course_resource(
    db: CurrentSession,
    resource_id: Annotated[int, Path(description='资源ID')]
):
    """预览课程资源"""
    # 获取资源信息
    resource = await CourseResourceService.get_resource_detail(db=db, resource_id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    # 构建文件完整路径
    file_path = os.path.join("static", resource.file_path.lstrip("/"))
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 获取文件的MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    # 对于可预览的文件类型，直接返回文件内容
    previewable_types = [
        'text/plain', 'text/html', 'text/css', 'text/javascript',
        'application/json', 'application/xml', 'text/xml',
        'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
        'application/pdf'
    ]
    
    if mime_type in previewable_types or mime_type.startswith('text/'):
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            headers={"Content-Disposition": "inline"}
        )
    else:
        # 对于不可预览的文件类型，返回错误信息
        raise HTTPException(status_code=415, detail="该文件类型不支持预览")
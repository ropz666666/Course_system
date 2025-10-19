#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from app.api.v1.sapper.user_routes import router as user_router
from app.api.v1.sapper.agent_routes import router as agent_router
from app.api.v1.sapper.conversation_routes import router as conversation_router
from app.api.v1.sapper.plugin_routes import router as plugin_router
from app.api.v1.sapper.knowledge_base_routes import router as knowledge_base_router
from app.api.v1.sapper.collection_routes import router as collection_router
from app.api.v1.sapper.graph_collection_routes import router as graph_collection_router
from app.api.v1.sapper.text_block_routes import router as text_block_router
from app.api.v1.sapper.publish_routes import router as publish_router

router = APIRouter(prefix='/sapper')

router.include_router(user_router, prefix='/user', tags=['用户'])
router.include_router(agent_router, prefix='/agent', tags=['智能体'])
router.include_router(conversation_router, prefix='/conversation', tags=['会话'])
router.include_router(plugin_router, prefix='/plugin', tags=['插件'])
router.include_router(knowledge_base_router, prefix='/knowledge_base', tags=['知识库'])
router.include_router(collection_router, prefix='/collection', tags=['集合'])
router.include_router(graph_collection_router, prefix='/graph-collection', tags=['图谱集合'])
router.include_router(text_block_router, prefix='/text_block', tags=['文本块'])
router.include_router(publish_router, prefix='/publish', tags=['发布'])

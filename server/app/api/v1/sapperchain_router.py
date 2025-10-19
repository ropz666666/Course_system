#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from contextlib import suppress

import aiofiles
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
# from mcp import stdio_client, StdioServerParameters, ClientSession

from app.schema.sapperchain_schema import GenerateSplFormParam, GenerateSplChainParam, GenerateAnswerParam, \
    GenerateAvatarParam, GenerateConversationNameParam
from app.service.agent_service import agent_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-spl-form")
async def require_2_spl_form(request: Request, obj: GenerateSplFormParam):
    return StreamingResponse(agent_service.generate_spl_form(request=request, requirement=obj.requirement),
                             media_type="text/plain")


@router.post("/generate-spl-chain")
async def require_2_spl_chain(request: Request, obj: GenerateSplChainParam):
    return StreamingResponse(agent_service.generate_spl_chain(request=request, agent_data=obj.agent_data),
                             media_type="text/plain")


@router.post("/generate-answer")
async def run_spl_chain(request: Request, obj: GenerateAnswerParam):
    return StreamingResponse(agent_service.generate_answer
                             (agent_data=obj.agent_data,
                              conversation_data=obj.conversation_data,
                              query=obj.query
                              ),
                             media_type="text/plain")


@router.post("/generate-avatar")
async def run_generate_avatar(request: Request, obj: GenerateAvatarParam):
    return StreamingResponse(agent_service.generate_avatar(requirement=obj.requirement), media_type="text/plain")


@router.post("/generate-conversation-name")
async def run_generate_conversation_name(request: Request, obj: GenerateConversationNameParam):
    return StreamingResponse(agent_service.generate_conversation_name(query=obj.query), media_type="text/plain")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import inspect
from datetime import datetime
from http.client import HTTPException
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import HTTPException, status as httpstatus
import json
from typing import AsyncGenerator
import hashlib
from app.crud.crud_conversation import conversation_dao
from app.schema import (
    CreateAgentParam,
    AddAgentPluginParam,
    AddAgentKnowledgeBaseParam,
    UpdateAgentParam,
    QueryAgentParam, GetAgentList, GetAgentDetail, CreatePluginParam, CreateInteractionParam, UpdateInteractionParam
)
from app.schema.conversation_schema import CreateConversationParam, UpdateConversationParam
from app.service.agent_service import agent_service
from app.service.conversation_service import conversation_service
from app.service.interaction_service import interaction_service
from common.pagination import DependsPagination, paging_data
from common.exception.errors import RequestError
from common.security.jwt import DependsJwtAuth
from common.security.permission import RequestPermission
from database.db_mysql import CurrentSession, async_db_session
from utils.serializers import select_as_dict
from common.log import log as logger
from app.conf import admin_settings
from xml.etree import ElementTree as ET
import time
from fastapi import Response
import xmltodict
from async_timeout import timeout as async_timeout
router = APIRouter()


@router.get('/all', summary='查看所有智能体', dependencies=[DependsJwtAuth])
async def get_all_agents(
        request: Request,
        description: Annotated[str | None, Query()] = None,
        name: Annotated[str | None, Query()] = None,
):
    # 获取所有会话
    agents = await agent_service.get_all(user_uuid=request.user.uuid, description=description, name=name)

    # 转换为响应所需的格式
    data = [GetAgentList(**select_as_dict(agent)) for agent in agents]
    return data


@router.get(
    '/all/public',
    summary='分页获取所有智能体',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_public_agents(
        request: Request,
        db: CurrentSession,
        name: Annotated[str | None, Query()] = None,
        description: Annotated[str | None, Query()] = None,
        tag: Annotated[str | None, Query()] = None,
):
    agent_select = await agent_service.get_select(name=name, description=description, status=2, tag=tag)
    page_data = await paging_data(db, agent_select, GetAgentList)
    return page_data


@router.post('', summary='添加智能体', dependencies=[DependsJwtAuth])
async def add_agent(request: Request, obj: CreateAgentParam):
    obj.user_uuid = request.user.uuid
    agent = await agent_service.add(obj=obj)
    await conversation_service.add(request=request, obj=CreateConversationParam(
        user_uuid=request.user.uuid,
        agent_uuid=agent.uuid,
        status=2
    ))
    agent_data = GetAgentList(**select_as_dict(agent))
    return agent_data


@router.put('/{agent_uuid}', summary='更新智能体信息', dependencies=[DependsJwtAuth])
async def update_agent(request: Request, agent_uuid: Annotated[str, Path(...)], obj: UpdateAgentParam):
    count = await agent_service.update(request=request, agent_uuid=agent_uuid, obj=obj)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{agent_uuid}/status', summary='修改智能体状态', dependencies=[DependsJwtAuth])
async def update_agent_status(request: Request, agent_uuid: Annotated[str, Path(...)],
                              status: Annotated[bool, Query()]):
    count = await agent_service.update_status(request=request, agent_uuid=agent_uuid, status=status)
    if count > 0:
        return ''
    raise RequestError


@router.put('/{agent_uuid}/favorite')
async def update_agent_favorite(
    request: Request,
    agent_uuid: str,
    favorite: bool = Body(..., embed=True)
):
    count = await interaction_service.update_by_agent_user(
        request=request,
        agent_uuid=agent_uuid,
        obj=UpdateInteractionParam(is_favorite=favorite)
    )
    if count > 0:
        return {}
    raise RequestError()


@router.put('/{agent_uuid}/rating')
async def update_agent_rating(
    request: Request,
    agent_uuid: str,
    rating_value: float = Body(..., embed=True)
):
    count = await interaction_service.update_by_agent_user(
        request=request,
        agent_uuid=agent_uuid,
        obj=UpdateInteractionParam(rating_value=rating_value)
    )
    if count > 0:
        return {}
    raise RequestError()


@router.post('/{agent_uuid}/plugin', summary='给智能体添加插件', dependencies=[DependsJwtAuth])
async def reset_plugin_to_agent(request: Request, agent_uuid: Annotated[str, Path(...)],
                                plugin_param: AddAgentPluginParam):
    await agent_service.add_plugin(request=request, agent_uuid=agent_uuid, plugin_param=plugin_param)
    return ''


@router.post('/{agent_uuid}/knowledge_base', summary='给智能体添加知识库', dependencies=[DependsJwtAuth])
async def reset_knowledge_base_to_agent(request: Request, agent_uuid: Annotated[str, Path(...)],
                                        knowledge_base_param: AddAgentKnowledgeBaseParam):
    await agent_service.add_knowledge_base(request=request, agent_uuid=agent_uuid,
                                           knowledge_base_param=knowledge_base_param)
    return ''


@router.get('/{agent_uuid}', summary='查看智能体信息', dependencies=[DependsJwtAuth])
async def get_agent_info(request: Request, agent_uuid: Annotated[str, Path(...)]):
    try:
        await interaction_service.add(obj = CreateInteractionParam(
            user_uuid=request.user.uuid,
            agent_uuid=agent_uuid
        ))
    except Exception as e:
        pass
    current_agent = await agent_service.get_with_relation(request=request, agent_uuid=agent_uuid)
    data = GetAgentDetail(**select_as_dict(current_agent), operator_uuid=request.user.uuid)
    return data


@router.get(
    '',
    summary='分页获取所有智能体',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_agents(
        request: Request,
        db: CurrentSession,
        name: Annotated[str | None, Query()] = None,
        description: Annotated[str | None, Query()] = None,
        tag: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,
):
    agent_select = await agent_service.get_select(user_uuid=request.user.uuid, name=name, description=description,
                                                  status=status, tag=tag)
    page_data = await paging_data(db, agent_select, GetAgentList)
    return page_data


@router.delete(
    path='/{agent_uuid}',
    summary='删除智能体',
    description='删除后智能体将从数据库中删除',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:agent:del'))],
)
async def delete_agent(request: Request, agent_uuid: Annotated[str, Path(...)]):
    count = await agent_service.delete(request=request, agent_uuid=agent_uuid)  # no need for request here
    if count > 0:
        return ''
    raise RequestError


@router.get("/generate_spl_form/{agent_uuid}")
async def require_2_spl_form(request: Request, agent_uuid: Annotated[str, Path(...)]):
    return StreamingResponse(agent_service.generate_spl_form(request=request, agent_uuid=agent_uuid),
                             media_type="text/plain")


@router.get(
    "/generate_spl_chain/{agent_uuid}",
    dependencies=[DependsJwtAuth],
)
async def require_2_spl_chain(request: Request, agent_uuid: Annotated[str, Path(...)]):
    return StreamingResponse(agent_service.generate_spl_chain(request=request, agent_uuid=agent_uuid),
                             media_type="text/plain")


async def generate_stream(request: Request, query: QueryAgentParam, agent_uuid) -> AsyncGenerator[str, None]:
    # Initialize chat history
    generate_conversation_name_flag = False
    conversation_uuid = query.conversation_uuid

    history = []
    units = None
    try:
        if conversation_uuid is not None:
            async with async_db_session() as db:
                conversation = await conversation_dao.get_with_relation(
                    db=db,
                    conversation_uuid=conversation_uuid
                )
                if not conversation:
                    raise HTTPException(
                        status_code=httpstatus.HTTP_404_NOT_FOUND,
                        detail="Conversation not found"
                    )

                history = json.loads(conversation.chat_history or "[]")
                if len(history) == 0:
                    generate_conversation_name_flag = True
                history.append({"role": "user", "contents": query.message})

                # Save user message immediately
                await conversation_dao.update(
                    db,
                    conversation_uuid=conversation_uuid,
                    obj=UpdateConversationParam(chat_history=history)
                )
                await db.commit()

        async for chunk in agent_service.generate_answer(
                agent_uuid=agent_uuid,
                conversation_uuid=conversation_uuid,
                query=query.message
        ):
            try:
                if await request.is_disconnected():
                    print("客户端中断了连接")
                    client_disconnected = True
                    break

                chunk_data = json.loads(chunk)

                if units is None:
                    units = chunk_data.get('units')

                current_unit = chunk_data['current_unit']
                current_unit_content = current_unit.get("output")
                current_unit_name = current_unit.get("unit_name")

                if units.get(current_unit_name) is not None:
                    current_unit_output = units[current_unit_name].get("output", [])

                    def add_output(output_arr, output_content):
                        if output_content.get('type', 'text').lower() == 'url':
                            output_content["type"] = 'image'
                            output_arr.append(output_content)
                        elif output_content.get('type', 'text').lower() == 'text':
                            if len(output_arr) == 0 or output_arr[-1]["type"] != "text":
                                output_arr.append({"content": "", "type": "text"})
                            output_arr[-1]["content"] = output_arr[-1].get("content") + output_content.get("content")
                        return output_arr

                    current_unit_output = add_output(current_unit_output, current_unit_content)
                    current_unit["output"] = current_unit_output
                    current_unit["input"] = None
                    units[current_unit_name] = current_unit

                chunk_data_ = json.loads(chunk)
                chunk_data_["input"] = None
                yield f"data: {json.dumps(chunk_data_, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)

            except json.JSONDecodeError:
                continue
        yield "[DONE]"

    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        raise

    finally:
        await interaction_service.update_usage_count(
            request=request,
            agent_uuid=agent_uuid
        )
        # 无论是否完成或中断，都保存已生成的内容
        if conversation_uuid is not None:
            try:

                # 如果有生成的内容，添加到历史记录
                if units is not None:
                    history.append({
                        "role": "system",
                        "units": list(units.values())  # 显式转换为列表
                    })

                async with async_db_session() as db:
                    update_params = UpdateConversationParam(chat_history=history)

                    # 如果是新对话，尝试生成名称
                    if generate_conversation_name_flag and len(history) > 1:
                        try:
                            conservation_name = await conversation_service.generate_name(query=json.dumps(history))
                            update_params.name = conservation_name
                        except Exception as e:
                            print(f"生成对话名称失败: {str(e)}")

                    # 更新数据库
                    update_result = await conversation_dao.update(
                        db=db,
                        conversation_uuid=conversation_uuid,
                        obj=update_params
                    )
                    print(f"数据库更新结果: {update_result}")

            except Exception as e:
                print(f"保存对话历史失败: {str(e)}")
                # 尝试最小化保存
                try:
                    async with async_db_session() as db:
                        await conversation_dao.update(
                            db=db,
                            conversation_uuid=conversation_uuid,
                            obj=UpdateConversationParam(
                                chat_history=history
                            )
                        )
                        await db.commit()
                except Exception as inner_e:
                    print(f"严重错误: 无法保存最小对话历史: {str(inner_e)}")


@router.post(
    "/generate_answer/{agent_uuid}",
    dependencies=[DependsJwtAuth],
    response_class=StreamingResponse,
)
async def run_spl_chain(
        request: Request,
        agent_uuid: Annotated[str, Path(...)],
        query: QueryAgentParam
) -> StreamingResponse:
    """
    Generate streaming response for agent conversation

    Args:
        request:
        agent_uuid: UUID of the conversation
        query: User query parameters

    Returns:
        StreamingResponse: SSE stream of LLM responses
    """
    try:
        return StreamingResponse(
            generate_stream(request, query, agent_uuid),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except HTTPException as e:
        print(f"Error processing request: {str(e)}")
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     detail=f"Error processing request: {str(e)}"
        # )


@router.post(
    "/generate_debug/{agent_uuid}",
    dependencies=[DependsJwtAuth],
    response_class=StreamingResponse,
)
async def debug_spl_chain(
        request: Request,
        agent_uuid: Annotated[str, Path(...)],
        query: QueryAgentParam
) -> StreamingResponse:
    """
    Generate streaming response for agent conversation

    Args:
        agent_uuid: UUID of the conversation
        query: User query parameters

    Returns:
        StreamingResponse: SSE stream of LLM responses
    """
    try:
        # Initialize chat history
        conversation_uuid = query.conversation_uuid
        if conversation_uuid is not None:
            async with async_db_session() as db:
                conversation = await conversation_dao.get_with_relation(
                    db=db,
                    conversation_uuid=conversation_uuid
                )
                if not conversation:
                    raise HTTPException(
                        status_code=httpstatus.HTTP_404_NOT_FOUND,
                        detail="Conversation not found"
                    )

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generator function for streaming LLM response"""
            llm_response_chunks = []
            current_result = []
            try:
                async for chunk in agent_service.generate_answer(
                        agent_uuid=agent_uuid,
                        query=query.message,
                        conversation_uuid=conversation_uuid,
                        debug=True,
                        debug_unit=query.debug_unit
                ):
                    try:
                        chunk_data = json.loads(chunk)
                        chunk_data = chunk_data.get('content', '')
                        if conversation_uuid is not None:
                            if chunk_data.get('response_type', 'text') == 'image':
                                current_result.append({'type': 'text', 'content': ''.join(llm_response_chunks)})
                                current_result.append({'type': 'image', 'content': chunk_data.get("content", "")})
                                llm_response_chunks = []
                            if chunk_data.get('response_type', 'text') == 'progress':
                                current_result.append({'type': 'text', 'content': ''.join(llm_response_chunks)})
                                llm_response_chunks = []
                            else:
                                llm_response_chunks.append(chunk_data.get("content", ""))

                        res = {'content': chunk_data.get("content", ""),
                               'type': chunk_data.get('response_type', 'text')}

                        yield f"data: {json.dumps(res, ensure_ascii=False)}\n"
                        # 保持流式响应活跃
                        await asyncio.sleep(0.01)
                    except json.JSONDecodeError:
                        # logger.error(f"Invalid JSON chunk: {chunk}")
                        continue

            except Exception as e:
                # logger.error(f"Error during streaming: {str(e)}")
                raise

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        # logger.exception("Unexpected error in run_spl_chain")
        raise HTTPException(
            status_code=httpstatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@router.post(
    "/generate_avatar",
    dependencies=[DependsJwtAuth],
)
async def generate_agent_avatar(request: Request, agent_uuid: Annotated[str, Path(...)]):
    download_data = await agent_service.download_agent(request=request, agent_uuid=agent_uuid)
    json_data = jsonable_encoder(download_data)
    return JSONResponse(content=json_data, media_type="application/json", headers={
        "Content-Disposition": f"attachment; filename=agent_data.json"
    })


@router.post(
    "/download/{agent_uuid}",
    dependencies=[DependsJwtAuth],
)
async def download_agent_endpoint(request: Request, agent_uuid: Annotated[str, Path(...)]):
    download_data = await agent_service.download_agent(request=request, agent_uuid=agent_uuid)
    json_data = jsonable_encoder(download_data)
    return JSONResponse(content=json_data, media_type="application/json", headers={
        "Content-Disposition": f"attachment; filename=agent_data.json"
    })


def parse_xml(xml_data):
    msg = {}
    root = ET.fromstring(xml_data)
    for child in root:
        msg[child.tag] = child.text
    return msg


async def generate_reply(from_user, to_user, msg_type, content, agent_uuid):
    if msg_type != "text":
        return _build_reply_xml(from_user, to_user, "暂不支持此类型消息")

    res = ""
    start_time = datetime.now()
    query = QueryAgentParam(message=[{"type": "text", "content": content}])

    try:
        # 添加超时控制
        async with async_timeout(4.5):  # 比4秒稍长，给清理留时间
            generator = agent_service.generate_answer(
                agent_uuid=agent_uuid,
                query=query.message
            )
            try:
                async for chunk in generator:
                    chunk_data = json.loads(chunk)
                    print(chunk_data["current_unit"]["output"]["content"])
                    if chunk_data["current_unit"]["output"]["type"] != 'progress':
                        res += chunk_data["current_unit"]["output"]["content"]
            finally:
                await _safe_close_async_gen(generator)
    except asyncio.TimeoutError:
        print("reply", res)
        res = f"{res}（部分回复，已超时）" if res else "请求超时，请稍后再试"
    except Exception as e:
        logger.error(f"生成回复出错: {str(e)}")
        res = "服务暂时不可用，请稍后再试"

    return _build_reply_xml(from_user, to_user, res)


async def _safe_close_async_gen(gen):
    """安全关闭异步生成器"""
    try:
        if gen and inspect.isasyncgen(gen):
            try:
                await gen.aclose()
            except (RuntimeError, GeneratorExit):
                pass  # 已经关闭的生成器会抛出这些异常
    except Exception as e:
        logger.warning(f"关闭生成器时出错: {str(e)}")


def _build_reply_xml(from_user: str, to_user: str, content: str) -> str:
    """构造微信XML回复"""
    return f"""
    <xml>
      <ToUserName><![CDATA[{from_user}]]></ToUserName>
      <FromUserName><![CDATA[{to_user}]]></FromUserName>
      <CreateTime>{int(time.time())}</CreateTime>
      <MsgType><![CDATA[text]]></MsgType>
      <Content><![CDATA[{content}]]></Content>
    </xml>
    """


@router.post("/wechat/generate_answer/{agent_uuid}")
async def run_spl_chain_to_wx(request: Request, agent_uuid: Annotated[str, Path(...)]):
    # 解析 XML 数据
    xml_data = await request.body()
    msg_dict = xmltodict.parse(xml_data)["xml"]

    # 提取关键字段
    msg_type = msg_dict.get("MsgType")
    from_user = msg_dict.get("FromUserName")
    to_user = msg_dict.get("ToUserName")
    content = msg_dict.get("Content", "") if msg_type == "text" else ""
    agent_data = await agent_service.get_with_relation(request=request, agent_uuid=agent_uuid, is_wx_auth=True)
    for publishment in agent_data.publishments:
        if publishment.channel.name == '微信订阅号':
            # 生成回复
            reply = await generate_reply(from_user, to_user, msg_type, content, agent_uuid)
            return Response(content=reply, media_type="application/xml")


@router.get("/wechat/generate_answer/{agent_uuid}")
async def get_we_chat_signature(request: Request, agent_uuid: Annotated[str, Path(...)]):
    # 获取微信验证参数
    params = request.query_params
    signature = params.get("signature", "")
    timestamp = params.get("timestamp", "")
    nonce = params.get("nonce", "")
    echostr = params.get("echostr", "")
    agent_data = await agent_service.get_with_relation(request=request, agent_uuid=agent_uuid, is_wx_auth=True)
    for publish in agent_data.publishments:
        if publish.channel.name == '微信订阅号':
            # 校验签名
            tmp_list = sorted([publish.publish_config.get('Token'), timestamp, nonce])
            tmp_str = "".join(tmp_list).encode("utf-8")
            hash_str = hashlib.sha1(tmp_str).hexdigest()
            if hash_str == signature:
                return Response(content=echostr)  # 验证成功返回 echostr
    return Response(content="Verification Failed", status_code=403)

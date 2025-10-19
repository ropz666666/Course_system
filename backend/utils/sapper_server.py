import asyncio
from common.log import log
import httpx
from httpx import Timeout
import aiohttp
from typing import Dict, Any, Optional
import json
from fastapi import HTTPException

timeout = Timeout(60.0, read=360.0)  # 连接超时为5秒，读取超时为30秒


async def send_async_request(url, headers, data, timeout=30.0):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=data) as response:
                async for part in response.aiter_lines():
                    if part and not part.isspace():
                        part_str = part
                        if part_str.startswith('data: '):
                            part_str = part_str[6:]
                            if part_str == '[DONE]':
                                break
                            try:
                                decoded_part = json.loads(part_str)
                                if decoded_part.get("error"):
                                    raise ValueError(f"API error: {decoded_part.get('error')}")
                                yield decoded_part
                            except json.JSONDecodeError as e:
                                log.warning(f"JSON解析失败: {part_str}")
                                continue
    except GeneratorExit:
        log.debug("生成器被正常关闭")
        raise
    except Exception as e:
        log.error(f"请求出错: {str(e)}")
        raise
    finally:
        log.debug("请求资源清理完成")


async def send_async_rag_request(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 60
):
    """
    发送异步 RAG 请求 (非文件类型)

    参数:
    - url: 目标API地址
    - headers: 请求头 (可选)
    - data: form-data格式数据 (可选)
    - json_data: JSON格式数据 (可选)
    - timeout: 超时时间(秒) 默认60秒

    返回:
    - 响应JSON数据

    异常:
    - HTTPException: 包含错误详情
    """

    # 设置默认headers
    final_headers = headers or {}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    headers=final_headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                # 检查响应状态
                if response.status != 200:
                    error_detail = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"RAG请求失败: {error_detail}"
                    )

                # 尝试解析JSON响应
                try:
                    return await response.json()
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"响应JSON解析失败: {str(e)}"
                    )

    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=503,
            detail=f"RAG服务连接错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理RAG请求时发生意外错误: {str(e)}"
        )


async def send_async_embed_request(
        url: str,
        headers: Dict[str, str],
        content: str,
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Send an asynchronous embedding request with proper error handling and retries.

    Args:
        url: The endpoint URL for the embedding service
        headers: Request headers including content-type, authorization etc.
        content: The text content to be embedded
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Dictionary containing the embedding response or None if failed
    """
    payload = {
        "content": content,
    }

    timeout_config = aiohttp.ClientTimeout(total=timeout)

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                        url,
                        headers=headers,
                        json=payload,
                        raise_for_status=True
                ) as response:

                    # Validate response content type
                    if 'application/json' not in response.headers.get('Content-Type', ''):
                        raise ValueError("Invalid response content type")

                    response_data = await response.json()

                    # Validate response structure
                    if not isinstance(response_data, dict) or 'embed_result' not in response_data:
                        raise ValueError("Invalid response format")

                    return response_data

        except json.JSONDecodeError as e:
            log.error(f"JSON decode error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                raise ValueError("Failed to decode response JSON") from e

        except aiohttp.ClientError as e:
            log.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                raise ConnectionError(f"Request failed after {max_retries} attempts") from e

        except ValueError as e:
            log.error(f"Validation error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                raise ValueError(f"Validation failed after {max_retries} attempts") from e

        # Exponential backoff for retries
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay * (attempt + 1))

    return None

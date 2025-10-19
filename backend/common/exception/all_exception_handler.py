# 集中处理所有异常类型，包括 FastAPI 原生异常和自定义异常。
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.conf import settings
from common.response.response_code import CustomResponseCode
from common.response.response import ErrorResponse
from common.exception.custom_exception import BusinessError, UnauthorizedError
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局兜底处理，捕获所有未处理的异常，防止敏感信息泄露"""

    cid = request.headers.get("X-Request-ID", "unknown")
    logger.bind(correlation_id=cid).opt(exception=exc).error(
        "Unhandled exception occurred",
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=CustomResponseCode.HTTP_500.code,
        content=ErrorResponse(
            code=CustomResponseCode.HTTP_500.code,
            msg=CustomResponseCode.HTTP_500.msg,
            detail={
                "error": "Internal Server Error",
                "correlation_id": cid,
                "detail": "Please contact support with the correlation ID"
            } if settings.DEBUG else None  # 生产环境隐藏细节
        ).model_dump()
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理 FastAPI 原生 HTTPException"""

    # 仅处理 StarletteHTTPException
    if isinstance(exc, StarletteHTTPException):
        cid = request.headers.get("X-Request-ID", "unknown")
        logger.bind(correlation_id=cid).warning(
            "HTTP Exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.status_code,  # 建议 exc.status_code * 100 如 404 -> 40400
                msg=exc.detail if isinstance(exc.detail, dict) else exc.detail,
                detail={
                "error": exc.detail,
                "correlation_id": cid
                } if isinstance(exc.detail, dict) else None
            ).model_dump()
        )
    else:
        cid = request.headers.get("X-Request-ID", "unknown")
        logger.bind(correlation_id=cid).opt(exception=exc).error(
            "Unhandled exception occurred",
            path=request.url.path,
            method=request.method
        )

        return JSONResponse(
            status_code=CustomResponseCode.HTTP_500.code,
            content=ErrorResponse(
                code=CustomResponseCode.HTTP_500.code,
                msg=CustomResponseCode.HTTP_500.msg,
                detail={
                    "error": "Internal Server Error",
                    "correlation_id": cid,
                    "detail": "Please contact support with the correlation ID"
                } if settings.DEBUG else None  # 生产环境隐藏细节
            ).model_dump()
        )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理请求参数校验错误"""
    cid = request.headers.get("X-Request-ID", "unknown")
    logger.bind(correlation_id=cid).opt(exception=exc).error(
        "Unhandled exception occurred",
        path=request.url.path,
        method=request.method
    )
    # 仅处理 RequestValidationError
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=CustomResponseCode.HTTP_422.code,
            content=ErrorResponse(
                code=CustomResponseCode.HTTP_422.code,
                msg=CustomResponseCode.HTTP_422.msg,
                detail={
                    "error": exc.body,
                    "correlation_id": cid
                } if isinstance(exc.body, dict) else None
            ).model_dump()
        )
    else:
        return JSONResponse(
            status_code=CustomResponseCode.HTTP_500.code,
            content=ErrorResponse(
                code=CustomResponseCode.HTTP_500.code,
                msg=CustomResponseCode.HTTP_500.msg,
                detail={
                    "error": "Internal Server Error",
                    "correlation_id": cid,
                    "detail": "Please contact support with the correlation ID"
                } if settings.DEBUG else None  # 生产环境隐藏细节
            ).model_dump()
        )


async def business_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理自定义业务异常"""
    if isinstance(exc, BusinessError):
        cid = request.headers.get("X-Request-ID", "unknown")
        logger.bind(correlation_id=cid).warning(
            exc.msg,
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path
        )

        response = JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.code,
                msg=exc.msg,
                detail={
                    "error": exc.detail,
                    "correlation_id": cid
                } if isinstance(exc.detail, dict) else None
            ).model_dump()
        )
        # 执行后台任务（如果有）
        if exc.background:
            response.background = exc.background
        return response
    else:
        cid = request.headers.get("X-Request-ID", "unknown")
        logger.bind(correlation_id=cid).opt(exception=exc).error(
            "Unhandled exception occurred",
            path=request.url.path,
            method=request.method
        )

        return JSONResponse(
            status_code=CustomResponseCode.HTTP_500.code,
            content=ErrorResponse(
                code=CustomResponseCode.HTTP_500.code,
                msg=CustomResponseCode.HTTP_500.msg,
                detail={
                    "error": "Internal Server Error",
                    "correlation_id": cid,
                    "detail": "Please contact support with the correlation ID"
                } if settings.DEBUG else None  # 生产环境隐藏细节
            ).model_dump()
        )


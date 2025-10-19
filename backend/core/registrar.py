#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware
from middleware.opera_log_middleware import OperaLogMiddleware
from app.router import route
from common.log import setup_logging
from core.conf import settings
# from core.config import settings as conf_setting
from core.path_conf import STATIC_DIR, FILES_DIR
# from backend.database.db_mysql import create_table
# from backend.database.db_redis import redis_client
from middleware.jwt_auth_middleware import JwtAuthMiddleware
from middleware.state_middleware import StateMiddleware
from utils.demo_site import demo_site
from utils.health_check import ensure_unique_route_names, http_limit_callback
from utils.openapi import simplify_operation_ids
from utils.serializers import MsgSpecJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from common.exception.all_exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    business_exception_handler
)
from common.exception.custom_exception import BusinessError, UnauthorizedError

@asynccontextmanager
async def register_init(app: FastAPI) -> object:
    """
    启动初始化

    :return:
    """
    print("Starting up...")
    yield
    # 执行一些清理操作
    print("Shutting down...")

    # # 创建数据库表
    # print("Initializing model on startup...\n")
    # await initialize_model()
    # print("Model initialized on startup.\n")
    # await create_table()
    # # 连接 redis
    # await redis_client.open()
    # # 初始化 limiter
    # await FastAPILimiter.init(
    #     redis=redis_client, prefix=settings.REQUEST_LIMITER_REDIS_PREFIX, http_callback=http_limit_callback
    # )
    #
    # yield
    #
    # # 关闭 redis 连接
    # await redis_client.close()
    # # 关闭 limiter
    # await FastAPILimiter.close()


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOCS_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    # CORS中间件将在register_middleware中配置

    # 日志
    register_logger()

    # 静态文件
    register_static_file(app)

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

    # 分页
    # register_page(app)

    # 全局异常处理
    register_exception(app)

    return app



def register_logger() -> None:
    """
    系统日志

    :return:
    """
    setup_logging()


def register_static_file(app: FastAPI):
    """
    静态文件交互开发模式, 生产使用 nginx 静态资源服务

    :param app:
    :return:
    """
    if settings.FASTAPI_STATIC_FILES:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists(STATIC_DIR):
            os.mkdir(STATIC_DIR)

        if not os.path.exists(FILES_DIR):
            os.mkdir(FILES_DIR)

        print(STATIC_DIR)
        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
        app.mount('/files', StaticFiles(directory=FILES_DIR), name='files')


def register_middleware(app: FastAPI):
    """
    中间件，执行顺序从下往上

    :param app:
    :return:
    """
    # Opera log (required)
    app.add_middleware(OperaLogMiddleware)
    # app.add_middleware(
    #     EnhancedLogMiddleware,
    #     config=LogMiddlewareConfig(
    #         sensitive_keys={"password", "ssn", "credit_card"},
    #         exclude_paths={"/healthcheck"}
    #     )
    # )

    # JWT auth (required)
    app.add_middleware(
        AuthenticationMiddleware, backend=JwtAuthMiddleware(), on_error=JwtAuthMiddleware.auth_exception_handler
    )
    # Access log
    # if settings.MIDDLEWARE_ACCESS:
    #     from middleware.access_middleware import AccessMiddleware
    #
    #     app.add_middleware(AccessMiddleware)
    # State
    app.add_middleware(StateMiddleware)
    # Trace ID (required)
    app.add_middleware(CorrelationIdMiddleware, validator=False)
    # CORS: Always at the end
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    app.include_router(route, dependencies=dependencies)

    # Extra
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_page(app: FastAPI):
    """
    分页查询

    :param app:
    :return:
    """
    add_pagination(app)

def register_exception(app: FastAPI):
    # 注册全局处理器（注意覆盖顺序，很重要！）
    app.add_exception_handler(Exception, global_exception_handler)  # 兜底处理
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # 注册自定义异常
    app.add_exception_handler(BusinessError, business_exception_handler)
    app.add_exception_handler(UnauthorizedError, http_exception_handler)

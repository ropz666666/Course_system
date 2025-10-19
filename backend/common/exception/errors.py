#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局业务异常类

业务代码执行异常时，可以使用 raise xxxError 触发内部错误，它尽可能实现带有后台任务的异常，但它不适用于**自定义响应状态码**
如果要求使用**自定义响应状态码**，则可以通过 return response_base.fail(res=CustomResponseCode.xxx) 直接返回
"""  # noqa: E501

from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from common.response.response_code import CustomResponseCode, StandardResponseCode
from common.exception.custom_exception import BusinessError


class HTTPError(HTTPException):
    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None):
        super().__init__(status_code=code, detail=msg, headers=headers)


class RequestError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_400.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_400.code,
            msg=msg,
            detail=detail,
            background=background
        )


class ForbiddenError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_403.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_403.code,
            msg=msg,
            detail=detail,
            background=background
        )


class NotFoundError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_404.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_404.code,
            msg=msg,
            detail=detail,
            background=background
        )


class ServerError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_500.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_500.code,
            msg=msg,
            detail=detail,
            background=background
        )


class GatewayError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_502.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_502.code,
            msg=msg,
            detail=detail,
            background=background
        )


class AuthorizationError(BusinessError):
    def __init__(
            self,
            msg: str = CustomResponseCode.HTTP_401.msg,
            detail: dict = None,
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_401.code,
            msg=msg,
            detail=detail,
            background=background
        )


class TokenError(BusinessError):
    def __init__(
        self,
        msg: str = "认证失败",
        detail: dict = None,
        headers: dict[str, Any] | None = None
    ):
        super().__init__(
            code=StandardResponseCode.HTTP_401.code,
            msg=msg,
            detail=detail
        )
        self.headers = headers or {'WWW-Authenticate': 'Bearer'}

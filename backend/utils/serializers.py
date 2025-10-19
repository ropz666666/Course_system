#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Any, Sequence, TypeVar

from fastapi.encoders import decimal_encoder
from msgspec import json
from sqlalchemy import Row, RowMapping
from sqlalchemy.orm import ColumnProperty, SynonymProperty, class_mapper
from starlette.responses import JSONResponse
from common.response.response import ErrorResponse, SuccessResponse
from core.conf import settings

RowData = Row | RowMapping | Any

R = TypeVar('R', bound=RowData)


def select_columns_serialize(row: R) -> dict:
    """
    Serialize SQLAlchemy select table columns, does not contain relational columns

    :param row:
    :return:
    """
    result = {}
    for column in row.__table__.columns.keys():
        v = getattr(row, column)
        if isinstance(v, Decimal):
            v = decimal_encoder(v)
        result[column] = v
    return result


def select_list_serialize(row: Sequence[R]) -> list:
    """
    Serialize SQLAlchemy select list

    :param row:
    :return:
    """
    result = [select_columns_serialize(_) for _ in row]
    return result


def select_as_dict(row: R, use_alias: bool = False) -> dict:
    """
    Converting SQLAlchemy select to dict, which can contain relational data,
    depends on the properties of the select object itself

    If set use_alias is True, the column name will be returned as alias,
    If alias doesn't exist in columns, we don't recommend setting it to True

    :param row:
    :param use_alias:
    :return:
    """
    if not use_alias:
        result = row.__dict__
        if '_sa_instance_state' in result:
            del result['_sa_instance_state']
            return result
    else:
        result = {}
        mapper = class_mapper(row.__class__)
        for prop in mapper.iterate_properties:
            if isinstance(prop, (ColumnProperty, SynonymProperty)):
                key = prop.key
                result[key] = getattr(row, key)
        return result


class MsgSpecJSONResponse(JSONResponse):
    """覆盖 FastAPI 的默认响应类，强制所有响应通过 ErrorResponse 或 SuccessResponse 模型序列化"""
    def render(self, content: Any) -> bytes:
        # 正常响应包装为 SuccessResponse
        if self.status_code < 400:
            content = SuccessResponse(data=content).model_dump()
        # 错误响应已由异常处理器处理，此处仅兜底异常情况
        else:
            if not isinstance(content, dict) or "code" not in content:
                content = ErrorResponse(
                    code=50000,
                    msg="未知错误",
                    detail=content if settings.DEBUG else None
                ).model_dump()
        return super().render(content)

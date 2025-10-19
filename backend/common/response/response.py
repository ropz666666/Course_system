
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic
from common.response.response_code import CustomResponseCode

DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    code: int = CustomResponseCode.HTTP_200.code       # 成功固定为 0
    msg: str = CustomResponseCode.HTTP_200.msg # 默认消息
    data: Optional[DataT] = None  # 业务数据


class ErrorResponse(BaseModel):
    code: int    # 自定义错误码（如 40001=业务错误）
    msg: str # 错误码详细说明
    detail: Optional[dict] = None  # 开发调试详情（可选）

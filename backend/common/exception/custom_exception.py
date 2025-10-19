from starlette.background import BackgroundTask
from common.response.response_code import CustomResponseCode


class BusinessError(Exception):
    def __init__(
        self,
        code: int = CustomResponseCode.HTTP_400.code,
        msg: str = CustomResponseCode.HTTP_400.msg,
        status_code: int = CustomResponseCode.HTTP_200.code,
        detail: dict = None,
        background: BackgroundTask | None = None
    ):
        self.code = code
        self.msg = msg
        self.status_code = status_code
        self.detail = detail
        self.background = background  # 后台任务


class UnauthorizedError(BusinessError):
    """401 未授权异常"""
    def __init__(
            self,
            msg: str = "身份验证失败",
            background: BackgroundTask | None = None
    ):
        super().__init__(
            code=CustomResponseCode.HTTP_401.code,
            msg=msg,
            status_code=CustomResponseCode.HTTP_401.code,
            background=background
        )

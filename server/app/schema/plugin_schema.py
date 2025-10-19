from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import model_validator

from common.schema import SchemaBase


class PluginSchemaBase(SchemaBase):
    name: str
    description: str
    cover_image: str | None = None
    status: int


class PluginDetailSchema(PluginSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    server_url: Optional[str] = None
    api_parameter: Union[str, Dict, None] = None
    parse_path: Optional[list] = None
    return_value_type: Optional[str] = 'Text'
    content_type: str
    authorization: str
    created_time: datetime
    stream: bool = False
    updated_time: Optional[datetime] = None

    @model_validator(mode='before')
    def check(cls, values):
        server_url = values.get("server_url", '')
        if 'sapper/agent' in server_url:
            values["stream"] = True
        return values


class ImageRequest(SchemaBase):
    image_url: Optional[str] = None  # 图片 URL
    base64_image: Optional[str] = None  # Base64 编码的图片数据


class MarkdownConvertRequest(SchemaBase):
    content: str

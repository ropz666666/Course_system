import json
from datetime import datetime
from typing import Optional, List, Dict, Union

from pydantic import Field, model_validator, HttpUrl

from common.dataclasses import SPLSection
from common.enums import StatusType
from common.schema import SchemaBase


# 基础的 Plugin 信息结构
from utils.serializers import select_as_dict


class PluginSchemaBase(SchemaBase):
    name: str
    description: str
    cover_image: str | None = None
    status: int


# 创建 Plugin 参数
class CreatePluginParam(PluginSchemaBase):
    status: int = Field(default=StatusType.enable.value)
    cover_image: str | None = ''
    user_uuid: Optional[str] = None
    server_url: Optional[str] = None
    header_info: Optional[str] = None
    return_info: Optional[str] = None
    api_parameter: Optional[str] = None

    @model_validator(mode='before')
    def validate_and_transform(cls, values: Dict) -> Dict:
        # Handle header_info transformation
        content_type = values.get('content_type', 'application/json')
        authorization = values.get('authorization', None)
        if authorization is not None and content_type is not None:
            values['header_info'] = json.dumps({
                "content_type": content_type,
                "authorization": authorization
            })

        # Handle return_info transformation
        parse_path = values.get('parse_path', [])
        return_value_type = values.get('return_value_type', 'Text')
        if parse_path is not None and return_value_type is not None:
            values['return_info'] = json.dumps({
                "return_value_type": return_value_type,
                "parse_path": parse_path
            })

        # Handle api_parameter transformation
        api_parameter = values.get('api_parameter')
        if api_parameter is not None and not isinstance(api_parameter, str):
            values['api_parameter'] = json.dumps(api_parameter)

        # Remove temporary fields
        values.pop('return_value_type', None)
        values.pop('parse_path', None)
        values.pop('content_type', None)
        values.pop('authorization', None)
        return values


# 更新 Plugin 参数
class UpdatePluginParam(PluginSchemaBase):
    name: str | None = None
    description: str | None = None
    cover_image: str | None = None
    status: int | None = None
    server_url: str | None = None
    header_info: str | None = None
    return_info: str | None = None
    api_parameter: str | None = None

    @model_validator(mode='before')
    def validate_and_transform(cls, values: Dict) -> Dict:
        # Handle header_info transformation
        content_type = values.get('content_type', 'application/json')
        authorization = values.get('authorization', None)
        if authorization is not None and content_type is not None:
            values['header_info'] = json.dumps({
                "content_type": content_type,
                "authorization": authorization
            })

        # Handle return_info transformation
        parse_path = values.get('parse_path', [])
        return_value_type = values.get('return_value_type', 'Text')
        if parse_path is not None and return_value_type is not None:
            values['return_info'] = json.dumps({
                "return_value_type": return_value_type,
                "parse_path": parse_path
            })

        # Handle api_parameter transformation
        api_parameter = values.get('api_parameter')
        if api_parameter is not None and not isinstance(api_parameter, str):
            values['api_parameter'] = json.dumps(api_parameter)

        # Remove temporary fields
        values.pop('return_value_type', None)
        values.pop('parse_path', None)
        values.pop('content_type', None)
        values.pop('authorization', None)
        return values


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
    updated_time: Optional[datetime] = None

    @model_validator(mode='before')
    def validate_and_transform(cls, data: Union[Dict, 'Plugin']) -> Dict:
        # Convert model instance to dict if needed
        values = data if isinstance(data, dict) else select_as_dict(data)
        try:
            # Handle header_info transformation
            if 'header_info' in values:
                header_info = json.loads(values.get('header_info', '{}'))
                values['content_type'] = header_info.get('content_type', '')
                values['authorization'] = header_info.get('authorization', '')

            # Handle return_info transformation
            if 'return_info' in values:
                return_info = json.loads(values.get('return_info', '{}'))
                values['return_value_type'] = return_info.get('return_value_type', 'Text')
                values['parse_path'] = return_info.get('parse_path', [])

            # Handle api_parameter transformation
            if 'api_parameter' in values and isinstance(values['api_parameter'], str):
                values['api_parameter'] = json.loads(values['api_parameter'])

        except json.JSONDecodeError:
            # Handle JSON decode errors gracefully
            pass

        # Remove temporary fields
        values.pop('header_info', None)
        values.pop('return_info', None)

        return values


# Plugin 列表信息结构
class PluginListSchema(PluginSchemaBase):
    id: int
    uuid: str
    user_uuid: str

    created_time: datetime
    updated_time: datetime | None = None


# 当前 Plugin 信息详情
class GetPluginDetail(PluginDetailSchema):
    pass


# 当前 Plugin 信息详情
class GetPluginList(PluginListSchema):
    pass


class ImageRequest(SchemaBase):
    image_url: Optional[str] = None  # 图片 URL
    base64_image: Optional[str] = None  # Base64 编码的图片数据


class MarkdownConvertRequest(SchemaBase):
    content: str

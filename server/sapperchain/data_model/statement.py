from pydantic import BaseModel,HttpUrl

from typing import Union
from typing import Optional, Dict
from .data import DataView


class APIInput(BaseModel):
    server_url: Optional[str] = None
    api_parameter: Union[str, Dict, None] = None
    parse_path: Optional[list] = None
    return_value_type: Optional[str] = 'Text'
    content_type: str
    authorization: Optional[str] = ''
    stream: bool = False


class DataInput(BaseModel):
    api_parameter: Union[str, Dict, None] = None
    content_type: str
    return_value_type: Optional[str] = 'Text'
    # query: str
    data_view: DataView
    stream: bool = False


class ModelInput(BaseModel):
    server_url: Optional[str] = None
    api_parameter: Union[str, Dict, None] = None
    parse_path: Optional[list] = None
    return_value_type: Optional[str] = 'Text'
    content_type: str
    authorization: Optional[str] = ''
    stream: bool = False


class Tool(BaseModel):
    tool_def: dict
    server_url: Optional[str] = None
    tool_parameter: Union[str, Dict, None] = None
    parse_path: Optional[list] = None
    return_value_type: Optional[str] = 'Text'
    content_type: str
    authorization: str
    stream: bool = False


from pydantic import BaseModel,HttpUrl
from .data import TextData, GraphData
from typing import Optional, Dict, Union, Literal
from typing import Any, Optional, List, Dict



class API(BaseModel):
    name: str
    description: str
    uuid: str
    server_url: Optional[str] = None
    api_parameter: Union[str, Dict, None] = None
    parse_path: Optional[list] = None
    return_value_type: Optional[str] = 'Text'
    content_type: str
    authorization: str
    stream: bool = False


class KnowledgeBase(BaseModel):
    uuid: str
    name: str
    description: str
    embedding_model: str
    text_collections: list[TextData] | None = None
    graph_collections: list[GraphData]

class Parameter(BaseModel):
    uuid: str
    type: str
    placeholder: str
    description: str
    value: str

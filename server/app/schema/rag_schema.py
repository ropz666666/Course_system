from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RAGRetrievalResponse(BaseModel):
    uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    server_url: Optional[str] = None
    header_info: Optional[str] = None
    return_info: Optional[str] = None
    api_parameter: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None


class RAGReadResponse(BaseModel):
    content: str


class RAGChunkResponse(BaseModel):
    chunk: str


class RAGChunk(BaseModel):
    content: str
    process: str


class RAGReadHtml(BaseModel):
    urls: str

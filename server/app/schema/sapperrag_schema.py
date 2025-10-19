from app.schema import GetKnowledgeBaseWorkSpace
from pydantic import BaseModel as SchemaBase


class ContentEmbeddingParam(SchemaBase):
    content: str


class FileEmbeddingParam(SchemaBase):
    file_url: str


class FileReadingParam(SchemaBase):
    file_url: str

class KnowledgeRetrivalParam(SchemaBase):
    knowledge_base: GetKnowledgeBaseWorkSpace
    query: str

from pydantic import BaseModel


class FileProcessRequest(BaseModel):
    file: str


from pydantic import BaseModel

class Prompt(BaseModel):
    name: str

class AI_REVIEWER_Output(BaseModel):
    score: int
    suggestion: str

class AI_WRITER_Output(BaseModel):
    content: str

class CommonOutput(BaseModel):
    content: str


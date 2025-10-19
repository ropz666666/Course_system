from pydantic import BaseModel
from .unit import Statement
from .statement import APIInput, DataInput, ModelInput
class Unit(BaseModel):
    name: str
    description: str
    input: dict | APIInput | DataInput | ModelInput
    type: str
    func_statements: list[Statement]


class FuncDef(BaseModel):
    name: str
    func_type: str
    func_des: list
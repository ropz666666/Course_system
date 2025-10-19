from common.schema import SchemaBase


# 基础的 Interaction 信息结构
class InteractionSchemaBase(SchemaBase):
    rating_value: float | None
    is_favorite: bool
    usage_count: int


# 创建 Interaction 参数
class CreateInteractionParam(InteractionSchemaBase):
    user_uuid: str | None = None
    agent_uuid: str | None = None
    rating_value: float | None = None
    is_favorite: bool | None = None
    usage_count: int | None = None


# 更新 Interaction 参数
class UpdateInteractionParam(InteractionSchemaBase):
    rating_value: float | None = None
    is_favorite: bool | None = None
    usage_count: int | None = None


class GetInteractionDetail(InteractionSchemaBase):
    user_uuid: str | None = None
    agent_uuid: str | None = None


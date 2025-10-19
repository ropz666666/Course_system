from sqlalchemy import Column, ForeignKey, Table
from common.model import MappedBase

# Association Tables for Many-to-Many relationships
user_agent_map = Table(
    'user_agent_map',
    MappedBase.metadata,
    Column('user_uuid', ForeignKey('user.uuid', ondelete='CASCADE'), primary_key=True),
    Column('agent_uuid', ForeignKey('agent.uuid', ondelete='CASCADE'), primary_key=True)
)



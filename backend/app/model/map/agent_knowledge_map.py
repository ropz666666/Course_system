from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from common.model import MappedBase

# Association Tables for Many-to-Many relationships
agent_knowledge_map = Table(
    'agent_knowledge_map',
    MappedBase.metadata,
    Column('agent_uuid', ForeignKey('agent.uuid', ondelete='CASCADE'), primary_key=True),
    Column('knowledge_base_uuid', ForeignKey('knowledge_base.uuid', ondelete='CASCADE'), primary_key=True)
)

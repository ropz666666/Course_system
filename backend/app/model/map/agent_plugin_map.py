from sqlalchemy import Column, ForeignKey, Table
from common.model import MappedBase

# Association Tables for Many-to-Many relationships
agent_plugin_map = Table(
    'agent_plugin_map',
    MappedBase.metadata,
    Column('agent_uuid', ForeignKey('agent.uuid', ondelete='CASCADE'), primary_key=True),
    Column('plugin_uuid', ForeignKey('plugin.uuid', ondelete='CASCADE'), primary_key=True)
)

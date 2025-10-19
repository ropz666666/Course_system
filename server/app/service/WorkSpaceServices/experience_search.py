import json
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from ..view_service import get_view_by_uuid
from ..exbase_service import get_exbase_by_uuid
import requests
from io import StringIO

class SearchViewFromRep:
    def __init__(self, data_source: str, filter_condition: list, valid_field: list, template: str, top_n: int) -> None:
        self.data_source = data_source
        self.filter_condition = filter_condition
        self.valid_field = valid_field
        self.template = template
        self.top_n = top_n

    @classmethod
    async def create(cls, db: AsyncSession, view_uuid: str, top_n: int):
        view = await cls.get_view_by_uuid(db, view_uuid)
        data_url = await cls.get_exbase_by_uuid(db, view.data_source)
        print(data_url)
        return cls(data_url, json.loads(view.filter_condition), json.loads(view.use_field),
                   view.template, top_n)

    @staticmethod
    async def get_view_by_uuid(db: AsyncSession, view_uuid: str):
        view = await get_view_by_uuid(db, view_uuid)
        return view if view else ''

    @staticmethod
    async def get_exbase_by_uuid(db: AsyncSession, uuid: str):
        view = await get_exbase_by_uuid(db, uuid)
        return view.url if view else ''

    @staticmethod
    async def read_csv_from_url(url: str):
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        csv_data = StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        return df

    async def SearchView(self, Request: str):
        data = await SearchViewFromRep.read_csv_from_url(self.data_source)
        return json.dumps({'type': 'options', 'content': "hello"})


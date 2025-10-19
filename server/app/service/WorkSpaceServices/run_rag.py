import re

from ..view_service import get_view_by_uuid
from ...common.AgentFunctionModuleBase.RAGModule import DataViewDefiner, DBGetter, DataRetriever
from ...common.AgentProperties import LongTerm_Memory
import json
from ...common.Tool import DataUsageUtility
from sqlalchemy.ext.asyncio import AsyncSession

class RunRAG:
    def __init__(self, data_usage_utility) -> None:
        self.data_usage_utility = data_usage_utility

    @staticmethod
    async def get_view_by_uuid(db: AsyncSession, agent_uuid: str):
        views = await get_view_by_uuid(db, agent_uuid)
        return views if views else []

    @classmethod
    async def create(cls, db: AsyncSession, view_uuid, ** kwargs):
        parameters = kwargs.get('parameters', {})
        view = await cls.get_view_by_uuid(db, view_uuid)
        storage = LongTerm_Memory()
        DataView_Definer = DataViewDefiner(StorageLoc=storage.View, DataLoader=None)
        File_Path = view.data_source
        relation_db = view.relation_uuid
        vector_db = view.vector_uuid
        Valid_Field = json.loads(view.use_field)
        SearchExpression_Elements = []
        for condition in json.loads(view.filter_condition):
            condition_content = condition["content"]
            matches = re.findall(r'\$\{(.*?)\}\$', condition["content"])
            for m in matches:
                condition_content.replace("${" + m + "}$", parameters[m])
            SearchExpression_Elements.append({"Search_Field": condition["field"],
                                              "Relational_Operators": condition["operation"],
                                              "Search_Value": condition_content,
                                              "Logical_Operators": condition["logic"]})
        DefViewName = view.name
        StorageForm = "Variable"
        OutputForm = view.template
        DataView_Definer.DefData("", File_Path, relation_db, vector_db, Valid_Field, SearchExpression_Elements,
                                 DefViewName, StorageForm, OutputForm)

        data_usage_utility = DataUsageUtility(DefView=storage.View[DefViewName],
                                            DBGetter=DBGetter(),
                                            DataRetriever=DataRetriever(
                                                Valid_Fields=Valid_Field,
                                                SearchExpression_Element=SearchExpression_Elements,
                                                OutPut_Format=OutputForm))

        return cls(data_usage_utility)

    async def run_rag(self):
        Res = self.data_usage_utility.GetData()
        return Res
        # except Exception as e:
        #     yield json.dumps({"type": "error", "content": "Something went wrong while running the agent. Please try again."})

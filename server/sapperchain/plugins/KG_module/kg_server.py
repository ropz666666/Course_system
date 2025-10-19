from KG_module.function_module.graph_extractor import SubGraphExtractor
from KG_module.function_module.graph_importer import GraphImporter
# from rag.graph_rag import GraphRAG,GraphContextBuilder
from model_module.function_moudle.llm_call.openai_ import EmbeddingModel
from model_module.function_moudle.llm_call.deepseek import ChatModel
from data_module.function_moudle.retriever import SemanticRetriever
from data_module.function_moudle.ranker import FieldRanker
from data_module.function_moudle.parser import JsonParser

json_parser = JsonParser()

graph_importer = GraphImporter(json_parser)


chat_model = ChatModel(
    base_url="https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    api_key="2275c4c0-3a6b-44c0-957c-f453b246e4a8",
    model_name= "deepseek-v3-241226",
   )
embedding_model = EmbeddingModel(
    base_url= "https://api.rcouyi.com/v1",
    api_key = "sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd",
    model_name="text-embedding-3-small"
)
retriever = SemanticRetriever(llm=embedding_model)
ranker = FieldRanker()
sub_graph_extractor = SubGraphExtractor(graph_level=None)
context_builder = GraphContextBuilder(max_context_tokens=8000, ranker=ranker)

index_path = r"sapperrag/index.json"

graph = graph_importer.import_(index_path)




graph_rag = GraphRAG(
    graph=graph,
    embedding_llm= embedding_model,
    retriever= retriever,
    ranker= ranker,
    graph_extractor= sub_graph_extractor,
    context_builder = context_builder,
    chat_llm= chat_model,
)
query = "介绍一下ping,也介绍一下吴贻顺？"
response = graph_rag.run(query)
print(response)

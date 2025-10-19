import json
from collections import defaultdict
from typing import Any, cast

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from sapperrag.embedding import LocalModelEmbedding
from sapperrag.graphrag.KG_ops.base import Graph
from sapperrag.graphrag.KG_ops.function_module.graph_importer import GraphImporter
from sapperrag.graphrag.KG_ops.function_module.util import remove_unrelated_attributes, get_entity_information_by_id, \
    num_tokens
from sapperrag.graphrag.data_ops.function_moudle.parser import JsonParser
from sapperrag.graphrag.data_ops.function_moudle.ranker import FieldRanker
from sapperrag.graphrag.model_ops.function_moudle.llm.deepseek import ChatModel
from sapperrag.graphrag.model_ops.function_moudle.llm.openai_ import EmbeddingModel
from sapperrag.retriver.structured_search.local_search.system_prompt import EXTRACT_ENTITIES_FROM_QUERY


class GraphDataRetriever:
    def __init__(self):
        pass

    def __extract_entities_by_llm(self, user_input, chat_llm):
        extract_prompt = EXTRACT_ENTITIES_FROM_QUERY.format(query=user_input)
        while True:
            try:
                entities = json.loads(chat_llm.generate(extract_prompt))
                if entities:
                    return entities
            except Exception as e:
                print(e)

    def __retrieve(self, queries, database):
        if not queries:
            return []

        entities_list = []

        for entity_name, extracted_embed in queries.items():
            similarities = []

            for entity in database:
                entity_embed = np.array(entity.attributes_embedding)
                if entity_embed.ndim == 1:
                    entity_embed = entity_embed.reshape(1, -1)

                similarity = cosine_similarity(extracted_embed, entity_embed)[0][0]
                similarities.append((entity, similarity))

            entities_list.extend(similarities)

        # ==================
        entities_list.sort(key=lambda x: x[1], reverse=True)
        top_k_entities = [entity for entity, similarity in entities_list[:10]]

        # 去重
        unique_top_k_entities = list({entity.id: entity for entity in top_k_entities}.values())

        return unique_top_k_entities

    def __extract_subgraph_from_graph(self, retrieved_entities, graph, sub_graph_extractor):
        subgraph = sub_graph_extractor.extract_by_entities(retrieved_entities, graph)
        return subgraph

    def __build_context(self, subgraph, context_builder):
        context_str, context_df = context_builder.build_context(subgraph)
        return context_str, context_df

    def Execute(self, search_query, graph):
        json_parser = JsonParser()
        graph_importer = GraphImporter(json_parser)
        graph = graph_importer.import_(graph)
        chat_llm = ChatModel(
            base_url="https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            api_key="2275c4c0-3a6b-44c0-957c-f453b246e4a8",
            model_name="deepseek-v3-241226",
        )
        entities = self.__extract_entities_by_llm(search_query, chat_llm)
        sub_graph_extractor = SubGraphExtractor(graph_level=None)
        ranker = FieldRanker()
        context_builder = GraphContextBuilder(max_context_tokens=8000, ranker=ranker)
        # embeder = LocalModelEmbedding("D:\workplace\\agentdy\\app\common\RAGModuleBase\embedding\model")
        embeder = EmbeddingModel(
            base_url="https://api.rcouyi.com/v1",
            api_key="sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd",
            model_name="text-embedding-3-small"
        )
        # await embeder.wait_for_model_to_load()
        entity_embedding = {}
        for entity in entities:
            embedding = np.array(embeder.generate(entity))
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)

            entity_embedding[entity] = embedding
        retrieved_entities = self.__retrieve(entity_embedding, graph.entities)
        subgraph = self.__extract_subgraph_from_graph(retrieved_entities, graph, sub_graph_extractor)
        context_str, context_df = self.__build_context(subgraph, context_builder)
        return context_str


class GraphContextBuilder():
    def __init__(self, max_context_tokens, ranker):
        self.max_context_tokens = max_context_tokens
        self.ranker = ranker

    def __ranking_data(self, data):
        ranked_data = self.ranker.rank(data)
        return ranked_data

    def __build_entity_context(self, graph):
        current_context_text = f"-----Entities-----" + "\n"
        current_token = 0

        # 添加表头
        header = ["id", "entity_type", "entity_name", "text"]
        current_context_text += "|".join(header) + "\n"
        all_context_records = [header]


        # 依据匹配的实体列表中实体的顺序进行排序
        for id, entity in enumerate(graph.entities):
            attributes = " ".join(
                [f"{k}: {v}" for k, v in remove_unrelated_attributes(entity.attributes).items()])
            new_context = [
                str(id),
                entity.type,
                entity.name,
                attributes
            ]

            new_context_text = "|".join(new_context) + "\n"
            current_context_text += new_context_text
            all_context_records.append(new_context)
            current_token += num_tokens(current_context_text)
            if current_token >= self.max_context_tokens:
                break

        if len(all_context_records) > 1:
            record_df = pd.DataFrame(
                all_context_records[1:], columns=cast(Any, all_context_records[0])
            )
        else:
            record_df = pd.DataFrame()

        return current_context_text, record_df

    def __build_relationship_context(self, graph):
        self.ranker.init_field(lambda x: x.attributes["links"] if "links" in x.attributes else float("inf"))
        graph.relationship_instances = self.__ranking_data(graph.relationship_instances)
        # 添加上下文标题
        current_context_text = f"-----Relationships-----" + "\n"
        current_token = 0

        # 添加表头
        header = ["id", "name", "source", "target", "text"]
        current_context_text += "|".join(header) + "\n"
        all_context_records = [header]

        # 添加关系数据
        for id, relationship in enumerate(graph.relationship_instances):
            source_entity_name = next(
                (entity.name for entity in graph.entities if str(entity.id) == relationship.source),
                None)
            target_entity_name = next(
                (entity.name for entity in graph.entities if str(entity.id) == relationship.target),
                None)
            source_entity = get_entity_information_by_id(graph.entities, relationship.source)
            target_entity = get_entity_information_by_id(graph.entities, relationship.target)
            attributes = f"({source_entity}, {relationship.name}, {target_entity})"
            new_context = [
                str(id),
                relationship.name,
                source_entity_name,
                target_entity_name,
                attributes
            ]

            new_context_text = "|".join(new_context) + "\n"
            current_context_text += new_context_text
            all_context_records.append(new_context)
            current_token += num_tokens(current_context_text)
            if current_token >= self.max_context_tokens:
                break

        if len(all_context_records) > 1:
            record_df = pd.DataFrame(
                all_context_records[1:], columns=cast(Any, all_context_records[0])
            )
        else:
            record_df = pd.DataFrame()

        return current_context_text, record_df

    def __build_community_context(self, graph):
        self.ranker.init_field(lambda x: x.attributes["links"] if "links" in x.attributes else float("inf"))
        graph.community_reports = self.__ranking_data(graph.community_reports)

        def _is_included(report) -> bool:
            return report.rating is not None and float(report.rating) >= 1

        selected_reports = [report for report in graph.community_reports if _is_included(report)]
        if not selected_reports:
            return "", pd.DataFrame()

        current_context_text = f"-----Reports-----\n"
        current_token = 0

        # 添加表头
        header = ["id", "text"]
        current_context_text += "|".join(header) + "\n"
        all_context_records = [header]

        # 构建上下文文本和记录
        for id, report in enumerate(selected_reports):
            new_context = [
                str(id),
                "\n".join([
                    f"社区名称: {json.loads(report.full_content)['title']}",
                    f"社区摘要: {json.loads(report.full_content)['summary']}",
                    *[
                        f"  详细摘要({index + 1}): {finding['summary']}\n 摘要说明({index + 1}): {finding['explanation']}"
                        for index, finding in enumerate(json.loads(report.full_content)["findings"])
                    ]
                ])
            ]
            new_context_text = "|".join(new_context) + "\n"
            current_context_text += new_context_text
            all_context_records.append(new_context)
            current_token += num_tokens(current_context_text)
            if current_token >= self.max_context_tokens:
                break

        if len(all_context_records) > 1:
            record_df = pd.DataFrame(all_context_records[1:], columns=all_context_records[0])
        else:
            record_df = pd.DataFrame()

        return current_context_text, record_df

    def __build_triple_source_context(self, graph):
        if graph.relationship_instances is None or len(graph.relationship_instances ) == 0:
            return ""
        # 添加上下文标题
        current_context_text = f"-----Sources-----" + "\n"
        current_token = 0

        # 添加表头
        header = ["id", "text"]
        current_context_text += "|".join(header) + "\n"
        all_context_records = [header]


        select_triple_sources = set()
        select_triple_sources.update(
            relationship.triple_source
            for relationship in graph.relationship_instances
            if relationship.triple_source
        )

        # 提取每个实体对应的三元组的信息源
        for id, unit in enumerate(select_triple_sources):
            new_context = [
                str(id),
                unit
            ]
            new_context_text = "|".join(new_context) + "\n"

            current_context_text += new_context_text
            all_context_records.append(new_context)
            current_token += num_tokens(current_context_text)
            if current_token >= self.max_context_tokens:
                break

        if len(all_context_records) > 1:
            record_df = pd.DataFrame(
                all_context_records[1:], columns=cast(Any, all_context_records[0])
            )
        else:
            record_df = pd.DataFrame()

        return current_context_text, record_df


    def build_context(self, graph):
        entity_context_str, entity_context_df = self.__build_entity_context(graph)
        relationship_context_str, relationship_context_df = self.__build_relationship_context(graph)
        community_context_str, community_context_df = self.__build_community_context(graph)
        triple_source_context_str, triple_source_context_df = self.__build_triple_source_context(graph)
        context_str = entity_context_str+relationship_context_str+community_context_str+triple_source_context_str
        context_df = {
            "entity": entity_context_df,
            "relationship": relationship_context_df,
            "community": community_context_df,
            "triple_source": triple_source_context_df,
        }
        return context_str, context_df


class SubGraphExtractor():
    def __init__(self, graph_level):
        self.graph_level = graph_level

    def __get_relationship_instances(self, entities, graph):
        # get relationship
        # 第一优先级：网络内关系（即所选实体之间的关系）
        selected_entity_ids = [str(entity.id) for entity in entities]
        for relationship in graph.relationship_instances:
            relationship.attributes = {}
        in_network_relationships = [
            relationship
            for relationship in graph.relationship_instances
            if relationship.source in selected_entity_ids
               and relationship.target in selected_entity_ids
        ]
        # 第二优先级 - 网络外关系（即所选实体与不在所选实体中的其他实体之间的关系）
        source_relationships = [
            relationship
            for relationship in graph.relationship_instances
            if relationship.source in selected_entity_ids
               and relationship.target not in selected_entity_ids
        ]
        target_relationships = [
            relationship
            for relationship in graph.relationship_instances
            if relationship.target in selected_entity_ids
               and relationship.source not in selected_entity_ids
        ]
        out_network_relationships = source_relationships + target_relationships

        # 在网络外关系中，优先考虑相互关系（即与多个选定实体共享的网络外实体的关系）
        out_network_source_ids = [
            relationship.source
            for relationship in out_network_relationships
            if relationship.source not in selected_entity_ids
        ]
        out_network_target_ids = [
            relationship.target
            for relationship in out_network_relationships
            if relationship.target not in selected_entity_ids
        ]
        out_network_entity_ids = list(
            set(out_network_source_ids + out_network_target_ids)
        )
        out_network_entity_links = defaultdict(int)
        for entity_name in out_network_entity_ids:
            targets = [
                relationship.target
                for relationship in out_network_relationships
                if relationship.source == entity_name
            ]
            sources = [
                relationship.source
                for relationship in out_network_relationships
                if relationship.target == entity_name
            ]
            out_network_entity_links[entity_name] = len(set(targets + sources))
        # 按链接数量和rank_attributes对网络外关系进行排序
        for rel in out_network_relationships:
            rel.attributes["links"] = (
                out_network_entity_links[rel.source]
                if rel.source in out_network_entity_links
                else out_network_entity_links[rel.target]
            )
        # 先按 attributes[links] 排序，然后按 ranking_attributes 排序

        # for out_network_relationship in out_network_relationships:
        #     del out_network_relationship.attr
        #       ibutes["links"]
        relationships = in_network_relationships + out_network_relationships
        return relationships

    def __get_community_reports(self, entities, graph):
        community_matches = {}
        for entity in entities:
            # 计算社区所包含选中实体的数量
            if entity.community_ids:
                for community_id in entity.community_ids:
                    community_matches[community_id] = (
                            community_matches.get(community_id, 0) + 1
                    )

        community_reports_id_dict = {
            community.id: community for community in graph.community_reports
        }

        # 防止部分社区没有报告
        select_communities = [
            community_reports_id_dict.get(community_id)
            for community_id in community_matches
            if community_id in community_reports_id_dict
        ]

        for community in select_communities:
            if community.attributes is None:
                community.attributes = {}
            community.attributes["matches"] = community_matches[community.id]
        for community in select_communities:
            community.level = int(community.level)
        if self.graph_level != None:
            temp_communities = []
            for community in select_communities:
                if community.level == self.graph_level:
                    temp_communities.append(community)
            return temp_communities
        return select_communities

    def __get_out_graph_entities(self,in_graph_entities, graph):

        mapped_entities_id = [entity.id for entity in in_graph_entities]
        out_network_entities = set()
        for mapped_entity in in_graph_entities:
            for relationship in graph.relationship_instances:
                if relationship.source == mapped_entity.id and relationship.target not in mapped_entities_id:
                    out_network_entities.add(relationship.target)
                if relationship.target == mapped_entity.id and relationship.source not in mapped_entities_id:
                    out_network_entities.add(relationship.source)
        return [entity for entity in graph.entities if entity.id in out_network_entities]


    def extract_by_entities(self, entities, graph):
        out_entities = self.__get_out_graph_entities(entities, graph)
        relationship_instances = self.__get_relationship_instances(entities, graph)
        community_reports = self.__get_community_reports(entities, graph)
        subgraph = Graph(entities=entities+out_entities, relationship_instances=relationship_instances, community_reports=community_reports)
        return subgraph


# if __name__ == "__main__":
#     json_parser = JsonParser()
#     graph_importer = GraphImporter(json_parser)
#     index_path = r"D:\PycharmProjects\sapperrag_re\sapperrag\index.json"
#     graph = graph_importer.import_(index_path)
#     query = "介绍一下ping,也介绍一下吴贻顺？"
#     retriever = GraphDataRetriever()
#     context = retriever.Execute(query, graph)
#     print(context)

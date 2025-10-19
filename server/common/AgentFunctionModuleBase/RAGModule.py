import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.conf import admin_settings

from sapperrag.embedding import LocalModelEmbedding


class DataViewDefiner:
    def __init__(self, StorageLoc, DataLoader):
        self.StorageLoc = StorageLoc
        self.DataLoader = DataLoader

    # def def_data(self, def_name, db_data):
    #     self.StorageLoc[def_name] = db_data

    def def_data(self, def_name, db_data):
        # 分开存储 text_blocks 和图数据
        self.StorageLoc[def_name] = db_data


class DBGetter:
    def __init__(self, data_base):
        self.Database = data_base

    def GetDB(self, FilePath):
        # DB = self.Database[FilePath]
        # 根据FileName在数据库中找到对应的relationDB和VectorDB
        # 这里按道理来说应该是上传文件名，然后从数据库中找到对应的文件名
        return None


class DataRetriever:
    def __init__(self):
        pass

    @staticmethod
    async def Execute(search_query, db_data):
        embeder = LocalModelEmbedding(admin_settings.EMBEDDING_MODEL_PATH)
        await embeder.wait_for_model_to_load()
        query_embed = embeder.embed(search_query)
        query_vector = np.array(query_embed, dtype=np.float32).reshape(1, -1)
        for emb in db_data:
            stored_emb = np.array(emb.embedding, dtype=np.float32).reshape(1, -1)
            emb.similarity = cosine_similarity(query_vector, stored_emb)[0][0]
        sorted_embeddings = sorted(db_data, key=lambda x: x.similarity, reverse=True)
        result = ""
        for emb in sorted_embeddings[:15]:
            result += emb.content
        return result

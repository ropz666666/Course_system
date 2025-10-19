import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ....common.RAGModuleBase.embedding import get_sentence_embedding
from app import get_shared_state

model_state = get_shared_state()


async def query_embedding(query, embeddings):
    query_emb = await get_sentence_embedding(query, model_state.embedding_model)
    for emb in embeddings:
        stored_emb = np.frombuffer(emb.embedding, dtype=np.float32).reshape(1, -1)
        emb.similarity = cosine_similarity(query_emb, stored_emb)[0][0]
    sorted_embeddings = sorted(embeddings, key=lambda x: x.similarity, reverse=True)
    return sorted_embeddings

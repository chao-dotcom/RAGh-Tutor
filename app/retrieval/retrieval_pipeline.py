"""Retrieval pipeline orchestrator"""
import logging
from typing import List, Tuple, Optional
import time

from app.retrieval.vector_store import InMemoryVectorStore
from app.retrieval.hybrid_search import HybridSearchStore
from app.retrieval.reranker import Reranker
from app.retrieval.query_expansion import QueryExpander
from app.embedding.embedding_model import EmbeddingModel
from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """Complete retrieval pipeline with reranking"""
    
    def __init__(
        self,
        vector_store: InMemoryVectorStore,
        embedding_model: EmbeddingModel,
        reranker: Optional[Reranker] = None,
        query_expander: Optional[QueryExpander] = None,
        use_hybrid: bool = False
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.reranker = reranker
        self.query_expander = query_expander
        self.hybrid_store = None
        
        if use_hybrid:
            self.hybrid_store = HybridSearchStore(vector_store)
            self.hybrid_store.build_bm25_index()
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        rerank: bool = True,
        expand_query: bool = False
    ) -> Tuple[List[Tuple[Chunk, float]], float]:
        """Retrieve relevant chunks for query"""
        start_time = time.time()
        
        # Expand query if requested
        if expand_query and self.query_expander:
            queries = await self.query_expander.expand_with_llm(query)
        else:
            queries = [query]
        
        # Retrieve for all query variations
        all_candidates = []
        
        for q in queries:
            # Generate embedding
            query_embedding = await self.embedding_model.encode_async([q])
            query_embedding = query_embedding[0]
            
            # Search
            if self.hybrid_store:
                candidates = self.hybrid_store.hybrid_search(
                    q,
                    query_embedding,
                    top_k=top_k * 2  # Get more for reranking
                )
            else:
                candidates = self.vector_store.search(
                    query_embedding,
                    top_k=top_k * 2
                )
            
            all_candidates.extend(candidates)
        
        # Deduplicate
        seen = set()
        unique_candidates = []
        for chunk, score in all_candidates:
            if chunk.chunk_id not in seen:
                seen.add(chunk.chunk_id)
                unique_candidates.append((chunk, score))
        
        # Rerank if requested
        if rerank and self.reranker:
            results = await self.reranker.rerank(
                query,
                unique_candidates,
                top_k=top_k
            )
        else:
            results = sorted(
                unique_candidates,
                key=lambda x: x[1],
                reverse=True
            )[:top_k]
        
        retrieval_time = time.time() - start_time
        return results, retrieval_time
    
    async def retrieve_by_document(
        self,
        query: str,
        doc_ids: List[str],
        top_k: int = 5
    ) -> List[Tuple[Chunk, float]]:
        """Retrieve chunks only from specific documents"""
        # Get all candidates
        candidates, _ = await self.retrieve(query, top_k=top_k * 3, rerank=False)
        
        # Filter by document
        filtered = [
            (chunk, score)
            for chunk, score in candidates
            if chunk.doc_id in doc_ids
        ]
        
        # Rerank filtered results
        if self.reranker and filtered:
            filtered = await self.reranker.rerank(query, filtered, top_k=top_k)
        
        return filtered[:top_k]


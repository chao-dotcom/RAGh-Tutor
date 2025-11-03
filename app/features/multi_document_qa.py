"""Multi-document QA"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class MultiDocumentQA:
    """Answer questions requiring multiple documents"""
    
    def __init__(
        self,
        retrieval_pipeline,
        llm_client
    ):
        self.retrieval = retrieval_pipeline
        self.llm = llm_client
    
    async def answer_with_cross_document_reasoning(
        self,
        query: str,
        top_k_docs: int = 5
    ) -> Dict[str, Any]:
        """Answer query using multiple documents"""
        
        # Retrieve chunks
        chunks, _ = await self.retrieval.retrieve(
            query,
            top_k=top_k_docs * 3,  # Get more chunks
            rerank=True
        )
        
        # Group by document
        doc_groups = self._group_by_document(chunks, top_k_per_doc=3)
        
        # Build multi-document prompt
        from app.generation.prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_multi_document_prompt(query, doc_groups)
        
        # Generate synthesis
        response = await self.llm.generate(
            prompt,
            system="You are an expert at synthesizing information from multiple sources. When sources disagree, acknowledge the disagreement."
        )
        
        # Extract document usage
        documents_used = list(doc_groups.keys())
        
        return {
            'synthesized_answer': response,
            'documents_used': documents_used,
            'num_sources': len(documents_used),
            'citations': self._extract_citations(response, chunks)
        }
    
    def _group_by_document(
        self,
        chunks: List[Tuple[Any, float]],
        top_k_per_doc: int = 3
    ) -> Dict[str, List[Tuple[Any, float]]]:
        """Group chunks by source document"""
        doc_groups = defaultdict(list)
        
        for chunk, score in chunks:
            doc_id = chunk.doc_id
            if len(doc_groups[doc_id]) < top_k_per_doc:
                doc_groups[doc_id].append((chunk, score))
        
        return dict(doc_groups)
    
    def _extract_citations(self, text: str, chunks: List[Tuple[Any, float]]) -> Dict:
        """Extract citations from response"""
        from app.generation.citation_tracker import CitationTracker
        tracker = CitationTracker()
        return tracker.format_citations(text, [chunk for chunk, _ in chunks])
    
    async def compare_documents(
        self,
        query: str,
        doc_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare information across specific documents"""
        
        # Retrieve from each document
        doc_contents = {}
        for doc_id in doc_ids:
            chunks, _ = await self.retrieval.retrieve_by_document(
                query,
                doc_ids=[doc_id],
                top_k=3
            )
            doc_contents[doc_id] = chunks
        
        # Build comparison prompt
        prompt = self._build_comparison_prompt(query, doc_contents)
        
        # Generate comparison
        response = await self.llm.generate(prompt)
        
        return {
            'comparison': response,
            'documents_compared': doc_ids,
            'doc_contents': {
                doc_id: [chunk.content for chunk, _ in chunks]
                for doc_id, chunks in doc_contents.items()
            }
        }
    
    def _build_comparison_prompt(
        self,
        query: str,
        doc_contents: Dict[str, List[Tuple[Any, float]]]
    ) -> str:
        """Build prompt for document comparison"""
        parts = [
            "Compare how different documents address this query:",
            f"Query: {query}",
            ""
        ]
        
        for doc_id, chunks in doc_contents.items():
            parts.append(f"## Document: {doc_id}")
            for chunk, score in chunks:
                parts.append(chunk.content)
            parts.append("")
        
        parts.extend([
            "## Instructions",
            "1. Identify common themes across documents",
            "2. Note any contradictions or differences",
            "3. Highlight unique insights from each document",
            "4. Provide a synthesized answer",
            "",
            "## Comparison"
        ])
        
        return "\n".join(parts)

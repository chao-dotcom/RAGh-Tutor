"""Performance benchmark tests"""
import pytest
import time
import asyncio
from statistics import mean, median


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_retrieval_performance():
    """Benchmark retrieval speed"""
    from app.main import app_state
    
    retrieval_pipeline = app_state['retrieval_pipeline']
    
    queries = [
        "What is machine learning?",
        "Explain neural networks",
        "How does backpropagation work?",
        "What is gradient descent?",
        "Explain transformers"
    ]
    
    latencies = []
    
    for query in queries:
        start = time.time()
        results = await retrieval_pipeline.retrieve(query, top_k=5)
        latency = time.time() - start
        latencies.append(latency)
        
        assert len(results) == 5
    
    avg_latency = mean(latencies)
    median_latency = median(latencies)
    
    print(f"\nRetrieval Performance:")
    print(f"Average latency: {avg_latency*1000:.2f}ms")
    print(f"Median latency: {median_latency*1000:.2f}ms")
    print(f"Max latency: {max(latencies)*1000:.2f}ms")
    
    # Assert reasonable performance
    assert avg_latency < 1.0  # Should be under 1 second


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_generation_performance():
    """Benchmark LLM generation speed"""
    from app.main import app_state
    
    llm_client = app_state['llm_client']
    
    prompts = [
        "Explain this in one sentence: Machine learning is a subset of AI.",
        "Summarize: Neural networks are computational models.",
        "Answer briefly: What is deep learning?"
    ]
    
    latencies = []
    tokens_per_second = []
    
    for prompt in prompts:
        start = time.time()
        response = await llm_client.generate(prompt, max_tokens=100)
        latency = time.time() - start
        latencies.append(latency)
        
        # Estimate tokens (rough approximation)
        tokens = len(response.split()) * 1.3
        tokens_per_second.append(tokens / latency)
    
    print(f"\nGeneration Performance:")
    print(f"Average latency: {mean(latencies)*1000:.2f}ms")
    print(f"Average tokens/sec: {mean(tokens_per_second):.2f}")
    
    assert mean(latencies) < 5.0  # Should be under 5 seconds


@pytest.mark.benchmark
def test_embedding_performance():
    """Benchmark embedding generation speed"""
    from app.main import app_state
    
    embedding_model = app_state['embedding_model']
    
    # Test various batch sizes
    texts = ["Test sentence"] * 100
    
    batch_sizes = [1, 10, 32, 64]
    results = {}
    
    for batch_size in batch_sizes:
        start = time.time()
        embeddings = embedding_model.encode(texts, batch_size=batch_size)
        latency = time.time() - start
        
        throughput = len(texts) / latency
        results[batch_size] = {
            'latency': latency,
            'throughput': throughput
        }
    
    print(f"\nEmbedding Performance:")
    for batch_size, metrics in results.items():
        print(f"Batch size {batch_size}: {metrics['throughput']:.2f} texts/sec")
    
    # Larger batch sizes should be faster
    assert results[32]['throughput'] > results[1]['throughput']


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_concurrent_queries():
    """Test performance under concurrent load"""
    from app.main import app_state
    
    retrieval_pipeline = app_state['retrieval_pipeline']
    llm_client = app_state['llm_client']
    
    async def single_query(query: str):
        start = time.time()
        chunks = await retrieval_pipeline.retrieve(query, top_k=5)
        
        from app.generation.prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_rag_prompt(query, chunks)
        
        response = await llm_client.generate(prompt)
        return time.time() - start
    
    # Test with 10 concurrent queries
    queries = [f"Test query {i}" for i in range(10)]
    
    start = time.time()
    latencies = await asyncio.gather(*[single_query(q) for q in queries])
    total_time = time.time() - start
    
    print(f"\nConcurrent Query Performance:")
    print(f"10 queries completed in: {total_time:.2f}s")
    print(f"Average per query: {mean(latencies):.2f}s")
    print(f"Queries per second: {len(queries)/total_time:.2f}")
    
    # Should handle concurrent load reasonably
    assert total_time < 30.0  # 10 queries under 30 seconds


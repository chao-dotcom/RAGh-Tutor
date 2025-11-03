"""Process items in batches for efficiency"""
from typing import List, Callable, Any, TypeVar, Generic
import asyncio
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')
R = TypeVar('R')


class BatchProcessor(Generic[T, R]):
    """Process items in batches for efficiency"""
    
    def __init__(
        self,
        batch_size: int = 32,
        max_workers: int = 4
    ):
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(
        self,
        items: List[T],
        process_func: Callable[[List[T]], List[R]]
    ) -> List[R]:
        """Process items in batches"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await self._process_single_batch(batch, process_func)
            results.extend(batch_results)
        
        return results
    
    async def _process_single_batch(
        self,
        batch: List[T],
        process_func: Callable[[List[T]], List[R]]
    ) -> List[R]:
        """Process a single batch"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            process_func,
            batch
        )
    
    async def process_concurrent(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        max_concurrent: int = 10
    ) -> List[R]:
        """Process items concurrently with limit"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(item: T) -> R:
            async with semaphore:
                if asyncio.iscoroutinefunction(process_func):
                    return await process_func(item)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        self.executor,
                        process_func,
                        item
                    )
        
        tasks = [process_with_semaphore(item) for item in items]
        return await asyncio.gather(*tasks)


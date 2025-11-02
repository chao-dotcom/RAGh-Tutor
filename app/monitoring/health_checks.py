"""Comprehensive health checks"""
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """Comprehensive health checks"""
    
    def __init__(self, app_state: Dict[str, Any]):
        self.app_state = app_state
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            'vector_store': await self._check_vector_store(),
            'llm': await self._check_llm(),
            'embedding_model': await self._check_embedding_model(),
            'memory': self._check_memory(),
            'disk': self._check_disk()
        }
        
        overall_healthy = all(check['healthy'] for check in checks.values())
        
        return {
            'healthy': overall_healthy,
            'checks': checks
        }
    
    async def _check_vector_store(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            vector_store = self.app_state['vector_store']
            size = vector_store.size
            
            return {
                'healthy': size > 0,
                'message': f'Vector store has {size} chunks',
                'size': size
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Vector store error: {str(e)}'
            }
    
    async def _check_llm(self) -> Dict[str, Any]:
        """Check LLM connectivity"""
        try:
            llm_client = self.app_state['llm_client']
            
            # Try a simple generation
            response = await asyncio.wait_for(
                llm_client.generate("Say 'OK'", max_tokens=10),
                timeout=10.0
            )
            
            return {
                'healthy': True,
                'message': 'LLM responding normally'
            }
        except asyncio.TimeoutError:
            return {
                'healthy': False,
                'message': 'LLM timeout'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'LLM error: {str(e)}'
            }
    
    async def _check_embedding_model(self) -> Dict[str, Any]:
        """Check embedding model"""
        try:
            embedding_model = self.app_state['embedding_model']
            
            # Try encoding a test string
            embedding = embedding_model.encode("test")
            
            return {
                'healthy': len(embedding) == embedding_model.dimension,
                'message': 'Embedding model working'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Embedding model error: {str(e)}'
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            return {
                'healthy': percent_used < 90,
                'message': f'Memory usage: {percent_used}%',
                'percent_used': percent_used
            }
        except ImportError:
            return {
                'healthy': True,
                'message': 'psutil not available, skipping memory check'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Memory check error: {str(e)}'
            }
    
    def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            percent_used = disk.percent
            
            return {
                'healthy': percent_used < 90,
                'message': f'Disk usage: {percent_used}%',
                'percent_used': percent_used
            }
        except ImportError:
            return {
                'healthy': True,
                'message': 'psutil not available, skipping disk check'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Disk check error: {str(e)}'
            }


# Backward compatibility functions
async def check_vector_store(vector_store) -> bool:
    """Check if vector store is healthy (backward compatibility)"""
    return vector_store.index is not None and vector_store.size >= 0

async def check_embedding_model(embedding_model) -> bool:
    """Check if embedding model is healthy (backward compatibility)"""
    return embedding_model.model is not None

async def check_llm_client(llm_client) -> bool:
    """Check if LLM client is healthy (backward compatibility)"""
    return llm_client.client is not None


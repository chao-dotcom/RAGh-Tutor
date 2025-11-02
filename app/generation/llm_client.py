"""LLM client for various providers"""
import logging
from typing import Optional, AsyncIterator, Dict, Any, List
import os

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Universal LLM client supporting multiple providers"""
    
    def __init__(
        self,
        provider: str = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        self.provider = provider or settings.LLM_PROVIDER
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self._initialize_client(model, api_key)
    
    def _initialize_client(self, model: str = None, api_key: str = None):
        """Initialize LLM client based on provider"""
        if self.provider == "anthropic":
            self.model = model or settings.ANTHROPIC_MODEL
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=api_key or settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY"))
            except ImportError:
                logger.error("anthropic package required. Install with: pip install anthropic")
                raise
        elif self.provider == "openai":
            self.model = model or settings.OPENAI_MODEL
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
            except ImportError:
                logger.error("openai package required. Install with: pip install openai")
                raise
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate completion (non-streaming)"""
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tok,
                temperature=temp,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
                stop_sequences=stop_sequences
            )
            return response.content[0].text
        
        elif self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stop=stop_sequences
            )
            return response.choices[0].message.content
    
    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """Generate completion with streaming"""
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "anthropic":
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tok,
                temperature=temp,
                system=system or "",
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        
        elif self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
    
    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate with tool calling support"""
        if self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
                tools=tools
            )
            return response
        
        elif self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            return response


"""Transcribe audio files to text"""
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Transcribe audio files to text"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self.device = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Whisper model"""
        try:
            import whisper
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = whisper.load_model(self.model_size).to(self.device)
        except ImportError:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            self.model = None
    
    async def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file"""
        if not self.model:
            raise RuntimeError("Whisper model not initialized")
        
        result = self.model.transcribe(
            audio_path,
            language="en",
            fp16=False
        )
        
        return {
            "text": result["text"],
            "language": result.get("language", "en"),
            "duration": result.get("duration"),
            "segments": result.get("segments", [])
        }
    
    async def transcribe_with_timestamps(self, audio_path: str) -> List[dict]:
        """Transcribe with word-level timestamps"""
        if not self.model:
            raise RuntimeError("Whisper model not initialized")
        
        result = self.model.transcribe(
            audio_path,
            word_timestamps=True
        )
        
        return result.get("segments", [])


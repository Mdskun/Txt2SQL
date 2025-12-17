"""
Configuration management for Txt2SQL.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            model_path: Path to the T5 model directory (from env or parameter)
        """
        # Only model path comes from environment
        self.model_path = model_path or os.getenv("WIKISQL_MODEL")
        
        # Model settings - fixed defaults
        self.max_length = 128
        self.num_beams = 2
        self.torch_threads = 2
        
        # Validate model path
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration values."""
        if not self.model_path:
            raise ValueError(
                "Model path not configured. Set WIKISQL_MODEL environment variable "
                "or pass model_path parameter."
            )
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at: {self.model_path}")
    
    def __repr__(self) -> str:
        return f"Config(model_path='{self.model_path}')"
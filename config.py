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
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        db_path: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize configuration.
        
        Args:
            model_path: Path to the T5 model directory
            db_path: Path to SQLite database file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.model_path = model_path or os.getenv("WIKISQL_MODEL")
        self.db_path = db_path or os.getenv("DB_PATH", "mydb.db")
        self.log_level = os.getenv("LOG_LEVEL", log_level)
        
        # Model settings
        self.max_length = int(os.getenv("MAX_SQL_LENGTH", "128"))
        self.num_beams = int(os.getenv("NUM_BEAMS", "2"))
        self.torch_threads = int(os.getenv("TORCH_THREADS", "2"))
        
        # Validate configuration
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
        
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found at: {self.db_path}")
    
    def __repr__(self) -> str:
        return (
            f"Config(model_path='{self.model_path}', "
            f"db_path='{self.db_path}', "
            f"log_level='{self.log_level}')"
        )
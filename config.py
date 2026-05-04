"""
Configuration management for Txt2SQL.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Config:
    """
    Application configuration.

    Model path is read from the WIKISQL_MODEL environment variable (or passed
    directly).  Validation is *lazy* — it only runs when you call validate(),
    so a missing/wrong path won't crash the process before the CLI has a
    chance to show a helpful error message.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            model_path: Path to the T5 model directory.
                        Falls back to the WIKISQL_MODEL environment variable.
        """
        self.model_path: Optional[str] = model_path or os.getenv("WIKISQL_MODEL")

        # Model generation settings — sensible fixed defaults
        self.max_length: int = 128
        self.num_beams: int = 2
        self.torch_threads: int = 2

    # ------------------------------------------------------------------
    # Validation (called explicitly so the CLI controls when it fires)
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If model_path is not set.
            FileNotFoundError: If the model directory does not exist.
        """
        if not self.model_path:
            raise ValueError(
                "Model path not configured.\n"
                "  • Set the WIKISQL_MODEL environment variable, or\n"
                "  • Pass model_path= when constructing Config."
            )

        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model directory not found: {self.model_path}\n"
                "Check that WIKISQL_MODEL points to a valid model directory."
            )

    def __repr__(self) -> str:
        return f"Config(model_path={self.model_path!r})"

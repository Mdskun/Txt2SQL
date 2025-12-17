"""
SQL generation using T5 transformer model.
"""
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

class SQLGenerator:
    """
    Generates SQL queries from natural language using T5 model.
    """
    
    def __init__(
        self,
        model_path: str,
        max_length: int = 128,
        num_beams: int = 3,
        torch_threads: int = 2
    ):
        """
        Initialize SQL generator.
        
        Args:
            model_path: Path to the T5 model directory
            max_length: Maximum length of generated SQL
            num_beams: Number of beams for beam search(removed because of issues)
            torch_threads: Number of torch CPU threads
        """
        self.model_path = model_path
        self.max_length = max_length
        self.num_beams = num_beams
        
        # Configure torch for CPU efficiency
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        torch.set_num_threads(torch_threads)
        
        logger.info(f"Loading model from: {model_path}")
        self._load_model()
        logger.info("Model loaded successfully")
    
    def _load_model(self) -> None:
        """Load the T5 model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            self.model.eval()  # Set to evaluation mode
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def generate_sql(
        self,
        question: str,
        schema: str,
        return_confidence: bool = False
    ) -> str:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: Natural language question
            schema: Database schema information
            return_confidence: Whether to return confidence score (not implemented)
        
        Returns:
            Generated SQL query string
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Prepare input
        input_text = f"translate to SQL: {question.strip()} | {schema}"
        try:
            # Tokenize
            inputs = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Generate SQL
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=self.max_length,
                    num_beams=self.num_beams,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.2
                )
            
            # Decode
            sql = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Basic validation
            sql = sql.strip()
            sql = sql.split('|', 1)[0]
            if not sql:
                raise ValueError("Model generated empty SQL")
            
            logger.debug(f"Generated SQL: {sql[0]}")
            return sql
        
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise RuntimeError(f"Failed to generate SQL: {e}")
    
    def batch_generate(self, questions: list, schema: str) -> list:
        """
        Generate SQL for multiple questions.
        
        Args:
            questions: List of natural language questions
            schema: Database schema information
        
        Returns:
            List of generated SQL queries
        """
        results = []
        for question in questions:
            try:
                sql = self.generate_sql(question, schema)
                results.append(sql)
            except Exception as e:
                logger.error(f"Failed to generate SQL for '{question}': {e}")
                results.append(None)
        return results
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        logger.debug("SQL generator cleaned up")
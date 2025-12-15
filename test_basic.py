"""
Basic tests for Txt2SQL.

Run with: pytest test_basic.py
"""
import pytest
import sqlite3
import tempfile
from pathlib import Path

from database import DatabaseManager
from utils import validate_sql, format_results, truncate_text


class TestDatabaseManager:
    """Test database operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary test database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # Create test schema
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        conn.execute("""
            INSERT INTO users (name, email) VALUES 
            ('Alice', 'alice@example.com'),
            ('Bob', 'bob@example.com')
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink()
    
    def test_database_initialization(self, temp_db):
        """Test database manager initialization."""
        db_manager = DatabaseManager(temp_db)
        assert db_manager.db_path == temp_db
    
    def test_get_schema(self, temp_db):
        """Test schema extraction."""
        db_manager = DatabaseManager(temp_db)
        schema = db_manager.get_schema()
        
        assert "users" in schema
        assert "id" in schema
        assert "name" in schema
        assert "email" in schema
    
    def test_get_tables(self, temp_db):
        """Test table listing."""
        db_manager = DatabaseManager(temp_db)
        tables = db_manager.get_tables()
        
        assert "users" in tables
        assert len(tables) == 1
    
    def test_execute_select_query(self, temp_db):
        """Test SELECT query execution."""
        db_manager = DatabaseManager(temp_db)
        success, results = db_manager.execute_query("SELECT * FROM users")
        
        assert success is True
        assert "rows" in results
        assert len(results["rows"]) == 2
    
    def test_execute_invalid_query(self, temp_db):
        """Test invalid query handling."""
        db_manager = DatabaseManager(temp_db)
        success, results = db_manager.execute_query("INVALID SQL")
        
        assert success is False
        assert "Error" in results


class TestUtils:
    """Test utility functions."""
    
    def test_validate_sql_valid(self):
        """Test SQL validation with valid queries."""
        assert validate_sql("SELECT * FROM users") is True
        assert validate_sql("INSERT INTO users VALUES (1, 'test')") is True
        assert validate_sql("UPDATE users SET name='test'") is True
    
    def test_validate_sql_invalid(self):
        """Test SQL validation with invalid queries."""
        assert validate_sql("") is False
        assert validate_sql("   ") is False
        assert validate_sql("RANDOM TEXT") is False
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "a" * 150
        truncated = truncate_text(text, 100)
        
        assert len(truncated) == 100
        assert truncated.endswith("...")
    
    def test_truncate_text_short(self):
        """Test truncation of short text."""
        text = "short text"
        truncated = truncate_text(text, 100)
        
        assert truncated == text


class TestConfig:
    """Test configuration management."""
    
    def test_config_validation(self):
        """Test config validation."""
        from config import Config
        
        # Should raise error without model path
        with pytest.raises(ValueError):
            Config(model_path=None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
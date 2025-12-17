"""
Database operations for Txt2SQL.
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._validate_database()
        self._schema_cache = None
    
    def _validate_database(self) -> None:
        """Validate that database file exists and is accessible."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Test connection
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            raise RuntimeError(f"Cannot connect to database: {e}")
    
    def get_schema(self, force_refresh: bool = False) -> str:
        """
        Get database schema information.
        
        Args:
            force_refresh: Force refresh of cached schema
        
        Returns:
            Formatted schema string
        """
        if self._schema_cache and not force_refresh:
            return self._schema_cache
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                schema_info = []
                
                # Get all tables
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "ORDER BY name;"
                )
                tables = cursor.fetchall()
                
                if not tables:
                    logger.warning("No tables found in database")
                    return "Database schema: No tables found"
                
                # Get columns for each table
                for table_name, in tables:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    col_names = [col[1] for col in columns]
                    schema_info.append(f"{table_name}({', '.join(col_names)})")
                
                self._schema_cache = "Database schema:\n" + "\n".join(schema_info)
                logger.info(f"Loaded schema with {len(tables)} tables")
                return self._schema_cache
        
        except Exception as e:
            logger.error(f"Error reading schema: {e}")
            raise RuntimeError(f"Failed to read database schema: {e}")
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """
        Execute SQL query on the database.
        
        Args:
            query: SQL query string
        
        Returns:
            Tuple of (success: bool, results: List or error message)
        """
        query = query.strip()
        
        if not query:
            return False, "Empty query"
        
        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Potentially dangerous query detected: {keyword}")
                confirm = input(
                    f"\n⚠️  WARNING: Query contains {keyword}. "
                    f"Execute anyway? (yes/no): "
                )
                if confirm.lower() != "yes":
                    return False, "Query execution cancelled by user"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Check if query returns results
                if query_upper.startswith("SELECT"):
                    results = cursor.fetchall()
                    
                    if not results:
                        return True, "Query executed successfully (0 rows returned)"
                    
                    # Get column names
                    col_names = [description[0] for description in cursor.description]
                    return True, {"columns": col_names, "rows": results}
                else:
                    # For INSERT, UPDATE, DELETE
                    conn.commit()
                    rows_affected = cursor.rowcount
                    return True, f"Query executed successfully ({rows_affected} rows affected)"
        
        except sqlite3.Error as e:
            logger.error(f"SQL execution error: {e}")
            return False, f"SQL Error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Error: {e}"
    
    def get_tables(self) -> List[str]:
        """
        Get list of all table names in database.
        
        Returns:
            List of table names
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "ORDER BY name;"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching tables: {e}")
            return []
    
    def close(self) -> None:
        """Cleanup resources."""
        self._schema_cache = None
        logger.debug("Database manager closed")
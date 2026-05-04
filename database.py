"""
Database operations for Txt2SQL.
"""
import re
import sqlite3
import logging
from pathlib import Path
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers for safe query analysis
# ---------------------------------------------------------------------------

# Tokenise only real SQL keywords, not substrings inside identifiers/strings.
# Matches whole words at token boundaries so "DELETE_LOG" won't trigger DELETE.
_DANGEROUS_PATTERN = re.compile(
    r"\b(DROP|DELETE|TRUNCATE|ALTER)\b",
    re.IGNORECASE,
)

# Simple pattern to strip single-quoted strings and -- line comments before
# keyword scanning, reducing false positives from string literals.
_STRIP_STRINGS   = re.compile(r"'[^']*'")
_STRIP_COMMENTS  = re.compile(r"--[^\n]*")


def _find_dangerous_keywords(query: str) -> List[str]:
    """
    Return any dangerous DML/DDL keywords found in *query*.

    Strips string literals and line comments first so that content such as
    ``SELECT * FROM log WHERE msg = 'DROP TABLE'`` does not trigger a warning.
    """
    cleaned = _STRIP_STRINGS.sub("''", query)
    cleaned = _STRIP_COMMENTS.sub("", cleaned)
    return list({m.group(1).upper() for m in _DANGEROUS_PATTERN.finditer(cleaned)})


def _is_safe_identifier(name: str) -> bool:
    """
    Return True if *name* is a safe SQLite identifier.

    Allows only characters that SQLite itself permits in unquoted names.
    This is used to guard against injection via table names sourced from
    sqlite_master.
    """
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]*", name))


# ---------------------------------------------------------------------------
# DatabaseManager
# ---------------------------------------------------------------------------

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
        self._schema_cache: str | None = None

    def _validate_database(self) -> None:
        """Validate that database file exists and is accessible."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

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

                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
                )
                tables = cursor.fetchall()

                if not tables:
                    logger.warning("No tables found in database")
                    return "Database schema: No tables found"

                schema_info = []
                for (table_name,) in tables:
                    # FIX: Use parameterised PRAGMA to guard against injected
                    # table names (e.g. a table whose name contains SQL).
                    # SQLite's PRAGMA doesn't support ? placeholders, so we
                    # validate the name against a safe-identifier whitelist instead.
                    if not _is_safe_identifier(table_name):
                        logger.warning(f"Skipping table with unsafe name: {table_name!r}")
                        continue

                    cursor.execute(f'PRAGMA table_info("{table_name}");')
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

        Dangerous DML/DDL operations (DROP, DELETE, TRUNCATE, ALTER) are
        detected via whole-word regex matching rather than a plain substring
        search, so identifiers like ``DELETE_LOG`` no longer trigger a false
        warning.

        Args:
            query: SQL query string

        Returns:
            Tuple of (success: bool, results: dict | str)
        """
        query = query.strip()

        if not query:
            return False, "Empty query"

        # FIX: replaced naive `keyword in query_upper` substring check with
        # whole-word regex that ignores keywords inside string literals.
        dangerous = _find_dangerous_keywords(query)
        if dangerous:
            keyword_list = ", ".join(dangerous)
            logger.warning(f"Potentially dangerous keywords detected: {keyword_list}")
            confirm = input(
                f"\n⚠️  WARNING: Query contains {keyword_list}. "
                f"Execute anyway? (yes/no): "
            )
            if confirm.strip().lower() != "yes":
                return False, "Query execution cancelled by user"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if query.upper().lstrip().startswith("SELECT"):
                    results = cursor.fetchall()

                    if not results:
                        return True, "Query executed successfully (0 rows returned)"

                    col_names = [d[0] for d in cursor.description]
                    return True, {"columns": col_names, "rows": results}
                else:
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
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching tables: {e}")
            return []

    def close(self) -> None:
        """Cleanup resources."""
        self._schema_cache = None
        logger.debug("Database manager closed")

"""
Utility functions for Txt2SQL.
"""
import logging
import sys
import os
from typing import Any, Union, Dict, List


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity of transformers library
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)


def format_results(results: Any) -> str:
    """
    Format query results for display.
    
    Args:
        results: Query results (string, dict, or list)
    
    Returns:
        Formatted string for display
    """
    if isinstance(results, str):
        return f"{Colors.GREEN}✓ {results}{Colors.RESET}\n"
    
    if isinstance(results, dict) and "columns" in results and "rows" in results:
        return format_table(results["columns"], results["rows"])
    
    return f"{Colors.GREEN}✓ {results}{Colors.RESET}\n"


def format_table(columns: List[str], rows: List[tuple]) -> str:
    """
    Format query results as a table.
    
    Args:
        columns: Column names
        rows: Row data
    
    Returns:
        Formatted table string
    """
    if not rows:
        return f"{Colors.YELLOW}No rows returned{Colors.RESET}\n"
    
    # Calculate column widths
    col_widths = [len(str(col)) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # Add padding
    col_widths = [w + 2 for w in col_widths]
    
    # Build table
    output = []
    
    # Header
    header = "│".join(
        f" {str(col).ljust(w-1)}" for col, w in zip(columns, col_widths)
    )
    separator = "─".join("─" * w for w in col_widths)
    
    output.append(f"{Colors.BOLD}{header}{Colors.RESET}")
    output.append(separator)
    
    # Rows
    for row in rows:
        row_str = "│".join(
            f" {str(val).ljust(w-1)}" for val, w in zip(row, col_widths)
        )
        output.append(row_str)
    
    output.append("")
    output.append(f"{Colors.CYAN}({len(rows)} row{'s' if len(rows) != 1 else ''}){Colors.RESET}\n")
    
    return "\n".join(output)


def validate_sql(sql: str) -> bool:
    logging.debug(f"Validating SQL: {sql}")
    """
    Basic SQL validation.
    
    Args:
        sql: SQL query string
    
    Returns:
        True if SQL appears valid
    """
    if not sql or not sql.strip():
        return False
    
    sql_upper = sql.upper().strip()
    
    # Check for basic SQL keywords
    valid_starts = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"]
    
    return any(sql_upper.startswith(keyword) for keyword in valid_starts)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
"""
Command-line interface for Txt2SQL.
"""
import sys
import argparse
import logging
from typing import Optional
from pathlib import Path

from config import Config
from database import DatabaseManager
from generator import SQLGenerator
from utils import setup_logging, format_results, Colors


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert natural language to SQL queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python txt2sql.py
  
  # Single query
  python txt2sql.py --query "show all customers"
  
  # Custom database
  python txt2sql.py --database /path/to/db.sqlite
  
  # Verbose output
  python txt2sql.py --verbose
        """
    )
    
    parser.add_argument(
        "-d", "--database",
        help="Path to SQLite database file",
        type=str
    )
    
    parser.add_argument(
        "-m", "--model",
        help="Path to T5 model directory",
        type=str
    )
    
    parser.add_argument(
        "-q", "--query",
        help="Single query to execute (non-interactive)",
        type=str
    )
    
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    
    parser.add_argument(
        "--show-schema",
        help="Display database schema and exit",
        action="store_true"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Txt2SQL 1.0.0"
    )
    
    return parser


def interactive_mode(
    generator: SQLGenerator,
    db_manager: DatabaseManager,
    schema: str
) -> None:
    """
    Run interactive query mode.
    
    Args:
        generator: SQL generator instance
        db_manager: Database manager instance
        schema: Database schema string
    """
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Txt2SQL Interactive Mode{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"\n{Colors.GREEN}✓ Model loaded{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Database connected{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Commands:{Colors.RESET}")
    print("  - Type your question in natural language")
    print("  - Type 'schema' to show database schema")
    print("  - Type 'tables' to list all tables")
    print("  - Type 'exit' or 'quit' to exit")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    query_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input(f"{Colors.BOLD}Query> {Colors.RESET}").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}")
                break
            
            elif user_input.lower() == 'schema':
                print(f"\n{Colors.YELLOW}{schema}{Colors.RESET}\n")
                continue
            
            elif user_input.lower() == 'tables':
                tables = db_manager.get_tables()
                print(f"\n{Colors.YELLOW}Tables: {', '.join(tables)}{Colors.RESET}\n")
                continue
            
            # Generate SQL
            print(f"\n{Colors.BLUE}Generating SQL...{Colors.RESET}")
            sql_query = generator.generate_sql(user_input, schema)
            print(f"{Colors.GREEN}Generated SQL:{Colors.RESET} {sql_query}\n")
            
            # Execute query
            success, results = db_manager.execute_query(sql_query)
            
            if success:
                print(format_results(results))
                query_count += 1
            else:
                print(f"{Colors.RED}✗ Error: {results}{Colors.RESET}\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Interrupted. Goodbye!{Colors.RESET}")
            break
        
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}\n")
            logging.error(f"Interactive mode error: {e}")
    
    print(f"\n{Colors.CYAN}Queries executed: {query_count}{Colors.RESET}")


def single_query_mode(
    query: str,
    generator: SQLGenerator,
    db_manager: DatabaseManager,
    schema: str
) -> int:
    """
    Execute a single query and exit.
    
    Args:
        query: Natural language query
        generator: SQL generator instance
        db_manager: Database manager instance
        schema: Database schema string
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(f"\n{Colors.YELLOW}Question:{Colors.RESET} {query}")
        
        # Generate SQL
        sql_query = generator.generate_sql(query, schema)
        print(f"{Colors.GREEN}Generated SQL:{Colors.RESET} {sql_query}\n")
        
        # Execute query
        success, results = db_manager.execute_query(sql_query)
        
        if success:
            print(format_results(results))
            return 0
        else:
            print(f"{Colors.RED}✗ Error: {results}{Colors.RESET}")
            return 1
    
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        logging.error(f"Single query error: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    try:
        # Load configuration
        config = Config(
            model_path=args.model,
            db_path=args.database,
            log_level=log_level
        )
        
        if args.verbose:
            print(f"\n{Colors.CYAN}Configuration:{Colors.RESET}")
            print(f"  Model: {config.model_path}")
            print(f"  Database: {config.db_path}")
        
        # Initialize database manager
        db_manager = DatabaseManager(config.db_path)
        schema = db_manager.get_schema()
        
        # Show schema and exit if requested
        if args.show_schema:
            print(f"\n{Colors.YELLOW}{schema}{Colors.RESET}\n")
            return 0
        
        # Initialize SQL generator
        generator = SQLGenerator(
            model_path=config.model_path,
            max_length=config.max_length,
            num_beams=config.num_beams,
            torch_threads=config.torch_threads
        )
        
        # Run appropriate mode
        if args.query:
            return single_query_mode(args.query, generator, db_manager, schema)
        else:
            interactive_mode(generator, db_manager, schema)
            return 0
    
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Interrupted{Colors.RESET}")
        return 130
    
    except Exception as e:
        print(f"{Colors.RED}✗ Fatal error: {e}{Colors.RESET}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
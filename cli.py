"""
Command-line interface for Txt2SQL with interactive features.
"""
import sys
import os
import logging
from pathlib import Path
from typing import Optional, List

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from config import Config
from database import DatabaseManager
from generator import SQLGenerator
from utils import setup_logging, format_results, Colors, clear_screen


def get_database_path() -> str:
    """Prompt user for database path."""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Database Selection{Colors.RESET}                                        {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    # List .db files in current directory
    db_files = list(Path('.').glob('*.db'))
    
    if db_files:
        print(f"{Colors.YELLOW}Found database files:{Colors.RESET}")
        for i, db in enumerate(db_files, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.RESET} {db.name}")
        print()
    
    while True:
        if db_files:
            db_input = input(f"{Colors.BOLD}Enter database path or number [1-{len(db_files)}]:{Colors.RESET} ").strip()
            
            # Check if user entered a number
            if db_input.isdigit():
                idx = int(db_input) - 1
                if 0 <= idx < len(db_files):
                    return str(db_files[idx])
        else:
            db_input = input(f"{Colors.BOLD}Enter database path:{Colors.RESET} ").strip()
        
        # Check if file exists
        if Path(db_input).exists():
            return db_input
        
        print(f"{Colors.RED}✗ Database not found: {db_input}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please enter a valid database path{Colors.RESET}\n")


def show_welcome_banner():
    """Display welcome banner."""
    clear_screen()
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  {Colors.BOLD}████████╗██╗  ██╗████████╗██████╗ ███████╗ ██████╗ ██╗     {Colors.RESET}{Colors.CYAN}     ║
║  {Colors.BOLD}╚══██╔══╝╚██╗██╔╝╚══██╔══╝╚════██╗██╔════╝██╔═══██╗██║     {Colors.RESET}{Colors.CYAN}     ║
║  {Colors.BOLD}   ██║    ╚███╔╝    ██║    █████╔╝███████╗██║   ██║██║     {Colors.RESET}{Colors.CYAN}     ║
║  {Colors.BOLD}   ██║    ██╔██╗    ██║   ██╔═══╝ ╚════██║██║▄▄ ██║██║     {Colors.RESET}{Colors.CYAN}     ║
║  {Colors.BOLD}   ██║   ██╔╝ ██╗   ██║   ███████╗███████║╚██████╔╝███████╗{Colors.RESET}{Colors.CYAN}     ║
║  {Colors.BOLD}   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝ ╚══▀▀═╝ ╚══════╝{Colors.RESET}{Colors.CYAN}     ║
║                                                                  ║
║            {Colors.YELLOW}Natural Language to SQL Query Converter{Colors.RESET}{Colors.CYAN}               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def show_status(db_path: str, tables: List[str]):
    """Show current status."""
    print(f"\n{Colors.GREEN}✓{Colors.RESET} {Colors.BOLD}Model loaded{Colors.RESET}")
    print(f"{Colors.GREEN}✓{Colors.RESET} {Colors.BOLD}Database:{Colors.RESET} {db_path}")
    print(f"{Colors.GREEN}✓{Colors.RESET} {Colors.BOLD}Tables:{Colors.RESET} {', '.join(tables)}")


def show_commands():
    """Show available commands."""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Available Commands{Colors.RESET}                                        {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════╣{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}?{Colors.RESET} or {Colors.YELLOW}help{Colors.RESET}      Show this help message                     {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}schema{Colors.RESET}         Show database schema                       {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}tables{Colors.RESET}         List all tables                            {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}clear{Colors.RESET}          Clear screen                               {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}exit{Colors.RESET} or {Colors.YELLOW}quit{Colors.RESET}   Exit the program                           {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"\n{Colors.BLUE}💡 Tip:{Colors.RESET} Just type your question in plain English!\n")


def get_user_input(history: Optional[object] = None) -> str:
    """
    Get user input with optional prompt_toolkit features.
    
    Args:
        history: Command history object
    
    Returns:
        User input string
    """
    if PROMPT_TOOLKIT_AVAILABLE and history:
        # Commands for autocomplete
        commands = ['schema', 'tables', 'clear', 'exit', 'quit', 'help', '?']
        completer = WordCompleter(commands, ignore_case=True)
        
        # Custom style
        style = Style.from_dict({
            'prompt': '#00aa00 bold',
        })
        
        try:
            return prompt(
                '❯ ',
                completer=completer,
                history=history,
                style=style,
                enable_history_search=True,
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return 'exit'
    else:
        # Fallback to basic input
        return input(f"{Colors.GREEN}❯{Colors.RESET} ").strip()


def interactive_mode(
    generator: SQLGenerator,
    db_manager: DatabaseManager,
    schema: str,
    db_path: str
) -> None:
    """
    Run interactive query mode.
    
    Args:
        generator: SQL generator instance
        db_manager: Database manager instance
        schema: Database schema string
        db_path: Path to database
    """
    show_welcome_banner()
    show_status(db_path, db_manager.get_tables())
    show_commands()
    
    # Setup history if prompt_toolkit is available
    history = InMemoryHistory() if PROMPT_TOOLKIT_AVAILABLE else None
    
    if not PROMPT_TOOLKIT_AVAILABLE:
        print(f"{Colors.YELLOW}💡 Install 'prompt-toolkit' for enhanced features (autocomplete, history){Colors.RESET}")
        print(f"   {Colors.CYAN}pip install prompt-toolkit{Colors.RESET}\n")
    
    query_count = 0
    
    while True:
        try:
            # Get user input
            user_input = get_user_input(history)
            if not user_input:
                continue
            
            # Handle commands
            cmd = user_input.lower()
            
            if cmd in ['exit', 'quit', 'q']:
                logging.info("Exiting interactive mode")
                print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
                print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}Session Summary{Colors.RESET}                                           {Colors.CYAN}║{Colors.RESET}")
                print(f"{Colors.CYAN}║{Colors.RESET}  Queries executed: {Colors.GREEN}{query_count}{Colors.RESET}                                      {Colors.CYAN}║{Colors.RESET}")
                print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
                print(f"\n{Colors.BOLD}Thank you for using Txt2SQL! 👋{Colors.RESET}\n")
                break
            
            elif cmd in ['?', 'help']:
                show_commands()
                continue
            
            elif cmd == 'schema':
                print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
                print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Database Schema{Colors.RESET}                                           {Colors.CYAN}║{Colors.RESET}")
                print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
                print(f"\n{Colors.YELLOW}{schema}{Colors.RESET}\n")
                continue
            
            elif cmd == 'tables':
                tables = db_manager.get_tables()
                print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
                print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Tables in Database{Colors.RESET}                                        {Colors.CYAN}║{Colors.RESET}")
                print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
                for i, table in enumerate(tables, 1):
                    print(f"  {Colors.GREEN}{i}.{Colors.RESET} {table}")
                print()
                continue
            
            elif cmd == 'clear':
                clear_screen()
                show_welcome_banner()
                show_status(db_path, db_manager.get_tables())
                print()
                continue
            # Generate SQL
            print(f"\n{Colors.BLUE}⚙ Generating SQL...{Colors.RESET}")
            sql_query = generator.generate_sql(user_input, schema)
            logging.info(f"Generated SQL: {sql_query}")
            print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Generated SQL{Colors.RESET}                                             {Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
            print(f"{Colors.GREEN}{sql_query}{Colors.RESET}\n")
            
            # Execute query
            print(f"{Colors.BLUE}⚙ Executing query...{Colors.RESET}\n")
            success, results = db_manager.execute_query(sql_query)
            
            if success:
                print(format_results(results))
                query_count += 1
            else:
                print(f"{Colors.RED}✗ Error: {results}{Colors.RESET}\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Use 'exit' command to quit{Colors.RESET}\n")
            continue
        
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}\n")
            logging.error(f"Interactive mode error: {e}")


def main() -> int:
    """Main entry point."""
    try:
        # Setup logging
        setup_logging("INFO")
        # Load configuration (only model path from env)
        print(f"\n{Colors.BLUE}⚙ Loading model...{Colors.RESET}")
        config = Config()
        
        # Ask user for database path
        db_path = get_database_path()
        
        # Initialize database manager
        print(f"\n{Colors.BLUE}⚙ Connecting to database...{Colors.RESET}")
        db_manager = DatabaseManager(db_path)
        schema = db_manager.get_schema()
        
        # Initialize SQL generator
        generator = SQLGenerator(
            model_path=config.model_path,
            max_length=config.max_length,
            num_beams=config.num_beams,
            torch_threads=config.torch_threads
        )
        
        # Run interactive mode
        interactive_mode(generator, db_manager, schema, db_path)
        return 0
    
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Interrupted{Colors.RESET}")
        return 130
    
    except Exception as e:
        print(f"\n{Colors.RED}✗ Fatal error: {e}{Colors.RESET}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
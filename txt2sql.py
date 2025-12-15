#!/usr/bin/env python3
"""
Txt2SQL - Convert natural language to SQL queries.

This is the main entry point that delegates to the CLI module.
"""
from cli import main

if __name__ == "__main__":
    exit(main())
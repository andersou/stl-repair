#!/usr/bin/env python3
"""
Legacy entry point for STL repair tool.
This file is kept for backward compatibility.
Use 'stl-repair' command or the CLI module directly.
"""
from __future__ import annotations

# Import and run the main CLI function
try:
    from stl_repair.cli import main

    if __name__ == "__main__":
        main()
except ImportError:
    print("Error: stl-repair package not properly installed.")
    print("Please install with: pip install -e .")
    import sys

    sys.exit(1)

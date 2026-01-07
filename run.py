#!/usr/bin/env python
"""
Wrapper script for running the voice-to-text application with uv.

Usage:
    uv run run.py
"""

from src.main import main

if __name__ == "__main__":
    exit(main())

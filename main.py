#!/usr/bin/env python3
"""
Indic Voice Studio — Main Program Entry Point
Interactive Terminal UI & Command-Line Interface for Voice Cloning & Reference Catalog.

Usage:
    # 1. Launch Interactive Studio Menu:
    python main.py

    # 2. Subcommands:
    python main.py list
    python main.py info <VOICE_KEY>
    python main.py prompts
    python main.py add --audio "path/to/audio.wav" --transcript "..."
    python main.py clone --voice deep_classic --text "..."
    python main.py batch --voice deep_classic --lang "1 2" --tier "2-4"
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from voice_studio.cli.app import main

if __name__ == "__main__":
    main()

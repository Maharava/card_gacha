"""
Simple launcher for the card game.
Run this from the project root directory.
"""
import os
import sys

# Add the current directory to sys.path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from src.main_gui import main

if __name__ == "__main__":
    sys.exit(main())
"""
Launcher script for the card game.
Run this from the root directory of the project.
"""
import os
import sys
import importlib.util

def main():
    # Ensure we're in the correct directory
    if not os.path.isdir('src'):
        print("Error: Please run this script from the root directory of the project")
        print("The 'src' directory should be in the same directory as this script")
        return 1
    
    # Add the current directory to sys.path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    # Import and run the main_gui module
    spec = importlib.util.spec_from_file_location("main_gui", "src/main_gui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Run the main function
    return module.main()

if __name__ == "__main__":
    sys.exit(main())

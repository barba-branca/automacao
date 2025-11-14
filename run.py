# This is the main entry point for the automation.
# Run this file from your terminal: python run.py

import sys
from pathlib import Path

# Add the project root to the Python path to allow absolute imports from the 'automation' package.
# This makes the project structure more robust.
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from automation.main import main

if __name__ == "__main__":
    # All paths inside the application (logs, screenshots, config, images)
    # are now relative to this root directory, which is what we want.
    main()

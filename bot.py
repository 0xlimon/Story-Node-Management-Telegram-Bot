#!/usr/bin/env python3
"""Entry point for the Story Validator Bot."""

import os
import sys
import logging

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.bot import main
except ImportError as e:
    logging.error(f"Failed to import bot package: {e}")
    logging.error("Please make sure all dependencies are installed and the package structure is correct.")
    sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
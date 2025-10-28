#!/usr/bin/env python3
"""
PythonAnywhere startup script for Telegram Vault Userbot
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Validate configuration
from config import Config
try:
    Config.validate()
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

# Start the userbot
if __name__ == '__main__':
    from userbot import main
    main()
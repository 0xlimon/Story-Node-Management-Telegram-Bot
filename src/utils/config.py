"""Configuration settings for the Story Validator Bot."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Node Configuration
SERVER_PORT = os.getenv("SERVER_PORT", "26657")
STORY_SERVICE = os.getenv("STORY_SERVICE")
STORY_GETH_SERVICE = os.getenv("STORY_GETH_SERVICE")
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", 300))

# RPC Endpoints
RPC_ENDPOINT_1 = os.getenv("RPC_ENDPOINT_1")
RPC_ENDPOINT_2 = os.getenv("RPC_ENDPOINT_2")

# Logging Configuration
LOGGING_CONFIG = {
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'level': logging.INFO,
    'handlers': [
        logging.StreamHandler()
    ]
}

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)

# Set logging levels for noisy libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('telegram.ext.Updater').setLevel(logging.INFO)
logging.getLogger('telegram.ext.Application').setLevel(logging.INFO)
logging.getLogger('telegram.ext.ExtBot').setLevel(logging.INFO)
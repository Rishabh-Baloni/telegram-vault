"""
Configuration loader for Telegram Vault Userbot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Userbot configuration from environment variables"""
    
    # Userbot config
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    
    # Common config
    VAULT_CHAT_ID = os.getenv('VAULT_CHAT_ID')
    TARGET_USER_ID = os.getenv('TARGET_USER_ID')
    TARGET_CHANNELS = os.getenv('TARGET_CHANNELS')
    
    # Parsed lists (set after validation)
    TARGET_USER_IDS = []
    TARGET_CHANNEL_IDS = []
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        missing = []
        
        # Required fields
        if not cls.VAULT_CHAT_ID:
            missing.append('VAULT_CHAT_ID')
        if not cls.TARGET_USER_ID and not cls.TARGET_CHANNELS:
            missing.append('TARGET_USER_ID or TARGET_CHANNELS (at least one required)')
        if not cls.API_ID:
            missing.append('API_ID')
        if not cls.API_HASH:
            missing.append('API_HASH')
        if not cls.PHONE_NUMBER:
            missing.append('PHONE_NUMBER')
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please create a .env file based on .env.example"
            )
        
        # Parse TARGET_USER_ID (can be comma-separated list)
        if cls.TARGET_USER_ID:
            try:
                # Split by comma and convert to integers
                cls.TARGET_USER_IDS = [
                    int(uid.strip()) 
                    for uid in cls.TARGET_USER_ID.split(',')
                    if uid.strip()
                ]
            except (ValueError, TypeError):
                raise ValueError("TARGET_USER_ID must be numeric IDs (comma-separated for multiple)")
        
        # Parse TARGET_CHANNELS (can be comma-separated list of IDs or @usernames)
        if cls.TARGET_CHANNELS:
            cls.TARGET_CHANNEL_IDS = [
                ch.strip() for ch in cls.TARGET_CHANNELS.split(',')
                if ch.strip()
            ]
            # Convert numeric channel IDs to integers
            for i, ch_id in enumerate(cls.TARGET_CHANNEL_IDS):
                if not ch_id.startswith('@'):
                    try:
                        cls.TARGET_CHANNEL_IDS[i] = int(ch_id)
                    except ValueError:
                        raise ValueError(f"Invalid channel ID: {ch_id}")
        
        # Convert API_ID to integer
        try:
            cls.API_ID = int(cls.API_ID)
        except (ValueError, TypeError):
            raise ValueError("API_ID must be a valid numeric ID")
        
        return True

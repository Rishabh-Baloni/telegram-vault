"""
Minimal configuration for Telegram Vault Userbot
User lists are read from Telegram pinned message
"""
import os

class Config:
    """Basic API configuration - user lists loaded from pinned message"""
    
    # API credentials (required)
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', 'your_api_hash_here')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', 'your_phone_number_here')
    
    # Vault (can be overridden by pinned message)
    VAULT_CHAT_ID = os.getenv('VAULT_CHAT_ID', 'your_vault_chat_id_here')
    
    # Dynamic lists (loaded from pinned message)
    TARGET_USER_IDS = []
    TARGET_CHANNEL_IDS = []
    TARGET_GROUP_IDS = []

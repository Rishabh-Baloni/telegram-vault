"""
Telegram Vault Userbot - User Mode
Monitors all groups using your personal Telegram account
"""
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Suppress Pyrogram and asyncio errors for unknown peers
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


async def message_handler(client: Client, message: Message):
    """
    Handle incoming messages and forward if from target user, channel, or anonymous admin
    """
    try:
        should_forward = False
        source_info = ""
        
        # Check 1: Regular user message
        if message.from_user:
            user_id = message.from_user.id
            user_name = message.from_user.username or message.from_user.first_name
            chat_title = message.chat.title if message.chat else "Private Chat"
            
            # Check if message is from target user
            if user_id in Config.TARGET_USER_IDS:
                should_forward = True
                source_info = f"User: {user_name} (ID: {user_id}) | Chat: {chat_title}"
        
        # Check 2: Anonymous admin or channel message (sender_chat)
        elif message.sender_chat:
            sender_chat_id = message.sender_chat.id
            sender_chat_title = message.sender_chat.title or message.sender_chat.username or "Unknown"
            chat_title = message.chat.title if message.chat else "Private Chat"
            
            # Check if message is from target channel/group
            # For anonymous admins, sender_chat is the group itself
            if sender_chat_id in Config.TARGET_CHANNEL_IDS or \
               message.chat.id in Config.TARGET_CHANNEL_IDS or \
               (message.sender_chat.username and f"@{message.sender_chat.username}" in Config.TARGET_CHANNEL_IDS):
                should_forward = True
                source_info = f"Channel/Group: {sender_chat_title} (ID: {sender_chat_id}) | Chat: {chat_title}"
        
        # Forward if matched
        if should_forward:
            logger.info(f"📩 Target message detected! {source_info}")
            
            try:
                # Try to parse vault chat ID as integer (for user/group IDs)
                try:
                    vault_id = int(Config.VAULT_CHAT_ID)
                except ValueError:
                    # If not an integer, use as-is (could be @username)
                    vault_id = Config.VAULT_CHAT_ID
                
                await message.forward(vault_id)
                
                logger.info(
                    f"✅ Successfully forwarded message {message.id} to vault"
                )
                
            except Exception as e:
                logger.error(
                    f"❌ Failed to forward message {message.id}: {str(e)}"
                )
            
    except Exception as e:
        logger.error(f"Error in message_handler: {str(e)}")


def main():
    """
    Start the userbot
    """
    try:
        # Validate configuration
        Config.validate()
        logger.info("✓ Configuration validated successfully")
        
        # Create Pyrogram client
        app = Client(
            "vault_userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            phone_number=Config.PHONE_NUMBER
        )
        
        # Register message handler for all incoming messages
        @app.on_message(filters.all)
        async def handle_message(client, message):
            # Skip edited messages
            if message.edit_date:
                return
            await message_handler(client, message)
        
        logger.info("👤 Telegram Vault Userbot started successfully!")
        if Config.TARGET_USER_IDS:
            logger.info(f"📌 Monitoring user IDs: {Config.TARGET_USER_IDS}")
        if Config.TARGET_CHANNEL_IDS:
            logger.info(f"📢 Monitoring channels: {Config.TARGET_CHANNEL_IDS}")
        logger.info(f"📦 Vault chat ID: {Config.VAULT_CHAT_ID}")
        logger.info("⏳ Running in USER MODE...")
        logger.info("💡 This will monitor ALL groups you're a member of")
        
        # Run the client
        app.run()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return
    except Exception as e:
        logger.error(f"Failed to start userbot: {str(e)}")
        return


if __name__ == '__main__':
    main()

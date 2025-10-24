"""
Telegram Vault Userbot - User Mode
Monitors all groups using your personal Telegram account
"""
import logging
import os
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

# Keep alive for Render (optional health check)
PORT = int(os.environ.get('PORT', 10000))

def start_health_server():
    """Start a simple HTTP server for Render health checks"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
        
        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Suppress HTTP logs
    
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health check server running on port {PORT}")


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
        # Start health check server for Render
        start_health_server()
        
        # Restore session from environment (supports chunked session for large files)
        import base64
        
        # Try to get session from chunks first (for large sessions)
        session_parts = []
        for i in range(1, 11):  # Support up to 10 chunks
            part = os.environ.get(f'SESSION_PART{i}')
            if part:
                session_parts.append(part)
            else:
                break
        
        if session_parts:
            # Combine all chunks
            try:
                session_base64 = ''.join(session_parts)
                session_data = base64.b64decode(session_base64)
                with open("vault_userbot.session", "wb") as f:
                    f.write(session_data)
                logger.info(f"✓ Session restored from {len(session_parts)} chunks")
            except Exception as e:
                logger.warning(f"Could not restore chunked session: {e}")
        else:
            # Try single SESSION_STRING (for backwards compatibility)
            session_base64 = os.environ.get('SESSION_STRING')
            if session_base64:
                try:
                    session_data = base64.b64decode(session_base64)
                    with open("vault_userbot.session", "wb") as f:
                        f.write(session_data)
                    logger.info("✓ Session restored from environment variable")
                except Exception as e:
                    logger.warning(f"Could not restore session: {e}")
        
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
        
        # Start client first
        app.start()
        
        # Cache vault channel on startup to prevent "Peer id invalid" errors
        try:
            logger.info("🔄 Caching vault channel...")
            vault_chat = app.get_chat(Config.VAULT_CHAT_ID)
            logger.info(f"✓ Vault cached: {vault_chat.title if vault_chat.title else 'Saved Messages'}")
        except Exception as e:
            logger.warning(f"⚠️  Could not cache vault: {e}")
        
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
        
        # Keep client running
        from pyrogram import idle
        idle()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return
    except Exception as e:
        logger.error(f"Failed to start userbot: {str(e)}")
        return


if __name__ == '__main__':
    main()

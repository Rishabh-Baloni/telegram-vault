"""
Telegram Vault Userbot - User Mode
Monitors all groups using your personal Telegram account
"""
import logging
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
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

# Track last seen message ID for each channel (for polling)
last_message_ids = {}

# Polling interval in seconds (3 minutes)
POLL_INTERVAL = 180

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
        logger.debug(f"🔍 Checking message {message.id} from chat {message.chat.id}")
        should_forward = False
        source_info = ""
        
        # Check 1: Message from a target channel/group (regardless of sender)
        if message.chat.id in Config.TARGET_CHANNEL_IDS:
            should_forward = True
            chat_title = message.chat.title or message.chat.username or "Unknown"
            sender = ""
            if message.from_user:
                sender = f"{message.from_user.username or message.from_user.first_name}"
            elif message.sender_chat:
                sender = f"{message.sender_chat.title or message.sender_chat.username}"
            source_info = f"Group/Channel: {chat_title} (ID: {message.chat.id}) | Sender: {sender}"
        
        # Check 2: Regular user message (from target user)
        elif message.from_user:
            user_id = message.from_user.id
            user_name = message.from_user.username or message.from_user.first_name
            chat_title = message.chat.title if message.chat else "Private Chat"
            
            # Check if message is from target user
            if user_id in Config.TARGET_USER_IDS:
                should_forward = True
                source_info = f"User: {user_name} (ID: {user_id}) | Chat: {chat_title}"
        
        # Check 3: Anonymous admin or channel message (sender_chat)
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


async def initialize_last_message_ids(client: Client):
    """
    Initialize last_message_ids by reading vault to find last forwarded message from each channel
    This allows the bot to survive restarts without missing messages
    """
    global last_message_ids
    
    logger.info("🔍 Initializing last message IDs from vault...")
    
    try:
        vault_id = int(Config.VAULT_CHAT_ID)
        
        # Check last 100 messages in vault to find latest from each channel
        async for msg in client.get_chat_history(vault_id, limit=100):
            # Check forwarded messages
            if msg.forward_from_chat:
                source_chat_id = msg.forward_from_chat.id
                if msg.forward_from_message_id and source_chat_id not in last_message_ids:
                    last_message_ids[source_chat_id] = msg.forward_from_message_id
                    logger.info(f"   📌 {msg.forward_from_chat.title}: last forwarded ID = {msg.forward_from_message_id}")
            
            # Check copied messages (for forward-restricted channels)
            elif msg.text and "🆔 Channel:" in msg.text and "| Msg:" in msg.text:
                try:
                    # Parse: "🆔 Channel: -1002083547614 | Msg: 1942"
                    lines = msg.text.split('\n')
                    for line in lines:
                        if "🆔 Channel:" in line:
                            parts = line.split('|')
                            channel_part = parts[0].replace("🆔 Channel:", "").strip()
                            msg_part = parts[1].replace("Msg:", "").strip()
                            
                            source_chat_id = int(channel_part)
                            message_id = int(msg_part)
                            
                            if source_chat_id not in last_message_ids:
                                last_message_ids[source_chat_id] = message_id
                                logger.info(f"   📌 Copied message from {source_chat_id}: last ID = {message_id}")
                            break
                except:
                    pass
        
        # For channels not in vault yet (or forward-restricted), get their current latest
        for channel_id in Config.TARGET_CHANNEL_IDS:
            if isinstance(channel_id, str) or channel_id in last_message_ids:
                continue
            
            try:
                chat = await client.get_chat(channel_id)
                if chat.type == ChatType.SUPERGROUP:
                    continue
                
                # Get latest message ID
                async for msg in client.get_chat_history(channel_id, limit=1):
                    last_message_ids[channel_id] = msg.id
                    logger.info(f"   📌 {chat.title}: initialized at current ID = {msg.id}")
                    break
            except:
                pass
        
        logger.info(f"✅ Initialized tracking for {len(last_message_ids)} channels")
        
    except Exception as e:
        logger.error(f"⚠️  Error initializing from vault: {e}")


async def poll_channels(client: Client):
    """
    Background task to poll channels for new messages
    Channels don't send real-time updates to regular subscribers, so we poll them periodically
    """
    global last_message_ids
    
    # Wait for client to be fully ready
    await asyncio.sleep(10)
    
    logger.info("🔄 Starting channel polling task...")
    
    # Initialize by reading vault to find last forwarded messages
    await initialize_last_message_ids(client)
    
    logger.info(f"⏱️  Checking channels every {POLL_INTERVAL} seconds")
    
    while True:
        try:
            for channel_id in Config.TARGET_CHANNEL_IDS:
                # Skip @username entries (handle them separately if needed)
                if isinstance(channel_id, str):
                    continue
                
                try:
                    # Check if this is actually a channel (not a supergroup)
                    chat = await client.get_chat(channel_id)
                    
                    # Skip supergroups - they get real-time updates
                    if chat.type == ChatType.SUPERGROUP:
                        continue
                    
                    # Get the latest messages
                    messages = []
                    async for msg in client.get_chat_history(channel_id, limit=10):
                        messages.append(msg)
                    
                    if not messages:
                        continue
                    
                    # If not initialized from vault, start from 10 messages back to catch recent ones
                    if channel_id not in last_message_ids:
                        # Start from 10 messages back (or earliest available)
                        start_id = messages[min(9, len(messages)-1)].id if len(messages) > 1 else messages[0].id
                        last_message_ids[channel_id] = start_id - 1  # Subtract 1 so we forward the last 10
                        logger.info(f"📌 New channel tracked: {chat.title} (will catch up from ID {start_id})")
                        # Don't continue - let it forward the messages in this cycle
                        pass
                    
                    # Check for new messages (messages are in reverse chronological order)
                    new_messages = []
                    for msg in reversed(messages):
                        if msg.id > last_message_ids[channel_id]:
                            new_messages.append(msg)
                    
                    # Forward new messages
                    if new_messages:
                        last_message_ids[channel_id] = messages[0].id
                        
                        for msg in new_messages:
                            try:
                                # Skip edited messages
                                if msg.edit_date:
                                    continue
                                
                                vault_id = int(Config.VAULT_CHAT_ID)
                                
                                try:
                                    # Try to forward first
                                    await msg.forward(vault_id)
                                    logger.info(
                                        f"✅ [POLL] Forwarded message {msg.id} from {chat.title} to vault"
                                    )
                                except Exception as forward_error:
                                    # If forward fails (restricted), send as text copy instead
                                    if "FORWARDS_RESTRICTED" in str(forward_error) or "CHAT_FORWARDS_RESTRICTED" in str(forward_error):
                                        text = msg.text or msg.caption or "[Media - forwarding restricted]"
                                        # Include channel ID and message ID in the copy for tracking
                                        await client.send_message(
                                            vault_id,
                                            f"📋 From: {chat.title}\n"
                                            f"🆔 Channel: {channel_id} | Msg: {msg.id}\n"
                                            f"📅 {msg.date}\n\n{text}"
                                        )
                                        logger.info(
                                            f"✅ [POLL] Copied message {msg.id} from {chat.title} (forward restricted)"
                                        )
                                    else:
                                        raise  # Re-raise if it's a different error
                                
                            except Exception as e:
                                logger.error(f"❌ Failed to forward polled message: {str(e)}")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Error polling channel {channel_id}: {str(e)}")
                    continue
                
                # Small delay between channels to avoid rate limits
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error in polling task: {str(e)}")
        
        # Wait before next poll cycle
        await asyncio.sleep(POLL_INTERVAL)


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
        
        # Register message handler BEFORE starting client
        @app.on_message(filters.all)
        async def handle_message(client, message):
            # Log every message received
            try:
                chat_info = f"Chat: {message.chat.id}"
                from_info = f"From: {message.from_user.id if message.from_user else 'None'}"
                text_preview = message.text[:30] if message.text else '[Media]'
                logger.info(f"📨 Message received | {chat_info} | {from_info} | {text_preview}")
            except:
                pass
            
            # Skip edited messages
            if message.edit_date:
                logger.info("⏭️  Skipped: edited message")
                return
            await message_handler(client, message)
        
        # Start client after handlers are registered
        app.start()
        
        # Cache vault channel on startup to prevent "Peer id invalid" errors
        try:
            logger.info("🔄 Caching vault channel...")
            vault_chat = app.get_chat(Config.VAULT_CHAT_ID)
            logger.info(f"✓ Vault cached: {vault_chat.title if vault_chat.title else 'Saved Messages'}")
        except Exception as e:
            logger.warning(f"⚠️  Could not cache vault: {e}")
        
        logger.info("👤 Telegram Vault Userbot started successfully!")
        if Config.TARGET_USER_IDS:
            logger.info(f"📌 Monitoring user IDs: {Config.TARGET_USER_IDS}")
        if Config.TARGET_CHANNEL_IDS:
            logger.info(f"📢 Monitoring channels: {Config.TARGET_CHANNEL_IDS}")
        logger.info(f"📦 Vault chat ID: {Config.VAULT_CHAT_ID}")
        logger.info("⏳ Running in USER MODE...")
        logger.info("💡 This will monitor ALL groups you're a member of")
        
        # Start background polling task for channels
        from pyrogram import idle
        app.loop.create_task(poll_channels(app))
        
        # Keep client running
        idle()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return
    except Exception as e:
        logger.error(f"Failed to start userbot: {str(e)}")
        return


if __name__ == '__main__':
    main()

async def get_monitored_ids_from_pinned(app, saved_messages_id):
    """Read and parse monitored user/channel/group IDs from pinned message in Saved Messages."""
    try:
        chat = await app.get_chat(saved_messages_id)
        pinned = chat.pinned_message
        if not pinned or not pinned.text:
            logger.warning("No pinned message found in Saved Messages.")
            return [], [], []
        # Example format:
        # USERS: 123456789, 987654321
        # CHANNELS: -1001234567890, -1009876543210
        # GROUPS: -1001122334455
        users, channels, groups = [], [], []
        for line in pinned.text.splitlines():
            if line.startswith("USERS:"):
                users = [int(x.strip()) for x in line.replace("USERS:","").split(",") if x.strip()]
            elif line.startswith("CHANNELS:"):
                channels = [int(x.strip()) for x in line.replace("CHANNELS:","").split(",") if x.strip()]
            elif line.startswith("GROUPS:"):
                groups = [int(x.strip()) for x in line.replace("GROUPS:","").split(",") if x.strip()]
        logger.info(f"Loaded from pinned: USERS={users}, CHANNELS={channels}, GROUPS={groups}")
        return users, channels, groups
    except Exception as e:
        logger.error(f"Error reading pinned message in Saved Messages: {e}")
        return [], [], []
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

# Track last seen message ID for each channel (for polling)
last_message_ids = {}

# Polling interval in seconds (3 minutes)
POLL_INTERVAL = 180


async def message_handler(client: Client, message: Message):
    """
    Handle incoming messages and forward if from target user, channel, or anonymous admin
    """
    try:
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
            logger.info(f"✅ Matched monitored channel/group: {source_info}")
        
        # Check 2: Regular user message (from target user) - check this regardless of chat
        if message.from_user and message.from_user.id in Config.TARGET_USER_IDS:
            should_forward = True
            user_name = message.from_user.username or message.from_user.first_name
            chat_title = message.chat.title if message.chat else "Private Chat"
            source_info = f"User: {user_name} (ID: {message.from_user.id}) | Chat: {chat_title}"
            logger.info(f"✅ Matched monitored user: {source_info}")
        
        # Debug: Log if message is from Anand specifically
        if message.from_user and message.from_user.id == 1163970079:
            logger.info(f"🔍 DEBUG: Message from Anand (1163970079) in chat {message.chat.id} - Monitored users: {Config.TARGET_USER_IDS}")
        
        # Check 3: Message from userbot owner in Saved Messages (special case)
        if not message.from_user and message.chat.type.name == "PRIVATE":
            me = await client.get_me()
            if message.chat.id == me.id:
                should_forward = True
                source_info = f"User: {me.first_name} (ID: {me.id}) | Chat: Saved Messages"
                logger.info(f"✅ Matched saved messages: {source_info}")
        
        # Check 4: Anonymous admin or channel message (sender_chat) - for supergroups
        if message.sender_chat:
            sender_chat_id = message.sender_chat.id
            sender_chat_title = message.sender_chat.title or message.sender_chat.username or "Unknown"
            chat_title = message.chat.title if message.chat else "Private Chat"
            
            # Check if message is from target channel/group
            if sender_chat_id in Config.TARGET_CHANNEL_IDS or \
               (message.sender_chat.username and f"@{message.sender_chat.username}" in Config.TARGET_CHANNEL_IDS):
                should_forward = True
                source_info = f"Anonymous Admin: {sender_chat_title} (ID: {sender_chat_id}) | Chat: {chat_title}"
                logger.info(f"✅ [REALTIME] Matched anonymous admin: {source_info}")
        
        if not should_forward:
            # Debug: Always log if it's from Anand to see why it's not matching
            from_user_id = message.from_user.id if message.from_user else "None"
            if from_user_id == "1163970079":
                logger.info(f"❌ DEBUG: Anand's message {message.id} not forwarded - Chat: {message.chat.id}, Monitored: {Config.TARGET_USER_IDS}")
            elif from_user_id != "None" and int(from_user_id) % 10 == 0:  # Log every 10th user
                logger.info(f"❌ No match found for message {message.id} from user {from_user_id}")
            return
        
        # Forward if matched
        if should_forward:
            logger.info(f"📩 FORWARDING: {source_info}")
            
            try:
                # Try to parse vault chat ID as integer (for user/group IDs)
                try:
                    vault_id = int(Config.VAULT_CHAT_ID)
                except ValueError:
                    # If not an integer, use as-is (could be @username)
                    vault_id = Config.VAULT_CHAT_ID
                
                await message.forward(vault_id)
                
                logger.info(f"✅ SUCCESS: Forwarded message {message.id} to vault")
                
            except Exception as e:
                logger.error(f"❌ FAILED: Forward message {message.id}: {str(e)}")
            
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
                # Only initialize channels, skip supergroups
                if chat.type.name == "SUPERGROUP":
                    logger.info(f"   ⏭️ Skipping supergroup {chat.title} initialization - real-time only")
                    continue
                    
                logger.info(f"   📍 Initializing {chat.title} (Type: {chat.type.name})")
                
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


async def cache_all_peers_startup(app: Client):
    """Cache all monitored targets and vault channel on startup"""
    logger.info("🚀 Caching all peers on startup...")
    
    # All target IDs
    user_ids = [993339693, 1290365086, 941927047, 582868822, 1010500439, 
                1303354830, 6096714326, 1163970079, 1078883294, 5515536284, 5058858285]
    
    channel_ids = [-1003074469948, -1001150779891, -1001177289429, -1001521790999,
                   -1002095518645, -1002083547614, -1001475939687, -1001827108721,
                   -1001409153549, -1001515619731, -1001885622550]
    
    vault_id = int(Config.VAULT_CHAT_ID)
    
    # Cache users
    for user_id in user_ids:
        try:
            user = await app.get_users(user_id)
            logger.info(f"✅ Cached user: {user.first_name}")
        except:
            pass
    
    # Cache channels
    for channel_id in channel_ids:
        try:
            chat = await app.get_chat(channel_id)
            logger.info(f"✅ Cached channel: {chat.title}")
        except:
            pass
    
    # Cache vault (CRITICAL)
    try:
        vault = await app.get_chat(vault_id)
        logger.info(f"✅ Cached vault: {vault.title}")
    except Exception as e:
        logger.error(f"❌ Failed to cache vault: {e}")
    
    # Cache Silicon Stories by username
    try:
        silicon = await app.get_chat("@GetHired01")
        logger.info(f"✅ Cached Silicon Stories: {silicon.title}")
    except:
        pass
    
    logger.info("🎉 All peers cached successfully!")


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
            logger.info("🔄 Starting poll cycle...")
            # Remove duplicates from channel list
            unique_channels = list(set(Config.TARGET_CHANNEL_IDS))
            for channel_id in unique_channels:
                # Skip @username entries (handle them separately if needed)
                if isinstance(channel_id, str):
                    continue
                
                try:
                    # Check if this is actually a channel (not a supergroup)
                    chat = await client.get_chat(channel_id)
                    
                    logger.info(f"  🔍 Checking {chat.title} (ID: {channel_id}, Type: {chat.type.name})")
                    
                    # Skip supergroups - only poll channels
                    if chat.type.name == "SUPERGROUP":
                        logger.info(f"  ⏭️ Skipping supergroup {chat.title} - waiting for real-time admin messages")
                        continue
                    
                    # Poll only channels
                    logger.info(f"  📊 Polling {chat.title} (ID: {channel_id}, Type: {chat.type.name})")
                    
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
                    
                    logger.info(f"� Checked {chat.title}: {len(new_messages)} new message(s)")
                    # Forward new messages
                    if new_messages:
                        last_message_ids[channel_id] = messages[0].id
                        
                        for msg in new_messages:
                            try:
                                # Log edited messages but don't skip them - channels often edit posts
                                if msg.edit_date:
                                    logger.info(f"✏️ [POLL] Processing edited message {msg.id} from {chat.title}")
                                vault_id = int(Config.VAULT_CHAT_ID)
                                logger.info(f"🔄 [POLL] Attempting to forward message {msg.id} from {chat.title}")
                                try:
                                    # Try to forward first
                                    await msg.forward(vault_id)
                                    logger.info(
                                        f"✅ [POLL] Forwarded message {msg.id} from {chat.title} to vault"
                                    )
                                except Exception as forward_error:
                                    error_str = str(forward_error)
                                    # If forward fails (restricted), send as text copy instead
                                    if "FORWARDS_RESTRICTED" in error_str or "CHAT_FORWARDS_RESTRICTED" in error_str:
                                        text = msg.text or msg.caption or "[Media - forwarding restricted]"
                                        await client.send_message(
                                            vault_id,
                                            f"📋 From: {chat.title}\n"
                                            f"🆔 Channel: {channel_id} | Msg: {msg.id}\n"
                                            f"📅 {msg.date}\n\n{text}"
                                        )
                                        logger.info(
                                            f"✅ [POLL] Copied message {msg.id} from {chat.title} (forward restricted)"
                                        )
                                    elif "MESSAGE_ID_INVALID" in error_str:
                                        logger.warning(f"⏭️ Skipped message {msg.id} in {chat.title}: MESSAGE_ID_INVALID")
                                        # Try to copy as text instead
                                        try:
                                            text = msg.text or msg.caption or "[Media - message ID invalid]"
                                            await client.send_message(
                                                vault_id,
                                                f"📋 From: {chat.title}\n"
                                                f"🆔 Channel: {channel_id} | Msg: {msg.id}\n"
                                                f"📅 {msg.date}\n\n{text}"
                                            )
                                            logger.info(f"✅ [POLL] Copied invalid message {msg.id} from {chat.title} as text")
                                        except:
                                            pass
                                        continue
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
                logger.error(f"Error restoring session: {str(e)}")
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
        

        # Create Pyrogram client
        app = Client(
            "vault_userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            phone_number=Config.PHONE_NUMBER
        )
        


        async def startup_config():
            # Get own user ID after starting client
            me = await app.get_me()
            my_id = me.id
            # Read monitored IDs from pinned message in Saved Messages
            users, channels, groups = await get_monitored_ids_from_pinned(app, my_id)
            # Set config for monitoring
            Config.TARGET_USER_IDS = users
            Config.TARGET_CHANNEL_IDS = channels + groups
            logger.info(f"Monitoring USERS: {users}")
            logger.info(f"Monitoring CHANNELS/GROUPS: {channels + groups}")
            return my_id

        # Register admin command handler BEFORE generic handler - only for actual commands
        @app.on_message(filters.me & filters.text & filters.regex(r"^/(add|remove)\s+(user|channel|group)\s+(-?\d+)"))
        async def admin_command_handler(client, message):
            # Only handle commands in saved messages
            me = await client.get_me()
            my_id = me.id
            if message.chat.id != my_id:
                return
            """
            Handle admin commands in Saved Messages to add/remove monitored IDs and update pinned config
            Commands:
            /add user <id>
            /add channel <id>
            /add group <id>
            /remove user <id>
            /remove channel <id>
            /remove group <id>
            """
            import re
            cmd = message.text.strip()
            logger.info(f"🔧 Admin handler: Processing command: {cmd}")
            match = re.match(r"/(add|remove)\s+(user|channel|group)\s+(-?\d+)", cmd, re.I)
            if not match:
                return
            action, typ, id_str = match.groups()
            id_val = int(id_str)
            users, channels, groups = await get_monitored_ids_from_pinned(client, my_id)
            changed = False
            if action.lower() == "add":
                if typ == "user" and id_val not in users:
                    users.append(id_val)
                    changed = True
                elif typ == "channel" and id_val not in channels:
                    channels.append(id_val)
                    changed = True
                elif typ == "group" and id_val not in groups:
                    groups.append(id_val)
                    changed = True
            elif action.lower() == "remove":
                if typ == "user" and id_val in users:
                    users.remove(id_val)
                    changed = True
                elif typ == "channel" and id_val in channels:
                    channels.remove(id_val)
                    changed = True
                elif typ == "group" and id_val in groups:
                    groups.remove(id_val)
                    changed = True
            if changed:
                # Build new config text
                config_text = (
                    f"USERS: {', '.join(str(u) for u in users)}\n"
                    f"CHANNELS: {', '.join(str(c) for c in channels)}\n"
                    f"GROUPS: {', '.join(str(g) for g in groups)}"
                )
                # Update pinned message in Saved Messages
                chat = await client.get_chat(my_id)
                pinned = chat.pinned_message
                if pinned:
                    await pinned.edit_text(config_text)
                else:
                    sent = await client.send_message(my_id, config_text)
                    await sent.pin()
                # Reload config instantly
                Config.TARGET_USER_IDS = users
                Config.TARGET_CHANNEL_IDS = channels + groups
                # Auto-cache new ID immediately
                try:
                    if action.lower() == "add":
                        if typ == "user":
                            user = await client.get_users(id_val)
                            logger.info(f"✅ Auto-cached user: {user.first_name}")
                        elif typ == "channel" or typ == "group":
                            chat_obj = await client.get_chat(id_val)
                            logger.info(f"✅ Auto-cached {typ}: {chat_obj.title}")
                except Exception as e:
                    logger.warning(f"⚠️ Auto-cache failed for {typ} {id_val}: {e}")
                logger.info(f"🔄 Updated monitored IDs via admin command: USERS={users}, CHANNELS={channels}, GROUPS={groups}")
                await message.reply(f"✅ Updated config: {typ} {action} {id_val}")
            else:
                await message.reply(f"ℹ️ No change: {typ} {action} {id_val}")

        # Register generic message handler - no filters to catch everything
        @app.on_message()
        async def handle_message(client, message):
            # Skip edited messages
            if message.edit_date:
                return
            # Only skip admin commands, allow all other messages including from saved messages
            if message.text:
                import re
                if re.match(r"/(add|remove)\s+(user|channel|group)\s+(-?\d+)", message.text.strip(), re.I):
                    return
            await message_handler(client, message)

        # Start the client and run startup tasks
        with app:
            # Load config from pinned message
            my_id = app.loop.run_until_complete(startup_config())
            
            # Cache all peers on startup to prevent "Peer id invalid" errors
            app.loop.run_until_complete(cache_all_peers_startup(app))
            
            logger.info("👤 Telegram Vault Userbot started successfully!")
            if Config.TARGET_USER_IDS:
                logger.info(f"📌 Monitoring user IDs: {Config.TARGET_USER_IDS}")
            if Config.TARGET_CHANNEL_IDS:
                logger.info(f"📢 Monitoring channels/groups: {Config.TARGET_CHANNEL_IDS}")
            logger.info(f"📦 Vault chat ID: {Config.VAULT_CHAT_ID}")
            logger.info("⏳ Running in USER MODE...")
            logger.info("💡 This will monitor ALL groups you're a member of")
            
            # Start background polling task for channels
            app.loop.create_task(poll_channels(app))
            
            # Keep running
            app.loop.run_forever()
        logger.info("Userbot client stopped cleanly.")

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return
    except Exception as e:
        logger.error(f"Failed to start userbot: {str(e)}")
        try:
            if 'app' in locals() and app.is_connected:
                app.stop()
        except:
            pass
        return


if __name__ == '__main__':
    main()

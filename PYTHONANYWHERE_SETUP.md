# PythonAnywhere Deployment Guide

## 1. Sign Up & Upload Files
1. Go to `pythonanywhere.com` and create a free account
2. Dashboard → Files → Upload files or use Git:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

## 2. Install Dependencies
Dashboard → Consoles → Bash:
```bash
pip3.10 install --user pyrogram tgcrypto python-dotenv
```

## 3. Configure Environment
Create `.env` file in your project directory:
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
VAULT_CHAT_ID=your_vault_chat_id
TARGET_USER_ID=user_ids_comma_separated
TARGET_CHANNELS=channel_ids_comma_separated
```

## 4. Upload Session File
- If you have `vault_userbot.session` file, upload it to your project directory
- Or run the bot once locally to generate it, then upload

## 5. Create Always-On Task
Dashboard → Tasks → Create scheduled task:
- **Command**: `python3.10 /home/yourusername/start_pythonanywhere.py`
- **Hour**: `*` (every hour)
- **Minute**: `0`
- **Enabled**: ✅

## 6. Test Run
Before creating the task, test manually:
```bash
cd /home/yourusername/your-project
python3.10 start_pythonanywhere.py
```

## Key Benefits
- ✅ **100% Free** - No credit card required
- ✅ **Always Running** - Tasks restart automatically if they crash
- ✅ **No Sleep** - Unlike Render/Heroku free tiers
- ✅ **512MB RAM** - Perfect for Telegram bots
- ✅ **Simple Setup** - Web-based interface

## Monitoring
- Dashboard → Tasks → View logs
- Dashboard → Consoles → Bash to check files
- Check error logs if the task fails

## Important Notes
- Free accounts get 1 always-on task
- Task runs every hour (restarts if stopped)
- Logs are available in the Tasks section
- Session file persists between restarts
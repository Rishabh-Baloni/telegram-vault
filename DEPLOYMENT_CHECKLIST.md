# PythonAnywhere Deployment Checklist

## Pre-Deployment (Local)
- [ ] Test bot locally to ensure it works
- [ ] Generate `vault_userbot.session` file
- [ ] Create `.env` file with all required variables
- [ ] Verify all target IDs are correct

## PythonAnywhere Setup
- [ ] Create free account at pythonanywhere.com
- [ ] Upload all project files via Files tab
- [ ] Install dependencies: `pip3.10 install --user pyrogram tgcrypto python-dotenv`
- [ ] Upload session file to project directory
- [ ] Test run: `python3.10 start_pythonanywhere.py`

## Create Always-On Task
- [ ] Go to Dashboard → Tasks
- [ ] Click "Create scheduled task"
- [ ] Command: `python3.10 /home/yourusername/start_pythonanywhere.py`
- [ ] Hour: `*`
- [ ] Minute: `0`
- [ ] Enable the task

## Verification
- [ ] Check task logs for successful startup
- [ ] Send test message to monitored channel/user
- [ ] Verify message appears in vault
- [ ] Monitor for 24 hours to ensure stability

## Files Needed
- `userbot.py` (modified for PythonAnywhere)
- `config.py`
- `start_pythonanywhere.py`
- `.env` (with your credentials)
- `vault_userbot.session`
- `requirements.txt`

## Environment Variables Required
```
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
PHONE_NUMBER=your_phone_number
VAULT_CHAT_ID=your_vault_chat_id
TARGET_USER_ID=comma_separated_user_ids
TARGET_CHANNELS=comma_separated_channel_ids
```
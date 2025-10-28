# 📦 Telegram Vault - Userbot

Automatically collects and forwards messages from specific users and channels to a private vault channel using your personal Telegram account.

## 🎯 Features

- **Personal Account Integration**: Uses your Telegram account to monitor all groups you're in
- **Multi-Target Support**: Track multiple users, channels, and groups simultaneously
- **Anonymous Admin Detection**: Captures anonymous admin messages from monitored groups
- **Real-time Forwarding**: Instantly forwards matching messages to your vault
- **Zero Database**: No storage required - messages are forwarded directly
- **24/7 Operation**: Runs continuously and reliably

## 📋 Requirements

- Python 3.8+
- Telegram API credentials (from [my.telegram.org/apps](https://my.telegram.org/apps))
- Your phone number
- Vault Channel/Chat ID
- Configuration via Telegram pinned message

## 🚀 Quick Setup

### 1. Get API Credentials

1. Go to [my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your phone number
3. Create an app and note down:
   - `API_ID` (numeric)
   - `API_HASH` (alphanumeric)

### 2. Create Virtual Environment

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure via Environment Variables

Set these environment variables (for deployment platforms):

```properties
# API Credentials from my.telegram.org/apps
API_ID=27102935
API_HASH=your_api_hash_here
PHONE_NUMBER=+1234567890

# Vault channel to forward messages to
VAULT_CHAT_ID=-1003224847847
```

### 5. Configure Targets via Pinned Message

Create a pinned message in your vault channel with this format:

```
🎯 USERBOT TARGETS

👤 USERS:
123456789
987654321

📢 CHANNELS:
-1001234567890
-1002209287228

👥 GROUPS:
-1001111111111
-1002222222222
```

### 6. Get Chat IDs

**For User IDs:**
- Forward a message from the user to [@userinfobot](https://t.me/userinfobot)
- It will show: `Id: 123456789`

**For Channel/Group IDs:**
- Forward a message from the channel/group to [@userinfobot](https://t.me/userinfobot)
- For channels/supergroups, add `-100` prefix to the ID
- Example: If bot shows `2209287228`, use `-1002209287228`

**For Vault Channel:**
- Create a private channel
- Add yourself as admin
- Get the ID using [@userinfobot](https://t.me/userinfobot)
- Use format: `-1003224847847`

### 7. Run the Userbot

```bash
python run.py
```

On first run, you'll be asked to enter:
1. Verification code (sent to your Telegram)
2. Two-factor password (if enabled)

The session will be saved and you won't need to login again.

## 📱 Usage Examples

### Track Multiple Users

Update your pinned message:
```
🎯 USERBOT TARGETS

👤 USERS:
123456789
987654321
555666777
```

### Track Channels and Groups

Update your pinned message:
```
🎯 USERBOT TARGETS

📢 CHANNELS:
-1001234567890
-1002209287228

👥 GROUPS:
-1001111111111
```

### Track Both Users and Channels

Update your pinned message:
```
🎯 USERBOT TARGETS

👤 USERS:
123456789
987654321

📢 CHANNELS:
-1001234567890
-1002209287228
```

### Anonymous Admin Messages

The userbot automatically captures messages from anonymous admins in monitored groups. Just add the group ID to your pinned message:

```
🎯 USERBOT TARGETS

👥 GROUPS:
-1002209287228
```

## 🔧 Troubleshooting

### "Peer id invalid" Error

**Solution:** You need to interact with the vault channel first:
1. Open your vault channel in Telegram
2. Send any message
3. Restart the userbot

### Messages Not Forwarding

**Check:**
1. Are you a member of the source group/channel?
2. Is the user ID correct? (use [@userinfobot](https://t.me/userinfobot))
3. For channels/groups, did you add `-100` prefix?
4. Did you interact with the vault channel first?
5. Is your pinned message formatted correctly?

### Anonymous Admin Messages Not Working

**Verify:**
1. Group ID has `-100` prefix in pinned message under 👥 GROUPS
2. You have admin rights in the group
3. The group allows anonymous posting
4. Check logs for "ANONYMOUS MESSAGE DETECTED"

### Session File Issues

**Solution:** Delete the session file and restart:
```bash
# Windows
Remove-Item "TelegramVault.session"

# Linux/Mac  
rm TelegramVault.session
```

Then run `python run.py` again to re-authenticate.

## 🌐 24/7 Deployment on Railway (FREE!)

For continuous operation, deploy to Railway.app - **completely FREE, no credit card required!**

### Railway.app (Recommended - Free Forever)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed step-by-step instructions.

**Benefits:**
- ✅ $5 free credit per month (enough for 24/7 operation)
- ✅ No credit card required
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ ~500+ hours free runtime monthly
- ✅ Simple setup in 10 minutes

### Quick Deploy Steps:
1. Push your code to GitHub (private repo)
2. Sign up on Railway.app with GitHub
3. Deploy from your repository
4. Add environment variables (API_ID, API_HASH, PHONE_NUMBER, VAULT_CHAT_ID)
5. Create pinned message in vault channel with targets
6. Done! Bot runs 24/7 for FREE

**Detailed guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

## 🛡️ Security Notes

1. **Never share your API credentials** - keep them secure
2. **Use 2FA** on your Telegram account
3. **Monitor session** - watch for unusual activity
4. **Respect Privacy** - only monitor content you have permission to access
5. **Backup Session** - keep `TelegramVault.session` file safe

## ⚠️ Important Warnings

- Using userbots is against Telegram's Terms of Service
- Excessive automation may result in account restrictions
- Use responsibly and only for personal/authorized purposes
- Consider rate limits (don't flood your vault)
- Keep the project private

## 📂 Project Structure

```
telegram-vault/
├── run.py              # Main launcher
├── userbot.py          # Userbot implementation
├── config.py           # Configuration loader
├── requirements.txt    # Python dependencies
├── RULES.txt          # Project rules
└── README.md          # This file
```

## 🐛 Debug Mode

To see detailed logs including Pyrogram debug info, the userbot already runs with DEBUG logging enabled. Check the console output for:

- `🔍 ANONYMOUS MESSAGE DETECTED:` - Anonymous admin message details
- `📩 Target message detected!` - Matched message info
- `✅ Successfully forwarded message` - Successful forwards
- `❌ Error:` - Any errors encountered

## 📝 License

This project is for educational purposes only. Use at your own risk.

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your `.env` configuration
3. Check console logs for error messages
4. Ensure Python 3.8+ is installed

## 🔄 Updates

To update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## 💡 Tips

1. **Test First**: Start with one user/channel before adding many
2. **Monitor Logs**: Keep an eye on console output initially
3. **Session Management**: Back up your session file regularly
4. **Rate Limiting**: Don't monitor too many high-volume channels
5. **Vault Organization**: Consider using topic/folder in vault channel for organization

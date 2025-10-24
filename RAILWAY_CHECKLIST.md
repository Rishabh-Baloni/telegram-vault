# 🚀 Quick Railway Deploy Checklist

## ✅ Pre-Deployment Checklist

Before deploying to Railway, make sure you have:

### 1. Files Ready
- [x] `run.py` - Main launcher
- [x] `userbot.py` - Userbot code
- [x] `config.py` - Configuration loader
- [x] `requirements.txt` - Dependencies
- [x] `Procfile` - Railway start command
- [x] `.env.example` - Template (don't commit real .env!)
- [x] `.gitignore` - Protects secrets
- [ ] `vault_userbot.session` - Your session file (optional - can authenticate on Railway)

### 2. Configuration Ready
- [ ] API_ID from my.telegram.org
- [ ] API_HASH from my.telegram.org
- [ ] PHONE_NUMBER with country code
- [ ] VAULT_CHAT_ID (your vault channel)
- [ ] TARGET_USER_ID (users to monitor)
- [ ] TARGET_CHANNELS (channels/groups to monitor)

### 3. Test Locally First
- [ ] Tested userbot locally
- [ ] Messages forwarding correctly
- [ ] Anonymous admin messages working
- [ ] No errors in logs

## 📦 Deployment Steps

### Step 1: GitHub Setup (5 min)
```powershell
cd "d:\Projects\Mini Project\New folder (3)"

# Initialize git
git init

# Add files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit - Railway ready"

# Create GitHub repo and push
# Follow instructions in DEPLOYMENT.md
```

### Step 2: Railway Setup (3 min)
1. Go to https://railway.app
2. Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Step 3: Configure (2 min)
1. Click your service → "Variables" tab
2. Click "RAW Editor"
3. Paste your .env contents
4. Click "Update Variables"

### Step 4: Deploy & Monitor
1. Railway auto-deploys
2. Go to "Deployments" → "View Logs"
3. Should see: "👤 Telegram Vault Userbot started successfully!"
4. Test by sending a message from monitored user

## 🎉 Done!

Your bot is now running 24/7 on Railway for FREE!

## 📊 Monitor Usage

Check Railway dashboard to see:
- Current credit usage
- Remaining free credits
- Deployment status
- Live logs

## 💡 Pro Tips

1. **Keep repo private** - Don't share your code publicly
2. **Monitor daily** - Check logs for first few days
3. **Backup session** - Keep local copy of session file
4. **Update regularly** - Push updates via git

## 🆘 Need Help?

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
2. Check Railway logs for errors
3. Verify all environment variables are set
4. Make sure you're in monitored groups/channels

## 🔄 Update Your Bot

```powershell
# Make changes to code
git add .
git commit -m "Update description"
git push

# Railway auto-deploys!
```

# 🚂 Railway.app Free Deployment Guide
## Deploy Your Telegram Userbot for FREE (No Credit Card Required!)

---

## 📋 What You'll Get
- ✅ $5 free credit per month (enough for 24/7 operation)
- ✅ No credit card required
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ 500+ hours free per month

**Total Setup Time: ~10 minutes**

---

## PART 1: Prepare Your Files

### Step 1: Create .gitignore
Make sure you have a `.gitignore` file to protect sensitive data:

```
venv/
__pycache__/
*.pyc
*.session
*.session-journal
.env
```

**IMPORTANT:** Don't commit `.env` or session files to GitHub!

---

## PART 2: Push to GitHub

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Name: `telegram-vault-userbot` (or any name you want)
3. Set to **Private** (important for security!)
4. Don't initialize with README
5. Click **"Create repository"**

### Step 2: Push Your Code
```powershell
cd "d:\Projects\Mini Project\New folder (3)"

# Initialize git (if not already done)
git init

# Add all files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/telegram-vault-userbot.git

# Push
git branch -M main
git push -u origin main
```

---

## PART 3: Deploy to Railway

### Step 1: Sign Up
1. Go to https://railway.app
2. Click **"Login"** or **"Start a New Project"**
3. Click **"Login with GitHub"**
4. Authorize Railway to access your GitHub

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `telegram-vault-userbot`
4. Click on the repository to deploy

### Step 3: Configure Environment Variables
1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"RAW Editor"**
4. Paste your `.env` contents:

```properties
API_ID=27102935
API_HASH=your_api_hash_here
PHONE_NUMBER=+919045516573
VAULT_CHAT_ID=-1003224847847
TARGET_USER_ID=993339693,1290365086,941927047,582868822,1010500439,1303354830,6096714326,1163970079,1078883294,5515536284
TARGET_CHANNELS=-1003074469948,-1001150779891,-1003137473266,-1001177289429,-1001521790999,-1002095518645,-1002083547614,-1001475939687,-1001827108721,-1001409153549,-1001515619731
```

5. Click **"Update Variables"**

### Step 4: Upload Session File
**IMPORTANT:** You need to upload your session file manually!

**Option A: Using Railway CLI (Recommended)**

1. Install Railway CLI:
```powershell
# Windows - using npm
npm install -g @railway/cli

# Or download from: https://docs.railway.app/develop/cli
```

2. Login and link project:
```powershell
railway login
railway link
```

3. Upload session file:
```powershell
# Connect to your service
railway shell

# Then in the Railway shell, upload your session files
# Exit the shell first with: exit
```

**Option B: Manual Upload via Service (Easier)**

Since Railway doesn't have direct file upload, we'll use a workaround:

1. Go to your service in Railway
2. Click **"Settings"** tab
3. Click **"Generate Domain"** (you'll get a URL like `xyz.railway.app`)
4. We'll modify the code to download session on first run

Let me create a helper script for you...

---

## PART 4: Handling Session File

### Option 1: Store Session in Environment Variable (Easiest)

Let me create a script to encode your session file:

**Run this locally:**
```powershell
# Encode session file to base64
$sessionContent = [Convert]::ToBase64String([IO.File]::ReadAllBytes("vault_userbot.session"))
$sessionContent | Out-File session_base64.txt

$journalContent = [Convert]::ToBase64String([IO.File]::ReadAllBytes("vault_userbot.session-journal"))
$journalContent | Out-File session_journal_base64.txt
```

Then add these to Railway environment variables:
- `SESSION_BASE64` = content of session_base64.txt
- `SESSION_JOURNAL_BASE64` = content of session_journal_base64.txt

### Option 2: Re-authenticate on Railway

If session upload is too complex, you can just let the userbot authenticate on Railway:

1. Deploy without session files
2. Go to Railway **"Deployments"** tab
3. Click on latest deployment → **"View Logs"**
4. You'll see the authentication code prompt
5. Enter the code from your Telegram

---

## PART 5: Configure Start Command

### Step 1: Add Procfile
Create a file named `Procfile` (no extension) in your project:

```
worker: python run.py
```

### Step 2: Or Set Start Command in Railway
1. Go to **"Settings"** tab
2. Scroll to **"Deploy"** section
3. Set **"Start Command"**: `python run.py`
4. Click **"Save"**

---

## PART 6: Deploy and Monitor

### Step 1: Deploy
1. Railway auto-deploys on code push
2. Or click **"Deploy"** button manually
3. Wait 2-3 minutes for deployment

### Step 2: Check Logs
1. Go to **"Deployments"** tab
2. Click latest deployment
3. Click **"View Logs"**
4. You should see:
```
👤 Starting Telegram Vault Userbot...
✓ Configuration validated successfully
👤 Telegram Vault Userbot started successfully!
📌 Monitoring user IDs: [...]
```

### Step 3: Verify It's Working
1. Send a test message from a monitored user
2. Check your vault channel
3. Message should appear instantly!

---

## 💰 Free Credit Usage

Railway gives you **$5 free credit per month**:
- ~500 hours of runtime
- More than enough for 24/7 operation
- Resets every month

**To get more free hours:**
1. Verify your account with GitHub
2. Join Railway Discord (optional extra credits)

---

## 🔧 Troubleshooting

### "Service keeps crashing"
- Check logs for errors
- Verify environment variables are set correctly
- Make sure session file is uploaded

### "No messages being forwarded"
- Check logs to see if bot started
- Verify TARGET_USER_ID and TARGET_CHANNELS are correct
- Make sure VAULT_CHAT_ID is accessible

### "Authentication required"
- If no session file, check logs for verification code prompt
- Enter code from Telegram app

### "Out of free credits"
- Railway gives $5/month free
- If you run out, add a small payment method (starts at $5)
- Or wait for next month's free credits

---

## 🔄 Updates and Maintenance

### Update Your Code
```powershell
# Make changes to your code
git add .
git commit -m "Update message"
git push

# Railway auto-deploys!
```

### View Logs
1. Go to Railway dashboard
2. Click your service
3. Go to **"Deployments"** → **"View Logs"**

### Restart Service
1. Go to **"Settings"**
2. Click **"Restart"**

---

## 🛡️ Security Tips

1. **Keep repository private** on GitHub
2. **Never commit** `.env` or session files
3. **Use strong passwords** for GitHub
4. **Enable 2FA** on both GitHub and Railway
5. **Monitor logs** regularly for unusual activity

---

## 🎉 Done!

Your Telegram Vault Userbot is now running 24/7 on Railway for FREE!

**Next Steps:**
- Monitor logs for first few hours
- Test with different message types
- Enjoy automated message collection!

---

## 💡 Pro Tips

1. **Railway CLI**: Use it for easier debugging and logs
2. **GitHub Actions**: Set up automated tests before deploy
3. **Monitoring**: Check Railway dashboard weekly
4. **Backup**: Keep local copy of session file safe
5. **Updates**: Pull latest Pyrogram updates occasionally

---

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check logs first - most issues show there!

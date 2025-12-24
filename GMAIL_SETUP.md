# Gmail Email Setup Guide

## Overview
The system is now configured to automatically email participant data to you via Gmail when they complete or exit the study. This works on Render's **free tier** without needing persistent disk storage!

## Step 1: Get Gmail App Password

You need to create an "App Password" for your Gmail account. This is a special password for applications.

### Requirements:
- ✅ Gmail account (can use your USC email if it's Gmail-based)
- ✅ 2-Step Verification enabled

### Instructions:

1. Go to your Google Account: https://myaccount.google.com
2. Click **Security** in the left sidebar
3. Scroll down to "How you sign in to Google"
4. Click **2-Step Verification**
   - If not enabled, click **Get Started** and follow the prompts
   - You'll need your phone for verification
5. Once 2-Step Verification is enabled, go back to **Security**
6. Scroll down and click **App passwords**
7. You may need to sign in again
8. Create an app password:
   - **Select app**: Mail
   - **Select device**: Other (custom name)
   - **Name it**: `a2i2-survey`
9. Click **Generate**
10. **IMPORTANT**: Copy the 16-character password that appears
    - It looks like: `abcd efgh ijkl mnop` (4 groups of 4 letters)
    - You won't see it again!
11. Save it somewhere secure (you'll need it for Render)

## Step 2: Configure Render Environment Variables

1. Go to your Render dashboard: https://dashboard.render.com
2. Find your service: `a2i2-survey-backend`
3. Click on it → **Environment** tab
4. Add these environment variables:

| Key | Value | Example |
|-----|-------|---------|
| `GMAIL_USER` | Your Gmail address | `tzhang62@gmail.com` or `tzhang62@usc.edu` |
| `GMAIL_APP_PASSWORD` | Your 16-char app password | `abcdefghijklmnop` (no spaces!) |
| `RESEARCHER_EMAIL` | Where data will be sent | `tzhang62@usc.edu` |

**Important Notes:**
- Remove all spaces from the app password (just 16 letters)
- `GMAIL_USER` is where emails come FROM
- `RESEARCHER_EMAIL` is where emails go TO
- They can be the same email address

5. Click **Save Changes**
6. Your service will automatically redeploy

## Step 3: Deploy Updated Code to Render

Your code is already pushed to GitHub. Now trigger a deploy:

1. In Render dashboard → Your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Watch the **Logs** tab during deployment
4. Look for successful build messages

## Step 4: Test It!

### Local Testing (Optional):
```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend

# Set environment variables temporarily
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export RESEARCHER_EMAIL="your-email@gmail.com"

# Restart server
python server.py
```

### On Render:
1. After deployment completes, go to your survey URL
2. Complete a test survey (all 6 conversations)
3. Check your email inbox!
4. You should receive an email with JSON attachment

## What Gets Emailed?

When a participant **completes** the study:
- **Subject**: "Study Complete: CCC001"
- **From**: Your Gmail address
- **To**: Your researcher email
- **Attachment**: `CCC001.json` with all data (survey, conversations, post-surveys)

When a participant **exits** early:
- **Subject**: "Study Exit: INC001"
- **Attachment**: `INC001.json` with partial data

Each email includes:
- Confirmation number
- Status (complete/incomplete)
- Timestamp
- Complete JSON data as attachment

## Gmail Limits

**Free Gmail Account:**
- ✅ 500 emails per day
- ✅ More than enough for research studies
- ✅ No cost

**Google Workspace (if using USC email):**
- ✅ 2,000 emails per day
- ✅ Better for large-scale studies

## Troubleshooting

### "Gmail credentials not set"
Check Render logs:
1. Go to your service → **Logs** tab
2. Look for `[EMAIL]` messages
3. Make sure all 3 environment variables are set correctly
4. No typos in variable names!

### "Authentication failed" or "Username and Password not accepted"
- ✅ Make sure 2-Step Verification is enabled
- ✅ Use the **App Password**, not your regular Gmail password
- ✅ Remove all spaces from the app password
- ✅ Copy-paste the password carefully

### "Connection refused" or "SMTP error"
- Gmail SMTP might be blocked by firewall
- Try regenerating the app password
- Make sure you're using `GMAIL_APP_PASSWORD` not regular password

### Test your Gmail credentials locally:
```python
import smtplib

gmail_user = "your-email@gmail.com"
gmail_password = "your-app-password"

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_password)
        print("✅ Gmail login successful!")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Check Render Logs
If emails aren't sending:
1. Go to Render → Your service → **Logs**
2. Look for messages like:
   - `[EMAIL] Sent CCC001 to your-email via Gmail` ✅ Success
   - `[EMAIL] Gmail credentials not set` ❌ Missing env vars
   - `[ERROR] Failed to email via Gmail` ❌ Check error details

## Email Storage

Your data is now in **two places**:
1. ✅ **Gmail inbox**: Permanent, searchable, easy to access
2. ✅ **Render disk** (if using paid tier): Backup on server

Even on free tier without persistent disk, you'll have all data in your Gmail inbox! 📧

## Security Notes

⚠️ **Keep your app password secure**:
- Never commit it to GitHub
- Only add it as environment variable in Render
- If compromised, revoke it in Google Account settings

✅ **Email privacy**:
- Only you can access your Gmail account
- Data is encrypted in transit (TLS/SSL)
- Consider using a dedicated research Gmail account

## Revoking App Password

If you need to revoke the password:
1. Go to https://myaccount.google.com/security
2. Click **App passwords**
3. Find "a2i2-survey" in the list
4. Click the ❌ to remove it
5. Generate a new one if needed

## Alternative: Using USC Email

If your USC email uses Gmail (like `@usc.edu`):
1. Use your USC email for `GMAIL_USER`
2. Follow the same app password process
3. Benefits: Higher sending limits, institutional backing

## Advantages Over SendGrid

✅ **No third-party signup needed**  
✅ **Use existing Gmail account**  
✅ **Higher daily limit (500 vs 100)**  
✅ **Simpler setup**  
✅ **Better for research/academic use**  

## Next Steps

1. ✅ Enable 2-Step Verification on Gmail
2. ✅ Generate App Password
3. ✅ Add environment variables to Render
4. ✅ Deploy the latest code
5. ✅ Test with a complete survey
6. ✅ Check your email!

---

**Questions or issues?** Check the Render logs first, then test your Gmail credentials locally!

## Quick Reference

### Environment Variables:
```
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
RESEARCHER_EMAIL=your-email@gmail.com
```

### Gmail SMTP Settings:
- **Server**: smtp.gmail.com
- **Port**: 465 (SSL)
- **Authentication**: Required

That's it! Your survey data will now be automatically emailed to you via Gmail! 📧✨


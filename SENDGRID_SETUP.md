# SendGrid Email Setup Guide

## Overview
The system is now configured to automatically email participant data to you when they complete or exit the study. This works on Render's **free tier** without needing persistent disk storage!

## Step 1: Create SendGrid Account

1. Go to https://sendgrid.com
2. Click **"Start for Free"**
3. Sign up with your email (use your USC email)
4. Verify your email address
5. Complete the account setup

**Free Tier Includes:**
- ✅ 100 emails per day (plenty for research studies)
- ✅ No credit card required
- ✅ Full API access

## Step 2: Verify Sender Identity

SendGrid requires you to verify your sender email address:

### Option A: Single Sender Verification (Easier, Recommended)
1. In SendGrid dashboard, go to **Settings** → **Sender Authentication**
2. Click **"Get Started"** under "Single Sender Verification"
3. Fill in:
   - **From Name**: A2I2 Survey System
   - **From Email Address**: Your email (e.g., tzhang62@usc.edu)
   - **Reply To**: Same email
   - **Nickname**: a2i2-survey
4. Click **"Create"**
5. Check your email and click the verification link
6. ✅ Done! This email will be used as the sender

### Option B: Domain Authentication (More Professional)
1. If you own a domain, go to **Settings** → **Sender Authentication**
2. Click **"Authenticate Your Domain"**
3. Follow the DNS setup instructions
4. Use your domain email as sender

## Step 3: Create API Key

1. In SendGrid dashboard, go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name it: `a2i2-survey-backend`
4. Select **"Full Access"** (for simplicity)
5. Click **"Create & View"**
6. **IMPORTANT**: Copy the API key now! You won't see it again
   - It looks like: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
7. Save it somewhere secure (you'll need it for Render)

## Step 4: Configure Render Environment Variables

### If Using Blueprint (render.yaml):
1. Go to your Render dashboard: https://dashboard.render.com
2. Find your service: `a2i2-survey-backend`
3. Click on it → **Environment** tab
4. Add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `SENDGRID_API_KEY` | `SG.xxx...` | Your SendGrid API key |
| `RESEARCHER_EMAIL` | `your-email@usc.edu` | Where data will be sent |
| `SENDER_EMAIL` | `your-verified-email@usc.edu` | Must match verified sender |

5. Click **"Save Changes"**
6. Your service will automatically redeploy

### If Manual Setup:
Add the same three variables during service creation or in the Environment tab.

## Step 5: Test It!

### Local Testing:
```bash
# In your backend directory
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend

# Set environment variables temporarily
export SENDGRID_API_KEY="SG.your-key-here"
export RESEARCHER_EMAIL="your-email@usc.edu"
export SENDER_EMAIL="your-verified-email@usc.edu"

# Restart server
python server.py
```

Then complete a test survey and check your email!

### On Render:
1. After adding environment variables, Render will redeploy
2. Check the **Logs** tab to see if there are any errors
3. Complete a test survey
4. Check your email inbox!

## What Gets Emailed?

When a participant **completes** the study:
- **Subject**: "Study Complete: CCC001"
- **Attachment**: `CCC001.json` with all data

When a participant **exits** early:
- **Subject**: "Study Exit: INC001"
- **Attachment**: `INC001.json` with partial data

Each email includes:
- Confirmation number
- Status (complete/incomplete)
- Timestamp
- Complete JSON data as attachment

## Troubleshooting

### "Email failed to send"
Check Render logs:
1. Go to your service → **Logs** tab
2. Look for `[EMAIL]` or `[ERROR]` messages
3. Common issues:
   - SENDGRID_API_KEY not set or incorrect
   - Sender email not verified in SendGrid
   - API key permissions insufficient

### "Sender email not verified"
1. Go to SendGrid → Settings → Sender Authentication
2. Make sure your email shows "Verified" status
3. If not, resend verification email

### "Daily send limit exceeded"
- Free tier: 100 emails/day
- If you exceed this, wait 24 hours or upgrade to paid tier
- For studies, this is usually sufficient (100 participants/day)

### Check SendGrid Activity
1. Go to SendGrid dashboard → **Activity**
2. See all emails sent, delivery status, and any errors
3. Very helpful for debugging!

## Email Storage

Your data is now in **two places**:
1. ✅ **Email inbox**: Permanent, searchable, easy to access
2. ✅ **Render disk** (if using paid tier): Backup on server

Even on free tier without persistent disk, you'll have all data in your email! 📧

## Security Notes

⚠️ **Keep your API key secure**:
- Never commit it to GitHub
- Only add it as environment variable in Render
- If compromised, regenerate in SendGrid dashboard

✅ **Email privacy**:
- Participant data is sent only to your verified email
- SendGrid is HIPAA compliant (if needed)
- Data is encrypted in transit (TLS)

## Upgrading Email Limits

If you need more than 100 emails/day:

### SendGrid Plans:
- **Free**: 100 emails/day
- **Essentials**: $19.95/month for 50,000 emails/month
- **Pro**: $89.95/month for 1.5M emails/month

For most research studies, **free tier is sufficient**!

## Next Steps

1. ✅ Create SendGrid account
2. ✅ Verify sender email
3. ✅ Get API key
4. ✅ Add to Render environment variables
5. ✅ Test with a complete survey flow
6. ✅ Check your email!

Need help? Check SendGrid's documentation: https://docs.sendgrid.com/

---

**Questions or issues?** Check the Render logs first, then SendGrid Activity feed!


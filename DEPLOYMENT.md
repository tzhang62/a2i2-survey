# Deployment Guide for A2I2 Survey System

This guide will help you deploy your survey system to make it publicly available.

## Prerequisites

- GitHub account
- Render account (for backend): https://render.com
- Netlify account (for frontend): https://netlify.com
- OpenAI API key

## Step 1: Prepare Your Repository

1. Create a new GitHub repository
2. Push your code to GitHub:
```bash
cd /Users/tzhang/projects/a2i2_survey
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/a2i2-survey.git
git push -u origin main
```

## Step 2: Deploy Backend to Render

### Option A: Using render.yaml (Recommended)

1. Go to https://render.com and sign in
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Set the following environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ADMIN_KEY`: Create a secure random string for data export (save this!)
   - `OPENAI_MODEL`: `gpt-4o-mini` (or your preferred model)

### Option B: Manual Setup

1. Go to https://render.com and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `a2i2-survey-backend`
   - **Root Directory**: `a2i2_chatbot/backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Instance Type**: Free (or paid for better performance)
5. Add Environment Variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ADMIN_KEY`: 02bc3a6563641db8b4f2e5aa37f64b89
   - `OPENAI_MODEL`: `gpt-4o-mini`
6. Click "Create Web Service"
7. **Add Persistent Disk** (Important for data storage):
   - Go to your service settings
   - Click "Disks" → "Add Disk"
   - **Name**: `survey-data`
   - **Mount Path**: `/opt/render/project/src/a2i2_chatbot/backend/survey_responses`
   - **Size**: 1GB (or more if needed)
   - Click "Save"

### Get Your Backend URL

After deployment, your backend URL will be:
```
https://a2i2-survey-backend.onrender.com
```
(or similar - copy the exact URL from Render dashboard)

## Step 3: Update Frontend Configuration

1. Edit `a2i2_chatbot/frontend/config.js`
2. Replace `'https://your-backend-url.onrender.com'` with your actual Render URL:
```javascript
API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8001' 
  : 'https://a2i2-survey-backend.onrender.com', // Your actual URL
```
3. Commit and push:
```bash
git add a2i2_chatbot/frontend/config.js
git commit -m "Update backend URL"
git push
```

## Step 4: Deploy Frontend to Netlify

### Option A: Using Netlify CLI

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Deploy:
```bash
cd a2i2_chatbot/frontend
netlify deploy --prod
```

3. Follow the prompts:
   - Create & configure a new site
   - Publish directory: `.` (current directory)

### Option B: Using Netlify Dashboard

1. Go to https://netlify.com and sign in
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub and select your repository
4. Configure:
   - **Branch**: `main`
   - **Base directory**: `a2i2_chatbot/frontend`
   - **Build command**: (leave empty)
   - **Publish directory**: `.`
5. Click "Deploy site"

### Get Your Frontend URL

Your survey will be available at:
```
https://your-site-name.netlify.app
```

## Step 5: Test Your Deployment

1. Visit your Netlify URL
2. Complete the consent form
3. Fill out the survey
4. Test the chat conversations
5. Verify data is being saved (check admin panel)

## Step 6: Download Collected Data

### Using the Admin Panel

1. Create `a2i2_chatbot/frontend/admin.html` (see below)
2. Visit: `https://your-site-name.netlify.app/admin.html`
3. Enter your ADMIN_KEY
4. Click "Download All Data" to get a ZIP file

### Using Direct API Call

You can also download data using curl:
```bash
curl "https://a2i2-survey-backend.onrender.com/api/admin/export-data?admin_key=YOUR_ADMIN_KEY" -o study_data.zip
```

### Get Statistics

```bash
curl "https://a2i2-survey-backend.onrender.com/api/admin/stats?admin_key=YOUR_ADMIN_KEY"
```

## Data Structure

Downloaded data will include:

```
study_data_export_TIMESTAMP.zip
├── _export_summary.json          # Export metadata
├── {participant_id}.json          # Individual survey responses
├── confirmation_numbers.json      # Confirmation number tracking
├── completed/
│   └── CCC###.json               # Complete study data
├── exits/
│   └── INC###.json               # Incomplete/exit data
└── post_surveys/
    ├── post_{session_id}.json    # Individual post-surveys
    └── all_post_surveys.jsonl    # All post-surveys (one per line)
```

## Security Notes

1. **Keep your ADMIN_KEY secret** - this is needed to download data
2. Never commit your `.env` file or expose your OPENAI_API_KEY
3. The admin panel should only be used by researchers
4. Render's free tier may spin down after inactivity - consider paid tier for production

## Costs

- **Render Free Tier**: $0/month (spins down after 15min inactivity)
- **Render Starter**: $7/month (always on)
- **Netlify**: Free for static sites
- **OpenAI API**: Pay per use (gpt-4o-mini is ~$0.15/$0.60 per 1M tokens)
- **Render Disk**: ~$0.25/GB/month

## Troubleshooting

### Backend not responding
- Check Render logs
- Verify environment variables are set
- Ensure disk is properly mounted

### Frontend can't connect to backend
- Verify backend URL in config.js
- Check CORS settings in server.py (already configured)
- Ensure backend is running (not spun down)

### Data not saving
- Check Render disk is mounted correctly
- Verify write permissions
- Check backend logs for errors

## Support

For issues, check:
1. Render logs: https://dashboard.render.com
2. Netlify logs: https://app.netlify.com
3. Browser console (F12) for frontend errors


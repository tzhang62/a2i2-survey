# Upload These Files to Hugging Face Space

This folder contains all the files you need to upload to your Hugging Face Space.

## Files in This Folder:

- ✅ `app.py` - FastAPI application for your IQL model
- ✅ `requirements.txt` - Python dependencies
- ✅ `label_map.json` - Policy label mappings
- ✅ `iql_model_embed.pt` - Your trained IQL model (~12MB)

## Upload Instructions:

### Step 1: Create Space
1. Go to **https://huggingface.co/spaces**
2. Click **"Create new Space"**
3. Fill in:
   - **Owner**: tzhang62 (your username)
   - **Space name**: `iql-fire-rescue-api`
   - **License**: Apache 2.0 (or your choice)
   - **Select SDK**: **Docker** (important!)
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public
4. Click **"Create Space"**

### Step 2: Upload Files

#### Option A: Via Web Interface (Easiest)
1. In your new Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload ALL 4 files from this folder:
   - `app.py`
   - `requirements.txt`
   - `label_map.json`
   - `iql_model_embed.pt`
4. Commit the changes

#### Option B: Via Git (Advanced)
```bash
# Clone your Space
git clone https://huggingface.co/spaces/tzhang62/iql-fire-rescue-api
cd iql-fire-rescue-api

# Copy files
cp /Users/tzhang/projects/a2i2_survey/hf_space_files/* .

# Push to Space
git add .
git commit -m "Add IQL model API"
git push
```

### Step 3: Wait for Build
- Space will automatically start building
- This takes **5-10 minutes** the first time
- Watch the **"Logs"** tab to see progress
- When you see "Application startup complete", it's ready!

### Step 4: Test Your Space
Once running, test it:

```bash
curl -X POST https://tzhang62-iql-fire-rescue-api.hf.space/ \
  -H "Content-Type: application/json" \
  -d '{"inputs": "I need help | What should I do?", "parameters": {"character": "bob"}}'
```

Expected response:
```json
{
  "policy": "give_direction",
  "q_values": {
    "provide_information": 0.123,
    "give_direction": 0.876,
    ...
  }
}
```

### Step 5: Update Render Backend

After your Space is running, update Render environment variables:

1. Go to **Render Dashboard** → Your service → **Environment**
2. Update/Add these variables:
   ```
   HUGGINGFACE_MODEL_ID = tzhang62-iql-fire-rescue-api.hf.space
   HUGGINGFACE_TOKEN = (get from https://huggingface.co/settings/tokens)
   ```
3. Click **"Save Changes"**
4. Render will auto-redeploy

### Step 6: Get HF Token

1. Go to https://huggingface.co/settings/tokens
2. Click **"Create new token"**
3. Name: `a2i2-render-backend`
4. Type: **Read**
5. Click **"Generate token"**
6. Copy the token (starts with `hf_...`)
7. Add to Render as `HUGGINGFACE_TOKEN`

## Your Space URL:

After deployment: `https://tzhang62-iql-fire-rescue-api.hf.space`

## Troubleshooting:

### Build Fails
- Check logs in "Logs" tab
- Make sure all 4 files are uploaded
- Verify SDK is set to "Docker"

### Model Not Loading
- Check that `label_map.json` and `iql_model_embed.pt` are in the root directory
- Check logs for error messages

### API Returns 404
- Wait for build to complete (check "Running" status)
- Make sure you're using the correct URL

## Cost:

✅ **FREE** - HF Spaces with CPU basic is free!

## Next Steps After Space is Running:

1. Test your Netlify survey
2. Go to Session 2 (role-play)
3. Should be **much faster** now (2-5 seconds)!

Good luck! 🚀


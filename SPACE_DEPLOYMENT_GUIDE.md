# 🚀 Hugging Face Space Deployment - Quick Guide

## ✅ Files Ready!

All files are prepared in: `/Users/tzhang/projects/a2i2_survey/hf_space_files/`

Files ready to upload:
- ✅ `app.py` (5.5KB) - Your API server
- ✅ `requirements.txt` (106B) - Dependencies
- ✅ `label_map.json` (73B) - Policy labels
- ✅ `iql_model_embed.pt` (7.0MB) - Your IQL model

---

## 📋 Step-by-Step Instructions

### Step 1: Create the Space (2 minutes)

1. **Open** → https://huggingface.co/spaces
2. **Click** → "Create new Space"
3. **Fill in**:
   ```
   Owner: tzhang62
   Space name: iql-fire-rescue-api
   SDK: Docker ⚠️ (MUST select Docker!)
   Hardware: CPU basic (free)
   Visibility: Public
   ```
4. **Click** → "Create Space"

---

### Step 2: Upload Files (3 minutes)

**Via Web Interface** (easiest):

1. In your new Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. **Drag and drop** all 4 files from `hf_space_files/` folder:
   - `app.py`
   - `requirements.txt`
   - `label_map.json`
   - `iql_model_embed.pt`
4. Click **"Commit to main"**

**Important**: Make sure all files are in the **root directory**, not in a subfolder!

---

### Step 3: Wait for Build (5-10 minutes)

1. Click **"Logs"** tab in your Space
2. You'll see:
   ```
   Building application...
   Installing dependencies...
   Starting server...
   Application startup complete
   ```
3. When you see **"Running"** status at top → ✅ **Ready!**

---

### Step 4: Test Your Space (1 minute)

Open a terminal and test:

```bash
curl -X POST https://tzhang62-iql-fire-rescue-api.hf.space/ \
  -H "Content-Type: application/json" \
  -d '{"inputs": "I need help", "parameters": {"character": "bob"}}'
```

**Expected response**:
```json
{
  "policy": "give_direction",
  "q_values": {
    "provide_information": 0.12,
    "offer_assistance": 0.15,
    "express_urgency": 0.45,
    "ask_question": 0.08,
    "give_direction": 0.78,
    "acknowledge_concern": 0.20,
    "build_rapport": 0.10
  }
}
```

If you get this → ✅ **Space is working!**

---

### Step 5: Get HF Token (1 minute)

1. Go to **https://huggingface.co/settings/tokens**
2. Click **"Create new token"**
3. Settings:
   ```
   Name: a2i2-render-backend
   Type: Read
   ```
4. Click **"Generate token"**
5. **Copy** the token (starts with `hf_...`)
6. **Save it** - you'll need it for Render!

---

### Step 6: Update Render (2 minutes)

1. Go to **Render Dashboard** → https://dashboard.render.com/
2. Select your service: **a2i2-survey-backend**
3. Click **"Environment"** in left sidebar
4. **Add/Update** these variables:

   ```
   HUGGINGFACE_MODEL_ID = tzhang62-iql-fire-rescue-api.hf.space
   HUGGINGFACE_TOKEN = hf_your_token_from_step5
   ```

5. Click **"Save Changes"**
6. Render will **automatically redeploy** (takes ~3 minutes)

---

### Step 7: Test Your Survey! (Success!)

1. Go to your **Netlify survey URL**
2. Complete the survey
3. Go through **Session 1** (should work as before)
4. Start **Session 2** (role-play conversation)
5. **Should be FAST now!** ⚡ (2-5 seconds per response)

---

## 📊 Before & After

| Metric | Before | After |
|--------|--------|-------|
| Session 2 Response Time | 15-30 sec ❌ | 2-5 sec ✅ |
| Render Build Time | 10-15 min | 2-3 min |
| Render Memory Usage | 500MB+ | 100MB |
| Backend Dependencies | 1.1GB | 50MB |
| Monthly Cost | $7+ | $0 🎉 |

---

## 🆘 Troubleshooting

### Space Build Fails
- **Check**: SDK is set to "Docker" (not Gradio/Streamlit)
- **Check**: All 4 files are uploaded
- **View**: Logs tab for error details

### Space Stuck on "Building"
- **Wait**: First build takes 5-10 minutes
- **Refresh**: Page after a few minutes
- **Check**: Logs for progress

### API Returns 404
- **Wait**: Build might not be complete
- **Check**: Space status shows "Running"
- **Try**: https://tzhang62-iql-fire-rescue-api.hf.space/health

### Render Deployment Fails
- **Check**: Environment variables are saved
- **Check**: HUGGINGFACE_MODEL_ID has no `https://` prefix
- **View**: Render logs for errors

### Session 2 Still Slow
- **Test**: Space API directly (Step 4)
- **Check**: Render logs show "[IQL-HF] Initialized"
- **Verify**: HUGGINGFACE_MODEL_ID is correct

---

## 🎯 Success Checklist

- [ ] Space created with **Docker SDK**
- [ ] All 4 files uploaded
- [ ] Space status shows **"Running"**
- [ ] Space API test returns JSON response
- [ ] HF token created (Read access)
- [ ] Render environment variables updated
- [ ] Render redeployed successfully
- [ ] Survey Session 2 is fast!

---

## 📞 Support

If you get stuck:
1. Check Space logs: https://huggingface.co/spaces/tzhang62/iql-fire-rescue-api
2. Check Render logs: Render Dashboard → Logs
3. Test Space API directly with curl

---

## 🎉 Expected Outcome

After completion:
- ✅ Session 1 (non-role-play): Fast (uses OpenAI)
- ✅ Session 2 (role-play): **Fast** (uses HF Space + OpenAI)
- ✅ All 6 conversations work smoothly
- ✅ Backend runs on Render **free tier**
- ✅ Space runs on HF **free tier**
- ✅ **Total cost: $0/month**

---

**Ready to start?** Go to https://huggingface.co/spaces and create your Space!

Good luck! 🚀


# API Keys Setup Guide

## 🔴 Current Issue

You're getting a **401 Unauthorized** error from Hugging Face API because the authentication token is not set.

**Error in logs** (line 721-825):
```
[IQL-HF] API error 401: Unauthorized access
[IQL-HF] API failed, using fallback policy
```

## 🔑 Required API Keys

Your system needs **TWO** API keys to work fully:

1. **OpenAI API Key** - For generating operator responses ✅ (Working)
2. **Hugging Face Token** - For IQL model inference ❌ (Missing)

---

## 📝 Step-by-Step Setup

### Step 1: Get Your API Keys

#### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-...`)

#### Hugging Face Token
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it: "A2I2 Survey Backend"
4. Select: **Read** access (or "Fine-grained" with read access to models)
5. Click "Generate token"
6. Copy the token (starts with `hf_...`)

### Step 2: Create .env File

In Terminal 3 (or any terminal):

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend

# Create .env file from template
cp env.example .env

# Edit the file with your keys
nano .env
# or
open -e .env
```

### Step 3: Fill in Your API Keys

Edit the `.env` file to look like this:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_KEY_HERE
OPENAI_MODEL=gpt-4o-mini

# Hugging Face Configuration (for IQL model)
HUGGINGFACE_TOKEN=hf_YOUR_ACTUAL_HUGGINGFACE_TOKEN_HERE
HUGGINGFACE_MODEL_ID=tzhang62/iql-fire-rescue

# Admin Access Key (for data export)
ADMIN_KEY=your-secure-admin-key-here

# Server Configuration (optional)
PORT=8001
HOST=0.0.0.0
```

**Save and close the file** (Ctrl+X, then Y, then Enter in nano)

### Step 4: Restart Server with Helper Script

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend

# Stop the current server (Ctrl+C in Terminal 3)

# Use the helper script to start with environment variables
./start_server.sh
```

The script will:
- ✅ Load variables from `.env`
- ✅ Check all required keys are present
- ✅ Activate virtual environment
- ✅ Start the server

---

## 🎯 What Will Change

### Before (Current - Fallback Mode)
```
[IQL-HF] API error 401: Unauthorized
[IQL-HF] API failed, using fallback policy
[IQL-HF] Fallback policy: express_urgency  ← Simple heuristic
```

### After (With HF Token)
```
[IQL-HF] Selected policy: bob              ← From your trained model!
[IQL-HF] Q-values: {
  'bob': 0.85,
  'lindsay': 0.62,
  'michelle': 0.41,
  'niki': 0.73,
  'ross': 0.58
}
```

---

## 🔄 Alternative: Manual Environment Setup

If you don't want to use the helper script, you can set variables manually:

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
source /Users/tzhang/projects/A2I2/venv/bin/activate

# Load from .env file
export $(grep -v '^#' .env | xargs)

# Start server
python server.py
```

---

## ✅ How to Verify It's Working

Once you restart with both tokens, you should see:

1. **At startup**:
```
[IQL-HF] Initialized with Inference API: https://router.huggingface.co/models/tzhang62/iql-fire-rescue
[IQL-HF] 5 policies available
```

2. **During conversation**:
```
[IQL-HF] Selected policy: bob
[RETRIEVAL] Got 2 examples (took 0.12s)
[OPENAI] Generated response (took 0.84s)
```

**No more 401 errors!** ✅

---

## 🔒 Security Notes

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Keep your tokens secret** - Don't share them publicly
3. **Rotate tokens periodically** - Especially if exposed

---

## 🐛 Troubleshooting

### Issue: "Permission denied" when running start_server.sh
```bash
chmod +x start_server.sh
```

### Issue: ".env file not found"
```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
cp env.example .env
# Then edit .env with your keys
```

### Issue: Still getting 401 error
1. Check token format: `hf_...` (40+ characters)
2. Verify token has **read access** to models
3. Check model ID is correct: `tzhang62/iql-fire-rescue`
4. Make sure token is not expired

### Issue: HF model is private
If your model `tzhang62/iql-fire-rescue` is private:
1. Your HF token must have access to your private models
2. Or make the model public on Hugging Face

---

## 📋 Quick Reference

| API | Where to Get | Starts With | Used For |
|-----|-------------|-------------|----------|
| OpenAI | platform.openai.com/api-keys | `sk-` | Generating operator responses |
| Hugging Face | huggingface.co/settings/tokens | `hf_` | IQL policy selection |

---

**Current Status**: 
- ✅ System works (using fallback policies)
- ⚠️ Not using your trained IQL model (needs HF token)
- ✅ Character matching system working
- ✅ OpenAI responses generating

**Next Step**: Set up `.env` file and restart server! 🚀


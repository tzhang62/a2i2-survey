# Hugging Face IQL Model Deployment Guide

## Overview
This guide will help you deploy your IQL model to Hugging Face, making it accessible via API. This will significantly speed up your application and reduce server costs.

## Step 1: Install Hugging Face CLI

```bash
pip install huggingface_hub
```

## Step 2: Login to Hugging Face

```bash
# Login to Hugging Face
huggingface-cli login
```

You'll need to:
1. Create account at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token (write access)
4. Paste it when prompted

## Step 3: Prepare Your Model for Upload

Your IQL model files are located at:
- `a2i2_chatbot/backend/iql/label_map.json`
- `a2i2_chatbot/backend/iql/selector/iql_model_embed.pt`

## Step 4: Upload Model to Hugging Face

I've created a script `upload_iql_to_hf.py` that will:
1. Package your model files
2. Upload them to Hugging Face
3. Create a model card with documentation

Run it:
```bash
cd a2i2_chatbot/backend
python upload_iql_to_hf.py
```

This will create a model at: `https://huggingface.co/YOUR_USERNAME/iql-fire-rescue`

## Step 5: Get Your Hugging Face API Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "Read" access
3. Copy the token (starts with `hf_...`)
4. Save it securely

## Step 6: Add Token to Render

In Render dashboard:
1. Go to your service → Environment
2. Add new environment variable:
   - Key: `HUGGINGFACE_TOKEN`
   - Value: Your token (e.g., `hf_abcdef123456...`)
3. Click Save

## Step 7: Deploy Updated Backend

The backend code has been updated to use Hugging Face API instead of local inference:
- Removed heavy dependencies (torch, sentence-transformers)
- Added lightweight Hugging Face API calls
- Faster responses
- Lower memory usage

Just redeploy on Render!

## How It Works

### Before (Slow):
```
User → Render Backend → Load PyTorch → Load Sentence-Transformers → Run IQL → Return
                        (Heavy, Slow, 512MB RAM)
```

### After (Fast):
```
User → Render Backend → Call Hugging Face API → Return
       (Lightweight)           (Fast GPU inference)
```

## API Usage

Your model will be accessible at:
```
https://api-inference.huggingface.co/models/YOUR_USERNAME/iql-fire-rescue
```

The backend automatically:
1. Sends conversation state to HF API
2. Gets policy recommendation back
3. Returns operator response

## Free Tier Limits

Hugging Face Inference API free tier:
- ✅ 30,000 requests per month
- ✅ Fast GPU inference
- ✅ Automatic caching
- ✅ No credit card required

For most research studies, this is more than enough!

## Monitoring

Check your API usage:
1. Go to https://huggingface.co/settings/tokens
2. Click on your token
3. View usage statistics

## Troubleshooting

### "Model is loading"
First request might take 20-30 seconds as HF loads your model. Subsequent requests are fast!

### "Rate limit exceeded"
You've exceeded 30k requests/month. Options:
1. Wait for reset (monthly)
2. Upgrade to Pro ($9/mo for unlimited)

### "Model not found"
Make sure:
- Model was uploaded successfully
- Model is public (or token has access)
- Using correct model name

## Alternative: Private Model

To keep your model private:
1. Upload as private model
2. Use token with "Read" access
3. Only your backend can access it

## Cost Comparison

| Option | Cost/Month | Speed | Memory |
|--------|------------|-------|--------|
| Render Free (Local IQL) | $0 | Slow | 512MB (barely works) |
| Render Starter (Local IQL) | $7 | Medium | 1GB |
| Render Free + HF API | $0 | Fast | 256MB (plenty!) |
| Render Free + HF Pro | $9 | Very Fast | 256MB |

**Best option**: Render Free + HF Free API = $0/month total! 🎉

## Next Steps

1. ✅ Run upload script
2. ✅ Get HF token
3. ✅ Add token to Render
4. ✅ Redeploy backend
5. ✅ Test your survey!

Your Session 2 should now be as fast as Session 1! 🚀


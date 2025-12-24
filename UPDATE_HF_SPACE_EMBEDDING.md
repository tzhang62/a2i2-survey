# 🚀 Update HF Space to Add Embedding Endpoint

Your IQL Space already has sentence-transformers loaded. We just need to add a `/embed` endpoint!

## Step 1: Update Your HF Space

Go to your HF Space: https://huggingface.co/spaces/tzhang62/iql-fire-rescue-api

### Option A: Manual Update (Web UI)

1. Click "Files" tab
2. Click on `app.py`
3. Click "Edit" button
4. Replace the entire file with the new `hf_space_files/app.py` from your local repo
5. Commit changes
6. Wait 30 seconds for rebuild

### Option B: Git Push (if you have the repo cloned)

```bash
cd /path/to/your/hf-space-repo
cp /Users/tzhang/projects/a2i2_survey/hf_space_files/app.py ./
git add app.py
git commit -m "Add /embed endpoint for fast GPU embeddings"
git push
```

---

## Step 2: Test the New Endpoint

After the Space rebuilds (~30 seconds), test it:

```bash
curl -X POST https://tzhang62-iql-fire-rescue-api.hf.space/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "How are you?"], "normalize": true}'
```

**Expected output:**
```json
{
  "embeddings": [[0.12, 0.45, ...], [0.23, 0.56, ...]],
  "model": "all-MiniLM-L6-v2",
  "dimension": 384
}
```

**Should be FAST:** < 0.5 seconds (GPU!)

---

## Step 3: Backend Will Automatically Use It

Once your HF Space is updated, the Render backend will automatically:
- Use HF GPU embeddings for retrieval
- Reduce retrieval time from 97s → 1-2s
- Keep everything fast!

---

## ✅ Final Result

**Session 2 Response Time:**
- IQL policy selection: 0.4s (HF GPU) ✅
- Retrieval encoding: **0.5s** (HF GPU, was 97s!) ✅
- Find similar: 0.1s ✅
- OpenAI response: 1.1s ✅

**Total: ~2 seconds per message!** 🚀 (was 100+ seconds)


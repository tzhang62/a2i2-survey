# 🔧 Update Hugging Face Space to Fix Q-values

## Problem
Your HF Space has the wrong `label_map.json` with character names instead of action policies.

## Solution

### Quick Fix (Manual Upload)

1. Go to your HF Space: https://huggingface.co/spaces/tzhang62/iql-fire-rescue-api
2. Click "Files" tab
3. Click on `label_map.json`
4. Click "Edit" button
5. Replace the entire contents with:

```json
{
  "provide_information": 0,
  "offer_assistance": 1,
  "express_urgency": 2,
  "ask_question": 3,
  "give_direction": 4,
  "acknowledge_concern": 5,
  "build_rapport": 6
}
```

6. Commit changes
7. Wait 30 seconds for Space to rebuild

### Or Use Git (If you have the repo cloned)

```bash
cd /path/to/your/hf-space-repo
cp /Users/tzhang/projects/a2i2_survey/hf_space_files/label_map.json ./
git add label_map.json
git commit -m "Fix label_map.json with correct action policies"
git push
```

## Expected Result

After updating, your logs should show:
```
[IQL-HF] Selected policy: provide_information  ✅ (not "niki")
[IQL-HF] Q-values: {'provide_information': 0.85, 'offer_assistance': 0.42, ...}  ✅ (not all zeros)
```


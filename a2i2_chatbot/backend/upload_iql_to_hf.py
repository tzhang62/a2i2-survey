"""
Upload IQL Model to Hugging Face

This script packages your IQL model and uploads it to Hugging Face,
making it accessible via their Inference API.
"""

import os
import json
import shutil
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

# Configuration
REPO_NAME = "iql-fire-rescue"  # Change this to your preferred name
MODEL_DIR = Path(__file__).parent / "iql"

def create_model_card():
    """Create a README for the Hugging Face model"""
    return """---
tags:
- reinforcement-learning
- iql
- fire-rescue
- emergency-response
license: mit
---

# IQL Fire Rescue Operator Model

This model uses Implicit Q-Learning (IQL) to select optimal conversation policies for emergency response scenarios.

## Model Description

- **Task**: Policy selection for fire rescue emergency conversations
- **Algorithm**: Implicit Q-Learning (IQL)
- **Input**: Conversation history (embedded using sentence-transformers)
- **Output**: Best policy and Q-values for all policies

## Policies

1. `provide_information` - Share facts, data, risk levels
2. `offer_assistance` - Provide help, resources, support
3. `express_urgency` - Convey time pressure, danger
4. `ask_question` - Gather information from resident
5. `give_direction` - Provide specific instructions
6. `acknowledge_concern` - Validate resident's feelings
7. `build_rapport` - Establish trust and connection

## Usage

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/YOUR_USERNAME/iql-fire-rescue"
headers = {"Authorization": f"Bearer YOUR_HF_TOKEN"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Example
output = query({
    "inputs": "Conversation state here",
    "parameters": {"character": "bob"}
})
```

## Training Data

Trained on emergency response conversations with multiple character profiles.

## Citation

If you use this model, please cite:
```
@misc{iql-fire-rescue,
  title={IQL-based Emergency Response Operator},
  author={Your Name},
  year={2025},
  publisher={Hugging Face}
}
```
"""

def create_config():
    """Create a config.json for the model"""
    return {
        "model_type": "iql-custom",
        "task": "policy-selection",
        "architecture": {
            "state_dim": 384,
            "num_policies": 7,
            "hidden_dim": 512
        },
        "policies": [
            "provide_information",
            "offer_assistance",
            "express_urgency",
            "ask_question",
            "give_direction",
            "acknowledge_concern",
            "build_rapport"
        ]
    }

def main():
    print("=" * 60)
    print("IQL Model Upload to Hugging Face")
    print("=" * 60)
    
    # Check if model files exist
    label_map_path = MODEL_DIR / "label_map.json"
    model_path = MODEL_DIR / "selector" / "iql_model_embed.pt"
    
    if not label_map_path.exists():
        print(f"❌ Error: label_map.json not found at {label_map_path}")
        return
    
    if not model_path.exists():
        print(f"❌ Error: iql_model_embed.pt not found at {model_path}")
        return
    
    print(f"✅ Found label_map.json")
    print(f"✅ Found iql_model_embed.pt")
    
    # Get username
    username = input("\nEnter your Hugging Face username: ").strip()
    if not username:
        print("❌ Username required!")
        return
    
    repo_id = f"{username}/{REPO_NAME}"
    print(f"\nWill create repository: {repo_id}")
    
    # Create temporary directory for upload
    temp_dir = Path("temp_hf_upload")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Copy model files
        print("\n📦 Preparing model files...")
        shutil.copy(label_map_path, temp_dir / "label_map.json")
        shutil.copy(model_path, temp_dir / "iql_model_embed.pt")
        
        # Create README
        with open(temp_dir / "README.md", "w") as f:
            f.write(create_model_card())
        
        # Create config
        with open(temp_dir / "config.json", "w") as f:
            json.dump(create_config(), f, indent=2)
        
        print("✅ Model files prepared")
        
        # Initialize Hugging Face API
        print("\n🚀 Uploading to Hugging Face...")
        api = HfApi()
        
        # Create repository
        try:
            create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
            print(f"✅ Created repository: {repo_id}")
        except Exception as e:
            print(f"⚠️  Repository might already exist: {e}")
        
        # Upload files
        api.upload_folder(
            folder_path=str(temp_dir),
            repo_id=repo_id,
            repo_type="model"
        )
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Model uploaded to Hugging Face!")
        print("=" * 60)
        print(f"\n📍 Model URL: https://huggingface.co/{repo_id}")
        print(f"📍 API URL: https://api-inference.huggingface.co/models/{repo_id}")
        print("\n✨ Next steps:")
        print("1. Get your HF token: https://huggingface.co/settings/tokens")
        print("2. Add token to Render environment: HUGGINGFACE_TOKEN")
        print(f"3. Update backend to use model: {repo_id}")
        print("4. Redeploy on Render")
        
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        print("\nMake sure you've run: huggingface-cli login")
        
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("\n🧹 Cleaned up temporary files")

if __name__ == "__main__":
    main()


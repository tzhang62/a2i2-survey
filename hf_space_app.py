"""
Hugging Face Space API for IQL Fire Rescue Model
Deploy this to HF Space to serve your custom IQL model

Upload to: https://huggingface.co/spaces/tzhang62/iql-fire-rescue-api
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json

app = FastAPI(title="IQL Fire Rescue API")

# Config
EMBED_MODEL = "all-MiniLM-L6-v2"
N_LAST = 3

# Policies
POLICIES = ["provide_information", "offer_assistance", "express_urgency", 
            "ask_question", "give_direction", "acknowledge_concern", "build_rapport"]

# ============================================================================
# IQL Model (same as your server.py)
# ============================================================================

class QNetworkEmbed(nn.Module):
    def __init__(self, state_dim: int, action_embeds: torch.Tensor, hidden_dim: int, p_drop: float = 0.3):
        super().__init__()
        self.action_embeds = nn.Parameter(action_embeds, requires_grad=False)
        input_dim = state_dim + action_embeds.shape[1]
        self.f1 = nn.Linear(input_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.f2 = nn.Linear(hidden_dim, hidden_dim)
        self.ln2 = nn.LayerNorm(hidden_dim)
        self.head = nn.Linear(hidden_dim, 1)
        self.drop = nn.Dropout(p_drop)

    def forward(self, state: torch.Tensor, action_id: torch.Tensor) -> torch.Tensor:
        a_emb = self.action_embeds[action_id]
        x = torch.cat([state, a_emb], dim=-1)
        x = self.f1(x); x = F.relu(x); x = self.ln1(x); x = self.drop(x)
        x = self.f2(x); x = F.relu(x); x = self.ln2(x); x = self.drop(x)
        return self.head(x).squeeze(-1)

def embed_state(model, texts):
    if not texts:
        return np.zeros((model.get_sentence_embedding_dimension(),), dtype=np.float32)
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.mean(embs, axis=0).astype(np.float32)

class IQLSelector:
    def __init__(self, pt_path, policy_names):
        self.device = torch.device("cpu")
        self.embed_model = SentenceTransformer(EMBED_MODEL)
        state_dict = torch.load(pt_path, map_location="cpu")
        
        ae_key = next((k for k in state_dict.keys() if k.endswith("action_embeds")), None)
        action_embeds_ckpt = state_dict[ae_key]
        if isinstance(action_embeds_ckpt, np.ndarray):
            action_embeds_ckpt = torch.tensor(action_embeds_ckpt)
        
        num_actions, action_dim = action_embeds_ckpt.shape
        f1w = state_dict["f1.weight"]
        hidden_dim = f1w.shape[0]
        state_dim = f1w.shape[1] - action_dim
        
        dummy = torch.zeros((num_actions, action_dim), dtype=torch.float32)
        self.qnet = QNetworkEmbed(state_dim, dummy, hidden_dim=hidden_dim).to(self.device)
        self.qnet.load_state_dict(state_dict, strict=True)
        self.qnet.eval()
        self.policy_names = policy_names
        print(f"[IQL] Loaded: {num_actions} policies, state_dim={state_dim}")

    def select_policy(self, history, n_last=N_LAST):
        texts = [h["text"] for h in history if h.get("role") == "resident"]
        last_n = texts[-n_last:] if texts else []
        s_vec = embed_state(self.embed_model, last_n)
        s = torch.tensor(s_vec, dtype=torch.float32, device=self.device).unsqueeze(0)

        q_vals = []
        with torch.no_grad():
            for a_id in range(len(self.policy_names)):
                a = torch.tensor([a_id], dtype=torch.long, device=self.device)
                q_vals.append(float(self.qnet(s, a).item()))

        best_idx = int(np.argmax(q_vals))
        return self.policy_names[best_idx], dict(zip(self.policy_names, q_vals))

# ============================================================================
# Global Model
# ============================================================================

iql_selector = None

@app.on_event("startup")
async def load_model():
    global iql_selector
    try:
        base = Path(__file__).parent
        label_map = json.loads((base / "label_map.json").read_text())
        policies = [k for k, _ in sorted(label_map.items(), key=lambda x: x[1])]
        iql_selector = IQLSelector(base / "iql_model_embed.pt", policies)
        print("[Space] Model loaded!")
    except Exception as e:
        print(f"[Space] Load failed: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# API
# ============================================================================

class Request(BaseModel):
    inputs: str
    parameters: Optional[Dict] = None

class Response(BaseModel):
    policy: str
    q_values: Dict[str, float]

@app.post("/", response_model=Response)
async def predict(req: Request):
    if not iql_selector:
        return {"policy": POLICIES[0], "q_values": {}}
    
    # Parse state: "msg1 | msg2 | msg3"
    if req.inputs == "START" or not req.inputs:
        messages = []
    else:
        messages = [m.strip() for m in req.inputs.split("|")]
    
    history = [{"role": "resident", "text": m} for m in messages]
    policy, q_vals = iql_selector.select_policy(history, n_last=N_LAST)
    
    return {"policy": policy, "q_values": q_vals}

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": iql_selector is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


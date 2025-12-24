

#!/usr/bin/env python3
"""
A06_select_policy.py

Selects the best operator policy using a trained Implicit Q-Learning (IQL) model.

Modes:
    --mode embed  → Q(s,a) = f([state, operator_embedding[a]])
    --mode state  → Q(s) = [Q(s,a1..aN)]

State = mean embedding of the last N resident utterances
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer

# --------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATAA = BASE_DIR / "dataA"
SELECTOR_DIR = DATAA / "iql" / "selector"
POLICY_DIR = DATAA / "indexes" / "policies"
PROTOTYPES_FILE = POLICY_DIR / "operator_prototypes.npy"
LABEL_MAP_FILE = DATAA / "iql" / "label_map.json"

# --------------------------------------------------------------------
# Config
# --------------------------------------------------------------------
N_LAST_RESIDENT = 3
EMBED_MODEL = "all-MiniLM-L6-v2"
p_drop = 0.3

# --------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------
def embed_state(model, last_n_res_texts):
    """Embed last-N resident utterances to form a single state vector."""
    if not last_n_res_texts:
        return np.zeros((model.get_sentence_embedding_dimension(),), dtype=np.float32)
    embs = model.encode(last_n_res_texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.mean(embs, axis=0).astype(np.float32)

# --------------------------------------------------------------------
# Q-Networks
# --------------------------------------------------------------------
class QNetworkEmbed(nn.Module):
    """Embedding-based Q-network: Q(s,a) = f([state, embedding[a]])"""
    def __init__(self, state_dim, action_embeds, hidden_dim=1024):
        super().__init__()
        self.action_embeds = nn.Parameter(action_embeds, requires_grad=False)
        input_dim = state_dim + action_embeds.shape[1]
        self.f1 = nn.Linear(input_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.f2 = nn.Linear(hidden_dim, hidden_dim)
        self.ln2 = nn.LayerNorm(hidden_dim)
        self.head = nn.Linear(hidden_dim, 1)
        self.drop = nn.Dropout(p_drop)

    def forward(self, state, action_id):
        a_emb = self.action_embeds[action_id]
        x = torch.cat([state, a_emb], dim=-1)
        x = self.f1(x); x = F.relu(x); x = self.ln1(x); x = self.drop(x)
        x = self.f2(x); x = F.relu(x); x = self.ln2(x); x = self.drop(x)
        return self.head(x).squeeze(-1)


class QNetworkState(nn.Module):
    """State-only Q-network: Q(s) = [Q(s,a1..aN)]"""
    def __init__(self, state_dim, num_actions, hidden_dim=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(p_drop),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(p_drop),
            nn.Linear(hidden_dim, num_actions)
        )
    def forward(self, x):
        return self.net(x)

# --------------------------------------------------------------------
# Main Selector Class
# --------------------------------------------------------------------
class IQLPolicySelector:
    def __init__(self, mode="state", n_last=N_LAST_RESIDENT):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.mode = mode
        self.n_last = n_last

        # Load label map and policy names
        label_map = json.load(open(LABEL_MAP_FILE))
        self.policy_names = [k for k, _ in sorted(label_map.items(), key=lambda x: x[1])]
        self.num_actions = len(self.policy_names)

        # Load operator embeddings
        if not PROTOTYPES_FILE.exists():
            raise FileNotFoundError(f"Missing {PROTOTYPES_FILE}. Run A05b_build_operatorPolicies.py first.")
        action_embeds = torch.tensor(np.load(PROTOTYPES_FILE), dtype=torch.float32, device=self.device)

        print(f"[INFO] Loaded {self.num_actions} operator embeddings from {PROTOTYPES_FILE}")
        print(f"[INFO] Operator policies: {self.policy_names}")

        # Load sentence transformer for state embeddings
        self.embed_model = SentenceTransformer(EMBED_MODEL)

        # Determine model path based on mode
        self.model_path = SELECTOR_DIR / f"iql_model_{mode}.pt"
        if not self.model_path.exists():
            raise FileNotFoundError(f"Missing trained IQL model: {self.model_path}")

        # Instantiate correct Q-network and load weights
        dummy_state = np.zeros((self.embed_model.get_sentence_embedding_dimension(),), dtype=np.float32)

        if mode == "embed":
            self.qnet = QNetworkEmbed(len(dummy_state), action_embeds).to(self.device)
        else:
            self.qnet = QNetworkState(len(dummy_state), self.num_actions).to(self.device)

        self.qnet.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.qnet.eval()

        print(f"[INFO] Loaded trained Q-network ({mode} mode) from {self.model_path}")

    # ----------------------------------------------------------------
    def select_policy(self, history):
        """Select the best operator policy given the conversation history."""
        # Extract last N resident utterances
        res_texts = [h["text"] for h in history if h["role"] == "resident"]
        last_n = res_texts[-self.n_last :] if res_texts else []

        # Encode state
        state_vec = embed_state(self.embed_model, last_n)
        state_tensor = torch.tensor(state_vec, dtype=torch.float32, device=self.device).unsqueeze(0)

        # Compute Q-values
        with torch.no_grad():
            if self.mode == "embed":
                q_values = []
                for a_id in range(self.num_actions):
                    a_tensor = torch.tensor([a_id], dtype=torch.long, device=self.device)
                    q_val = self.qnet(state_tensor, a_tensor).item()
                    q_values.append(q_val)
                q_values = np.array(q_values)
            else:
                q_values = self.qnet(state_tensor).cpu().numpy().flatten()

        # Pick best action
        best_idx = int(np.argmax(q_values))
        best_policy = self.policy_names[best_idx]
        q_dict = dict(zip(self.policy_names, q_values))

        return best_policy, q_dict

# --------------------------------------------------------------------
# Example usage
# --------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select best operator policy using trained IQL model.")
    parser.add_argument("--mode", choices=["embed", "state"], default="state",
                        help="Use embedding-based or state-only Q-network.")
    args = parser.parse_args()

    selector = IQLPolicySelector(mode=args.mode)

    history = [
        {"role": "resident", "text": "I will never leave my project like this."},
        {"role": "operator", "text": "Please note that fire conditions are worsening."},
        {"role": "resident", "text": "But I can't leave my project. My work is really important."},
    ]

    # history = [
    #     {"role": "resident", "text": "I will need a van to leave."},
    #     {"role": "operator", "text": "Please note that fire conditions are worsening."},
    #     {"role": "resident", "text": "Some of them are in wheelchairs."},
    # ]


    best_policy, qvals = selector.select_policy(history)

    print("\n[RESULT]")
    print(f"Selected policy: {best_policy}")
    print("Q-values:")
    for k, v in qvals.items():
        print(f"  {k:12s} : {v:.4f}")


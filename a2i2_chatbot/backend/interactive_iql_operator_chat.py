import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import requests
import warnings
# --- suppress noisy warnings/logs ---
os.environ["TOKENIZERS_PARALLELISM"] = "false"   # HuggingFace tokenizers fork warning
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"         # silence TF logs if any dependency pulls TF
warnings.filterwarnings("ignore")  # generic Python warnings (use with care)

# ----------------------------
# Config
# ----------------------------
N_LAST_RESIDENT = 3
EMBED_MODEL = "all-MiniLM-L6-v2"

MAX_TURNS = 5              # max resident turns
MIN_RESIDENT_TURNS = 3     # don't end before this many resident turns

QLOG_PATH = Path("q_values_log.jsonl")


# ----------------------------
# State encoding
# ----------------------------
def embed_state(model: SentenceTransformer, last_n_res_texts: List[str]) -> np.ndarray:
    if not last_n_res_texts:
        return np.zeros((model.get_sentence_embedding_dimension(),), dtype=np.float32)
    embs = model.encode(last_n_res_texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.mean(embs, axis=0).astype(np.float32)


# ----------------------------
# Q-network (embed mode)
# ----------------------------
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


class IQLSelectorEmbedFromPT:
    """
    Loads your trained embed-mode IQL model from .pt and infers hidden_dim/state_dim from checkpoint.
    """
    def __init__(self, pt_path: Path, policy_names: List[str]):
        self.device = torch.device("cpu")
        self.embed_model = SentenceTransformer(EMBED_MODEL)

        state_dict = torch.load(pt_path, map_location="cpu")

        ae_key = None
        for k in state_dict.keys():
            if k.endswith("action_embeds"):
                ae_key = k
                break
        if ae_key is None:
            raise RuntimeError("Could not find 'action_embeds' in checkpoint state_dict.")

        action_embeds_ckpt = state_dict[ae_key]
        if isinstance(action_embeds_ckpt, np.ndarray):
            action_embeds_ckpt = torch.tensor(action_embeds_ckpt)

        num_actions, action_dim = action_embeds_ckpt.shape

        f1w = state_dict.get("f1.weight")
        if f1w is None:
            raise RuntimeError("Checkpoint missing 'f1.weight'; unexpected architecture.")
        hidden_dim = f1w.shape[0]
        input_dim = f1w.shape[1]
        state_dim = input_dim - action_dim

        if len(policy_names) != num_actions:
            raise RuntimeError(
                f"policy_names length ({len(policy_names)}) != num_actions ({num_actions}). "
                "Fix label_map/order."
            )

        dummy_action_embeds = torch.zeros((num_actions, action_dim), dtype=torch.float32)
        self.qnet = QNetworkEmbed(state_dim, dummy_action_embeds, hidden_dim=hidden_dim).to(self.device)
        self.qnet.load_state_dict(state_dict, strict=True)
        self.qnet.eval()

        self.policy_names = policy_names

        print(f"[OK] Loaded IQL embed model: {pt_path}")
        print(f"[OK] num_actions={num_actions}, state_dim={state_dim}, action_dim={action_dim}, hidden_dim={hidden_dim}")
        print(f"[OK] policy_names={self.policy_names}")

    def select_policy(self, history: List[Dict[str, str]], n_last: int = N_LAST_RESIDENT) -> Tuple[str, Dict[str, float]]:
        res_texts = [h["text"] for h in history if h.get("role") == "resident"]
        last_n = res_texts[-n_last:] if res_texts else []
        s_vec = embed_state(self.embed_model, last_n)
        s = torch.tensor(s_vec, dtype=torch.float32, device=self.device).unsqueeze(0)

        q_vals = []
        with torch.no_grad():
            for a_id in range(len(self.policy_names)):
                a = torch.tensor([a_id], dtype=torch.long, device=self.device)
                q_vals.append(float(self.qnet(s, a).item()))

        best_idx = int(np.argmax(q_vals))
        return self.policy_names[best_idx], dict(zip(self.policy_names, q_vals))


# ----------------------------
# Retrieval (no faiss): cosine over *_op_embeds.npy + *_pairs.json
# ----------------------------
def cosine_topk(query_vec: np.ndarray, mat: np.ndarray, k: int) -> List[int]:
    sims = mat @ query_vec  # assumes normalize_embeddings=True produced unit vectors
    k = min(k, len(sims))
    if k <= 0:
        return []
    idx = np.argpartition(-sims, kth=k - 1)[:k]
    idx = idx[np.argsort(-sims[idx])]
    return idx.tolist()


class PolicyExampleRetriever:
    def __init__(self, base_dir: Path, embed_model: SentenceTransformer):
        self.base_dir = base_dir
        self.embed_model = embed_model
        self._cache = {}  # policy -> (pairs, embeds_matrix)

    def _pairs_path(self, policy: str) -> Path:
        return self.base_dir / "indexes" / "policies" / f"{policy}_pairs.json"

    def _embeds_path(self, policy: str) -> Path:
        return self.base_dir / "indexes" / "policies" / f"{policy}_op_embeds.npy"

    def _load_policy(self, policy: str):
        if policy in self._cache:
            return self._cache[policy]

        pairs_path = self._pairs_path(policy)
        embeds_path = self._embeds_path(policy)

        if not pairs_path.exists():
            raise FileNotFoundError(f"Missing pairs file: {pairs_path}")
        if not embeds_path.exists():
            raise FileNotFoundError(f"Missing embeds file: {embeds_path}")

        pairs = json.loads(pairs_path.read_text(encoding="utf-8"))
        embeds = np.load(embeds_path).astype(np.float32)

        # Expect embeds aligned with pairs order
        if len(pairs) != embeds.shape[0]:
            raise RuntimeError(f"Pairs/embeds length mismatch for {policy}: {len(pairs)} vs {embeds.shape[0]}")

        self._cache[policy] = (pairs, embeds)
        return pairs, embeds

    def retrieve_topk_pairs(self, policy: str, resident_query: str, k: int = 2) -> List[Dict[str, str]]:
        pairs, embeds = self._load_policy(policy)
        q = self.embed_model.encode([resident_query], convert_to_numpy=True, normalize_embeddings=True)[0].astype(np.float32)
        idxs = cosine_topk(q, embeds, k=k)

        out = []
        for ix in idxs:
            out.append({
                "resident": (pairs[ix].get("resident_text") or "").strip(),
                "operator": (pairs[ix].get("operator_text") or "").strip(),
            })
        return out


# ----------------------------
# LLM calls (HTTP, no openai SDK)
# ----------------------------
def call_openai_chat(prompt: str, model: str, temperature: float = 0.6, max_tokens: int = 180) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY")

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def judge_resident_stance(history: List[Dict[str, str]], model: str) -> dict:
    """
    Returns dict:
      {"stance":"AGREE|DELAY|REFUSE|UNKNOWN","confidence":0-1,"reason":"..."}
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY")

    tail = history[-12:]
    convo = "\n".join([f"{t['role'].capitalize()}: {t['text']}" for t in tail])

    prompt = (
        "You are judging ONLY the RESIDENT's stance about evacuating.\n"
        "Classify into exactly one stance:\n"
        "- AGREE: resident commits to evacuate/leave (including 'leaving ASAP', 'leaving soon', 'on my way', "
        "'I will grab essentials then leave').\n"
        "- REFUSE: clearly refuses to evacuate/leave.\n"
        "- DELAY: resident delays or stalls without a clear commitment to evacuate (NOT a refusal).\n"
        "- UNKNOWN: not enough info.\n"
        "Return ONLY valid JSON with keys: stance, confidence, reason. No markdown. No code fences.\n"
        "confidence must be a number from 0 to 1.\n\n"
        f"{convo}\n"
    )

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "temperature": 0,
            "max_tokens": 120,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    txt = (r.json()["choices"][0]["message"]["content"] or "").strip()

    # Some models wrap JSON in ```json ... ``` or add extra text; strip and extract first JSON object.
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*", "", txt.strip(), flags=re.IGNORECASE)
        txt = re.sub(r"\s*```$", "", txt.strip())
    m = re.search(r"\{[\s\S]*\}", txt)
    if m:
        txt = m.group(0)

    try:
        obj = json.loads(txt)
    except Exception:
        return {"stance": "UNKNOWN", "confidence": 0.0, "reason": f"Non-JSON judge output: {txt[:160]}"}

    stance = str(obj.get("stance", "UNKNOWN")).upper()
    conf = float(obj.get("confidence", 0.0) or 0.0)
    reason = str(obj.get("reason", ""))

    if stance not in {"AGREE", "DELAY", "REFUSE", "UNKNOWN"}:
        stance = "UNKNOWN"
    conf = max(0.0, min(1.0, conf))
    return {"stance": stance, "confidence": conf, "reason": reason}


# ----------------------------
# Prompt builder
# ----------------------------
def build_prompt(policy_id: str, history: List[Dict[str, str]], examples: List[Dict[str, str]], max_context_turns: int = 6) -> str:
    context = history[-max_context_turns:] if len(history) > max_context_turns else history
    context_text = "\n".join([f"{t['role'].capitalize()}: {t['text'].strip()}" for t in context])

    ex_block = "\n\n".join(
        [f"Resident: {ex['resident']}\nOperator: {ex['operator']}" for ex in examples if ex.get("resident") and ex.get("operator")]
    ).strip()

    instruction = (
        "You are the OPERATOR talking to a RESIDENT during a wildfire evacuation call.\n"
        f"Use the operator policy style optimized for: {policy_id}.\n"
        "Read the conversation so far, then produce the next operator reply.\n"
        "Rules:\n"
        "- 1–2 natural sentences.\n"
        "- Calm, professional, evacuation-focused.\n"
        "- If resident resists, emphasize urgency/danger; if they are cooperative, give clear next steps.\n"
        "- No role labels, no meta commentary.\n"
        "- Avoid gendered pronouns.\n"
        "Use the similar examples for style guidance."
    )

    return (
        f"{instruction}\n\n"
        f"Conversation so far:\n{context_text}\n\n"
        f"Similar example dialogues:\n{ex_block if ex_block else '(none)'}\n\n"
        "Operator:"
    )


# ----------------------------
# Path helpers
# ----------------------------
def find_first_existing(*paths: Path) -> Path:
    for p in paths:
        if p.exists():
            return p
    return paths[0]

def load_policy_names_from_label_map(label_map_path: Path) -> List[str]:
    label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
    return [k for k, _ in sorted(label_map.items(), key=lambda kv: kv[1])]


# ----------------------------
# Main loop
# ----------------------------
def main():
    base = Path(__file__).resolve().parent

    label_map_path = find_first_existing(
        base / "dataA" / "iql" / "label_map.json",
        base / "iql" / "label_map.json",
    )
    pt_path = find_first_existing(
        base / "dataA" / "iql" / "selector" / "iql_model_embed.pt",
        base / "iql" / "selector" / "iql_model_embed.pt",
    )

    if not label_map_path.exists():
        raise FileNotFoundError(f"Missing label_map.json at: {label_map_path}")
    if not pt_path.exists():
        raise FileNotFoundError(f"Missing iql_model_embed.pt at: {pt_path}")

    policy_names = load_policy_names_from_label_map(label_map_path)

    selector = IQLSelectorEmbedFromPT(pt_path=pt_path, policy_names=policy_names)
    retriever = PolicyExampleRetriever(base_dir=base, embed_model=selector.embed_model)

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY in your environment before running.")

    history: List[Dict[str, str]] = []
    print("\nYou are role-playing as Bob (resident). Type messages; Ctrl+C to exit.\n")

    history.append({"role": "operator", "text": "Hello, this is emergency services—are you safe right now?"})
    print(f"Operator: {history[-1]['text']}\n")

    resident_turns = 0
    consecutive_refuse = 0

    while True:
        user_in = input("Bob: ").strip()
        if not user_in:
            continue

        history.append({"role": "resident", "text": user_in})
        resident_turns += 1

        can_end = resident_turns >= MIN_RESIDENT_TURNS

        # ---- hard cap ----
        if resident_turns >= MAX_TURNS:
            closing = (
                "Understood. I have to end this call now—please evacuate immediately using the safest route, "
                "and contact emergency services again if you need help."
            )
            history.append({"role": "operator", "text": closing})
            print(f"Operator: {closing}\n")
            print("[END] Max resident turns reached.")
            break

        # ---- LLM stance judge ----
        judge = judge_resident_stance(history, model=model)
        stance = judge["stance"]
        conf = judge["confidence"]
        print(f"[JUDGE] stance={stance} conf={conf:.2f} reason={judge['reason']}")

        # Success end (only after MIN_RESIDENT_TURNS)
        if can_end and stance == "AGREE" and conf >= 0.70:
            closing = (
                "Thank you—evacuate immediately using the safest route available and stay alert for updates; "
                "reply if you need help."
            )
            history.append({"role": "operator", "text": closing})
            print(f"Operator: {closing}\n")
            print("[END] Success (resident agreed).")
            break

        # Track consecutive refusals
        if stance == "REFUSE" and conf >= 0.85:
            consecutive_refuse += 1
        else:
            consecutive_refuse = 0

        # Forced end only after repeated refusals + MIN_RESIDENT_TURNS
        if can_end and consecutive_refuse >= 2:
            closing = (
                "I understand. I need to end this call now—if you choose to stay, you are at serious risk; "
                "call back if you need assistance evacuating."
            )
            history.append({"role": "operator", "text": closing})
            print(f"Operator: {closing}\n")
            print("[END] No success (repeated refusal).")
            break

        # ---- IQL policy selection ----
        best_policy, qvals = selector.select_policy(history)

        # Print + save Q-values every turn
        q_sorted = sorted(qvals.items(), key=lambda kv: kv[1], reverse=True)
        print(f"\n[TURN {resident_turns}] Selected policy: {best_policy}")
        print("[Q(s,a) per policy]")
        for pol, q in q_sorted:
            mark = "<-- chosen" if pol == best_policy else ""
            print(f"  {pol:10s}: {q: .6f} {mark}")

        rec = {
            "ts": time.time(),
            "turn": resident_turns,
            "resident_text": user_in,
            "selected_policy": best_policy,
            "q_values": qvals,
            "judge": judge,
        }
        with QLOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        # ---- retrieval + operator generation ----
        examples = retriever.retrieve_topk_pairs(best_policy, resident_query=user_in, k=2)

        prompt = build_prompt(best_policy, history, examples)
        op = call_openai_chat(prompt, model=model)

        history.append({"role": "operator", "text": op})
        print(f"Operator: {op}\n")


if __name__ == "__main__":
    main()
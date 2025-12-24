"""
Emergency Response Chatbot Backend with IQL-based Operator
Integrates survey system with IQL-powered conversation system
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
import traceback
from pathlib import Path
import time
import uuid
from datetime import datetime
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Suppress warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = os.getenv('A2I2_BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SURVEY_RESPONSES_DIR = os.path.join(BASE_DIR, "survey_responses")
os.makedirs(SURVEY_RESPONSES_DIR, exist_ok=True)

# IQL Configuration
N_LAST_RESIDENT = 3
EMBED_MODEL = "all-MiniLM-L6-v2"
MAX_TURNS = 5
MIN_RESIDENT_TURNS = 3

# Import Hugging Face API wrapper (replaces local IQL)
try:
    from iql_hf_api import get_iql_hf
    HF_API_AVAILABLE = True
    print("[IMPORT] Hugging Face API wrapper imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import Hugging Face API wrapper: {e}")
    HF_API_AVAILABLE = False

# Character personas (simplified from persona.json)
CHARACTER_PERSONAS = {
    "bob": "Bob is around 30 years old. He prioritizes his work over safety.",
    "ben": "Ben is a 29-year-old computer technician who works from home.",
    "mary": "Mary is an elderly person living alone with a small dog.",
    "lindsay": "Lindsay is a babysitter caring for two children.",
    "ana": "Ana is a caregiver working at a senior center.",
    "ross": "Ross is a van driver helping evacuate elderly residents.",
    "niki": "Niki is at home with a partner, ready to cooperate.",
    "michelle": "Michelle is at home, skeptical of evacuation warnings.",
    "tom": "Tom is a high school teacher working on a home project.",
    "mia": "Mia is a high school student working on a robotics project."
}

# Persuasion strategies for non-role-play conversations
PERSUASION_STRATEGIES = {
    "rational-informational": {
        "name": "Rational-Informational",
        "description": "Provide facts, evidence, and reasoning. Share risk levels, factual updates, and clear instructions.",
        "guidelines": """- Use facts, statistics, and concrete data
- Explain cause-and-effect relationships
- Provide clear, logical step-by-step instructions
- Reference fire behavior, wind conditions, evacuation routes
- Be objective and information-focused
- Example: "The fire is spreading at 2 mph. Your area has a red flag warning. You need to evacuate within 30 minutes via Highway 101 south."
"""
    },
    "emotional-relational": {
        "name": "Emotional-Relational",
        "description": "Build emotional trust and empathy. Express care, reassurance, and shared experience.",
        "guidelines": """- Show empathy and understanding
- Express genuine concern for their safety and wellbeing
- Offer reassurance and emotional support
- Build rapport and trust
- Acknowledge their feelings and concerns
- Example: "I understand this is frightening. We're here to help you through this. Your safety is our top priority, and we'll make sure you get to safety."
"""
    },
    "social-normative": {
        "name": "Social-Normative",
        "description": "Leverage norms, duty, and authority. Emphasize rules, social proof, and authority.",
        "guidelines": """- Reference official protocols and regulations
- Mention what others in the community are doing
- Emphasize civic duty and responsibility
- Use authoritative language and credentials
- Cite emergency management standards
- Example: "This is an official mandatory evacuation order. All residents in your zone are evacuating now. As a fire department official, I'm authorized to direct you to leave immediately."
"""
    }
}

# ============================================================================
# IQL Model Components (DEPRECATED - NO LONGER USED)
# ============================================================================
# These classes are kept for reference only
# The system now uses Hugging Face Space API (iql_hf_api.py) for faster inference
# Local IQL model is no longer loaded to save memory and improve performance
# ============================================================================

class QNetworkEmbed(nn.Module):
    """Q-network for IQL policy selection (DEPRECATED - not used)"""
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


def embed_state(model: SentenceTransformer, last_n_res_texts: List[str]) -> np.ndarray:
    """Embed conversation state from last N resident messages"""
    if not last_n_res_texts:
        return np.zeros((model.get_sentence_embedding_dimension(),), dtype=np.float32)
    embs = model.encode(last_n_res_texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.mean(embs, axis=0).astype(np.float32)


class IQLSelector:
    """IQL-based policy selector (DEPRECATED - not used)"""
    def __init__(self, pt_path: Path, policy_names: List[str]):
        self.device = torch.device("cpu")
        self.embed_model = SentenceTransformer(EMBED_MODEL)
        
        # Load checkpoint
        state_dict = torch.load(pt_path, map_location="cpu")
        
        # Extract action embeds
        ae_key = next((k for k in state_dict.keys() if k.endswith("action_embeds")), None)
        if ae_key is None:
            raise RuntimeError("Could not find 'action_embeds' in checkpoint")
        
        action_embeds_ckpt = state_dict[ae_key]
        if isinstance(action_embeds_ckpt, np.ndarray):
            action_embeds_ckpt = torch.tensor(action_embeds_ckpt)
        
        num_actions, action_dim = action_embeds_ckpt.shape
        
        # Infer dimensions
        f1w = state_dict.get("f1.weight")
        if f1w is None:
            raise RuntimeError("Checkpoint missing 'f1.weight'")
        hidden_dim = f1w.shape[0]
        input_dim = f1w.shape[1]
        state_dim = input_dim - action_dim
        
        if len(policy_names) != num_actions:
            raise RuntimeError(f"policy_names length mismatch: {len(policy_names)} != {num_actions}")
        
        # Initialize model
        dummy_action_embeds = torch.zeros((num_actions, action_dim), dtype=torch.float32)
        self.qnet = QNetworkEmbed(state_dim, dummy_action_embeds, hidden_dim=hidden_dim).to(self.device)
        self.qnet.load_state_dict(state_dict, strict=True)
        self.qnet.eval()
        
        self.policy_names = policy_names
        print(f"[IQL] Loaded model: {num_actions} policies, state_dim={state_dim}")

    def select_policy(self, history: List[Dict[str, str]], n_last: int = N_LAST_RESIDENT) -> tuple:
        """Select best policy based on conversation history"""
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


def cosine_topk(query_vec: np.ndarray, mat: np.ndarray, k: int) -> List[int]:
    """Find top-k most similar vectors by cosine similarity"""
    sims = mat @ query_vec
    k = min(k, len(sims))
    if k <= 0:
        return []
    idx = np.argpartition(-sims, kth=k - 1)[:k]
    idx = idx[np.argsort(-sims[idx])]
    return idx.tolist()


class PolicyExampleRetriever:
    """Retrieves example responses for each policy"""
    def __init__(self, base_dir: Path, embed_model: SentenceTransformer):
        self.base_dir = base_dir
        self.embed_model = embed_model
        self._cache = {}

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
            print(f"Warning: Missing pairs file: {pairs_path}")
            return [], np.array([])
        if not embeds_path.exists():
            print(f"Warning: Missing embeds file: {embeds_path}")
            return [], np.array([])

        pairs = json.loads(pairs_path.read_text(encoding="utf-8"))
        embeds = np.load(embeds_path).astype(np.float32)

        if len(pairs) != embeds.shape[0]:
            raise RuntimeError(f"Pairs/embeds length mismatch for {policy}")

        self._cache[policy] = (pairs, embeds)
        return pairs, embeds

    def retrieve_topk_pairs(self, policy: str, resident_query: str, k: int = 2) -> List[Dict[str, str]]:
        """Retrieve top-k most similar examples for a policy"""
        pairs, embeds = self._load_policy(policy)
        if len(pairs) == 0:
            return []
        
        q = self.embed_model.encode([resident_query], convert_to_numpy=True, normalize_embeddings=True)[0].astype(np.float32)
        idxs = cosine_topk(q, embeds, k=k)

        out = []
        for ix in idxs:
            out.append({
                "resident": (pairs[ix].get("resident_text") or "").strip(),
                "operator": (pairs[ix].get("operator_text") or "").strip(),
            })
        return out


def call_openai_chat(prompt: str, model: str, temperature: float = 0.6, max_tokens: int = 80) -> str:
    """Call OpenAI API for operator response generation (default: short responses ~30-40 words)"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

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


def generate_natural_closing(history: list, end_reason: str, character: str, model: str = "gpt-4o-mini") -> str:
    """
    Generate a natural and contextual closing message for the conversation.
    
    Args:
        history: List of conversation turns with 'role' and 'text'
        end_reason: One of 'agreement', 'refusal', 'max_turns'
        character: Character name for context
        model: OpenAI model to use
    
    Returns:
        Natural closing message from the operator
    """
    # Build conversation context
    recent_turns = history[-6:] if len(history) > 6 else history
    conversation_context = "\n".join([
        f"{turn['role'].upper()}: {turn['text']}" 
        for turn in recent_turns
    ])
    
    # Define the ending context based on reason
    ending_contexts = {
        "agreement": {
            "situation": "The resident has agreed to evacuate and follow safety instructions.",
            "tone": "professional, supportive, and encouraging",
            "goal": "Reinforce their decision, provide final safety reminders, and end positively."
        },
        "refusal": {
            "situation": "The resident has repeatedly refused to evacuate despite multiple attempts to convince them.",
            "tone": "professional but firm, showing concern while respecting their autonomy",
            "goal": "Acknowledge their choice, emphasize the serious risk, offer future assistance, and close professionally."
        },
        "max_turns": {
            "situation": "The conversation has reached the maximum time limit and must end now.",
            "tone": "professional, brief, and warm",
            "goal": "Simply say goodbye and wish them safety. Instructions were already given in previous turns."
        }
    }
    
    context_info = ending_contexts.get(end_reason, ending_contexts["max_turns"])
    
    prompt = f"""You are a fire department emergency dispatcher ending a call with a resident during a wildfire evacuation.

CONVERSATION CONTEXT:
{conversation_context}

ENDING SITUATION:
{context_info['situation']}

INSTRUCTIONS:
- Generate a natural, contextual closing message
- Tone should be: {context_info['tone']}
- Goal: {context_info['goal']}
- CRITICAL: Keep it VERY brief (1-2 SHORT sentences, maximum 20-25 words total)
- For max_turns ending: Just say goodbye and wish safety in ONE sentence.
- For other endings: Still keep it to 1-2 sentences maximum
- Be direct and concise - no elaboration
- DO NOT use quotation marks or labels like "OPERATOR:" in your response
- Sound like a real human emergency dispatcher, not robotic

Generate ONLY the closing message:"""

    try:
        closing = call_openai_chat(prompt, model=model, temperature=0.7, max_tokens=60)
        # Clean up any potential formatting issues
        closing = closing.strip().strip('"').strip("'")
        return closing
    except Exception as e:
        print(f"[ERROR] Failed to generate natural closing: {e}")
        # Fallback to default messages
        fallback_messages = {
            "agreement": "Please evacuate now and stay safe.",
            "refusal": "I understand. Call if you need help. Stay alert.",
            "max_turns": "Stay safe. Goodbye."
        }
        return fallback_messages.get(end_reason, fallback_messages["max_turns"])


def generate_personalized_scenario(survey_data: dict, model: str = "gpt-4o-mini") -> str:
    """
    Generate a personalized emergency scenario based on participant's survey data.
    
    Args:
        survey_data: Dictionary containing survey responses (age, occupation, special needs, etc.)
        model: OpenAI model to use
    
    Returns:
        Personalized scenario description
    """
    age = survey_data.get('age', 'unknown age')
    occupation = survey_data.get('occupation', 'unknown occupation')
    special_needs = survey_data.get('specialNeeds', {})
    
    # Build context about special circumstances
    context_parts = []
    if special_needs.get('hasCondition'):
        context_parts.append("has mobility or communication challenges")
    if special_needs.get('responsibleForOthers'):
        context_parts.append("is responsible for others (children, elderly, or pets)")
    if special_needs.get('needsVehicle'):
        context_parts.append("may need vehicle assistance for evacuation")
    
    context = ", ".join(context_parts) if context_parts else "is at home"
    
    prompt = f"""Generate a brief, realistic emergency scenario (2-3 sentences) for a fire evacuation simulation.

Participant profile:
- Age: {age}
- Occupation: {occupation}
- Situation: {context}

Create a scenario that:
- Is personalized to their circumstances
- Describes a nearby wildfire requiring evacuation
- Sets up an urgent but realistic emergency situation
- Is written in second person ("You are...")
- Does NOT mention their exact age explicitly

Example: "You are at home working on your computer when you notice smoke in the distance. The local news reports a wildfire spreading rapidly through nearby neighborhoods. Your phone rings—it's the fire department."

Generate only the scenario text, no labels or extra formatting."""

    try:
        scenario = call_openai_chat(prompt, model=model, temperature=0.7, max_tokens=100)
        scenario = scenario.strip().strip('"').strip("'")
        print(f"[SCENARIO] Generated personalized scenario: {scenario[:100]}...")
        return scenario
    except Exception as e:
        print(f"[WARNING] Failed to generate scenario: {e}, using fallback")
        return "You are at home when you notice smoke in the distance. A wildfire is spreading rapidly through nearby neighborhoods. Your phone rings—it's the fire department calling about an emergency evacuation."


def generate_initial_greeting(character: str, persona: str, model: str = "gpt-4o-mini") -> str:
    """
    Generate a dynamic initial greeting based on character context.
    
    Args:
        character: Character name
        persona: Character description/persona
        model: OpenAI model to use
    
    Returns:
        Natural greeting message from fire dispatcher
    """
    prompt = f"""You are a fire department dispatcher making an emergency call about a nearby wildfire.

The resident you're calling is: {persona}

Generate a brief, professional opening message (1-2 sentences) that:
- Introduces yourself as fire department dispatch
- Shows awareness of their situation if relevant
- Asks about their immediate safety
- Sounds natural, urgent but calm
- Uses "you" not gendered pronouns

Just output the dispatcher's message, no quotes, no labels, no extra formatting.

Examples of good openings:
"Hello, this is the fire department dispatcher. There's a wildfire in your area. Are you safe right now?"
"Hi, this is fire dispatch calling. We're conducting emergency evacuations nearby. Can you confirm you're okay?"
"Hello, this is the fire department. We need to check on residents in your neighborhood. Are you at home?"
"""

    try:
        greeting = call_openai_chat(prompt, model=model, temperature=0.8, max_tokens=60)
        greeting = greeting.strip().strip('"').strip("'")
        
        # Ensure it's not too long or weird
        if len(greeting) > 200 or len(greeting) < 20:
            raise ValueError("Generated greeting length out of bounds")
            
        print(f"[GREETING] Generated for {character}: {greeting}")
        return greeting
    except Exception as e:
        print(f"[WARNING] Failed to generate greeting: {e}, using fallback")
        # Fallback to default
        return "Hello, this is the fire department dispatcher. Are you safe right now?"


def judge_resident_stance(history: List[Dict[str, str]], model: str) -> dict:
    """Judge whether resident agrees/refuses/delays evacuation"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"stance": "UNKNOWN", "confidence": 0.0, "reason": "API key not set"}

    tail = history[-12:]
    convo = "\n".join([f"{t['role'].capitalize()}: {t['text']}" for t in tail])

    prompt = (
        "You are judging ONLY the RESIDENT's stance about evacuating.\n"
        "Classify into exactly one stance:\n"
        "- AGREE: resident commits to evacuate/leave.\n"
        "- REFUSE: clearly refuses to evacuate/leave.\n"
        "- DELAY: resident delays or stalls without clear commitment.\n"
        "- UNKNOWN: not enough info.\n"
        "Return ONLY valid JSON with keys: stance, confidence, reason. No markdown.\n"
        "confidence must be a number from 0 to 1.\n\n"
        f"{convo}\n"
    )

    try:
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

        # Extract JSON
        import re
        if txt.startswith("```"):
            txt = re.sub(r"^```(?:json)?\s*", "", txt.strip(), flags=re.IGNORECASE)
            txt = re.sub(r"\s*```$", "", txt.strip())
        m = re.search(r"\{[\s\S]*\}", txt)
        if m:
            txt = m.group(0)

        obj = json.loads(txt)
        stance = str(obj.get("stance", "UNKNOWN")).upper()
        conf = float(obj.get("confidence", 0.0) or 0.0)
        reason = str(obj.get("reason", ""))

        if stance not in {"AGREE", "DELAY", "REFUSE", "UNKNOWN"}:
            stance = "UNKNOWN"
        conf = max(0.0, min(1.0, conf))
        return {"stance": stance, "confidence": conf, "reason": reason}
    except Exception as e:
        return {"stance": "UNKNOWN", "confidence": 0.0, "reason": f"Error: {str(e)}"}


def build_prompt(policy_id: str, character_name: str, history: List[Dict[str, str]], examples: List[Dict[str, str]], persuasion_strategy: str = None, max_context_turns: int = 6) -> str:
    """Build prompt for operator response generation
    
    Args:
        policy_id: IQL policy identifier
        character_name: Character being role-played (or "participant" for non-role-play)
        history: Conversation history
        examples: Policy example dialogues
        persuasion_strategy: One of "rational-informational", "emotional-relational", "social-normative" (for non-role-play)
        max_context_turns: Maximum conversation turns to include
    """
    context = history[-max_context_turns:] if len(history) > max_context_turns else history
    context_text = "\n".join([f"{t['role'].capitalize()}: {t['text'].strip()}" for t in context])

    ex_block = "\n\n".join(
        [f"Resident: {ex['resident']}\nOperator: {ex['operator']}" for ex in examples if ex.get("resident") and ex.get("operator")]
    ).strip()

    # Build instruction based on whether this is role-play or non-role-play
    if persuasion_strategy and persuasion_strategy in PERSUASION_STRATEGIES:
        # Non-role-play conversation with specific persuasion strategy
        strategy = PERSUASION_STRATEGIES[persuasion_strategy]
        instruction = (
            f"You are a FIRE DEPARTMENT OPERATOR talking to a RESIDENT during a wildfire evacuation call.\n"
            f"PERSUASION STRATEGY: {strategy['name']}\n"
            f"{strategy['description']}\n\n"
            f"Guidelines for this conversation:\n{strategy['guidelines']}\n"
            "Read the conversation so far, then produce the next operator reply.\n"
            "CRITICAL RULES:\n"
            "- KEEP IT BRIEF: Maximum 1-2 short sentences (20-30 words total).\n"
            "- Get straight to the point - no elaboration.\n"
            "- Stay in character as a professional fire department dispatcher.\n"
            "- Focus evacuation-related guidance.\n"
            "- No role labels, no meta commentary.\n"
            "- Consistently apply the persuasion strategy throughout.\n"
            f"- Use the {strategy['name']} approach in your response.\n"
            "- DO NOT over-explain. Be direct and concise."
        )
    else:
        # Role-play conversation with IQL policy
        instruction = (
            f"You are the OPERATOR talking to {character_name.upper()} (the RESIDENT) during a wildfire evacuation call.\n"
            f"Use the operator policy style optimized for: {policy_id}.\n"
            f"{character_name}'s background: {CHARACTER_PERSONAS.get(character_name.lower(), 'Unknown')}\n"
            "Read the conversation so far, then produce the next operator reply.\n"
            "CRITICAL RULES:\n"
            "- KEEP IT BRIEF: Maximum 1-2 short sentences (20-30 words total).\n"
            "- Get straight to the point - no elaboration.\n"
            "- Calm, professional, evacuation-focused.\n"
            "- If resident resists, emphasize urgency/danger; if cooperative, give clear next steps.\n"
            "- No role labels, no meta commentary.\n"
            "- Avoid gendered pronouns.\n"
            "- DO NOT over-explain. Be direct and concise.\n"
            "Use the similar examples for style guidance."
        )

    return (
        f"{instruction}\n\n"
        f"Conversation so far:\n{context_text}\n\n"
        f"Similar example dialogues:\n{ex_block if ex_block else '(none)'}\n\n"
        "Operator:"
    )


# ============================================================================
# Session Management
# ============================================================================

# In-memory session storage (for production, use Redis or database)
conversation_sessions = {}

# In-memory participant data storage (surveys and post-surveys)
# Structure: {participant_id: {"survey": {...}, "post_surveys": [...]}}
participant_data = {}


def get_session(session_id: str) -> Dict[str, Any]:
    """Get or create conversation session"""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "history": [],
            "turn_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "character": None,
            "participant_id": None,
            "iql_data": []  # Store IQL policy decisions for each turn
        }
    return conversation_sessions[session_id]


# Conversation history is now stored in memory and saved only when participant exits or completes study


# ============================================================================
# Initialize IQL System
# ============================================================================

def find_first_existing(*paths: Path) -> Path:
    """Find first existing path"""
    for p in paths:
        if p.exists():
            return p
    return paths[0]


def load_policy_names_from_label_map(label_map_path: Path) -> List[str]:
    """Load policy names from label map"""
    label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
    return [k for k, _ in sorted(label_map.items(), key=lambda kv: kv[1])]


# Global IQL system (lazy initialization)
iql_selector = None
policy_retriever = None


def initialize_policy_retriever_lazy():
    """Lazy initialization of policy retriever (loads on first use)"""
    global policy_retriever
    
    if policy_retriever is not None:
        return  # Already initialized
    
    import time as timing_module
    base = Path(__file__).resolve().parent
    
    try:
        print("[POLICY-RETRIEVER] Lazy loading sentence-transformers (first use, may take 30-60s)...")
        t1 = timing_module.time()
        
        # Load sentence-transformers model
        embed_model = SentenceTransformer(EMBED_MODEL)
        
        # Warm up with a dummy encoding
        _ = embed_model.encode(["warm up"], convert_to_numpy=True)
        
        t2 = timing_module.time()
        print(f"[POLICY-RETRIEVER] Model loaded in {t2-t1:.2f}s")
        
        # Initialize policy retriever
        policy_retriever = PolicyExampleRetriever(base_dir=base, embed_model=embed_model)
        print("[POLICY-RETRIEVER] Ready for fast retrieval")
        
    except Exception as e:
        print(f"[ERROR] Policy retriever lazy initialization failed: {e}")
        traceback.print_exc()
        policy_retriever = None


def initialize_iql():
    """Initialize IQL system using Hugging Face API ONLY"""
    global iql_selector, policy_retriever
    
    if iql_selector is not None:
        return  # Already initialized
    
    if not HF_API_AVAILABLE:
        print("[ERROR] Hugging Face API wrapper not available!")
        print("[ERROR] Make sure iql_hf_api.py is present and dependencies are installed")
        return
    
    try:
        import time as timing_module
        init_start = timing_module.time()
        
        # Use Hugging Face API - no local model
        iql_selector = get_iql_hf()
        
        # Use LAZY LOADING for policy retriever to save memory at startup
        # Will load on first Session 2 message instead of at startup
        print("[POLICY-RETRIEVER] Using lazy loading (will load on first use)")
        print("[POLICY-RETRIEVER] This keeps startup fast and saves memory")
        policy_retriever = None  # Will be initialized on first use
        
        init_end = timing_module.time()
        print(f"[IQL] System initialized successfully in {init_end-init_start:.2f}s (Hugging Face API)")
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize Hugging Face IQL API: {e}")
        print("[ERROR] Check HUGGINGFACE_MODEL_ID and HUGGINGFACE_TOKEN environment variables")
        traceback.print_exc()
        iql_selector = None


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(title="Emergency Response Chatbot Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Update with your Netlify URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.onrender.com", "*.netlify.app"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class SurveyResponse(BaseModel):
    timestamp: str
    background: Dict[str, str]
    personality: Dict[str, str]
    moral: Dict[str, str]
    specialNeeds: Dict[str, str]


class ChatMessage(BaseModel):
    role: str  # "resident" or "operator"
    text: str


class ChatRequest(BaseModel):
    session_id: str
    character: Optional[str] = None  # e.g., "bob", "ben", etc. (None for non-role-play)
    participant_id: Optional[str] = None
    message: str  # Resident's message


# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize IQL system on startup"""
    initialize_iql()


@app.get("/")
async def root():
    """Health check endpoint"""
    iql_status = "enabled" if iql_selector is not None else "disabled"
    return {
        "status": "ok",
        "message": "Emergency Response Chatbot Backend is running",
        "iql_status": iql_status
    }


@app.post("/api/survey")
async def submit_survey(survey: SurveyResponse):
    """Submit survey responses and generate a unique participant ID"""
    try:
        participant_id = str(uuid.uuid4())
        
        survey_data = survey.dict()
        survey_data['participantId'] = participant_id
        survey_data['serverTimestamp'] = datetime.utcnow().isoformat()
        
        # Store in memory only (no file creation yet)
        participant_data[participant_id] = {
            "survey": survey_data,
            "post_surveys": []
        }
        
        print(f"[SURVEY] Submitted and stored in memory: {participant_id}")
        
        return {
            "success": True,
            "participantId": participant_id,
            "message": "Survey submitted successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] Survey submission failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error submitting survey: {str(e)}")


@app.get("/api/survey/{participant_id}")
async def get_survey(participant_id: str):
    """Retrieve survey responses for a specific participant (from memory)"""
    try:
        if participant_id not in participant_data:
            raise HTTPException(status_code=404, detail="Participant not found")
        
        survey_data = participant_data[participant_id].get("survey")
        
        if not survey_data:
            raise HTTPException(status_code=404, detail="Survey not found for participant")
        
        return survey_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Survey retrieval failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving survey: {str(e)}")


@app.post("/api/chat/start")
async def start_chat(request: Request):
    """Start a new chat session (role-play or non-role-play)"""
    try:
        data = await request.json()
        if data is None:
            raise HTTPException(status_code=400, detail="Request body is required")
        
        character = data.get("character")
        character = character.lower() if character else None
        participant_id = data.get("participantId")
        persuasion_strategy = data.get("persuasionStrategy")  # For non-role-play conversations
        survey_data = data.get("surveyData")  # For generating personalized scenario
        
        # Get model configuration
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Handle non-role-play conversation
        if persuasion_strategy:
            if persuasion_strategy not in PERSUASION_STRATEGIES:
                raise HTTPException(status_code=400, detail=f"Unknown persuasion strategy: {persuasion_strategy}")
            
            # Create session for non-role-play
            session_id = f"{participant_id}_nonrole_{persuasion_strategy}_{int(time.time())}"
            session = get_session(session_id)
            session["character"] = None  # No character in non-role-play
            session["participant_id"] = participant_id
            session["persuasion_strategy"] = persuasion_strategy
            session["is_roleplay"] = False
            
            # Generate personalized scenario if survey data provided
            if survey_data:
                scenario = generate_personalized_scenario(survey_data, model=model)
                session["scenario"] = scenario
            else:
                scenario = "You are at home when you notice smoke in the distance. A wildfire is spreading rapidly. Your phone rings—it's the fire department."
                session["scenario"] = scenario
            
            # Generate initial greeting
            initial_message = generate_initial_greeting("participant", "a resident at home", model=model)
            session["history"].append({"role": "operator", "text": initial_message})
            
            print(f"[CHAT] Started non-role-play session: {session_id}, strategy: {persuasion_strategy}")
            print(f"[CHAT] Scenario: {scenario}")
            print(f"[CHAT] Initial greeting: {initial_message}")
            
            return {
                "session_id": session_id,
                "initial_message": initial_message,
                "scenario": scenario,
                "is_roleplay": False
                # Note: persuasion_strategy is kept server-side only, not exposed to participant
            }
        
        # Handle role-play conversation
        else:
            if character not in CHARACTER_PERSONAS:
                raise HTTPException(status_code=400, detail=f"Unknown character: {character}")
            
            # Create session for role-play
            session_id = f"{participant_id}_{character}_{int(time.time())}"
            session = get_session(session_id)
            session["character"] = character
            session["participant_id"] = participant_id
            session["persuasion_strategy"] = None
            session["is_roleplay"] = True
            
            # Generate dynamic initial greeting
            persona = CHARACTER_PERSONAS[character]
            initial_message = generate_initial_greeting(character, persona, model=model)
            session["history"].append({"role": "operator", "text": initial_message})
            
            print(f"[CHAT] Started role-play session: {session_id} for character: {character}")
            print(f"[CHAT] Initial greeting: {initial_message}")
            
            return {
                "session_id": session_id,
                "initial_message": initial_message,
                "character": character,
                "is_roleplay": True
            }
        
    except Exception as e:
        print(f"[ERROR] Chat start failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/message")
async def send_message(chat_req: ChatRequest):
    """Send a resident message and get operator response"""
    try:
        if iql_selector is None:
            # Fallback if IQL not available
            return {
                "response": "I understand. Please evacuate immediately if you can.",
                "session_id": chat_req.session_id,
                "policy": "fallback",
                "turn_count": 1,
                "conversation_ended": False
            }
        
        session = get_session(chat_req.session_id)
        history = session["history"]
        character_raw = chat_req.character
        character = character_raw.lower() if character_raw else session.get("character", "resident")
        
        # Add resident message to history
        history.append({"role": "resident", "text": chat_req.message})
        session["turn_count"] += 1
        resident_turns = session["turn_count"]
        
        print(f"[CHAT] Session: {chat_req.session_id}, Turn: {resident_turns}, Resident: {chat_req.message}")
        
        # Set model for all operations
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Check for hard cap
        if resident_turns >= MAX_TURNS:
            print(f"[CHAT] Max turns reached, generating natural closing")
            closing = generate_natural_closing(history, "max_turns", character, model=model)
            history.append({"role": "operator", "text": closing})
            print(f"[CHAT] Closing message: {closing}")
            
            # Conversation stays in memory until exit/completion
            
            return {
                "response": closing,
                "session_id": chat_req.session_id,
                "turn_count": resident_turns,
                "conversation_ended": True,
                "end_reason": "max_turns"
            }
        
        # Judge resident stance
        judge = judge_resident_stance(history, model=model)
        stance = judge["stance"]
        conf = judge["confidence"]
        
        can_end = resident_turns >= MIN_RESIDENT_TURNS
        
        # Success end
        if can_end and stance == "AGREE" and conf >= 0.70:
            print(f"[CHAT] Success end (resident agreed), generating natural closing")
            closing = generate_natural_closing(history, "agreement", character, model=model)
            history.append({"role": "operator", "text": closing})
            print(f"[CHAT] Closing message: {closing}")
            
            # Conversation stays in memory until exit/completion
            
            return {
                "response": closing,
                "session_id": chat_req.session_id,
                "turn_count": resident_turns,
                "conversation_ended": True,
                "end_reason": "agreement",
                "judge": judge
            }
        
        # Track consecutive refusals
        if not hasattr(session, 'consecutive_refuse'):
            session['consecutive_refuse'] = 0
        
        if stance == "REFUSE" and conf >= 0.85:
            session['consecutive_refuse'] += 1
        else:
            session['consecutive_refuse'] = 0
        
        # Forced end after repeated refusals
        if can_end and session['consecutive_refuse'] >= 2:
            print(f"[CHAT] Forced end (repeated refusal), generating natural closing")
            closing = generate_natural_closing(history, "refusal", character, model=model)
            history.append({"role": "operator", "text": closing})
            print(f"[CHAT] Closing message: {closing}")
            
            # Conversation stays in memory until exit/completion
            
            return {
                "response": closing,
                "session_id": chat_req.session_id,
                "turn_count": resident_turns,
                "conversation_ended": True,
                "end_reason": "refusal",
                "judge": judge
            }
        
        # Check if this is a non-role-play conversation with persuasion strategy
        persuasion_strategy = session.get("persuasion_strategy")
        best_policy = None
        qvals = None
        
        if persuasion_strategy:
            # Non-role-play conversation: use persuasion strategy directly
            print(f"[PERSUASION] Using strategy: {persuasion_strategy}")
            prompt = build_prompt("default", "participant", history, [], persuasion_strategy=persuasion_strategy)
            operator_response = call_openai_chat(prompt, model=model)
        else:
            # Role-play conversation: use IQL policy selection
            import time as timing_module
            t1 = timing_module.time()
            best_policy, qvals = iql_selector.select_policy(history, character=character, n_last=N_LAST_RESIDENT)
            t2 = timing_module.time()
            print(f"[IQL] Selected policy: {best_policy} (took {t2-t1:.2f}s)")
            
            # Retrieval + operator generation
            # Lazy load policy retriever on first use
            if policy_retriever is None:
                initialize_policy_retriever_lazy()
            
            t3 = timing_module.time()
            if policy_retriever:
                examples = policy_retriever.retrieve_topk_pairs(best_policy, resident_query=chat_req.message, k=2)
            else:
                print("[WARNING] Policy retriever not available, using no examples")
                examples = []
            t4 = timing_module.time()
            print(f"[RETRIEVAL] Got {len(examples)} examples (took {t4-t3:.2f}s)")
            
            t5 = timing_module.time()
            prompt = build_prompt(best_policy, character, history, examples)
            operator_response = call_openai_chat(prompt, model=model)
            t6 = timing_module.time()
            print(f"[OPENAI] Generated response (took {t6-t5:.2f}s)")
        
        history.append({"role": "operator", "text": operator_response})
        
        print(f"[CHAT] Operator: {operator_response}")
        
        # Store IQL data in session for role-play conversations
        if best_policy is not None:
            iql_turn_data = {
                "turn": resident_turns,
                "resident_message": chat_req.message,
                "operator_response": operator_response,
                "selected_policy": best_policy,
                "q_values": qvals,
                "judge": judge,
                "timestamp": datetime.utcnow().isoformat()
            }
            if "iql_data" not in session:
                session["iql_data"] = []
            session["iql_data"].append(iql_turn_data)
        
        # Build response based on conversation type
        response_data = {
            "response": operator_response,
            "session_id": chat_req.session_id,
            "turn_count": resident_turns,
            "conversation_ended": False,
            "judge": judge
        }
        
        # Add IQL-specific data only for role-play conversations
        if best_policy is not None:
            response_data["policy"] = best_policy
            response_data["q_values"] = qvals
        
        return response_data
        
    except Exception as e:
        print(f"[ERROR] Chat message failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = conversation_sessions[session_id]
    return {
        "history": session["history"],
        "turn_count": session["turn_count"],
        "character": session.get("character"),
        "created_at": session.get("created_at")
    }


def get_next_confirmation_number(prefix: str) -> str:
    """Generate next sequential confirmation number with given prefix (INC or CCC)"""
    confirmation_file = os.path.join(SURVEY_RESPONSES_DIR, "confirmation_numbers.json")
    
    # Load existing confirmation numbers
    if os.path.exists(confirmation_file):
        with open(confirmation_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"INC": 0, "CCC": 0}
    
    # Increment counter for this prefix
    data[prefix] = data.get(prefix, 0) + 1
    number = data[prefix]
    
    # Save updated counters
    os.makedirs(SURVEY_RESPONSES_DIR, exist_ok=True)
    with open(confirmation_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Return formatted confirmation number
    return f"{prefix}{number:03d}"


def email_participant_data(data: dict, subject: str):
    """Email participant data as JSON attachment via Gmail SMTP"""
    try:
        # Get Gmail credentials from environment
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient_email = os.getenv('RESEARCHER_EMAIL', 'tzhang62@usc.edu')
        
        if not gmail_user or not gmail_password:
            print("[EMAIL] Gmail credentials not set, skipping email")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        confirmation = data.get("confirmation_number", "UNKNOWN")
        status = data.get("status", "unknown")
        timestamp = data.get("completion_timestamp") or data.get("exit_timestamp", "N/A")
        
        # Email body
        body = f"""Participant Data Received

Confirmation Number: {confirmation}
Status: {status}
Timestamp: {timestamp}

Complete data is attached as JSON file.
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach JSON file
        json_str = json.dumps(data, indent=2)
        attachment = MIMEApplication(json_str.encode(), _subtype='json')
        attachment.add_header('Content-Disposition', 'attachment', 
                            filename=f'{confirmation}.json')
        msg.attach(attachment)
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        
        print(f"[EMAIL] Sent {confirmation} to {recipient_email} via Gmail")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to email via Gmail: {e}")
        traceback.print_exc()
        return False


@app.post("/api/exit-study")
async def exit_study(request: Request):
    """Handle early exit from study and generate INC confirmation number"""
    try:
        data = await request.json()
        participant_id = data.get("participantId")
        page = data.get("exitPage", "unknown")
        
        if not participant_id:
            raise HTTPException(status_code=400, detail="Participant ID required")
        
        # Generate INC confirmation number
        confirmation_number = get_next_confirmation_number("INC")
        
        # Gather all participant data from memory
        exit_data = {
            "confirmation_number": confirmation_number,
            "participant_id": participant_id,
            "status": "incomplete",
            "exit_page": page,
            "exit_timestamp": datetime.utcnow().isoformat()
        }
        
        # Get survey data from memory
        if participant_id in participant_data:
            if participant_data[participant_id].get("survey"):
                exit_data["survey"] = participant_data[participant_id]["survey"]
            if participant_data[participant_id].get("post_surveys"):
                exit_data["post_surveys"] = participant_data[participant_id]["post_surveys"]
        
        # Gather all conversations for this participant from conversation_sessions
        conversations = []
        for session_id, session in conversation_sessions.items():
            if session.get("participant_id") == participant_id:
                conv_data = {
                    "session_id": session_id,
                    "character": session.get("character"),
                    "conversation_type": "roleplay" if session.get("is_roleplay") else "non-roleplay",
                    "persuasion_strategy": session.get("persuasion_strategy"),
                    "history": session["history"],
                    "iql_data": session.get("iql_data", []),
                    "turn_count": session["turn_count"],
                    "created_at": session.get("created_at"),
                    "ended_at": datetime.utcnow().isoformat(),
                    "scenario": session.get("scenario")
                }
                conversations.append(conv_data)
        
        if conversations:
            exit_data["conversations"] = conversations
        
        # Save comprehensive exit record with ONE file
        exit_dir = os.path.join(SURVEY_RESPONSES_DIR, "exits")
        os.makedirs(exit_dir, exist_ok=True)
        
        exit_file = os.path.join(exit_dir, f"{confirmation_number}.json")
        with open(exit_file, 'w') as f:
            json.dump(exit_data, f, indent=2)
        
        # Email the data to researcher
        email_participant_data(exit_data, f"Study Exit: {confirmation_number}")
        
        # Clean up memory for this participant
        if participant_id in participant_data:
            del participant_data[participant_id]
        
        sessions_to_remove = [sid for sid, sess in conversation_sessions.items() 
                             if sess.get("participant_id") == participant_id]
        for sid in sessions_to_remove:
            del conversation_sessions[sid]
        
        print(f"[EXIT] Participant {participant_id} exited from {page}, confirmation: {confirmation_number}")
        
        return {
            "success": True,
            "confirmation_number": confirmation_number,
            "message": f"Thank you for your time. Your confirmation number is: {confirmation_number}"
        }
        
    except Exception as e:
        print(f"[ERROR] Exit study failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class PostSurveyResponse(BaseModel):
    sessionId: str
    participantId: Optional[str] = None
    character: Optional[str] = None  # None for non-role-play conversations
    conversationNumber: Optional[int] = 1
    timestamp: str
    willing: str  # 'yes', 'maybe', 'no'
    willingYesDetails: Optional[str] = ""
    willingNoDetails: Optional[str] = ""
    naturalness: str
    unnaturalUtterances: List[int] = []


@app.post("/api/post-survey")
async def submit_post_survey(survey: PostSurveyResponse):
    """Submit post-conversation survey responses"""
    try:
        survey_data = survey.dict()
        participant_id = survey.participantId
        
        # Store in memory only (no file creation yet)
        if participant_id in participant_data:
            participant_data[participant_id]["post_surveys"].append(survey_data)
            print(f"[POST-SURVEY] Stored in memory for session: {survey.sessionId}")
        else:
            print(f"[WARNING] Post-survey for unknown participant: {participant_id}")
            # Create entry anyway
            participant_data[participant_id] = {
                "survey": None,
                "post_surveys": [survey_data]
            }
        
        return {
            "success": True,
            "message": "Post-survey submitted successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] Post-survey submission failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error submitting post-survey: {str(e)}")


@app.post("/api/complete-study")
async def complete_study(request: Request):
    """Handle study completion and generate CCC confirmation number"""
    try:
        data = await request.json()
        participant_id = data.get("participantId")
        
        if not participant_id:
            raise HTTPException(status_code=400, detail="Participant ID required")
        
        # Generate CCC confirmation number
        confirmation_number = get_next_confirmation_number("CCC")
        
        # Gather all participant data from memory
        completion_data = {
            "confirmation_number": confirmation_number,
            "participant_id": participant_id,
            "status": "complete",
            "completion_timestamp": datetime.utcnow().isoformat()
        }
        
        # Get survey and post-survey data from memory
        if participant_id in participant_data:
            if participant_data[participant_id].get("survey"):
                completion_data["survey"] = participant_data[participant_id]["survey"]
            if participant_data[participant_id].get("post_surveys"):
                completion_data["post_surveys"] = participant_data[participant_id]["post_surveys"]
        
        # Gather ALL conversations for this participant from conversation_sessions
        conversations = []
        for session_id, session in conversation_sessions.items():
            if session.get("participant_id") == participant_id:
                conv_data = {
                    "session_id": session_id,
                    "character": session.get("character"),
                    "conversation_type": "roleplay" if session.get("is_roleplay") else "non-roleplay",
                    "persuasion_strategy": session.get("persuasion_strategy"),
                    "history": session["history"],
                    "iql_data": session.get("iql_data", []),
                    "turn_count": session["turn_count"],
                    "created_at": session.get("created_at"),
                    "ended_at": session.get("ended_at", datetime.utcnow().isoformat()),
                    "scenario": session.get("scenario")
                }
                conversations.append(conv_data)
        
        # Sort conversations by creation time
        conversations.sort(key=lambda x: x.get("created_at", ""))
        completion_data["conversations"] = conversations
        
        # Save complete record with ONE file
        complete_dir = os.path.join(SURVEY_RESPONSES_DIR, "completed")
        os.makedirs(complete_dir, exist_ok=True)
        
        complete_file = os.path.join(complete_dir, f"{confirmation_number}.json")
        with open(complete_file, 'w') as f:
            json.dump(completion_data, f, indent=2)
        
        # Email the data to researcher
        email_participant_data(completion_data, f"Study Complete: {confirmation_number}")
        
        # Clean up memory for this participant
        if participant_id in participant_data:
            del participant_data[participant_id]
        
        sessions_to_remove = [sid for sid, sess in conversation_sessions.items() 
                             if sess.get("participant_id") == participant_id]
        for sid in sessions_to_remove:
            del conversation_sessions[sid]
        
        print(f"[COMPLETE] Participant {participant_id} completed study, confirmation: {confirmation_number}")
        
        return {
            "success": True,
            "confirmation_number": confirmation_number,
            "message": f"Thank you for completing the study! Your confirmation number is: {confirmation_number}"
        }
        
    except Exception as e:
        print(f"[ERROR] Complete study failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/export-data")
async def export_all_data(admin_key: str = None):
    """Export all collected data as a ZIP file for download"""
    # Simple authentication - set your own admin key in environment variable
    expected_key = os.getenv("ADMIN_KEY", "your-secret-admin-key-here")
    
    if admin_key != expected_key:
        raise HTTPException(status_code=403, detail="Unauthorized. Invalid admin key.")
    
    try:
        import zipfile
        from io import BytesIO
        
        # Create a BytesIO buffer for the ZIP file
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all files from survey_responses directory
            for root, dirs, files in os.walk(SURVEY_RESPONSES_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Get relative path for ZIP
                    arcname = os.path.relpath(file_path, SURVEY_RESPONSES_DIR)
                    zip_file.write(file_path, arcname)
            
            # Add chat session data (if you want to include active sessions)
            # Create a summary file
            summary = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_surveys": len([f for f in os.listdir(SURVEY_RESPONSES_DIR) if f.endswith('.json')]),
                "active_sessions": len(conversation_sessions),
                "export_info": "All participant data exported"
            }
            
            summary_json = json.dumps(summary, indent=2)
            zip_file.writestr("_export_summary.json", summary_json)
        
        # Seek to beginning of buffer
        zip_buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"study_data_export_{timestamp}.zip"
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"[ERROR] Data export failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/stats")
async def get_stats(admin_key: str = None):
    """Get statistics about collected data"""
    expected_key = os.getenv("ADMIN_KEY", "your-secret-admin-key-here")
    
    if admin_key != expected_key:
        raise HTTPException(status_code=403, detail="Unauthorized. Invalid admin key.")
    
    try:
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_participants": len(participant_data),
            "active_sessions": len(conversation_sessions),
            "completed_studies": 0,
            "incomplete_exits": 0
        }
        
        # Count completed studies (CCC files)
        completed_dir = os.path.join(SURVEY_RESPONSES_DIR, "completed")
        if os.path.exists(completed_dir):
            stats["completed_studies"] = len([f for f in os.listdir(completed_dir) if f.endswith('.json')])
        
        # Count exits (INC files)
        exits_dir = os.path.join(SURVEY_RESPONSES_DIR, "exits")
        if os.path.exists(exits_dir):
            stats["incomplete_exits"] = len([f for f in os.listdir(exits_dir) if f.endswith('.json')])
        
        # Total participants
        stats["total_participants"] = stats["completed_studies"] + stats["incomplete_exits"]
        
        return stats
        
    except Exception as e:
        print(f"[ERROR] Stats retrieval failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
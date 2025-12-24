#!/usr/bin/env python3
"""
A07_simulate_with_iql_and_mavis.py

Single-run simulator:
  • IQL policy selection on last N resident utterances (embeddings)
  • In-policy retrieval (k=2) and single-turn ICL operator generation
  • Mavis generates resident replies (backend /chat)
  • Optional seed operator line
  • Alternating turns with early stop check (decision.py)
  • Returns a rich result dict consumed by A08

This file is /dataA-aware and returns full `history` for A08.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import requests
from requests import RequestException

from A06_select_policy import IQLPolicySelector
from A06c_generate_operator_reply_pairs import retrieve_topk_pairs
from decision import is_successful_session
from personas import PERSONA
# --------------------------------------------------------------------
# CONFIG (adjust if needed)
# --------------------------------------------------------------------
MAVIS_URL = "http://localhost:8001/chat"         # FastAPI backend for resident replies
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
MAX_TURNS = 16        # total turns (operator+resident entries) cap
K_EXAMPLES = 2        # ICL few-shots per operator turn
N_LAST_RESIDENT = 3   # used inside IQL selector (already configured there)

DATAA = Path(__file__).resolve().parent / "dataA"
RUN_DIR = DATAA / "runs" / f"run_{RUN_ID}"
RUN_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------
# UTILITIES
# --------------------------------------------------------------------
def call_ollama(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.7, max_tokens: int = 128) -> str:
    """Call Ollama local API; return text or a safe fallback."""
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
        )
        r.raise_for_status()
        obj = r.json()
        return (obj.get("response") or "").strip()
    except RequestException as e:
        print(f"[ERR] Ollama call failed: {e}")
        try:
            # Some servers include response body with details
            print("[DETAIL]", r.text)  # noqa: F821 (r may not exist if early failure)
        except Exception:
            pass
        # Short, safe fallback (1 sentence)
        return "Please evacuate immediately; conditions can worsen quickly."

def call_mavis_api(history: List[Dict[str, str]],
                   resident: str,
                   temperature: float = 0.7,
                   max_tokens: int = 64,
                   timeout_s: int = 30) -> str:
    """Send correct schema to Mavis backend to get the next resident reply."""
    last_op = ""
    for h in reversed(history):
        if h.get("role") == "operator":
            last_op = (h.get("text") or "").strip()
            break
    if not last_op:
        last_op = "Please respond."

    payload = {
        "speaker": "Resident",
        "resident": resident,
        "history": [{"role": h.get("role", ""), "text": h.get("text", "")} for h in history],
        "text": last_op,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    try:
        r = requests.post(MAVIS_URL, json=payload, timeout=timeout_s)
        r.raise_for_status()
        obj = r.json()
        return (obj.get("text") or "").strip()
    except RequestException as e:
        print(f"[ERR] Mavis backend failed: {e}")
        try:
            print("[DETAIL]", r.text)  # noqa: F821
        except Exception:
            pass
        # Fallback resident line so loop can continue
        return "Sorry, I didn’t quite understand that."

# def build_prompt(policy_id: str,
#                  history: List[Dict[str, str]],
#                  examples: List[Dict],
#                  one_sentence: bool = True) -> str:
#     """
#     Single-turn, policy-conditioned prompt:
#       - ONLY the latest resident utterance
#       - 2 policy-specific few-shot (resident/operator) examples
#       - strict 1-sentence constraint for operator
#     """
#     # latest resident line only
#     last_res = ""
#     for h in reversed(history):
#         if h.get("role") == "resident":
#             last_res = (h.get("text") or "").strip()
#             break
#     if not last_res:
#         last_res = "(no resident input)"

#     # format two examples
#     ex_lines = []
#     for ex in examples[:2]:
#         pair = ex.get("pair", ex)
#         r = (pair.get("resident") or "").strip()
#         o = (pair.get("operator") or "").strip()
#         if r and o:
#             ex_lines.append(f"Resident: {r}\nOperator: {o}")
#     if not ex_lines:
#         ex_block = (
#             "Resident: The fire doesn’t look too close.\n"
#             "Operator: Please evacuate immediately; winds can change quickly."
#         )
#     else:
#         ex_block = "\n\n".join(ex_lines)

#     constraints = (
#         "Write the next Operator reply.\n"
#         "Rules:\n"
#         "1) ONE sentence only.\n"
#         "2) Do not include labels like 'Operator:'.\n"
#         "3) Be calm, factual, and focused on evacuation safety.\n"
#         "4) Avoid emotional or dramatic tone.\n"
#     )

#     prompt = (
#         f"You are using the '{policy_id}' operator policy.\n\n"
#         f"Here are two past examples for this policy:\n"
#         f"{ex_block}\n\n"
#         f"Current Resident message:\nResident: {last_res}\n\n"
#         f"{constraints}\n"
#         f"Next Operator reply:"
#     )
#     return prompt


# ---------------------------------------------------------------------
# Improved prompt builder for operator replies
# ---------------------------------------------------------------------
def build_prompt(policy_id: str,
                 history: list,
                 k_examples: list,
                 persona_map: dict,
                 max_context_turns: int = 6) -> str:
    """
    Builds a richer operator prompt:
      • Includes last N turns of dialogue history
      • Anchors persona/tone to the chosen operator policy
      • Injects retrieved examples for in-context learning
    """

    # 1. Persona anchor ------------------------------------------------
    persona_text = persona_map.get(policy_id, "")
    if not persona_text:
        persona_text = (
            f"The operator '{policy_id}' is professional, calm, and persuasive. "
            "Their goal is to convince the resident to evacuate safely."
        )

    # 2. Context window (recent conversation) --------------------------
    context = history[-max_context_turns:] if len(history) > max_context_turns else history
    dialogue_snippets = []
    for turn in context:
        role = turn["role"].capitalize()
        dialogue_snippets.append(f"{role}: {turn['text'].strip()}")
    context_text = "\n".join(dialogue_snippets)

    # 3. Retrieved examples (few-shot) --------------------------------
    example_lines = []
    for ex in k_examples:
        r_line = ex.get("resident", "").strip()
        o_line = ex.get("operator", "").strip()
        if r_line and o_line:
            example_lines.append(f"Resident: {r_line}\nOperator: {o_line}")
    example_block = "\n\n".join(example_lines[:3])

    # 4. Instruction ---------------------------------------------------
    instruction = (
        # f"{persona_text}\n\n"
        "You are the OPERATOR talking to a RESIDENT during a wildfire evacuation call.\n"
        "Read the conversation so far, then produce your next short reply as the operator.\n"
        "Be persuasive and emphasize danger if the resident resists, or reassuring if they seem cooperative.\n"
        "State the importance of life if they still continue to be reluctant over leaving their house or work.\n"
        "Do not include role labels or meta commentary.\n"
        "Avoid using any gender based pronouns.\n"
        "Refer to the similar example dialgues in the situation and generate similar dialogue.\n "
        "Keep it coherent to the recent conversation.\n"
        "Aim for 1–2 natural sentences."
    )

    # 5. Final assembled prompt ---------------------------------------
    prompt = (
        f"{instruction}\n\n"
        "Conversation so far:\n"
        f"{context_text}\n\n"
        "Similar example dialogues:\n"
        f"{example_block}\n\n"
        "Operator:"
    )
    return prompt.strip()


# --------------------------------------------------------------------
# MAIN SIMULATION
# --------------------------------------------------------------------
def simulate_conversation(resident_name: str = "ross",
                          seed_text: Optional[str] = None,
                          temperature_op: float = 0.5,
                          temperature_res: float = 0.8,
                          max_tokens_op: int = 64,
                          max_tokens_res: int = 128) -> Dict:
    """
    Run one conversation.

    If `seed_text` is provided, we start with an OPERATOR turn using that seed,
    then the next turn is RESIDENT. If not provided, we start with a RESIDENT
    opener ("Hello? Who is this?") and the next turn is OPERATOR.
    """
    print("[INFO] Initializing IQL selector (first load may download SBERT)…")
    selector = IQLPolicySelector()

    # Seed history and who speaks next
    history: List[Dict[str, str]] = []
    if seed_text and seed_text.strip():
        history.append({"role": "operator", "text": seed_text.strip()})
        operator_next = False   # operator spoke → resident goes next
    else:
        history.append({"role": "resident", "text": "Hello? Who is this?"})
        operator_next = True    # resident spoke → operator goes next

    print(f"\n[START] Conversation Run: {RUN_ID}")
    print(f"Resident persona: {resident_name}")
    print("=" * 60)

    # loop
    for turn_idx in range(1, MAX_TURNS + 1):
        if operator_next:
            # ---------- OPERATOR TURN ----------
            # require at least one resident line before selecting policy
            if not any(h.get("role") == "resident" for h in history):
                # if somehow no resident line yet, skip to resident
                operator_next = False
                continue

            best_policy, qvals = selector.select_policy(history)
            # latest resident for retrieval query
            last_res = ""
            for h in reversed(history):
                if h.get("role") == "resident":
                    last_res = (h.get("text") or "").strip()
                    break

            retrieved = retrieve_topk_pairs(best_policy, last_res, k=K_EXAMPLES)
            print(f"[TURN {turn_idx}] Policy: {best_policy}, "
                  f"Q-values: {{ {', '.join(f'{k}: {round(v,3)}' for k,v in qvals.items())} }}")

            prompt = build_prompt(best_policy, history, retrieved, PERSONA)
            op_reply = call_ollama(prompt, model=OLLAMA_MODEL, temperature=temperature_op, max_tokens=max_tokens_op)

            history.append({
                "role": "operator",
                "text": op_reply,
                "selected_policy": best_policy,
                "examples_used": retrieved
            })
            print(f"Operator ({best_policy}): {op_reply}\n")

            operator_next = False
            continue

        # ---------- RESIDENT TURN ----------
        res_reply = call_mavis_api(
            history=history,
            resident=resident_name,
            temperature=temperature_res,
            max_tokens=max_tokens_res,
            timeout_s=30
        )
        history.append({"role": "resident", "text": res_reply})
        print(f"Resident: {res_reply}\n")

        # Early-stop check after resident turn
        # ------------------ DECISION CHECK ------------------
        decision, closing_msg = is_successful_session(
            conversation=history,
            min_turns=4,
            tail_window=3,
            max_turns=MAX_TURNS,
            allow_early_stop=True
        )

        if decision is True:
            print("[✓] Resident agreed to evacuate — conversation successful.")
            if closing_msg:
                history.append({"role": "operator", "text": closing_msg})
                print(f"Operator (closing): {closing_msg}\n")
            break
        elif decision is False:
            print("[✗] Resident repeatedly refused evacuation — marking as failed.")
            break


        operator_next = True
        time.sleep(0.8)

    # Persist conversation to JSONL
    out_file = RUN_DIR / f"dialogue_{resident_name}_{RUN_ID}.jsonl"
    with out_file.open("w", encoding="utf-8") as f:
        for t in history:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print(f"[OK] Saved to {out_file}")

    # Build rich return for A08
    decision_final, closing_final = is_successful_session(history)
    success = bool(decision_final)
    status = "SUCCESS" if success else "FAILURE"
    print(f"[FINAL STATUS] {status}")

    if closing_final and success:
        history.append({"role": "operator", "text": closing_final})

    return {
        "status": status,
        "path": str(out_file),
        "success": int(success),
        "turns": len(history),
        "history": history,
    }

# --------------------------------------------------------------------
if __name__ == "__main__":
    # Run a quick local test with a seed operator line
    simulate_conversation(resident_name="ross",
                          seed_text="Hello, this is the fire department. We need you to evacuate immediately.")




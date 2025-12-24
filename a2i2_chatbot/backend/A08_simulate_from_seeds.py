#!/usr/bin/env python3
"""
A08_simulate_from_seeds.py

Batch driver for A-pipeline:
  • Starts each conversation from hard-coded operator seed utterances.
  • Runs across one or more resident personas (ross, michelle, bob, lindsay, niki, …).
  • Uses the IQL + ICL conversation loop from A07_simulate_with_iql_and_mavis.py.
  • Saves:
      – One JSON file per conversation (with turn-wise operator policy + success flag)
      – A master summary JSON for the batch
"""

import argparse
import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from importlib.machinery import SourceFileLoader

from personas import PERSONA

# --------------------------------------------------------------------
# Import simulator from A07
# --------------------------------------------------------------------
SIM_FILE = Path("/Users/mousumi/A2I2_RAG/cross_policy/A07_simulate_with_iql_and_mavis.py")
sim = SourceFileLoader("sim_module", str(SIM_FILE)).load_module()
simulate_conversation = sim.simulate_conversation

# --------------------------------------------------------------------
# Seed operator openers
# --------------------------------------------------------------------
SEEDS = [
    "Hello, this is the fire department. We need you to evacuate immediately.",
    "Ma'am, there's a wildfire nearby. Please leave your home now.",
    "Sir, for your safety, we urge you to exit the house and move to the designated safe zone.",
    "This is an emergency alert, you must leave the area right away.",
    "The fire is moving quickly, please evacuate immediately.",
    "It's not safe to remain here, please head to the safe shelter now.",
    "For your safety, gather essentials and evacuate right away.",
    "Authorities have issued an evacuation order, you must leave now.",
    "The situation is critical, please prioritize safety over property.",
    "Emergency services require you to leave the area for your own safety."
]

# --------------------------------------------------------------------
# Main batch driver
# --------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--residents", type=str, required=True,
                    help="Comma-separated resident names (e.g. ross,michelle,bob)")
    ap.add_argument("--num_conversations", type=int, default=2,
                    help="How many seed utterances to use (first N from SEEDS)")
    ap.add_argument("--num_reps", type=int, default=1,
                    help="How many times to repeat each (seed,resident)")
    ap.add_argument("--run_id", type=str, required=True,
                    help="Run ID (creates folder under dataA/runs/seed_runs/)")
    args = ap.parse_args()

    # Parse arguments
    residents = [r.strip().lower() for r in args.residents.split(",") if r.strip()]
    seeds_to_use = SEEDS[:args.num_conversations]

    # Create directories
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base_dir = Path("/Users/mousumi/A2I2_RAG/cross_policy/dataA/runs/seed_runs") / f"{timestamp}_{args.run_id}"
    conversations_dir = base_dir / "conversations"
    conversations_dir.mkdir(parents=True, exist_ok=True)

    master = {"run_id": args.run_id, "timestamp": timestamp, "results": []}

    print("=" * 70)
    print(f"[A08] Starting batch run {args.run_id} for residents: {residents}")
    print("=" * 70)

    run_idx = 0
    for sid, seed_text in enumerate(seeds_to_use):
        for resident in residents:
            for rep in range(1, args.num_reps + 1):
                run_idx += 1
                print(f"\n[RUN {run_idx}] Seed={sid}  Resident={resident}  Rep={rep}")
                print(f"[SEED] {seed_text}")

                # --- Run one conversation ---
                result = simulate_conversation(resident_name=resident)

                # --- Fallback safety ---
                if result is None:
                    result = {"status": "unknown", "path": "", "history": []}

                # Extract turn-wise operator policies
                operator_turns = [
                    {"turn": i, "policy": t.get("selected_policy", None), "text": t.get("text", "")}
                    for i, t in enumerate(result.get("history", []), start=1)
                    if t.get("role", "").lower() == "operator"
                ]

                # Determine if resident agreed to evacuate
                success_flag = 0
                if "success" in result:
                    success_flag = result["success"]
                elif any("leave" in (t.get("text", "").lower()) for t in result.get("history", [])):
                    success_flag = 1

                # --- Construct conversation metadata ---
                conv_meta = {
                    "seed_id": sid,
                    "seed_text": seed_text,
                    "resident": resident,
                    "rep": rep,
                    "status": result.get("status", "unknown"),
                    "stop_reason": result.get("stop_reason", ""),
                    "num_turns": result.get("turns", len(result.get("history", []))),
                    "success": success_flag,
                    "operator_policies": operator_turns,
                    "history": result.get("history", []),
                    "file": result.get("path", "")
                }

                # --- Save per-conversation JSON ---
                outfile = conversations_dir / f"seed{sid}__{resident}__rep{rep}.json"
                outfile.write_text(json.dumps(conv_meta, indent=2, ensure_ascii=False), encoding="utf-8")

                # --- Append to master index ---
                master["results"].append({
                    "seed_id": sid,
                    "seed_text": seed_text,
                    "resident": resident,
                    "rep": rep,
                    "success": success_flag,
                    "stop_reason": conv_meta["stop_reason"],
                    "num_turns": conv_meta["num_turns"],
                    "file": str(outfile)
                })

    # --- Save master summary JSON ---
    index_file = base_dir / "master_index.json"
    index_file.write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[OK] Master index written → {index_file}")
    print("\nBatch completed successfully ✅")


    import csv

    # Save master summary JSON
    index_file = base_dir / "master_index.json"
    index_file.write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- New: Build CSV summary ---
    csv_file = base_dir / "master_index.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "seed_id", "seed_text", "resident", "rep",
            "success", "stop_reason", "num_turns",
            "policies_used", "file"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in master["results"]:
            # Try to read the per-conversation JSON to extract policy list
            conv_file = Path(entry["file"])
            policies_used = []
            if conv_file.exists():
                try:
                    conv_data = json.loads(conv_file.read_text())
                    if "history" in conv_data:
                        for turn in conv_data["history"]:
                            if turn.get("role") == "operator":
                                policy = turn.get("selected_policy", "")
                                if policy:
                                    policies_used.append(policy)
                except Exception:
                    pass
            entry["policies_used"] = policies_used
            writer.writerow(entry)

    print(f"\n[OK] Master index written → {index_file}")
    print(f"[OK] CSV summary written  → {csv_file}")
    print("\nBatch completed successfully ✅")


    # --------------------------------------------------------------------
if __name__ == "__main__":
    main()





# #!/usr/bin/env python3
# """
# A08_simulate_from_seeds.py

# Batch driver for A-pipeline:
#   • Starts each conversation from hard-coded operator seed utterances.
#   • Runs across one or more resident personas (ross, michelle, bob, lindsay, niki, …).
#   • Uses the IQL + ICL conversation loop from A07_simulate_with_iql_and_mavis.py.
#   • Saves:
#       – One JSON file per conversation
#       – A master summary JSON for the batch
#       – (optional CSV summary for easy analysis)

# Run example:
#   python3 A08_simulate_from_seeds.py --residents ross,michelle,bob,lindsay,niki --num_conversations 2 --run_id test1
# """

# import argparse
# import json
# import csv
# from datetime import datetime, timezone
# from pathlib import Path
# from importlib.machinery import SourceFileLoader

# # --------------------------------------------------------------------
# # Import simulator from A07
# # --------------------------------------------------------------------
# SIM_FILE = Path("/Users/mousumi/A2I2_RAG/cross_policy/A07_simulate_with_iql_and_mavis.py")
# sim = SourceFileLoader("sim_module", str(SIM_FILE)).load_module()
# simulate_conversation = sim.simulate_conversation

# # --------------------------------------------------------------------
# # Seed operator openers
# # --------------------------------------------------------------------
# SEEDS = [
    
#     "Hello, this is the fire department. We need you to evacuate immediately.",
#     "Ma'am, there's a wildfire nearby. Please leave your home now.",
#     "Sir, for your safety, we urge you to exit the house and move to the designated safe zone.",
#     "This is an emergency alert, you must leave the area right away.",
#     "The fire is moving quickly, please evacuate immediately.",
#     "It's not safe to remain here, please head to the safe shelter now.",
#     "For your safety, gather essentials and evacuate right away.",
#     "Authorities have issued an evacuation order, you must leave now.",
#     "The situation is critical, please prioritize safety over property.",
#     "Emergency services require you to leave the area for your own safety."
# ]

# # --------------------------------------------------------------------
# # Main batch driver
# # --------------------------------------------------------------------
# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--residents", type=str, required=True,
#                     help="Comma-separated resident names (e.g. ross,michelle,bob)")
#     ap.add_argument("--num_conversations", type=int, default=2,
#                     help="How many seed utterances to use (first N from SEEDS)")
#     ap.add_argument("--num_reps", type=int, default=1,
#                     help="How many times to repeat each (seed,resident)")
#     ap.add_argument("--run_id", type=str, required=True,
#                     help="Run ID (creates folder under dataA/runs/seed_runs/)")
#     args = ap.parse_args()

#     # Parse arguments
#     residents = [r.strip().lower() for r in args.residents.split(",") if r.strip()]
#     seeds_to_use = SEEDS[:args.num_conversations]

#     # Create directories
#     timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
#     base_dir = Path("/Users/mousumi/A2I2_RAG/cross_policy/dataA/runs/seed_runs") / f"{timestamp}_{args.run_id}"
#     conversations_dir = base_dir / "conversations"
#     conversations_dir.mkdir(parents=True, exist_ok=True)

#     master = {"run_id": args.run_id, "timestamp": timestamp, "results": []}

#     print("=" * 70)
#     print(f"[A08] Starting batch run {args.run_id} for residents: {residents}")
#     print("=" * 70)

#     run_idx = 0
#     for sid, seed_text in enumerate(seeds_to_use):
#         for resident in residents:
#             for rep in range(1, args.num_reps + 1):
#                 run_idx += 1
#                 print(f"\n[RUN {run_idx}] Seed={sid}  Resident={resident}  Rep={rep}")
#                 print(f"[SEED] {seed_text}")

#                 # Run one conversation
#                 result = simulate_conversation(resident_name=resident)

#                 # Fallback safety
#                 if result is None:
#                     result = {"status": "unknown", "path": ""}

#                 conv_meta = {
#                     "seed_id": sid,
#                     "seed_text": seed_text,
#                     "resident": resident,
#                     "rep": rep,
#                     "status": result.get("status", "unknown"),
#                     "file_path": result.get("path", "")
#                 }

#                 # Save conversation metadata JSON
#                 outfile = conversations_dir / f"seed{sid}__{resident}__rep{rep}.json"
#                 outfile.write_text(json.dumps(conv_meta, indent=2, ensure_ascii=False), encoding="utf-8")

#                 master["results"].append(conv_meta)

#     # Save master summary JSON
#     index_file = base_dir / "master_index.json"
#     index_file.write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")

#     # Optional: save a quick CSV summary too
#     # csv_file = base_dir / "summary.csv"
#     # with open(csv_file, "w", newline="", encoding="utf-8") as cf:
#     #     writer = csv.DictWriter(cf, fieldnames=["seed_id", "resident", "rep", "status", "file_path"])
#     #     writer.writeheader()
#     #     writer.writerows(master["results"])

#     print(f"\n[OK] Master index written → {index_file}")
#     # print(f"[OK] CSV summary written  → {csv_file}")
#     print("\nBatch completed successfully ✅")

# # --------------------------------------------------------------------
# if __name__ == "__main__":
#     main()

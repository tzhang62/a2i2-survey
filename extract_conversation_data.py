#!/usr/bin/env python3
"""
Extract conversation data from Terminal 7 logs and save to structured JSON
"""

import re
import json
from datetime import datetime
from pathlib import Path

TERMINAL_FILE = Path("/Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt")
OUTPUT_DIR = Path("conversation_data_exports")

def parse_terminal_logs():
    """Parse Terminal 7 logs and extract structured conversation data"""
    
    if not TERMINAL_FILE.exists():
        print(f"❌ Terminal file not found: {TERMINAL_FILE}")
        return None
    
    content = TERMINAL_FILE.read_text()
    lines = content.split('\n')
    
    conversations = []
    current_session = None
    
    for line in lines:
        # New session started
        if "[CHAT] Started role-play session:" in line:
            match = re.search(r"session: ([^\s]+) for character: (\w+)", line)
            if match:
                if current_session:
                    conversations.append(current_session)
                current_session = {
                    "session_id": match.group(1),
                    "character": match.group(2),
                    "turns": [],
                    "created_at": None
                }
        
        # Turn with resident message
        elif "[CHAT] Session:" in line and "Resident:" in line:
            match = re.search(r"Turn: (\d+), Resident: (.+)", line)
            if match and current_session:
                turn_data = {
                    "turn": int(match.group(1)),
                    "resident_message": match.group(2).strip(),
                    "policy": None,
                    "q_values": None,
                    "operator_response": None
                }
                current_session["turns"].append(turn_data)
        
        # Policy selected
        elif "[IQL-HF] Selected policy:" in line:
            match = re.search(r"Selected policy: (\w+)", line)
            if match and current_session and current_session["turns"]:
                current_session["turns"][-1]["policy"] = match.group(1)
        
        # Q-values
        elif "[IQL-HF] Q-values:" in line:
            match = re.search(r"Q-values: ({.+})", line)
            if match and current_session and current_session["turns"]:
                try:
                    q_vals = eval(match.group(1))  # Safe here since it's from our own logs
                    current_session["turns"][-1]["q_values"] = q_vals
                except:
                    pass
        
        # Operator response
        elif "[CHAT] Operator:" in line:
            match = re.search(r"Operator: (.+)", line)
            if match and current_session and current_session["turns"]:
                current_session["turns"][-1]["operator_response"] = match.group(1).strip()
    
    # Add last session
    if current_session:
        conversations.append(current_session)
    
    return conversations


def save_conversation_data():
    """Save extracted conversation data to JSON file"""
    
    print("=" * 80)
    print("CONVERSATION DATA EXTRACTOR")
    print("=" * 80)
    print()
    
    conversations = parse_terminal_logs()
    
    if not conversations:
        print("❌ No conversation data found in Terminal 7 logs")
        print()
        print("Make sure:")
        print("  1. Backend server is running")
        print("  2. You've had at least one conversation")
        print("  3. Terminal 7 contains the backend logs")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Prepare export data
    export_data = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "total_conversations": len(conversations),
        "conversations": conversations
    }
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"conversations_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Extracted {len(conversations)} conversation(s)")
    print(f"📁 Saved to: {output_file}")
    print()
    
    # Print summary
    print("📊 Summary:")
    print("-" * 80)
    for i, conv in enumerate(conversations, 1):
        char = conv.get('character', 'unknown')
        turns = len(conv.get('turns', []))
        print(f"  {i}. Character: {char:10} | Turns: {turns}")
        
        # Show policy selections
        policies = [t.get('policy') for t in conv.get('turns', []) if t.get('policy')]
        if policies:
            policy_str = ', '.join(policies)
            print(f"     Policies: {policy_str}")
    
    print()
    print("=" * 80)
    print("✅ Export complete!")
    print("=" * 80)
    print()
    
    return output_file


if __name__ == "__main__":
    save_conversation_data()


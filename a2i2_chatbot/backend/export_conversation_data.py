"""
Export conversation data from the running backend server
This script saves all active conversations including IQL policy selections and Q-values
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
OUTPUT_DIR = "exported_data"

def export_conversations():
    """Export all active conversation sessions"""
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Call the export endpoint (requires admin key)
    admin_key = os.getenv("ADMIN_KEY", "your-secret-admin-key-here")
    
    try:
        print("Exporting active conversation sessions...")
        response = requests.get(
            f"{BACKEND_URL}/api/admin/export-sessions",
            params={"admin_key": admin_key},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/conversations_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Success! Exported {data.get('sessions_exported', 0)} sessions")
            print(f"📁 Saved to: {filename}")
            
            # Print summary
            print("\n📊 Summary:")
            for session in data.get('data', {}).get('sessions', []):
                char = session.get('character', 'unknown')
                turns = session.get('turn_count', 0)
                iql_count = len(session.get('iql_data', []))
                print(f"  - Character: {char:10} | Turns: {turns} | IQL decisions: {iql_count}")
            
            return filename
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend at", BACKEND_URL)
        print("   Make sure the backend server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("=" * 80)
    print("CONVERSATION DATA EXPORTER")
    print("=" * 80)
    print()
    
    result = export_conversations()
    
    if result:
        print()
        print("=" * 80)
        print("✅ Export complete!")
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print("❌ Export failed - check errors above")
        print("=" * 80)


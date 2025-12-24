"""
Hugging Face API wrapper for IQL Model

This replaces the local IQL inference with API calls to Hugging Face,
making the backend much lighter and faster.
"""

import os
import requests
import json
from typing import Dict, List, Tuple
import time

# Hugging Face configuration
HF_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID", "tzhang62/iql-fire-rescue")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Check if it's a Space URL or model ID
if HF_MODEL_ID.endswith(".hf.space"):
    # It's a Space URL - use directly
    HF_API_URL = f"https://{HF_MODEL_ID}" if not HF_MODEL_ID.startswith("http") else HF_MODEL_ID
    IS_SPACE = True
else:
    # It's a model ID - use Inference API
    HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
    IS_SPACE = False

# Policy names (must match training)
POLICY_NAMES = [
    "bob",
    "lindsay",
    "michelle",
    "niki",
    "ross"
]

class IQLHuggingFace:
    """
    Lightweight IQL wrapper that uses Hugging Face Inference API
    """
    
    def __init__(self):
        self.policy_names = POLICY_NAMES
        self.api_url = HF_API_URL
        self.is_space = IS_SPACE
        self.headers = {"Content-Type": "application/json"}
        
        if HF_TOKEN and not IS_SPACE:
            # Token only needed for Inference API, not public Spaces
            self.headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        api_type = "Space" if IS_SPACE else "Inference API"
        print(f"[IQL-HF] Initialized with {api_type}: {self.api_url}")
        print(f"[IQL-HF] {len(self.policy_names)} policies available")
    
    def _prepare_state(self, history: List[Dict[str, str]], n_last: int = 3) -> str:
        """
        Convert conversation history to text state for API
        """
        # Take last N resident messages for context
        resident_messages = [
            msg["text"] for msg in history[-n_last*2:] 
            if msg["role"] == "resident"
        ]
        
        if not resident_messages:
            return "START"
        
        # Join messages into single state representation
        state_text = " | ".join(resident_messages[-n_last:])
        return state_text
    
    def _call_hf_api(self, inputs: dict, max_retries: int = 3) -> dict:
        """
        Call Hugging Face API (Space or Inference API) with retries
        """
        # Determine endpoint URL
        if self.is_space:
            # Space API uses root endpoint
            endpoint = f"{self.api_url.rstrip('/')}/"
        else:
            # Inference API uses model URL directly
            endpoint = self.api_url
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    json=inputs,
                    timeout=30  # 30 second timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    wait_time = 10 * (attempt + 1)
                    print(f"[IQL-HF] Model loading, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[IQL-HF] API error {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"[IQL-HF] Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None
                
            except Exception as e:
                print(f"[IQL-HF] API call failed: {e}")
                return None
        
        return None
    
    def select_policy(self, history: List[Dict[str, str]], 
                     character: str = None, 
                     n_last: int = 3) -> Tuple[str, Dict[str, float]]:
        """
        Select best policy using Hugging Face API
        
        Returns:
            (policy_name, q_values_dict)
        """
        # Prepare state from conversation history
        state_text = self._prepare_state(history, n_last)
        
        # Prepare API payload
        payload = {
            "inputs": state_text,
            "parameters": {
                "character": character or "unknown"
            }
        }
        
        print(f"[IQL-HF] Querying API for policy (character={character})...")
        
        # Call Hugging Face API
        result = self._call_hf_api(payload)
        
        if result is None:
            # Fallback to default policy if API fails
            print("[IQL-HF] API failed, using fallback policy")
            return self._fallback_policy(history)
        
        # Parse API response
        try:
            if isinstance(result, dict):
                policy = result.get("policy", self.policy_names[0])
                q_values = result.get("q_values", {})
            elif isinstance(result, list) and len(result) > 0:
                policy = result[0].get("label", self.policy_names[0])
                q_values = {p: 0.5 for p in self.policy_names}
            else:
                return self._fallback_policy(history)
            
            # Ensure all policies have Q-values
            q_values_dict = {p: q_values.get(p, 0.0) for p in self.policy_names}
            
            print(f"[IQL-HF] Selected policy: {policy}")
            print(f"[IQL-HF] Q-values: {q_values_dict}")
            
            return policy, q_values_dict
            
        except Exception as e:
            print(f"[IQL-HF] Error parsing API response: {e}")
            return self._fallback_policy(history)
    
    def _fallback_policy(self, history: List[Dict[str, str]]) -> Tuple[str, Dict[str, float]]:
        """
        Fallback policy selection when API is unavailable
        Uses simple heuristics based on conversation length
        """
        turn_count = len([m for m in history if m["role"] == "resident"])
        
        # Simple rule-based fallback
        if turn_count == 0:
            policy = "provide_information"
        elif turn_count == 1:
            policy = "express_urgency"
        elif turn_count < 4:
            policy = "give_direction"
        else:
            policy = "offer_assistance"
        
        # Create dummy Q-values
        q_values = {p: 0.5 for p in self.policy_names}
        q_values[policy] = 0.8  # Selected policy gets higher value
        
        print(f"[IQL-HF] Fallback policy: {policy}")
        return policy, q_values

# Global instance
_iql_hf_instance = None

def get_iql_hf():
    """Get or create the global IQL HF instance"""
    global _iql_hf_instance
    if _iql_hf_instance is None:
        _iql_hf_instance = IQLHuggingFace()
    return _iql_hf_instance


"""
Test script for character matching system
Run this to verify the similarity scoring works correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'a2i2_chatbot', 'backend'))

from server import calculate_character_similarity, select_character_pair, CHARACTER_PROFILES

# Test cases with different survey profiles
test_cases = [
    {
        "name": "Young Computer Professional",
        "survey": {
            "background": {"age": "28", "occupation": "software engineer"},
            "specialNeeds": {"condition": "no", "responsible": "no", "vehicle": "no"}
        },
        "expected_high_match": ["ben", "bob", "tom"]
    },
    {
        "name": "Elderly Person Living Alone",
        "survey": {
            "background": {"age": "72", "occupation": "retired"},
            "specialNeeds": {"condition": "yes", "responsible": "no", "vehicle": "yes"}
        },
        "expected_high_match": ["mary"]
    },
    {
        "name": "Young Parent/Caregiver",
        "survey": {
            "background": {"age": "26", "occupation": "teacher"},
            "specialNeeds": {"condition": "no", "responsible": "yes", "vehicle": "no"}
        },
        "expected_high_match": ["lindsay", "ana"]
    },
    {
        "name": "High School Student",
        "survey": {
            "background": {"age": "16", "occupation": "student"},
            "specialNeeds": {"condition": "no", "responsible": "no", "vehicle": "no"}
        },
        "expected_high_match": ["mia"]
    },
    {
        "name": "Middle-aged Professional",
        "survey": {
            "background": {"age": "42", "occupation": "manager"},
            "specialNeeds": {"condition": "no", "responsible": "no", "vehicle": "no"}
        },
        "expected_high_match": ["michelle", "tom", "ross"]
    }
]

def test_character_matching():
    """Test character matching for different profiles"""
    
    print("=" * 80)
    print("CHARACTER MATCHING SYSTEM TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test['name']}")
        print(f"{'='*80}")
        
        survey_data = test["survey"]
        print(f"Profile: Age {survey_data['background']['age']}, {survey_data['background']['occupation']}")
        print(f"Special Needs: {survey_data['specialNeeds']}")
        print()
        
        # Calculate scores for all characters
        print("SIMILARITY SCORES:")
        print("-" * 80)
        scores = {}
        for char_key in CHARACTER_PROFILES.keys():
            score = calculate_character_similarity(survey_data, char_key)
            scores[char_key] = score
            char = CHARACTER_PROFILES[char_key]
            print(f"  {char['name']:12} (age {char['age']:2}, {char['occupation']:20}): {score:.3f}")
        
        # Sort by score
        sorted_chars = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        print()
        print("RANKING:")
        print("-" * 80)
        for rank, (char_key, score) in enumerate(sorted_chars, 1):
            char = CHARACTER_PROFILES[char_key]
            marker = "✓" if char_key in test.get("expected_high_match", []) else " "
            print(f"  {rank:2}. [{marker}] {char['name']:12} - {score:.3f}")
        
        # Test character pair selection
        print()
        print("CHARACTER PAIR SELECTION:")
        print("-" * 80)
        highest_char, lowest_char, all_scores = select_character_pair(survey_data, [])
        highest_profile = CHARACTER_PROFILES[highest_char]
        lowest_profile = CHARACTER_PROFILES[lowest_char]
        
        print(f"  HIGH MATCH:  {highest_profile['name']:12} (score: {all_scores[highest_char]:.3f})")
        print(f"  LOW MATCH:   {lowest_profile['name']:12} (score: {all_scores[lowest_char]:.3f})")
        
        # Test with exclusions
        print()
        print("TESTING CHARACTER EXCLUSION:")
        print("-" * 80)
        excluded = [highest_char]
        print(f"  Excluding: {highest_char}")
        
        try:
            new_high, new_low, new_scores = select_character_pair(survey_data, excluded)
            new_high_profile = CHARACTER_PROFILES[new_high]
            new_low_profile = CHARACTER_PROFILES[new_low]
            print(f"  NEW HIGH MATCH: {new_high_profile['name']:12} (score: {new_scores[new_high]:.3f})")
            print(f"  NEW LOW MATCH:  {new_low_profile['name']:12} (score: {new_scores[new_low]:.3f})")
        except ValueError as e:
            print(f"  Error: {e}")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("NOTES:")
    print("  - ✓ indicates expected high matches for this profile")
    print("  - Scores range from 0.0 (no match) to 1.0 (perfect match)")
    print("  - The system selects highest and lowest scoring characters")
    print("  - Excluded characters are removed from future selections")
    print()

if __name__ == "__main__":
    test_character_matching()


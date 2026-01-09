"""
Standalone test script for character matching system
This version doesn't require server dependencies
"""

# Character profiles (copied from server.py for standalone testing)
CHARACTER_PROFILES = {
    "bob": {
        "name": "Bob",
        "age": 30,
        "occupation": "office worker",
        "traits": ["work-focused", "career-oriented", "busy", "independent"],
        "concerns": ["work deadlines", "career advancement"],
        "description": "Bob is around 30 years old. He prioritizes his work over safety."
    },
    "ben": {
        "name": "Ben",
        "age": 29,
        "occupation": "computer technician",
        "traits": ["tech-savvy", "home-based", "independent", "analytical"],
        "concerns": ["work projects", "technology"],
        "description": "Ben is a 29-year-old computer technician who works from home."
    },
    "mary": {
        "name": "Mary",
        "age": 75,
        "occupation": "retired",
        "traits": ["elderly", "lives alone", "has pet", "cautious"],
        "concerns": ["pet safety", "mobility", "independence"],
        "description": "Mary is an elderly person living alone with a small dog."
    },
    "lindsay": {
        "name": "Lindsay",
        "age": 25,
        "occupation": "babysitter",
        "traits": ["responsible for others", "caring", "young adult", "protective"],
        "concerns": ["children's safety", "responsibility"],
        "description": "Lindsay is a babysitter caring for two children."
    },
    "ana": {
        "name": "Ana",
        "age": 35,
        "occupation": "caregiver",
        "traits": ["caring", "responsible for others", "professional", "compassionate"],
        "concerns": ["elderly residents", "duty", "safety of others"],
        "description": "Ana is a caregiver working at a senior center."
    },
    "ross": {
        "name": "Ross",
        "age": 45,
        "occupation": "van driver",
        "traits": ["helpful", "service-oriented", "responsible", "community-focused"],
        "concerns": ["helping others evacuate", "elderly residents", "community"],
        "description": "Ross is a van driver helping evacuate elderly residents."
    },
    "niki": {
        "name": "Niki",
        "age": 32,
        "occupation": "homemaker",
        "traits": ["cooperative", "family-oriented", "partnered", "practical"],
        "concerns": ["family safety", "home", "partnership"],
        "description": "Niki is at home with a partner, ready to cooperate."
    },
    "michelle": {
        "name": "Michelle",
        "age": 40,
        "occupation": "homeowner",
        "traits": ["skeptical", "independent", "cautious", "self-reliant"],
        "concerns": ["false alarms", "property", "independence"],
        "description": "Michelle is at home, skeptical of evacuation warnings."
    },
    "tom": {
        "name": "Tom",
        "age": 38,
        "occupation": "high school teacher",
        "traits": ["dedicated", "project-focused", "educator", "practical"],
        "concerns": ["home projects", "work preparation", "time"],
        "description": "Tom is a high school teacher working on a home project."
    },
    "mia": {
        "name": "Mia",
        "age": 17,
        "occupation": "high school student",
        "traits": ["young", "student", "tech-focused", "ambitious"],
        "concerns": ["school projects", "robotics", "achievement"],
        "description": "Mia is a high school student working on a robotics project."
    }
}


def calculate_character_similarity(survey_data: dict, character_key: str) -> float:
    """
    Calculate similarity score between participant survey data and character profile.
    Returns a score between 0 and 1 (higher = more similar).
    """
    if character_key not in CHARACTER_PROFILES:
        return 0.0
    
    character = CHARACTER_PROFILES[character_key]
    score = 0.0
    max_score = 0.0
    
    # Extract survey data
    background = survey_data.get('background', {})
    participant_age = background.get('age', '')
    participant_occupation = background.get('occupation', '').lower()
    special_needs = survey_data.get('specialNeeds', {})
    
    # Age similarity (weight: 2.0)
    max_score += 2.0
    try:
        p_age = int(participant_age) if participant_age else 30
        c_age = character.get('age', 30)
        age_diff = abs(p_age - c_age)
        # Normalize age difference (0-50 years -> 0-1 score)
        age_score = max(0, 1 - (age_diff / 50.0))
        score += age_score * 2.0
    except (ValueError, TypeError):
        # If age is invalid, give neutral score
        score += 1.0
    
    # Occupation similarity (weight: 1.5)
    max_score += 1.5
    char_occupation = character.get('occupation', '').lower()
    if participant_occupation and char_occupation:
        # Direct match
        if participant_occupation == char_occupation:
            score += 1.5
        # Partial match (e.g., "teacher" in "high school teacher")
        elif participant_occupation in char_occupation or char_occupation in participant_occupation:
            score += 1.0
        # Similar occupations
        elif any(keyword in participant_occupation and keyword in char_occupation 
                for keyword in ['student', 'teacher', 'tech', 'care', 'driver', 'work']):
            score += 0.5
    
    # Responsibility for others (weight: 1.5)
    max_score += 1.5
    has_responsibility = special_needs.get('responsible') == 'yes'
    char_has_responsibility = any(trait in character.get('traits', []) 
                                 for trait in ['responsible for others', 'caring', 'protective'])
    if has_responsibility and char_has_responsibility:
        score += 1.5
    elif not has_responsibility and not char_has_responsibility:
        score += 0.5
    
    # Mobility/communication challenges (weight: 1.0)
    max_score += 1.0
    has_condition = special_needs.get('condition') == 'yes'
    char_elderly = 'elderly' in character.get('traits', [])
    if has_condition and char_elderly:
        score += 1.0
    elif not has_condition and not char_elderly:
        score += 0.5
    
    # Vehicle needs (weight: 1.0)
    max_score += 1.0
    needs_vehicle = special_needs.get('vehicle') == 'yes'
    char_has_vehicle = 'driver' in character.get('occupation', '').lower()
    if needs_vehicle and char_has_vehicle:
        score += 1.0
    elif not needs_vehicle:
        score += 0.3
    
    # Normalize to 0-1 range
    if max_score > 0:
        normalized_score = score / max_score
    else:
        normalized_score = 0.5
    
    return normalized_score


def select_character_pair(survey_data: dict, excluded_characters: list) -> tuple:
    """
    Select two characters for profile matching:
    - First: highest similarity score (not in excluded list)
    - Second: lowest similarity score (not in excluded list)
    
    Returns: (highest_char, lowest_char, scores_dict)
    """
    available_characters = [char for char in CHARACTER_PROFILES.keys() 
                          if char not in excluded_characters]
    
    if len(available_characters) < 2:
        raise ValueError("Not enough characters available for selection")
    
    # Calculate similarity scores for all available characters
    scores = {}
    for char_key in available_characters:
        scores[char_key] = calculate_character_similarity(survey_data, char_key)
    
    # Sort by score
    sorted_chars = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Select highest and lowest
    highest_char = sorted_chars[0][0]
    lowest_char = sorted_chars[-1][0]
    
    return highest_char, lowest_char, scores


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


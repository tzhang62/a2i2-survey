# Personalized Scenario Matching System

## Overview

The survey system now automatically recommends the most appropriate emergency scenario character based on each participant's survey responses. This creates a more immersive and relatable experience while maintaining research validity.

## How It Works

### 1. Data Collection (Survey)
Participants provide:
- Age
- Gender
- Occupation
- Special needs (physical conditions, responsibility for others, need for vehicle/assistance)

### 2. Character Matching (Scenario Page)
System analyzes survey responses and calculates match scores for all 10 characters.

### 3. Recommendation Display
- Scenario text updates to match recommended character
- Recommended character card highlighted with green border
- "✓ Recommended" badge shown on card
- Character is pre-selected

### 4. User Choice
Participants can still choose any character they prefer.

## The 10 Character Scenarios

### 1. **Bob** - Stubborn Worker
**Profile Match:**
- Age: 25-45
- Occupation: Tech, computer, software, engineering
- Gender: Any (slight preference for male)
- Special Needs: None

**Scenario:**
> You are working on an important computer project at home when your phone suddenly rings. You've been deeply focused on your work for hours, and you're at a critical point where stopping could mean losing progress. The caller ID shows the local fire department. You feel irritated by the interruption—your work is too important to stop right now, and you're skeptical about whether this is really an emergency.

---

### 2. **Niki** - Cooperative Person
**Profile Match:**
- Age: 25-45
- Occupation: Any
- Gender: Slight preference for female
- Special Needs: None specific

**Scenario:**
> You are at home with your partner on a regular day when your phone suddenly rings. The caller ID shows the local fire department. You can see some smoke in the distance through your window, but you're not sure how serious it is. You're ready to cooperate and follow instructions, but you need someone to explain what's happening and what you should do.

---

### 3. **Lindsay** - Babysitter/Caregiver
**Profile Match:**
- Age: 18-35
- Occupation: Babysitter, nanny, childcare
- Gender: Slight preference for female
- Special Needs: **Responsible for others (YES)**

**Scenario:**
> You are babysitting two young children at their home while their parents are out. You're keeping the kids entertained when your phone suddenly rings. The caller ID shows the local fire department. You immediately feel anxious—you're responsible for these children, and their parents trusted you to keep them safe. You're worried about making decisions without parental approval, but you want to do what's best for the kids.

---

### 4. **Michelle** - Property Protector
**Profile Match:**
- Age: 35-55
- Occupation: Any
- Gender: Slight preference for female
- Special Needs: None specific

**Scenario:**
> You are at home, and you've prepared extensively for wildfire season. You've cleared brush, installed fire-resistant materials, and stocked supplies. When your phone rings showing the local fire department, you feel defensive. You and your partner have worked hard to protect your home, and you believe your preparations will keep you safe. You're skeptical of outsiders telling you what to do with your own property.

---

### 5. **Ross** - Emergency Transport Driver
**Profile Match:**
- Age: 30-55
- Occupation: Driver, transport
- Gender: Slight preference for male
- Special Needs: **Responsible for others (YES)**, **Vehicle needed (YES)**

**Scenario:**
> You are a van driver who was helping evacuate elderly residents when your vehicle broke down on the roadside. You have several elderly passengers with mobility issues who cannot walk long distances or evacuate on their own. When your phone rings showing the local fire department, you feel stressed and responsible. You need real help—not just advice to abandon these vulnerable people you're responsible for.

---

### 6. **Mary** - Elderly Person with Pet
**Profile Match:**
- Age: 60+
- Occupation: Retired, librarian
- Gender: Slight preference for female
- Special Needs: **Physical condition (YES)**, **Vehicle needed (YES)**, Pet mentioned

**Scenario:**
> You are a 67-year-old person living alone at home with your small dog. You used to work as a librarian and now enjoy a quiet life. You have arthritis that makes you move slowly. When your phone rings showing the local fire department, you feel concerned but calm. You know you'll need time to gather your things, especially making sure your beloved dog can come with you. You cannot drive and will need help getting to safety.

---

### 7. **Ben** - Young Tech Professional
**Profile Match:**
- Age: 25-35
- Occupation: Tech, computer, software
- Gender: Slight preference for male
- Special Needs: Pet mentioned (optional)

**Scenario:**
> You are a 29-year-old computer technician working from home. You're currently deep into troubleshooting a client's urgent problem while streaming a sports event in the background. When your phone rings showing the local fire department, you feel torn. You can evacuate on your own, but you need to save your work first, and you're worried about your pet gecko. You're confident you can handle this quickly and efficiently.

---

### 8. **Ana** - Professional Caregiver
**Profile Match:**
- Age: 35-55
- Occupation: Caregiver, nurse, medical, social work
- Gender: Slight preference for female
- Special Needs: **Responsible for others (YES)**, **Vehicle needed (YES)**

**Scenario:**
> You are a 42-year-old caregiver working at a senior center. You're currently helping several elderly residents with their daily activities. When your phone rings showing the local fire department, you feel the weight of responsibility. You're responsible for multiple seniors, some with mobility issues. You need to evacuate them all safely, which will require coordination and transportation. You'll do whatever it takes to protect those in your care.

---

### 9. **Tom** - Community Helper/Teacher
**Profile Match:**
- Age: 45-60
- Occupation: Teacher, education
- Gender: Slight preference for male
- Special Needs: Helps others (inferred)

**Scenario:**
> You are a 54-year-old high school teacher working on a woodworking project at home. You're known in the community as someone who helps others. When your phone rings showing the local fire department, your first thought is whether your neighbors know about this. You have a pickup truck and could evacuate easily, but you're thinking about who else might need help. You're torn between leaving now and checking on others first.

---

### 10. **Mia** - Student/Young Researcher
**Profile Match:**
- Age: 17-25
- Occupation: Student
- Gender: Slight preference for female
- Special Needs: None

**Scenario:**
> You are a 17-year-old high school student working on an exciting robotics project at the school lab. You're completely absorbed in testing your robot—it's finally working! When your phone rings showing the local fire department, you're startled out of your focus. You can drive yourself home, but part of you wants to finish this test first. This moment of progress took weeks to achieve.

---

## Matching Algorithm

### Scoring System

Each character receives a score based on participant attributes:

```javascript
// Age scoring (0-3 points)
if (age >= 60) → mary +3, tom +2
if (age 40-59) → ana +3, michelle +2, tom +2
if (age 25-39) → bob +3, ben +2, niki +2
if (age 18-24) → mia +3, ben +2

// Occupation scoring (0-3 points)
'teacher' → tom +3
'student' → mia +3
'tech/computer' → bob +3, ben +3
'caregiver/nurse' → ana +3, lindsay +2
'driver/transport' → ross +3
'babysitter' → lindsay +3
'retired' → mary +2

// Special needs scoring (0-3 points)
Physical condition: YES → mary +2, ross +1
Responsible for others: YES → lindsay +3, ana +3, ross +2
Vehicle needed: YES → ross +3, mary +2, ana +2
Pet mentioned → mary +2, ben +1

// Gender scoring (0-1 points)
Slight bias based on character gender
```

### Example Matches

**Participant 1:**
- Age: 28
- Gender: Male
- Occupation: Software Engineer
- Special Needs: None
→ **Matched to: Bob** (tech + age + male)

**Participant 2:**
- Age: 67
- Gender: Female
- Occupation: Retired Librarian
- Special Needs: Arthritis, has dog
→ **Matched to: Mary** (age + retired + physical + pet)

**Participant 3:**
- Age: 23
- Gender: Female
- Occupation: Babysitter
- Special Needs: Responsible for 2 children
→ **Matched to: Lindsay** (occupation + responsible + age)

**Participant 4:**
- Age: 43
- Gender: Female
- Occupation: Nurse
- Special Needs: Responsible for 6 elderly patients
→ **Matched to: Ana** (caregiver + responsible + age)

**Participant 5:**
- Age: 19
- Gender: Female
- Occupation: Student (Robotics)
- Special Needs: None
→ **Matched to: Mia** (student + age + young)

## Visual Display

### Recommended Character Highlight
```css
- Green border (3px solid #27ae60)
- Light green background (rgba(39, 174, 96, 0.1))
- "✓ Recommended" badge in top-right corner
- Character pre-selected
```

### Scenario Text Update
The main scenario description updates automatically to show the recommended character's perspective.

### User Choice Preserved
Participants can still select any character they want—the recommendation is just a suggestion.

## Benefits

### For Research
✅ More authentic participant responses
✅ Better ecological validity
✅ Participants relate more to scenario
✅ Natural variation in engagement

### For Participants
✅ Personalized experience
✅ Relevant to their situation
✅ More immersive
✅ Still maintains choice

## Technical Implementation

### Files Modified

1. **scenario.js**
   - Added SCENARIOS object with all 10 character descriptions
   - Added `matchCharacterToProfile()` function
   - Added `loadRecommendedScenario()` function
   - Scoring algorithm implementation

2. **scenario.html**
   - Added personalization note
   - Dynamic scenario text container
   - Visual feedback for recommended character

### Data Flow

```
Survey Completion
    ↓
Store participantId in sessionStorage
    ↓
Navigate to Scenario Page
    ↓
Fetch survey data from backend
    ↓
Calculate match scores for all characters
    ↓
Select highest scoring character
    ↓
Update scenario text + highlight character
    ↓
Pre-select recommended character
    ↓
User can confirm or choose different character
    ↓
Proceed to chat with selected character
```

## Testing

### Test Case 1: Tech Worker
```javascript
Survey Data: {
  age: 29,
  gender: 'male',
  occupation: 'Software Developer',
  specialNeeds: { condition: 'no', responsible: 'no', vehicle: 'no' }
}
Expected Match: Bob or Ben
```

### Test Case 2: Caregiver
```javascript
Survey Data: {
  age: 45,
  gender: 'female',
  occupation: 'Nurse',
  specialNeeds: { condition: 'no', responsible: 'yes', vehicle: 'yes' }
}
Expected Match: Ana
```

### Test Case 3: Student
```javascript
Survey Data: {
  age: 19,
  gender: 'female',
  occupation: 'Student',
  specialNeeds: { condition: 'no', responsible: 'no', vehicle: 'no' }
}
Expected Match: Mia
```

## Configuration

To adjust matching weights, modify the scoring values in `scenario.js`:

```javascript
// Increase age importance
if (age >= 60) {
  scores.mary += 5;  // was 3
}

// Adjust occupation weights
if (occupation.includes('teacher')) {
  scores.tom += 5;  // was 3
}
```

## Future Enhancements

Possible additions:
- [ ] Machine learning-based matching
- [ ] Personality trait integration
- [ ] Moral foundation alignment
- [ ] Cultural background consideration
- [ ] Language preference matching

## Privacy Note

The matching happens client-side (in browser) for privacy. Survey data is only fetched if already submitted to backend. No additional tracking or profiling occurs.

---

**Version**: 1.0  
**Created**: December 2025  
**Status**: ✅ Active


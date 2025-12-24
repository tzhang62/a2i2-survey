# Enhanced Survey Validation - Statistical Quality Control

## Overview

The survey now includes advanced statistical validation to ensure high-quality research data by detecting low-effort or rushed responses.

## Validation Rules (All Automatic - Block Submission)

### 1. ✅ All Questions Must Be Answered
- **What**: Every required field must be completed
- **Why**: Incomplete data cannot be analyzed
- **Applies to**:
  - Nickname, age, gender, education, ideology
  - All 10 personality questions
  - All 12 moral foundation questions
  - All 3 special needs questions

### 2. ✅ Standard Deviation > 0.8
- **What**: Responses must show sufficient variation
- **Why**: Prevents participants from selecting similar values across all questions
- **Formula**: 
  ```
  SD = √(Σ(x - μ)² / n)
  ```
- **Applies to**:
  - Personality section (10 questions)
  - Moral foundations section (12 questions)
- **Example violations**:
  - ❌ All responses are 3, 3, 3, 3, 4, 3, 3, 3, 3, 3 (SD = 0.30)
  - ❌ All responses are 2, 3, 3, 2, 3, 2, 3, 3, 2, 3 (SD = 0.48)
  - ✅ Responses are 2, 4, 3, 5, 2, 4, 3, 1, 4, 3 (SD = 1.14)

### 3. ✅ No Single Value > 80% of Responses
- **What**: No one rating can dominate a section
- **Why**: Catches participants who change just 1-2 answers to bypass detection
- **Threshold**: 80% per section
- **Applies to**:
  - Personality section (≤8 of 10 questions can have same value)
  - Moral foundations section (≤9 of 12 questions can have same value)
- **Example violations**:
  - ❌ Personality: 3,3,3,3,3,3,3,3,4,3 (90% are "3")
  - ❌ Moral: 4,4,4,4,4,4,4,4,4,4,5,4 (92% are "4")
  - ✅ Personality: 3,3,4,3,4,3,4,3,2,5 (50% are "3")

### 4. ⚠️ Survey Completed in < 1 Minute
- **What**: Participants must spend at least 60 seconds on survey
- **Why**: Reading and thoughtfully responding takes time
- **Timer**: Starts when survey page loads
- **Calculation**: Automatic timestamp tracking
- **Example violations**:
  - ❌ Completed in 35 seconds
  - ❌ Completed in 48 seconds
  - ✅ Completed in 2 minutes 15 seconds

## How It Works

### Step 1: Timer Starts
```javascript
// When page loads
sessionStorage.setItem('surveyStartTime', Date.now());
```

### Step 2: User Fills Survey
- Visual feedback as they answer
- Questions turn green when completed

### Step 3: User Clicks Submit
System checks:
1. All required fields filled? ✓
2. Personality SD > 0.8? ✓
3. Personality dominant value < 80%? ✓
4. Moral SD > 0.8? ✓
5. Moral dominant value < 80%? ✓
6. Time spent ≥ 60 seconds? ✓

### Step 4: Pass or Fail
- **Pass**: Submit to backend → Proceed to scenario
- **Fail**: Show detailed error modal → User reviews/corrects

## Error Messages

### Low Variance (SD < 0.8)
```
⚠️ Your personality responses show very little variation 
(SD: 0.45). Please ensure each answer reflects your genuine 
traits. Try to use more of the rating scale.
```

### Dominant Response (>80%)
```
⚠️ You selected "3" for 90% (9/10) of personality questions. 
Please use the full scale to reflect the variety in your traits.
```

### Too Fast (<1 minute)
```
⚠️ You completed the survey in 42 seconds. Please take more 
time to read each question carefully and respond thoughtfully. 
This ensures high-quality research data.
```

### Multiple Issues
```
⚠️ Please Complete the Survey

• Your personality responses show very little variation (SD: 0.52)
• You selected "4" for 83% (10/12) of moral foundation questions
• You completed the survey in 38 seconds

[Got it, I'll review my answers]
```

## Example Scenarios

### Scenario 1: Straight-Lining
**Participant tries:**
- All personality: 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
- All moral: 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4

**Result:**
- ❌ SD = 0.00 (< 0.8)
- ❌ 100% dominant value (> 80%)
- **Blocked**

### Scenario 2: Minimal Variation
**Participant tries:**
- Personality: 3, 3, 3, 3, 4, 3, 3, 3, 3, 3
- Moral: 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 4

**Result:**
- ❌ Personality SD = 0.30 (< 0.8)
- ❌ Personality: 90% are "3" (> 80%)
- ❌ Moral SD = 0.29 (< 0.8)
- ❌ Moral: 92% are "4" (> 80%)
- **Blocked**

### Scenario 3: Rushing Through
**Participant:**
- Completes entire survey in 45 seconds
- Even with varied responses

**Result:**
- ✅ SD checks pass
- ✅ Dominance checks pass
- ❌ Time = 45 seconds (< 60)
- **Blocked**

### Scenario 4: Valid Submission
**Participant:**
- Personality: 2, 4, 3, 5, 2, 4, 3, 1, 4, 3 (SD = 1.14)
- Moral: 5, 6, 4, 5, 3, 5, 4, 6, 4, 5, 3, 4 (SD = 0.99)
- Time: 3 minutes 12 seconds

**Result:**
- ✅ SD > 0.8
- ✅ No dominant value
- ✅ Sufficient time
- **Accepted**

## Statistical Details

### Standard Deviation Calculation
```javascript
function calculateStandardDeviation(values) {
  const n = values.length;
  const mean = values.reduce((sum, val) => sum + val, 0) / n;
  const variance = values.reduce((sum, val) => 
    sum + Math.pow(val - mean, 2), 0) / n;
  return Math.sqrt(variance);
}
```

### Why SD > 0.8?
For a 5-point Likert scale:
- **SD = 0**: All same value
- **SD < 0.5**: Almost all same, 1-2 different
- **SD = 0.8**: Minimum acceptable variation
- **SD = 1.0-1.5**: Good variation
- **SD > 2**: Maximum possible variation

For 6-point scale, same threshold works well.

### Why 80% Threshold?
- **10 personality questions**: Max 8 can be same (2 must differ)
- **12 moral questions**: Max 9 can be same (3 must differ)
- Balances catching low-effort with allowing genuine patterns

## Benefits for Research

### Data Quality
- ✅ Reduces noise from inattentive participants
- ✅ Increases reliability of personality measures
- ✅ Improves validity of moral foundation scores
- ✅ Better statistical power in analyses

### Participant Behavior
- ✅ Encourages thoughtful responses
- ✅ Reduces satisficing behavior
- ✅ Clear expectations set upfront
- ✅ Educational value about survey quality

### Analysis
- ✅ Less post-hoc filtering needed
- ✅ Higher confidence in results
- ✅ Fewer outliers to handle
- ✅ Better reproducibility

## Testing the Validation

### Test 1: Try Straight-Lining
```
1. Fill background info
2. Select all "3" for personality
3. Select all "4" for moral
4. Click submit
→ Should block with SD and dominance errors
```

### Test 2: Try Minimal Change
```
1. Fill background info
2. Select: 3,3,3,3,3,3,3,3,4,3 for personality
3. Select: 4,4,4,4,4,4,4,4,4,4,5,4 for moral
4. Click submit
→ Should block (SD < 0.8, >80% dominant)
```

### Test 3: Rush Through
```
1. Fill all fields quickly (< 1 minute)
2. Use varied responses
3. Click submit within 60 seconds
→ Should block with time warning
```

### Test 4: Valid Response
```
1. Fill background info
2. Use varied responses (SD > 0.8)
3. No value appears >80%
4. Wait > 60 seconds
5. Click submit
→ Should succeed
```

## Configuration

Current thresholds (can be adjusted if needed):

```javascript
const MIN_STANDARD_DEVIATION = 0.8;
const MAX_DOMINANT_PERCENTAGE = 0.8;  // 80%
const MIN_TIME_SECONDS = 60;  // 1 minute
```

To adjust, modify these values in `survey.js`.

## Monitoring & Analytics

Consider tracking these metrics:
- % of submissions blocked by each rule
- Average SD for personality/moral sections
- Average completion time
- Most common error combinations

This helps refine thresholds over time.

## Limitations

### May Block Valid Responses If:
- Participant genuinely has consistent traits
- Participant genuinely has consistent moral values
- Participant is a very fast reader

### Mitigation:
- Thresholds are set relatively lenient (0.8, 80%, 60s)
- Clear error messages explain what's needed
- Participants can retry immediately

## References

- Satisficing in surveys: Krosnick (1991)
- Response quality indicators: Meade & Craig (2012)
- Straight-lining detection: Kim et al. (2019)

---

**Implementation Date**: December 2025  
**Version**: 2.0 (Enhanced Statistical Validation)


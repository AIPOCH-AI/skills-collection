---
name: symptom-checker-triage
description: Suggest triage levels based on red flag symptoms for emergency vs outpatient
  care
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Symptom Checker Triage (ID: 165)

Suggests triage levels (Emergency vs Outpatient) based on red flags in common symptoms.

## Features

- Analyzes symptom descriptions entered by users
- Identifies red flags (life-threatening symptoms)
- Suggests triage level: Emergency or Outpatient
- Provides triage rationale and medical advice

## Input

### Command Line Arguments

```bash
python scripts/main.py "symptom description"
```

Or interactive mode:

```bash
python scripts/main.py --interactive
```

### Input Format

Symptom description (natural language), for example:
- "Chest pain, difficulty breathing, lasting 30 minutes"
- "Headache, fever 38.5 degrees, vomiting"
- "Abdominal pain, right lower quadrant tenderness, fever"

## Output

JSON format:

```json
{
  "triage_level": "emergency|outpatient|urgent",
  "confidence": 0.85,
  "red_flags": ["Chest pain", "Difficulty breathing"],
  "reason": "Chest pain with difficulty breathing may be a sign of myocardial infarction or pulmonary embolism",
  "recommendation": "Please go to emergency department immediately",
  "department": "Emergency/Cardiology",
  "warning": "This is AI-assisted advice and cannot replace professional medical diagnosis"
}
```

## Triage Levels

| Level | Description | Recommendation |
|------|------|------|
| emergency | Life-threatening | Call 120 immediately or go to emergency |
| urgent | Urgent but not immediately fatal | Seek medical care within 2-4 hours |
| outpatient | Non-urgent | Schedule outpatient appointment |

## Red Flags List

### Cardiovascular System
- Chest pain/chest tightness (especially with difficulty breathing, sweating)
- Severe palpitations with syncope
- Extremely high blood pressure (>180/120)

### Respiratory System
- Severe difficulty breathing/sensation of suffocation
- Hemoptysis
- Blood oxygen saturation <90%

### Nervous System
- Sudden severe headache ("worst headache of my life")
- Altered consciousness/coma
- Slurred speech/hemiplegia (stroke signs)
- Status epilepticus

### Digestive System
- Hematemesis/melena
- Severe abdominal pain with abdominal rigidity
- Intestinal obstruction symptoms (abdominal distension, cessation of flatus and defecation)

### Others
- Severe trauma/bleeding
- High fever (>40°C) with altered consciousness
- Drug overdose/poisoning
- Pregnant women: vaginal bleeding, severe abdominal pain, decreased fetal movement

## Usage Examples

```bash
# Direct symptom input
python scripts/main.py "Chest pain, radiating to left arm, sweating"

# Interactive mode
python scripts/main.py --interactive

# Detailed output
python scripts/main.py "Headache, fever" --verbose
```

## Disclaimer

⚠️ **Important Notice**:
- This tool only provides AI-assisted triage advice
- **Cannot replace professional medical diagnosis**
- If in doubt, please seek medical care immediately
- Call 120 in emergency situations

## Technical Implementation

- Rule-based engine + keyword matching
- Supports symptom synonym expansion
- Configurable red flag weights
- Supports confidence calculation

## File Structure

```
skills/symptom-checker-triage/
├── SKILL.md
└── scripts/
    └── main.py
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

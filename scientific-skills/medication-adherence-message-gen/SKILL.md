---
name: medication-adherence-message-gen
description: Generate medication reminder messages using behavioral psychology principles
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Skill: Medication Adherence Message Gen

**ID:** 136  
**Name:** medication-adherence-message-gen  
**Description:** Uses behavioral psychology principles to generate SMS/push notification copy for reminding patients to take medication.  
**Version:** 1.0.0  

---

## Overview

This skill generates personalized medication reminder messages based on behavioral psychology and behavioral economics principles. By applying psychological mechanisms such as social norms, loss aversion, implementation intentions, commitment consistency, etc., it improves patient medication adherence.

## Psychological Principles Used

| Principle | English | Description |
|------|------|------|
| Social Norms | Social Norms | Emphasizes "most patients can adhere to medication" |
| Loss Aversion | Loss Aversion | Emphasizes what will be lost if medication is not taken on time |
| Implementation Intentions | Implementation Intentions | "If-then" plans |
| Immediate Rewards | Immediate Rewards | Immediate positive feedback after taking medication |
| Commitment Consistency | Commitment | Reinforces patient commitment and responsibility |
| Self-Efficacy | Self-Efficacy | Enhances patient confidence in self-management |
| Anchoring Effect | Anchoring | Provides specific quantifiable goals |
| Scarcity | Scarcity | Emphasizes timeliness of treatment |

## Usage

### Command Line

```bash
python scripts/main.py [options]
```

### Options

| Parameter | Short | Type | Required | Description |
|------|------|------|------|------|
| `--name` | `-n` | str | No | Patient name |
| `--medication` | `-m` | str | Yes | Medication name |
| `--dosage` | `-d` | str | No | Dosage information |
| `--time` | `-t` | str | No | Medication time |
| `--principle` | `-p` | str | No | Psychology principle (social_norms/loss_aversion/implementation/intent/reward/commitment/self_efficacy/anchoring/scarcity/random) |
| `--tone` |  | str | No | Tone style (gentle/firm/encouraging/urgent) |
| `--language` | `-l` | str | No | Language (zh/en) |
| `--output` | `-o` | str | No | Output format (text/json) |

### Examples

```bash
# Basic usage
python scripts/main.py -m "Atorvastatin" -n "Mr. Zhang"

# Specify psychology principle
python scripts/main.py -m "Metformin" -p "loss_aversion" -t "After breakfast"

# Generate JSON format
python scripts/main.py -m "Antihypertensive" -p "social_norms" -o json

# English output
python scripts/main.py -m "Metformin" -n "John" -l en -p "commitment"
```

### Python API

```python
from scripts.main import generate_message

message = generate_message(
    medication="Atorvastatin",
    patient_name="Mr. Zhang",
    dosage="20mg",
    time="After dinner",
    principle="social_norms",
    tone="encouraging"
)
print(message)
```

## Output Format

### Text Mode
```
【Medication Reminder】Mr. Zhang, it's time after dinner. 95% of patients taking Atorvastatin can adhere to daily medication, and you're one of them! Please take 20mg to keep your heart healthy.
```

### JSON Mode
```json
{
  "medication": "Atorvastatin",
  "patient_name": "Mr. Zhang",
  "principle": "social_norms",
  "tone": "encouraging",
  "message": "【Medication Reminder】Mr. Zhang, it's time after dinner...",
  "psychology_insight": "Uses social norms principle to enhance patient behavioral motivation by emphasizing high adherence rates"
}
```

## Message Templates

Each psychology principle has multiple copy templates, randomly selected to avoid repetition fatigue.

---

**Author:** OpenClaw  
**License:** MIT

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

---
name: drug-interaction-checker
description: Check for drug-drug interactions between multiple medications. Trigger
  when user asks about medication compatibility, "can I take X with Y", drug interactions,
  contraindications, or safety of combining pharmaceuticals.
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

# Drug Interaction Checker

Check for interactions between multiple medications, including severity classification and mechanism explanations.

## Features

- **Multi-drug analysis**: Check interactions between 2+ medications simultaneously
- **Severity classification**: Critical / Major / Moderate / Minor / Unknown
- **Mechanism explanation**: Pharmacological basis for each interaction
- **Clinical guidance**: Recommendations for management

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **Critical** | Life-threatening interaction | Absolute contraindication |
| **Major** | Significant risk, may need medical intervention | Avoid combination or monitor closely |
| **Moderate** | Moderate risk, may require dose adjustment | Monitor for adverse effects |
| **Minor** | Mild interaction, unlikely to cause issues | Be aware, usually acceptable |
| **Unknown** | Insufficient data | Proceed with caution |

## Usage

### Python Script

```bash
python scripts/main.py --drugs "Warfarin" "Aspirin" "Ibuprofen"
```

### As a Module

```python
from scripts.main import check_interactions

result = check_interactions(["Metformin", "Simvastatin", "Amlodipine"])
```

## Parameters

- `drugs`: List of drug names (generic or brand names accepted)
- `include_mechanism`: Include pharmacological mechanism (default: True)
- `include_management`: Include clinical recommendations (default: True)

## Output Format

```json
{
  "drugs_checked": ["Drug A", "Drug B"],
  "interactions": [
    {
      "drug_pair": ["Drug A", "Drug B"],
      "severity": "Major",
      "mechanism": "Pharmacodynamic synergism...",
      "effect": "Increased bleeding risk",
      "recommendation": "Avoid combination or monitor INR closely"
    }
  ],
  "summary": {
    "critical": 0,
    "major": 1,
    "moderate": 0,
    "minor": 0
  }
}
```

## Data Sources

This skill uses a curated drug interaction database stored in `references/interactions_db.json`. The database includes:

- FDA-approved drug interaction data
- Known metabolic pathways (CYP450 enzymes)
- Pharmacodynamic interactions
- Common supplement interactions

## Limitations

- Database may not include all possible drug combinations
- Always consult healthcare professionals for medical decisions
- Does not account for patient-specific factors (age, renal function, etc.)
- Not a substitute for professional medical advice

## Technical Difficulty

**High** - Requires extensive pharmacological knowledge database, accurate severity classification, and clear mechanism explanations.

## References

See `references/` directory for:
- `interactions_db.json` - Drug interaction database
- `severity_criteria.md` - Classification criteria
- `cyp450_substrates.json` - Metabolic pathway data

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

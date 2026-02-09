---
name: usmle-case-generator
description: Generate USMLE Step 1/2 style clinical cases with patient history, physical
  exam, lab results, and diagnosis options. Trigger when user requests medical case
  studies, USMLE practice questions, clinical vignettes, or medical board exam preparation
  materials.
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

# USMLE Case Generator

Generate USMLE Step 1 and Step 2 CK style clinical cases for medical education and board exam preparation.

## Features

- **Step 1 Cases**: Basic science concepts, pathophysiology, pharmacology
- **Step 2 Cases**: Clinical diagnosis, management, next best steps
- **Complete Vignettes**: History, physical exam, labs, imaging
- **Multiple Choice Questions**: Single best answer format
- **Answer Explanations**: Detailed rationale for learning

## Usage

```python
# Generate a Step 1 case (pathophysiology focus)
python scripts/main.py --step 1 --topic cardiology --difficulty medium

# Generate a Step 2 case (clinical management focus)
python scripts/main.py --step 2 --topic nephrology --include-diagnosis

# Generate case with specific conditions
python scripts/main.py --step 2 --condition "diabetic ketoacidosis" --format json
```

## Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| `--step` | 1, 2 | USMLE Step level |
| `--topic` | See references/topics.json | Medical specialty |
| `--condition` | Any condition | Specific disease/condition |
| `--difficulty` | easy, medium, hard | Case complexity |
| `--format` | text, json, markdown | Output format |
| `--include-diagnosis` | flag | Include answer key |
| `--count` | 1-10 | Number of cases to generate |

## Topics Covered

- Cardiology
- Pulmonology
- Gastroenterology
- Nephrology
- Endocrinology
- Hematology/Oncology
- Infectious Disease
- Neurology
- Psychiatry
- Musculoskeletal
- Dermatology
- Obstetrics/Gynecology
- Pediatrics
- Surgery

## Case Structure

Each generated case includes:

1. **Patient Demographics**: Age, gender, relevant background
2. **Chief Complaint**: Presenting problem
3. **History of Present Illness**: Detailed symptom timeline
4. **Past Medical History**: Relevant comorbidities
5. **Medications**: Current drug regimen
6. **Allergies**: Drug/environmental allergies
7. **Family History**: Genetic conditions
8. **Social History**: Smoking, alcohol, occupation
9. **Physical Examination**: Vital signs, relevant findings
10. **Laboratory Studies**: CBC, CMP, specific markers
11. **Imaging/Diagnostics**: X-ray, CT, ECG, etc.
12. **Question**: USMLE-style multiple choice
13. **Answer Options**: 5 choices (A-E)
14. **Correct Answer**: With detailed explanation
15. **Educational Objectives**: Key learning points

## Output Formats

### Text Format (Default)
Plain text suitable for printing or reading.

### JSON Format
Structured data for integration with applications.

### Markdown Format
Formatted for documentation or web display.

## Technical Difficulty

**High** - Requires medical knowledge validation and clinical accuracy.

⚠️ **Manual Review Required**: Generated cases should be reviewed by medical professionals before use in high-stakes educational settings.

## References

- `references/topics.json` - Medical specialty taxonomy
- `references/case_templates.json` - Case structure templates
- `references/usmle_patterns.md` - USMLE question patterns
- `references/conditions/` - Condition-specific case data

## Example Output

```
Case: A 58-year-old male with chest pain

A 58-year-old man presents to the emergency department with 
crushing substernal chest pain radiating to his left arm, 
beginning 2 hours ago at rest...

[History, physical, labs, ECG findings...]

Question: What is the most appropriate next step in management?

A. Administer aspirin and nitroglycerin
B. Order CT pulmonary angiography
C. Perform immediate synchronized cardioversion
D. Start heparin drip and call cardiology
E. Discharge with outpatient stress test

Correct Answer: D
Explanation: [Detailed rationale...]
```

## Safety & Limitations

- Cases are AI-generated and may contain inaccuracies
- Not a substitute for professional medical education
- Always verify clinical details with authoritative sources
- Intended for educational purposes only

## Dependencies

- Python 3.8+
- No external API dependencies (template-based generation)
- Optional: LLM integration for case variation

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

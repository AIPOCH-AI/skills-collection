---
name: lab-result-interpretation
description: 'Interprets complex biochemical laboratory test results and converts
  them into patient-friendly explanations. Trigger when: user provides lab test results
  (blood work, urine analysis, lipid panel, liver/kidney function tests, etc.) and
  needs plain-language interpretation of values, reference ranges, and clinical significance.'
version: 1.0.0
category: Clinical
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Lab Result Interpretation Skill

A medical assistant tool that transforms complex biochemical laboratory test results into clear, patient-friendly explanations.

## Features

- Parses various lab test formats (numeric values, units, reference ranges)
- Compares values against standard reference ranges
- Generates patient-friendly explanations in Chinese
- Flags abnormal values with severity indicators
- Provides contextual health recommendations

## Supported Test Types

| Category | Tests |
|----------|-------|
| **Blood Routine** | WBC, RBC, Hemoglobin, Platelets, Hematocrit |
| **Lipid Panel** | Total Cholesterol, LDL, HDL, Triglycerides |
| **Liver Function** | ALT, AST, ALP, GGT, Bilirubin, Total Protein, Albumin |
| **Kidney Function** | Creatinine, BUN, eGFR, Uric Acid |
| **Blood Sugar** | Fasting Glucose, HbA1c |
| **Thyroid** | TSH, T3, T4, FT3, FT4 |
| **Electrolytes** | Sodium, Potassium, Chloride, Calcium, Magnesium |
| **Inflammation** | CRP, ESR |

## Usage

### As Module

```python
from scripts.main import LabResultInterpreter

interpreter = LabResultInterpreter()
result = interpreter.interpret("总胆固醇: 5.8 mmol/L (参考: 3.1-5.7)")
print(result.explanation)
```

### CLI

```bash
python scripts/main.py --file lab_report.txt
python scripts/main.py --interactive
```

## Input Format

Accepts flexible formats:
```
Test Name: Value Unit (Reference: Min-Max)
Test Name Value Unit Ref: Min-Max
Test Name: Value (Min-Max)
```

## Output Format

```json
{
  "test_name": "总胆固醇",
  "value": 5.8,
  "unit": "mmol/L",
  "reference_min": 3.1,
  "reference_max": 5.7,
  "status": "high",
  "explanation": "您的总胆固醇略高于正常范围...",
  "severity": "mild",
  "recommendation": "建议减少饱和脂肪摄入..."
}
```

## Technical Details

**Difficulty:** Medium

**Key Components:**
- Lab value parsing with regex patterns
- Reference range comparison logic
- Medical knowledge base (references/lab_reference_ranges.json)
- Patient-friendly explanation templates

**Safety:**
- Includes medical disclaimer in all outputs
- Flags values requiring immediate medical attention
- Does not diagnose - only explains test meanings

## References

- `references/lab_reference_ranges.json` - Standard reference ranges
- `references/explanation_templates.json` - Patient-friendly templates
- `references/test_metadata.json` - Test descriptions and clinical notes

## Medical Disclaimer

This tool provides educational information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for interpretation of lab results.

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

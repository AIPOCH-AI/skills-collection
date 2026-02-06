---
name: lab-result-interpretation
description: >
  Interprets complex biochemical laboratory test results and converts them into patient-friendly explanations.
  Trigger when: user provides lab test results (blood work, urine analysis, lipid panel, liver/kidney function tests, etc.)
  and needs plain-language interpretation of values, reference ranges, and clinical significance.
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

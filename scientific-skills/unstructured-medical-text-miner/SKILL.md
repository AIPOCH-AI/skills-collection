---
name: unstructured-medical-text-miner
description: Mine unstructured clinical text from MIMIC-IV to extract diagnostic logic
  and treatment details
version: 1.0.0
category: General
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

# Unstructured Medical Text Miner (ID: 213)

## Overview

Mine "text data" that has been long overlooked in MIMIC-IV, extracting unstructured diagnostic logic, order details, and progress notes.

## Purpose

The MIMIC-IV database contains large amounts of structured data (vital signs, laboratory results, etc.), but its true clinical value is often hidden in unstructured text:
- Diagnostic reasoning chains in discharge summaries
- Subtle finding descriptions in imaging reports
- Treatment decision logic in progress notes
- Personalized medication considerations in orders

This Skill provides a complete text mining toolchain to transform raw medical text into analyzable structured insights.

## Features

### 1. Text Extraction
- **NOTEEVENTS**: Extract clinical notes from MIMIC-IV NOTE module
- **Radiology Reports**: Extract imaging diagnostic text
- **ECG Reports**: Parse ECG interpretation text
- **Discharge Summaries**: Extract complete diagnostic and treatment course

### 2. Information Extraction
- **Entity Recognition**: Diseases, symptoms, medications, procedures, anatomical sites
- **Relation Extraction**: Medication-disease treatment relationships, symptom-disease diagnostic relationships
- **Timeline Extraction**: Event occurrence times, disease progression sequence
- **Negation Detection**: Identify negated clinical findings (e.g., "no fever")

### 3. Clinical Logic Parsing
- **Diagnostic Reasoning Chain**: Reasoning path from symptoms → examination → diagnosis
- **Treatment Decision Tree**: Clinical basis for medication selection and dosage adjustment
- **Disease Progression**: Disease progression and outcome descriptions

### 4. Structured Output
- FHIR-compatible clinical document format
- Knowledge graph-friendly triple format
- Temporal event sequences

## Usage

```python
from skills.unstructured_medical_text_miner.scripts.main import MedicalTextMiner

# Initialize miner
miner = MedicalTextMiner()

# Load MIMIC-IV note data
miner.load_notes(notes_path="path/to/noteevents.csv")

# Extract all text records for a specific patient
patient_texts = miner.get_patient_texts(subject_id=10000032)

# Execute complete information extraction
insights = miner.extract_insights(
    text=patient_texts,
    extract_entities=True,
    extract_relations=True,
    extract_timeline=True
)
```

## Input

### Data Sources
- MIMIC-IV NOTEEVENTS table (csv/parquet format)
- Discharge summary files
- Imaging report files
- Custom medical text

### Field Requirements
| Field Name | Description | Required |
|--------|------|------|
| subject_id | Patient unique identifier | Yes |
| hadm_id | Hospital admission record identifier | No |
| note_type | Note type (DS/RR/ECG, etc.) | Yes |
| note_text | Note text content | Yes |
| charttime | Record time | No |

## Output

### Entity Extraction Results
```json
{
  "entities": [
    {
      "text": "acute myocardial infarction",
      "type": "DISEASE",
      "start": 156,
      "end": 183,
      "confidence": 0.94
    },
    {
      "text": "aspirin 81mg",
      "type": "MEDICATION",
      "start": 245,
      "end": 257,
      "attributes": {
        "dose": "81mg",
        "frequency": "daily"
      }
    }
  ]
}
```

### Clinical Logic Graph
```json
{
  "clinical_logic": {
    "presenting_complaint": "chest pain",
    "differential_diagnoses": ["ACS", "PE", "aortic dissection"],
    "workup": ["ECG", "troponin", "CTA chest"],
    "final_diagnosis": "STEMI",
    "treatment_plan": ["PCI", "dual antiplatelet"]
  }
}
```

### Temporal Events
```json
{
  "timeline": [
    {
      "time": "2020-03-15 08:30",
      "event": "admission",
      "description": "presented with chest pain"
    },
    {
      "time": "2020-03-15 09:15",
      "event": "ECG",
      "description": "ST elevation in V1-V4"
    }
  ]
}
```

## Dependencies

```
pandas>=1.3.0
spacy>=3.4.0
scispacy>=0.5.1
radlex (for radiology terminology)
negspacy (for negation detection)
```

## Configuration

```yaml
# config.yaml
extraction:
  entity_types: ["DISEASE", "SYMPTOM", "MEDICATION", "PROCEDURE", "ANATOMY"]
  relation_types: ["TREATS", "CAUSES", "CONTRAINDICATED_WITH"]
  enable_negation_detection: true
  
models:
  ner_model: "en_core_sci_lg"  # or "en_core_sci_scibert"
  relation_model: "custom_relation_extractor"
  
output:
  format: "json"  # json/fhir/kg
  include_raw_text: false
```

## CLI Usage

```bash
# Process single file
python -m skills.unstructured_medical_text_miner.scripts.main \
  --input notes.csv \
  --output extracted.json \
  --extract all

# Process specific patient
python -m skills.unstructured_medical_text_miner.scripts.main \
  --subject-id 10000032 \
  --db-path mimic_iv.db \
  --output patient_insights.json
```

## References

1. MIMIC-IV Clinical Database: https://physionet.org/content/mimiciv/
2. scispacy: https://allenai.github.io/scispacy/
3. NegEx/negspacy for negation detection
4. FHIR Clinical Document specifications

## Author

Skill ID: 213
Category: Medical Data Mining
Complexity: Advanced

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

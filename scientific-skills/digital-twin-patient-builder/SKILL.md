---
name: digital-twin-patient-builder
description: Build digital twin patient models to test drug efficacy and toxicity
  in virtual environments
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Digital Twin Patient Builder (ID: 208)

## Function Overview

Build a "digital twin" model of a patient, integrating genotype, clinical history, and imaging data to test the efficacy and toxicity of different drug doses in a virtual environment.

## Use Cases

- Personalized drug treatment plan design
- Drug dose optimization
- Adverse reaction risk assessment
- Clinical trial virtual simulation

## Input

| Data Type | Description | Format |
|---------|------|------|
| `genotype` | Patient genotype data (SNPs, CNVs) | JSON |
| `clinical_history` | Clinical history and laboratory indicators | JSON |
| `imaging_features` | Imaging features (MRI, CT, etc.) | JSON |

## Output

| Output Type | Description |
|---------|------|
| `efficacy_prediction` | Efficacy prediction results |
| `toxicity_prediction` | Toxicity reaction prediction |
| `optimal_dose` | Optimal dose recommendation |

## Usage

### Command Line Usage

```bash
python scripts/main.py --patient patient_data.json --drug drug_profile.json --doses "[50, 100, 150]"
```

### Python API

```python
from scripts.main import DigitalTwinBuilder

builder = DigitalTwinBuilder()
twin = builder.build_twin(patient_data)
results = twin.simulate_drug_regimen(drug_profile, dose_range)
```

## Technical Architecture

```
digital-twin-patient-builder/
├── SKILL.md              # This file
├── scripts/
│   └── main.py           # Core implementation
│
├── Core Components:
│   ├── PatientProfile    # Patient profile management
│   ├── GenotypeModel     # Genotype modeling
│   ├── ClinicalModel     # Clinical data modeling
│   ├── ImagingModel      # Imaging feature modeling
│   ├── DigitalTwin       # Digital twin main class
│   ├── PharmacokineticModel  # Pharmacokinetic model
│   └── DrugSimulator     # Drug simulator
```

## Dependencies

- numpy >= 1.21.0
- scipy >= 1.7.0
- pandas >= 1.3.0

## Example Data Format

### Patient Data (patient_data.json)
```json
{
  "patient_id": "P001",
  "genotype": {
    "CYP2D6": "*1/*4",
    "TPMT": "*1/*3C",
    "SNPs": {"rs12345": "AG", "rs67890": "CC"}
  },
  "clinical": {
    "age": 58,
    "weight": 70.5,
    "height": 170,
    "lab_values": {"creatinine": 1.2, "alt": 45, "ast": 38},
    "comorbidities": ["hypertension", "diabetes"]
  },
  "imaging": {
    "tumor_volume": 45.2,
    "perfusion_rate": 0.85,
    "texture_features": {"entropy": 5.2, "uniformity": 0.45}
  }
}
```

### Drug Profile (drug_profile.json)
```json
{
  "drug_name": "ExampleDrug",
  "drug_class": "chemotherapy",
  "metabolizing_enzymes": ["CYP2D6", "CYP3A4"],
  "target_genes": ["EGFR", "KRAS"],
  "pk_params": {
    "clearance": 15.5,
    "volume_distribution": 45.0,
    "half_life": 8.0
  },
  "efficacy_biomarkers": ["tumor_reduction", "survival_rate"],
  "toxicity_markers": ["neutropenia", "hepatotoxicity"]
}
```

## Model Principles

1. **Genotype Modeling**: Parse drug metabolizing enzyme genotypes to predict metabolic phenotypes (ultrarapid/normal/poor metabolizer)
2. **Physiological Modeling**: Calculate personalized pharmacokinetic parameters based on age, weight, and organ function
3. **Imaging Modeling**: Extract tumor features to predict drug responsiveness
4. **Integrated Model**: Multi-modal data fusion to build a comprehensive digital twin
5. **Drug Simulation**: PBPK (physiologically-based pharmacokinetics) + PD (pharmacodynamics) model

## References

- PBPK modeling guidelines (FDA, 2018)
- Pharmacogenomics in precision medicine (Nature Reviews, 2020)

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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

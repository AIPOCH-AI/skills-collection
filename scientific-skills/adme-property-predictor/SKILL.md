---
name: adme-property-predictor
description: Predict ADME properties (Absorption, Distribution, Metabolism, Excretion)
  for drug candidates to evaluate druggability.
version: 1.0.0
category: Pharma
tags:
- adme
- pharmacokinetics
- druglikeness
- lipinski
- qsar
- molecule
- prediction
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# ADME Property Predictor

Predicts Absorption, Distribution, Metabolism, and Excretion properties of drug candidates using molecular descriptors and cheminformatics rules.

## Features

### Absorption (A)
- **Caco-2 Permeability** prediction (oral absorption potential)
- **Human Intestinal Absorption (HIA)** estimation
- **Solubility** classification (aqueous/therapeutic)
- **Lipinski's Rule of 5** compliance check
- **Veber's Rules** (rotatable bonds, polar surface area)

### Distribution (D)
- **Plasma Protein Binding (PPB)** prediction
- **Blood-Brain Barrier (BBB)** permeability
- **Volume of Distribution (Vd)** estimation
- **Tissue Distribution** potential

### Metabolism (M)
- **CYP450 Metabolic Stability** assessment
- **Drug-Drug Interaction** risk (CYP inhibition)
- **Metabolic Liability** hotspots identification

### Excretion (E)
- **Half-life (T1/2)** estimation
- **Clearance** prediction
- **Renal/Biliary Excretion** tendency

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `smiles` | string | Yes | SMILES string of the molecule |
| `properties` | list | No | Specific properties to calculate (default: all) |
| `format` | string | No | Output format: json/table (default: json) |

## Output Format

```json
{
  "molecule": {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "molecular_weight": 180.16,
    "formula": "C9H8O4"
  },
  "absorption": {
    "lipinski_violations": 0,
    "lipinski_pass": true,
    "caco2_permeability": "high",
    "hia": 95.2,
    "solubility_class": "soluble",
    "psa": 63.6,
    "logp": 1.19
  },
  "distribution": {
    "bbb_permeable": false,
    "ppb_percent": 45.3,
    "vd_estimate": 0.15
  },
  "metabolism": {
    "cyp3a4_substrate": true,
    "cyp2c9_substrate": true,
    "metabolic_stability": "moderate"
  },
  "excretion": {
    "t12_hours": 4.5,
    "clearance_ml_min_kg": 8.2,
    "excretion_route": "renal"
  },
  "druglikeness_score": 0.78,
  "recommendation": "Good drug candidate"
}
```

## Usage Examples

### Basic Prediction
```python
python scripts/main.py --smiles "CC(=O)Oc1ccccc1C(=O)O"
```

### Specific Properties Only
```python
python scripts/main.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --properties absorption distribution
```

### Batch Processing
```python
python scripts/main.py --input molecules.csv --output results.json
```

## Interpretation Guide

| Property | Good Range | Caution |
|----------|-----------|---------|
| MW | < 500 Da | > 500 Da |
| LogP | 1-3 | < 0 or > 5 |
| PSA | < 140 Å² | > 140 Å² |
| HIA | > 80% | < 50% |
| BBB | LogBB > 0.3 | LogBB < -1 |
| T1/2 | 2-8h | < 1h or > 24h |

## References

1. Lipinski et al. (2001) - Rule of 5
2. Veber et al. (2002) - Oral bioavailability rules
3. Egan et al. (2000) - BBB permeability model

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

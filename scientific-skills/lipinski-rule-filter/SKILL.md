---
name: lipinski-rule-filter
description: Filter compound libraries based on Lipinski's Rule of Five for drug-likeness
trigger: lipinski, rule of five, drug-like, filter, admet
tier: C
---

# Lipinski Rule Filter

Filter small molecule compound libraries based on Lipinski's Rule of Five to identify compounds with poor absorption.

## Usage

```bash
python scripts/main.py --input compounds.smi --output filtered.smi
python scripts/main.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --check
```

## Parameters

- `--input`: Input SMILES/SDF file
- `--smiles`: Single SMILES string to check
- `--output`: Output file for passing compounds
- `--violations`: Max allowed violations (default: 1)

## Lipinski's Rules

- MW < 500 Da
- LogP < 5
- H-bond donors < 5
- H-bond acceptors < 10

## Output

- Filtered compound list
- Rule violation report
- Drug-likeness score

---
name: smiles-de-salter
description: Batch process chemical SMILES strings to remove salt ions and retain
  only active pharmaceutical ingredients
version: 1.0.0
category: Pharma
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

# SMILES De-salter

ID: 176

Batch process chemical structure strings, removing salt ion portions and retaining only the active core.

## Function Description

This Skill is used to process chemical SMILES strings, automatically identifying and removing counterions, retaining only the active pharmaceutical ingredient (API).

### Salt Ion Identification Rules

- Identify multiple components through `.` separator
- Salt ions are usually smaller ions (such as Na⁺, Cl⁻, K⁺, Br⁻, etc.)
- Retain the component with the most atoms as the core
- Support common inorganic salts and organic acid salts

### Supported Salt Types

| Type | Examples |
|------|------|
| Inorganic salts | NaCl, KCl, HCl, H₂SO₄ |
| Organic acid salts | Citrate, Tartrate, Maleate |
| Quaternary ammonium salts | Various quaternary ammonium compounds |

## Usage

### Command Line

```bash
python scripts/main.py -i input.csv -o output.csv -c smiles_column
```

### Parameter Description

| Parameter | Short | Description | Default |
|------|------|------|--------|
| `--input` | `-i` | Input file path (CSV/TSV/SMILES) | Required |
| `--output` | `-o` | Output file path | desalted_output.csv |
| `--column` | `-c` | SMILES column name | smiles |
| `--keep-largest` | `-k` | Keep largest component (by atom count) | True |

### Single Processing Example

```bash
python scripts/main.py -s "CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C.[Na+]"
# Output: CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C
```

## Input Format

### CSV/TSV Files

```csv
id,smiles,name
1,CCO.[Na+],ethanol_sodium
2,c1ccccc1.[Cl-],benzene_hcl
```

### Pure SMILES Files

One SMILES string per line:
```
CCO.[Na+]
c1ccccc1.[Cl-]
```

## Output Format

Output file contains original data and new processing result columns:

```csv
id,smiles,name,desalted_smiles,status
1,CCO.[Na+],ethanol_sodium,CCO,success
2,c1ccccc1.[Cl-],benzene_hcl,c1ccccc1,success
```

## Dependencies

- Python >= 3.8
- rdkit >= 2022.03.1

## Install Dependencies

```bash
pip install rdkit pandas
```

## Processing Logic

1. **Parse SMILES**: Use RDKit to parse input string
2. **Component Splitting**: Identify multiple molecular components separated by `.`
3. **Core Identification**:
   - Default selects component with the most atoms
   - Optional: based on molecular weight, ring count, etc.
4. **Output Result**: Return clean core SMILES

## Error Handling

| Error Type | Handling Method |
|----------|----------|
| Invalid SMILES | Mark as invalid_smiles |
| Empty input | Mark as empty_input |
| No salt structure | Return as-is, mark as no_salt |

## Examples

### Example 1: Simple Inorganic Salt

Input: `CCO.[Na+]`
Output: `CCO`

### Example 2: HCl Salt

Input: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C.Cl`
Output: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C`

### Example 3: Complex Organic Salt

Input: `CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C.C(C(=O)O)C(CC(=O)O)(C(=O)O)O`
Output: `CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C` (retains larger caffeine molecule)

## Notes

1. This tool assumes the core is the component with the most atoms
2. For co-crystals or multi-component drugs, manual review may be needed
3. Some hydrochloride salts may exist as `[Cl-]` or `Cl`
4. It is recommended to sample and verify results

## Author

OpenClaw Skill Hub

## Version

v1.0.0

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

No additional Python packages required.

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

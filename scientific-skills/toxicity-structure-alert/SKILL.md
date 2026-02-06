---
name: toxicity-structure-alert
description: Identify potential toxic structural alerts in drug molecules by scanning
  SMILES/SMARTS structures for known toxicophores and assessing toxicity risk levels.
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

# Toxicity Structure Alert (Skill ID: 141)

Identify potential toxic structural alerts in drug molecules.

## Features

- Scan molecular structures (SMILES/SMARTS)
- Identify known toxic structural alerts
- Assess potential toxicity risk levels
- Generate detailed reports

## Supported Alert Structures

| Alert Structure | Toxicity Type | Risk Level |
|---------|---------|---------|
| Aromatic Nitro | Mutagenicity | High |
| Aromatic Amine | Carcinogenicity | High |
| Epoxide | Alkylating Agent | High |
| Aldehyde | Reactive Toxicity | Medium |
| Acyl Chloride | Reactive Toxicity | Medium |
| Michael Acceptor | Electrophilic Toxicity | Medium |
| Hydrazine | Hepatotoxicity | High |
| Haloalkyl | Alkylating Agent | High |
| Quinone | Oxidative Stress | Medium |
| Thiol-Reactive Groups | Protein Binding | Low-Medium |

## Dependencies

- Python 3.8+
- RDKit

## Usage

```bash
python scripts/main.py --input <smiles_string> [--format json|text]
```

### Parameters

- `--input, -i`: Input SMILES string (required)
- `--format, -f`: Output format, optional `json` or `text` (default: text)
- `--detail, -d`: Detail level, optional `basic`, `standard`, `full` (default: standard)

### Examples

```bash
# Basic text output
python scripts/main.py -i "O=[N+]([O-])c1ccccc1"

# JSON format output
python scripts/main.py -i "O=C1OC1c1ccccc1" -f json

# Detailed report
python scripts/main.py -i "c1ccc2c(c1)ccc1c3ccccc3ccc21" -d full
```

### Python API

```python
from scripts.main import ToxicityAlertScanner

scanner = ToxicityAlertScanner()
result = scanner.scan("O=[N+]([O-])c1ccccc1")
print(result.alerts)
```

## Output Format

### JSON Output

```json
{
  "input": "O=[N+]([O-])c1ccccc1",
  "mol_weight": 123.11,
  "alert_count": 1,
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "alerts": [
    {
      "name": "Aromatic Nitro",
      "type": "mutagenic",
      "smarts": "[N+](=O)[O-]",
      "risk_level": "HIGH",
      "description": "May cause DNA damage and mutagenicity"
    }
  ],
  "recommendations": [
    "Recommend Ames test validation",
    "Consider structural optimization to reduce toxicity"
  ]
}
```

## Risk Levels

- **HIGH**: Known significant toxicity, strongly recommended to avoid
- **MEDIUM**: Potential toxicity, further evaluation recommended
- **LOW**: Minor concern, can be considered based on specific circumstances

## Notes

1. This tool is based on known alert structures and cannot replace comprehensive toxicological assessment
2. False positives and false negatives may both exist
3. Recommended to use with other ADMET prediction tools

## References

- Ashby J., Tennant R.W. (1988) Chemical structure, Salmonella mutagenicity...
- Kazius J., McGuire R., Bursi R. (2005) Derivation and validation of toxicophores...
- Enoch S.J., Cronin M.T.D. (2010) A review of the electrophilic reaction chemistry...

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

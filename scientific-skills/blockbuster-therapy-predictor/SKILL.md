---
name: blockbuster-therapy-predictor
description: Predict which early-stage technologies (PROTAC, mRNA, gene editing) will
  become the next blockbuster therapy
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

# Blockbuster Therapy Predictor

**ID**: 202

## Function Overview

Combine clinical trial data, patent landscape, and early-stage VC funding data to predict which early-stage technology pathways (such as PROTAC, mRNA, gene editing, etc.) are likely to become the next "blockbuster" therapy.

## Data Dimensions

### 1. Clinical Trials Data
- Trial phase distribution (Phase I/II/III)
- Indication coverage breadth
- Trial success rates and timelines
- Key clinical endpoint achievement

### 2. Patent Landscape Data
- Patent application trends and growth rates
- Technology moat depth (number of core patents)
- Patent family geographic coverage
- Major player layout density

### 3. Funding Data (VC Funding)
- Early-stage funding rounds and amounts
- Investor quality (top-tier VC participation)
- Funding frequency and valuation growth
- Time from company founding to funding

## Technology Pathway Assessment Model

### Maturity Score
```
Maturity = 0.4 × Clinical_Stage + 0.3 × Patent_Depth + 0.3 × Funding_Stage
```

### Market Potential Score
```
Market_Potential = 0.35 × Addressable_Market + 0.35 × Unmet_Need + 0.30 × Competitive_Landscape
```

### Blockbuster Index
```
Blockbuster_Index = 0.5 × Market_Potential + 0.3 × Maturity + 0.2 × Momentum
```

## Output Format

### 1. Technology Pathway Ranking Table
| Rank | Technology Pathway | Blockbuster Index | Maturity | Market Potential | Investment Recommendation |
|------|----------|--------------|--------|----------|----------|

### 2. Detailed Assessment Report
- Technology pathway overview
- Key driving factors
- Risk factors
- Timeline prediction

### 3. Investment Recommendations
- **Strongly Recommended**: Index ≥ 80
- **Recommended**: Index 60-79
- **Watch**: Index 40-59
- **Cautious**: Index < 40

## Usage

```bash
# Run full analysis
python skills/blockbuster-therapy-predictor/scripts/main.py --mode full

# Analyze specific technology pathways only
python skills/blockbuster-therapy-predictor/scripts/main.py --tech PROTAC,mRNA,CRISPR

# Output JSON format
python skills/blockbuster-therapy-predictor/scripts/main.py --output json

# Set minimum blockbuster index threshold
python skills/blockbuster-therapy-predictor/scripts/main.py --threshold 70
```

## Dependencies

- Python 3.9+
- pandas
- numpy
- requests
- python-dotenv

## Technology Pathway List

- **PROTAC** (Proteolysis Targeting Chimera)
- **mRNA** (Messenger RNA therapy)
- **CRISPR** (Gene editing)
- **CAR-T** (Chimeric Antigen Receptor T-cell)
- **Bispecific Antibodies** (Bispecific antibodies)
- **ADC** (Antibody-Drug Conjugate)
- **Cell Therapy** (Universal cell therapy)
- **Gene Therapy** (AAV gene therapy)
- **RNAi** (RNA interference)
- **Allogeneic** (Allogeneic cell therapy)

## Changelog

- v1.0.0: Initial version, integrated three major data sources, basic prediction model

## Reference Data Sources

- ClinicalTrials.gov
- USPTO/EPO patent databases
- PitchBook/Crunchbase funding data
- Evaluate Pharma market data

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

---
name: mouse-colony-planner
description: Calculate breeding timelines and cage requirements for transgenic mouse
  colonies
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

# Mouse Colony Planner

Calculate timelines and cage numbers required for transgenic mouse breeding to optimize breeding costs.

## Functions

- **Timeline Calculation**: Calculate time required for each stage based on breeding scheme
- **Cage Planning**: Estimate cage numbers needed for experiments
- **Cost Estimation**: Calculate total breeding costs (cage fees, husbandry fees, genotyping fees, etc.)

## Usage

### Command Line

```bash
python scripts/main.py --scheme <breeding_scheme> --females <number_of_females> --males <number_of_males> [options]
```

### Parameters

| Parameter | Description | Default |
|------|------|--------|
| `--scheme` | Breeding scheme: `heterozygote`, `homozygote`, `conditional` | Required |
| `--females` | Starting number of females | Required |
| `--males` | Starting number of males | Required |
| `--gestation` | Gestation period (days) | 21 |
| `--weaning` | Weaning age (days) | 21 |
| `--sexual-maturity` | Sexual maturity age (days) | 42 |
| `--cage-capacity` | Maximum cage capacity | 5 |
| `--cage-cost` | Cage cost per day (CNY) | 3.0 |
| `--genotyping-cost` | Genotyping cost per mouse (CNY) | 15.0 |
| `--target-pups` | Target number of specific genotype mice | 10 |

### Breeding Scheme Descriptions

1. **heterozygote (Heterozygote breeding)**: Heterozygote x Wild type → 50% Heterozygotes
2. **homozygote (Homozygote breeding)**: Heterozygote x Heterozygote → 25% Homozygotes
3. **conditional (Conditional knockout)**: Requires two-step breeding, introducing Cre/loxp system

### Examples

```bash
# Heterozygote breeding scheme, starting with 10 females and 5 males, target to obtain 10 heterozygote offspring
python scripts/main.py --scheme heterozygote --females 10 --males 5 --target-pups 10

# Homozygote breeding, custom cycle parameters
python scripts/main.py --scheme homozygote --females 20 --males 10 --target-pups 20 --gestation 21 --weaning 21

# Conditional knockout scheme
python scripts/main.py --scheme conditional --females 15 --males 15 --target-pups 15
```

## Output

- Timeline for each stage
- Cage numbers required at each stage
- Estimated total cost
- Breeding flowchart

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

---
name: adaptive-trial-simulator
description: Design and simulate adaptive clinical trial designs in silico with interim
  analysis and sample size re-estimation
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

# Adaptive Trial Simulator

**ID**: 205  
**Category**: Clinical Research / Biostatistics  
**Language**: Python 3.10+

## Overview

Design and simulate Adaptive Clinical Trial designs in silico. This tool enables:

- **Interim Analysis**: Decision-making logic at planned analysis points
- **Sample Size Re-estimation**: Adaptive adjustment based on observed data
- **Early Stopping Rules**: Futility and efficacy boundaries
- **Type I Error Control**: Validation via simulation
- **Optimal Design**: Identify best parameters for trial success

## Usage

```bash
python scripts/main.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--design` | str | "group_sequential" | Design type: `group_sequential`, `adaptive_reestimate`, `drop_the_loser` |
| `--n-simulations` | int | 10000 | Number of Monte Carlo simulations |
| `--sample-size` | int | 200 | Initial per-arm sample size |
| `--effect-size` | float | 0.3 | True treatment effect (Cohen's d) |
| `--alpha` | float | 0.05 | Overall Type I error rate |
| `--power` | float | 0.80 | Target power (1 - Type II error) |
| `--interim-looks` | int | 1 | Number of interim analyses |
| `--spending-function` | str | "obrien_fleming" | Alpha spending: `obrien_fleming`, `pocock`, `power_family` |
| `--reestimate-method` | str | "promising_zone" | SSR method: `promising_zone`, `conditional_power`, `inverse_normal` |
| `--output` | str | "results.json" | Output file path |
| `--visualize` | flag | False | Generate visualization plots |

### Examples

**Group Sequential Design**:
```bash
python scripts/main.py --design group_sequential --sample-size 300 --interim-looks 2 --spending-function obrien_fleming
```

**Sample Size Re-estimation**:
```bash
python scripts/main.py --design adaptive_reestimate --sample-size 200 --effect-size 0.25 --reestimate-method promising_zone
```

**Comprehensive Simulation**:
```bash
python scripts/main.py --n-simulations 50000 --sample-size 150 --effect-size 0.35 --interim-looks 1 --alpha 0.025 --visualize
```

## Output

The tool generates a JSON report with:

```json
{
  "design_config": { ... },
  "simulation_results": {
    "overall_success_rate": 0.823,
    "type_i_error": 0.049,
    "expected_sample_size": 285.4,
    "early_stop_rate": {
      "efficacy": 0.342,
      "futility": 0.118
    }
  },
  "interim_analysis": {
    "look_1": {
      "stop_efficacy": 0.18,
      "stop_futility": 0.08,
      "continue": 0.74
    }
  },
  "optimal_design": {
    "recommended_n_per_arm": 320,
    "expected_power": 0.85,
    "max_sample_size": 480
  }
}
```

## Technical Details

### Supported Designs

1. **Group Sequential Design**
   - O'Brien-Fleming boundaries (conservative early stops)
   - Pocock boundaries (aggressive early stops)
   - Lan-DeMets spending functions

2. **Adaptive Sample Size Re-estimation**
   - Promising zone approach (Mehta & Pocock)
   - Conditional power based adjustment
   - Inverse normal combination test

3. **Drop-the-Loser Design**
   - Multi-arm multi-stage (MAMS) selection
   - Seamless Phase II/III adaptation

### Statistical Methods

- **Boundary Calculation**: Numerical integration for group sequential tests
- **Conditional Power**: CP under current trend and hypothesized effect
- **Variance Estimation**: Pooled variance from interim data
- **Multiplicity Control**: Bonferroni, Holm, Hochberg, or closed testing

## Dependencies

```
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
```

Install via:
```bash
pip install numpy scipy matplotlib
```

## References

1. Jennison C, Turnbull BW. Group Sequential Methods with Applications to Clinical Trials. CRC Press; 1999.
2. Chow SC, Chang M. Adaptive Design Methods in Clinical Trials. Chapman & Hall/CRC; 2011.
3. Mehta CR, Pocock SJ. Adaptive increase in sample size when interim results are promising. Trials. 2011;12:94.
4. Bauer P, Kieser M. Combining different phases in the development of medical treatments within a single trial. Stat Med. 1999;18(14):1833-1848.

## Author

Clinical Biostatistics Skill Set

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

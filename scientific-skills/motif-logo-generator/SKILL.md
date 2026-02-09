---
name: motif-logo-generator
description: Generate publication-quality sequence logos for DNA or protein motifs
  to visualize conserved positions and sequence patterns.
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

# Motif Logo Generator

Generate sequence logos for DNA or protein motifs to visualize conserved positions.

## Installation

```bash
cd /Users/z04030865/.openclaw/workspace/skills/motif-logo-generator
pip install -r requirements.txt
```

Dependencies:
- `logomaker` - Generate publication-quality sequence logos
- `pandas` - Data manipulation for sequence alignment
- `numpy` - Numerical operations
- `matplotlib` - Visualization backend

## Quick Start

```bash
# Generate logo from FASTA file
python scripts/main.py --input sequences.fasta --output logo.png --type dna

# Generate logo from raw sequences
python scripts/main.py --sequences "ACGT\nACCT\nAGGT" --output logo.png --type dna

# Protein sequences with custom styling
python scripts/main.py --input proteins.fasta --output logo.pdf --type protein --title "Conserved Domain"
```

## Usage

### Python API

```python
from motif_logo_generator import generate_logo

# From file
logo = generate_logo(
    input_file="sequences.fasta",
    seq_type="dna",
    output_path="logo.png",
    title="My Motif"
)

# From sequences list
sequences = [
    "ACGTAGCT",
    "ACGTAGCT",
    "ACCTAGCT",
    "ACGTAGTT"
]
logo = generate_logo(
    sequences=sequences,
    seq_type="dna",
    output_path="logo.png"
)
```

### Command Line

```bash
python scripts/main.py [OPTIONS]

Required:
  --input PATH       Input FASTA file (or use --sequences)
  --sequences TEXT   Raw sequences separated by newline (or use --input)
  --output PATH      Output file path (.png, .pdf, .svg)

Optional:
  --type {dna,protein}   Sequence type (default: dna)
  --title TEXT           Logo title
  --width INT            Figure width in inches (default: 10)
  --height INT           Figure height in inches (default: 3)
  --colorscheme TEXT     Color scheme (default: classic)
                         DNA: classic, base_pairing
                         Protein: chemistry, hydrophobicity, classic
```

## Output

Generates a sequence logo showing:
- Letter height = information content (conservation)
- Letter stack = frequency at each position
- Y-axis: bits (information content) for DNA, or relative frequency for protein

## Example

Input (FASTA):
```
>seq1
ACGT
>seq2
ACGT
>seq3
ACCT
>seq4
AGGT
```

Output: Logo with position 2 showing C/G variability and other positions conserved.

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

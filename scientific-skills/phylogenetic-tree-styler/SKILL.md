---
name: phylogenetic-tree-styler
description: Beautify phylogenetic trees with taxonomy color blocks, bootstrap values,
  and timeline annotations. Supports Newick format with customizable styling options.
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

# Phylogenetic Tree Styler

## Features
Beautify phylogenetic trees, add taxonomy color blocks, Bootstrap values, and timelines.

## Usage

```bash
python3 scripts/main.py --input <input_tree.nwk> --output <output.png> [options]
```

### Parameters

| Parameter | Description | Default |
|------|------|--------|
| `-i`, `--input` | Input Newick format phylogenetic tree file | Required |
| `-o`, `--output` | Output image file path | tree_styled.png |
| `-f`, `--format` | Output format: png, pdf, svg | png |
| `-w`, `--width` | Image width (pixels) | 1200 |
| `-h`, `--height` | Image height (pixels) | 800 |
| `--show-bootstrap` | Show Bootstrap values | False |
| `--bootstrap-threshold` | Only show Bootstrap values above this threshold | 50 |
| `--taxonomy-file` | Species taxonomy information file (CSV format: name,domain,phylum,class,order,family,genus) | None |
| `--show-timeline` | Show timeline | False |
| `--root-age` | Root node age (million years ago) | None |
| `--branch-color` | Branch color | black |
| `--leaf-color` | Leaf node label color | black |

## Examples

### Basic Beautification
```bash
python3 scripts/main.py -i tree.nwk -o tree_basic.png
```

### Show Bootstrap Values
```bash
python3 scripts/main.py -i tree.nwk -o tree_bootstrap.png --show-bootstrap --bootstrap-threshold 70
```

### Add Taxonomy Color Blocks
```bash
python3 scripts/main.py -i tree.nwk -o tree_taxonomy.png --taxonomy-file taxonomy.csv
```

### Add Timeline
```bash
python3 scripts/main.py -i tree.nwk -o tree_timeline.png --show-timeline --root-age 500
```

### Comprehensive Usage
```bash
python3 scripts/main.py -i tree.nwk -o tree_full.png \
    --show-bootstrap --bootstrap-threshold 70 \
    --taxonomy-file taxonomy.csv \
    --show-timeline --root-age 500
```

## Taxonomy Information File Format

taxonomy.csv example:
```csv
name,domain,phylum,class
Species_A,Bacteria,Proteobacteria,Gammaproteobacteria
Species_B,Bacteria,Firmicutes,Bacilli
Species_C,Archaea,Euryarchaeota,Methanobacteria
```

## Dependencies

- Python 3.8+
- ete3
- matplotlib
- numpy
- pandas

Install dependencies:
```bash
pip install ete3 matplotlib numpy pandas
```

## Input Format

Supports standard Newick format (.nwk or .newick):
```
((A:0.1,B:0.2)95:0.3,(C:0.4,D:0.5)88:0.6);
```

Bootstrap values can be placed at node label positions (like the 95, 88 above).

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

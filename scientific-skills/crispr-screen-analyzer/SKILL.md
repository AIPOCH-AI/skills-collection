---
name: crispr-screen-analyzer
description: Process CRISPR screening data to identify essential genes
trigger: CRISPR, screen, MAGeCK, BAGEL, essential genes, analysis
tier: B
---

# CRISPR Screen Analyzer

Process CRISPR screening data to identify essential genes and hit candidates.

## Usage

```bash
python scripts/main.py --counts counts.txt --samples samplesheet.csv --output results/
```

## Parameters

- `--counts`: sgRNA count matrix
- `--samples`: Sample annotation file
- `--control`: Control sample names
- `--treatment`: Treatment sample names
- `--method`: Analysis method (MAGeCK/BAGEL/RRA)

## Analysis Features

- Quality control metrics
- Essential gene identification
- Hit candidate ranking
- Pathway enrichment
- Visualization

## Output

- Gene-level statistics
- sgRNA-level results
- Essential gene lists
- QC plots

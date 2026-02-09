---
name: volcano-plot-labeler
description: Automatically label top significant genes in volcano plots with repulsion
  algorithm
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

# Volcano Plot Labeler (ID: 148)

Automatically identify and label the Top 10 most significant genes in volcano plots using a repulsion algorithm to prevent label overlap.

## Features

- **Smart Gene Selection**: Automatically identifies the top 10 most significant genes based on p-value and fold change
- **Repulsion Algorithm**: Uses force-directed positioning to prevent text label overlap
- **Customizable**: Configurable thresholds, label styling, and positioning options
- **Multiple Output Formats**: PNG, PDF, SVG support

## Installation

```bash
pip install pandas matplotlib numpy scipy
```

## Usage

### Basic Usage

```python
from volcano_plot_labeler import label_volcano_plot
import pandas as pd

# Load your data
df = pd.read_csv('differential_expression_results.csv')

# Generate labeled volcano plot
fig = label_volcano_plot(
    df,
    log2fc_col='log2FoldChange',
    pvalue_col='padj',
    gene_col='gene_name',
    top_n=10
)
fig.savefig('volcano_plot_labeled.png', dpi=300, bbox_inches='tight')
```

### Advanced Usage

```python
from volcano_plot_labeler import label_volcano_plot

fig = label_volcano_plot(
    df,
    log2fc_col='log2FoldChange',
    pvalue_col='padj',
    gene_col='gene_name',
    top_n=10,
    pvalue_threshold=0.05,
    log2fc_threshold=1.0,
    figsize=(12, 10),
    repulsion_iterations=100,
    repulsion_force=0.05,
    label_fontsize=10,
    label_color='black',
    arrow_color='gray',
    save_path='output.png'
)
```

### Command Line Usage

```bash
python scripts/main.py \
    --input data/deseq2_results.csv \
    --output volcano_labeled.png \
    --log2fc-col log2FoldChange \
    --pvalue-col padj \
    --gene-col gene_name \
    --top-n 10
```

## Input Format

Expected CSV/TSV columns:
- `log2FoldChange`: Log2 fold change values
- `padj` or `pvalue`: Adjusted p-values or raw p-values
- `gene_name`: Gene identifiers

## Algorithm

### Significance Calculation
1. Calculate `-log10(pvalue)` for all genes
2. Rank genes by combined score: `|log2FC| * -log10(pvalue)`
3. Select top N genes with highest significance

### Repulsion Algorithm
1. **Initial Placement**: Place labels at gene coordinates
2. **Force Calculation**: 
   - Repulsive force between overlapping labels
   - Spring force pulling label toward its gene point
   - Boundary forces to keep labels within plot area
3. **Iterative Optimization**: Update positions for N iterations until convergence
4. **Arrow Drawing**: Draw connecting lines from labels to gene points

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | DataFrame | - | Input data |
| `log2fc_col` | str | 'log2FoldChange' | Column name for log2 fold change |
| `pvalue_col` | str | 'padj' | Column name for p-value |
| `gene_col` | str | 'gene_name' | Column name for gene names |
| `top_n` | int | 10 | Number of top genes to label |
| `pvalue_threshold` | float | 0.05 | P-value cutoff for coloring |
| `log2fc_threshold` | float | 1.0 | Log2FC cutoff for coloring |
| `repulsion_iterations` | int | 100 | Iterations for repulsion algorithm |
| `repulsion_force` | float | 0.05 | Strength of repulsion force |
| `label_fontsize` | int | 10 | Font size for labels |
| `figsize` | tuple | (10, 10) | Figure size |

## Output

- Labeled volcano plot with:
  - Color-coded points (up/down/not significant)
  - Top 10 gene labels with leader lines
  - No overlapping text labels

## License

MIT

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

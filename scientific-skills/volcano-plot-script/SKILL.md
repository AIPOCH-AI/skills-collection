---
name: volcano-plot-script
description: Generate R/Python code for volcano plots from DEG (Differentially Expressed Genes) analysis results. Triggered when user needs visualization of gene expression data, p-value vs fold-change scatter plots, publication-ready figures for bioinformatics analysis.
version: 1.0.0
category: Data Visualization
tags: [volcano-plot, bioinformatics, deg-analysis, r, python, visualization]
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: 
last_updated: 2026-02-06
---

# Volcano Plot Script Generator

A skill for generating publication-ready volcano plots from differential gene expression analysis results.

## Overview

Volcano plots visualize the relationship between statistical significance (p-values) and magnitude of change (fold changes) in gene expression data. This skill generates customizable R or Python scripts for creating high-quality figures suitable for publications.

## Use Cases

- Visualize RNA-seq DEG analysis results
- Identify significantly upregulated and downregulated genes
- Highlight genes of interest (markers, pathways)
- Generate publication-quality figures for manuscripts
- Compare multiple experimental conditions

## Input Requirements

Required input data format:
- Gene identifier (gene symbol or ENSEMBL ID)
- Log2 fold change values
- Adjusted or raw p-values
- Optional: gene annotations, pathways

## Output

- Publication-ready volcano plot (PNG/PDF/SVG)
- Customizable R or Python script
- Optional: labeled significant gene lists

## Usage

```python
# Example: Run the volcano plot generator
python scripts/main.py --input deg_results.csv --output volcano_plot.png
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input` | Path to DEG results CSV/TSV | required |
| `--output` | Output plot file path | volcano_plot.png |
| `--log2fc-col` | Column name for log2 fold change | log2FoldChange |
| `--pvalue-col` | Column name for p-value | padj |
| `--gene-col` | Column name for gene IDs | gene |
| `--log2fc-thresh` | Log2 FC threshold for significance | 1.0 |
| `--pvalue-thresh` | P-value threshold | 0.05 |
| `--label-genes` | File with genes to label | None |
| `--top-n` | Label top N significant genes | 10 |
| `--color-up` | Color for upregulated genes | #E74C3C |
| `--color-down` | Color for downregulated genes | #3498DB |
| `--color-ns` | Color for non-significant genes | #95A5A6 |

## Technical Difficulty

**Medium** - Requires understanding of:
- DEG analysis concepts (fold change, p-values, FDR)
- Data visualization principles
- Matplotlib/ggplot2 plotting libraries

## Dependencies

### Python
- pandas
- matplotlib
- seaborn
- numpy

### R
- ggplot2
- dplyr
- ggrepel (for label positioning)

## References

- [Example datasets and templates](references/)
- Best practices for volcano plot visualization
- Color schemes for accessibility

## Author

Auto-generated skill for bioinformatics visualization.

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output plots | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited (pandas, matplotlib, seaborn, numpy)

## Prerequisites

```bash
# Python dependencies
pip install pandas matplotlib seaborn numpy

# R dependencies (if using R)
install.packages(c("ggplot2", "dplyr", "ggrepel"))
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully generates executable Python/R script
- [ ] Output plot is publication-ready quality
- [ ] Correctly identifies significant genes based on thresholds
- [ ] Handles missing or malformed data gracefully
- [ ] Color scheme is accessible (colorblind-friendly)

### Test Cases
1. **Basic DEG Visualization**: Input standard DESeq2 results → Valid volcano plot
2. **Custom Thresholds**: Adjust log2FC and p-value thresholds → Correct gene classification
3. **Gene Labeling**: Specify genes to label → Labels appear correctly
4. **Large Dataset**: Input 20,000+ genes → Performance remains acceptable
5. **Malformed Data**: Input with missing values → Graceful error handling

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Add interactive plot option (Plotly)
  - Support for multiple comparison groups
  - Integration with pathway enrichment tools

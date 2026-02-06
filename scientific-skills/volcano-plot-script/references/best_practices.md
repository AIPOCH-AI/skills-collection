# Volcano Plot Best Practices

## Overview

Volcano plots are scatter plots that visualize differential gene expression results, showing the relationship between statistical significance and magnitude of change.

## Key Elements

### X-axis: Log2 Fold Change
- Represents the magnitude of change in gene expression
- Positive values = upregulation
- Negative values = downregulation
- Log2 scale: +1 = 2x increase, +2 = 4x increase, etc.

### Y-axis: -Log10 P-value
- Represents statistical significance
- Higher values = more significant
- Common thresholds: 0.05 (y=1.3), 0.01 (y=2), 0.001 (y=3)

## Interpretation

1. **Top-right quadrant**: Highly significant upregulated genes
2. **Top-left quadrant**: Highly significant downregulated genes
3. **Center-bottom**: Genes with no significant change
4. **Far left/right (low)**: Large fold changes but not statistically significant

## Best Practices

### Threshold Selection
- **Log2FC threshold**: Typically 0.5-1.0 (1.5x to 2x change)
- **P-value threshold**: Usually 0.05 (FDR-corrected recommended)

### Color Schemes
- Use colorblind-friendly palettes
- Clear distinction between up/down/non-significant
- Avoid red-green combinations (colorblindness)

### Labeling
- Label only key genes of interest
- Avoid cluttering with too many labels
- Use repelling algorithms for label placement

### Publication Quality
- High DPI (300+) for print
- Clear axis labels and titles
- Include sample size in caption
- Provide threshold values in methods

## Common Variations

1. **Enhanced volcano plots**: Add gene labels, annotations
2. **Interactive plots**: Hover for gene info (plotly)
3. **Multi-condition**: Faceted or overlay plots
4. **Pathway highlighting**: Color by pathway membership

## References

1. Cui X, Churchill GA. Statistical tests for differential expression in cDNA microarray experiments. Genome Biol. 2003;4(4):210.
2. Ritchie ME, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res. 2015;43(7):e47.
3. Blighe K, Rana S, Lewis M. EnhancedVolcano: publication-ready volcano plots with enhanced colouring and labeling. R/Bioconductor package.

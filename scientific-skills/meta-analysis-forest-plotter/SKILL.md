---
name: meta-analysis-forest-plotter
description: Generate forest plots for meta-analysis with R/Python code
version: 1.0.0
category: Data
---

# Meta-Analysis Forest Plotter

Create publication-quality forest plots for meta-analyses.

## Use Cases
- Systematic review visualization
- Meta-analysis publication
- Evidence synthesis reporting

## Parameters
- `studies`: Study data with OR/RR and CI
- `effect_measure`: OR, RR, or MD
- `subgroup`: Subgroup analysis variable (optional)

## Returns
- Forest plot code (R meta package)
- Funnel plot for publication bias
- Heterogeneity statistics (I²)

## Example
Input: 15 studies with OR and 95% CI
Output: Publication-ready forest plot with pooled estimate

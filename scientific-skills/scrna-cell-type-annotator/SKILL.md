---
name: scrna-cell-type-annotator
description: Auto-annotate cell clusters from single-cell RNA data using marker genes
version: 1.0.0
category: Bioinfo
---

# ScRNA Cell Type Annotator

Single-cell cluster identification.

## Use Cases
- Post-clustering annotation
- Novel cell type discovery
- Cross-study comparison
- Atlas construction

## Parameters
- `cluster_markers`: DEG per cluster
- `tissue_type`: Organ context
- `species`: Human/mouse

## Returns
- Cell type predictions
- Marker gene support
- Confidence levels
- Alternative suggestions

## Example
Cluster 1: IL2RA, CD3D → CD4 T cells

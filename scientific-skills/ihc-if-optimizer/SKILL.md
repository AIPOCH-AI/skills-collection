---
name: ihc-if-optimizer
description: Optimize IHC/IF protocols for specific tissues and antigens
version: 1.0.0
category: Wet Lab
---

# IHC/IF Optimizer

Immunostaining protocol optimization.

## Use Cases
- Brain tissue staining
- Liver antigen retrieval
- Antibody dilution optimization
- Fluorescence panel design

## Parameters
- `tissue_type`: Brain/Liver/Kidney/etc
- `antigen`: Target protein
- `detection_method`: IHC or IF

## Returns
- Recommended retrieval method
- Antibody dilutions
- Blocking conditions
- Counterstain suggestions

## Example
Brain tissue + Phospho-protein → Citrate retrieval, 1:200 antibody

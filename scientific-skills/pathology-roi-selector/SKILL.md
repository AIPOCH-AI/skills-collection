---
name: pathology-roi-selector
description: Auto-identify regions of interest in whole slide images
version: 1.0.0
category: Clinical
---

# Pathology ROI Selector

WSI region detection for AI training.

## Use Cases
- Tissue microarray creation
- AI model training data
- Pathology education
- Research sampling

## Parameters
- `wsi_file`: Whole slide image
- `tissue_type`: Tumor/normal
- `magnification`: 20x/40x

## Returns
- ROI coordinates
- Tissue percentage
- Quality metrics
- Export ready crops

## Example
Identify tumor-rich regions from 100K x 100K image

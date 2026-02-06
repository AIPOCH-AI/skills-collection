---
name: flow-panel-designer
description: Design multicolor flow cytometry panels minimizing spectral overlap
version: 1.0.0
category: Wet Lab
---

# Flow Panel Designer

Fluorophore selection optimizer.

## Use Cases
- Multicolor panel design (10+ colors)
- Compensation planning
- Marker-fluorophore matching
- Spectral flow setup

## Parameters
- `markers`: Target antigens
- `instrument`: Cytometer model
- `n_colors`: Number of fluorophores

## Returns
- Optimal fluorophore assignments
- Spillover predictions
- Compensation control list
- Panel validation checks

## Example
T-cell panel: CD3-BV421, CD4-FITC, CD8-PE...

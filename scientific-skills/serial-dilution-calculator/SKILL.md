---
name: serial-dilution-calculator
description: Generate qPCR/ELISA dilution protocols with precise pipetting steps
version: 1.0.0
category: Wet Lab
---

# Serial Dilution Calculator

Step-by-step dilution protocol generator.

## Use Cases
- qPCR standard curves
- ELISA plate setup
- Drug dose responses
- MIC determinations

## Parameters
- `starting_conc`: Stock concentration
- `final_conc`: Target concentration
- `dilution_factor`: Step dilution
- `total_volume`: Per well volume

## Returns
- Pipetting scheme table
- Required volumes
- Plate layout suggestion
- Common pitfall warnings

## Example
"Take 10uL stock + 90uL diluent for 1:10..."

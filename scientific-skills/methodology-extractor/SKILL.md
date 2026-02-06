---
name: methodology-extractor
description: Batch extraction of experimental methods from multiple papers for protocol comparison
version: 1.0.0
category: Research
---

# Methodology Extractor

Extract and compare experimental protocols across papers.

## Use Cases
- Protocol optimization
- Methods comparison for systematic reviews
- Reproducibility assessment

## Parameters
- `paper_ids`: List of papers to analyze
- `method_type`: Target method (e.g., "Western Blot", "qPCR")

## Returns
- Comparison table of protocols
- Parameter variations across studies
- Best practice recommendations

## Example
Input: 50 papers, method_type="Western Blot"
Output: Table showing antibody concentrations, blocking conditions, wash times

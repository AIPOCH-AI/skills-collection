---
name: sanger-chromatogram-qa
description: Quality check Sanger sequencing traces for mutations
version: 1.0.0
category: Wet Lab
---

# Sanger Chromatogram QA

Sequencing quality assessment.

## Use Cases
- Mutation verification
- Clone confirmation
- Genotyping QC
- SNP validation

## Parameters
- `ab1_file`: Chromatogram
- `expected_seq`: Reference
- `variant_pos`: Mutation site

## Returns
- Quality scores
- Mixed peak detection
- Variant confirmation
- Repeat recommendation

## Example
Flags heterozygous peak at position 234

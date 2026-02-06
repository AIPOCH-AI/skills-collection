---
name: primer-design-check
description: Check primers for dimers, hairpins, and off-target amplification
version: 1.0.0
category: Wet Lab
---

# Primer Design Check

In silico primer validation tool.

## Use Cases
- qPCR primer design
- Sequencing primer check
- Mutagenesis primer validation

## Parameters
- `forward_primer`: F sequence
- `reverse_primer`: R sequence
- `template`: Target genome (optional)

## Returns
- Dimer prediction
- Hairpin analysis
- Off-target BLAST results
- Tm and GC% calculations

## Example
Flags: Self-dimer detected at 3' end → redesign recommended

---
name: randomization-gen
description: Generate block randomization lists for RCTs
version: 1.0.0
category: Pharma
---

# Randomization Gen

RCT randomization table generator.

## Use Cases
- Clinical trial design
- Animal study randomization
- Blocked randomization
- Stratified allocation

## Parameters
- `n_subjects`: Total sample size
- `n_groups`: Number of arms
- `block_size`: Block size (multiple of n_groups)

## Returns
- Randomization sequence
- Block assignments
- Allocation concealment ready

## Example
Input: n=120, 3 groups, block=6
Output: Sealed randomization list

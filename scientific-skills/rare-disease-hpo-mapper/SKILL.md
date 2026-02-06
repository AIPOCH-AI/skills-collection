---
name: rare-disease-hpo-mapper
description: Map patient symptoms to Human Phenotype Ontology terms for gene diagnosis
version: 1.0.0
category: Clinical
---

# Rare Disease HPO Mapper

Clinical phenotype standardization tool.

## Use Cases
- Exome/genome analysis
- Rare disease diagnosis
- Genetic counseling
- Research cohort building

## Parameters
- `symptoms`: Clinical description
- `age_onset`: Pediatric/adult
- `inheritance_pattern`: AD/AR/XL

## Returns
- HPO term suggestions
- Confidence scores
- Differential diagnosis genes
- Literature links

## Example
"Wide-set eyes" → HP:0000316 (Hypertelorism)

---
name: variant-pathogenicity-predictor
description: Integrate REVEL, CADD, PolyPhen scores to predict variant pathogenicity
trigger: variant, pathogenicity, REVEL, CADD, PolyPhen, ACMG
tier: C
---

# Variant Pathogenicity Predictor

Integrate REVEL, CADD, PolyPhen and other scores to predict variant pathogenicity.

## Usage

```bash
python scripts/main.py --variant "chr17:43094692:G:A" --gene "BRCA1"
python scripts/main.py --vcf variants.vcf --output report.json
```

## Parameters

- `--variant`: Variant in format chr:pos:ref:alt
- `--vcf`: VCF file with variants
- `--gene`: Gene symbol
- `--scores`: Prediction scores to use (REVEL,CADD,PolyPhen)

## Integrated Scores

- REVEL (Rare Exome Variant Ensemble Learner)
- CADD (Combined Annotation Dependent Depletion)
- PolyPhen-2 (Polymorphism Phenotyping)
- SIFT (Sorting Intolerant From Tolerant)
- MutationTaster

## Output

- Pathogenicity classification
- ACMG guideline interpretation
- Individual score breakdown
- Confidence assessment

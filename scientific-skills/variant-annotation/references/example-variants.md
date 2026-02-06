# Example Variants for Testing

## Pathogenic Variants (High Confidence)

### BRCA1 - Breast Cancer
```json
{
  "variant": "rs80357410",
  "hgvs_cdna": "NM_007294.3:c.5096G>A",
  "hgvs_protein": "NP_009225.1:p.Arg1699Gln",
  "expected": "Pathogenic",
  "disease": "Hereditary breast and ovarian cancer syndrome"
}
```

### BRCA1 - Pathogenic Truncating
```json
{
  "variant": "rs80357775",
  "hgvs_cdna": "NM_007294.3:c.68_69delAG",
  "hgvs_protein": "NP_009225.1:p.Glu23ValfsTer17",
  "expected": "Pathogenic",
  "disease": "Hereditary breast and ovarian cancer syndrome"
}
```

### BRCA2 - Pathogenic
```json
{
  "variant": "rs80359550",
  "hgvs_cdna": "NM_000059.3:c.9097_9098delCC",
  "hgvs_protein": "NP_000050.1:p.Pro3033Ter",
  "expected": "Pathogenic",
  "disease": "Hereditary breast and ovarian cancer syndrome"
}
```

### CFTR - Cystic Fibrosis
```json
{
  "variant": "rs113993960",
  "hgvs_cdna": "NM_000492.3:c.1521_1523delCTT",
  "hgvs_protein": "NP_000483.3:p.Phe508del",
  "expected": "Pathogenic",
  "disease": "Cystic fibrosis"
}
```

### LDLR - Familial Hypercholesterolemia
```json
{
  "variant": "rs28942080",
  "hgvs_cdna": "NM_000527.4:c.2389G>A",
  "hgvs_protein": "NP_000518.1:p.Asp797Asn",
  "expected": "Pathogenic/Likely pathogenic",
  "disease": "Familial hypercholesterolemia"
}
```

## Benign Variants

### Common SNP
```json
{
  "variant": "rs1801133",
  "gene": "MTHFR",
  "hgvs_cdna": "NM_005957.4:c.665C>T",
  "hgvs_protein": "NP_005948.3:p.Ala222Val",
  "expected": "Benign/Likely benign",
  "note": "Common polymorphism, high frequency in populations"
}
```

### Benign BRCA1 Variant
```json
{
  "variant": "rs80356920",
  "gene": "BRCA1",
  "hgvs_cdna": "NM_007294.3:c.2311T>C",
  "hgvs_protein": "NP_009225.1:p.Ser771Pro",
  "expected": "Benign",
  "note": "Common variant, no disease association"
}
```

## Variants of Uncertain Significance (VUS)

### BRCA2 VUS
```json
{
  "variant": "rs80358872",
  "gene": "BRCA2",
  "hgvs_cdna": "NM_000059.3:c.8754+3A>G",
  "expected": "Uncertain significance",
  "note": "Intronic variant with insufficient evidence"
}
```

### SCN5A VUS
```json
{
  "variant": "rs199473101",
  "gene": "SCN5A",
  "hgvs_cdna": "NM_198056.2:c.1855G>A",
  "hgvs_protein": "NP_932173.1:p.Ala619Thr",
  "expected": "Uncertain significance",
  "note": "Possible association with Brugada syndrome"
}
```

## Test Queries for Validation

### Single Query Tests
```
# rsID
rs80357410
rs113993960
rs1801133

# HGVS cDNA
NM_007294.3:c.5096G>A
NM_000492.3:c.1521_1523delCTT

# Genomic coordinates
chr17:43094692:G>A
chr7:117199563:GTT>G

# Gene:AA format
BRCA1:R1699Q
CFTR:F508del
```

### Batch Test File
```
# Pathogenic variants
rs80357410
rs113993960
rs80359550

# Benign variants
rs1801133
rs80356920

# VUS
rs80358872
rs199473101
```

## Expected Output Examples

### Pathogenic Output (BRCA1 p.R1699Q)
```json
{
  "variant_id": "rs80357410",
  "gene": "BRCA1",
  "chromosome": "17",
  "position": 43094692,
  "clinical_significance": "Pathogenic",
  "acmg": {
    "classification": "Pathogenic",
    "criteria": ["PS4", "PM1", "PM2", "PP2", "PP3", "PP5"],
    "score": 13.0
  },
  "interpretation_summary": "Variant in BRCA1 gene has Pathogenic clinical significance in ClinVar. ACMG classification: Pathogenic. Associated with: Hereditary breast and ovarian cancer syndrome"
}
```

## Edge Cases

### Novel Variant (Not in ClinVar)
```
chr1:123456:A>T
Expected: Not found in ClinVar, minimal or no data returned
```

### Large Deletion
```
NM_000314.6:c.1010_1045del36
Expected: Partial deletion annotation
```

### Synonymous Variant
```
NM_007294.3:c.435G>A (p.Pro145Pro)
Expected: Likely benign, check for splicing impact
```

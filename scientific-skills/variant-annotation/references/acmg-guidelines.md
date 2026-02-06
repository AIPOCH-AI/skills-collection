# ACMG/AMP Guidelines for Variant Classification

## Reference
Richards S, Aziz N, Bale S, et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genet Med. 2015;17(5):405-424.

DOI: 10.1038/gim.2015.30

## Overview

The ACMG/AMP guidelines provide a framework for interpreting sequence variants in clinical genetic testing. Variants are classified into five categories based on available evidence.

## Classification Categories

| Classification | Definition |
|----------------|------------|
| **Pathogenic** | Very strong evidence of causing disease |
| **Likely Pathogenic** | Strong evidence of causing disease |
| **Uncertain Significance (VUS)** | Insufficient or conflicting evidence |
| **Likely Benign** | Strong evidence of not causing disease |
| **Benign** | Very strong evidence of not causing disease |

## Evidence Criteria

### Very Strong Pathogenic (PVS)
- **PVS1**: Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multiexon deletion) in a gene where LOF is a known mechanism of disease

### Strong Pathogenic (PS)
- **PS1**: Same amino acid change as a previously established pathogenic variant regardless of nucleotide change
- **PS2**: De novo (both maternity and paternity confirmed) in a patient with the disease and no family history
- **PS3**: Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product
- **PS4**: The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls

### Moderate Pathogenic (PM)
- **PM1**: Located in a mutational hot spot and/or critical and well-established functional domain without benign variation
- **PM2**: Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes, or ExAC
- **PM3**: For recessive disorders, detected in trans with a pathogenic variant
- **PM4**: Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants
- **PM5**: Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before
- **PM6**: Assumed de novo, but without confirmation of paternity and maternity

### Supporting Pathogenic (PP)
- **PP1**: Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease
- **PP2**: Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease
- **PP3**: Multiple lines of computational evidence support a deleterious effect on the gene or gene product
- **PP4**: Patient's phenotype or family history is highly specific for a disease with a single genetic etiology
- **PP5**: Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation

### Stand-Alone Benign (BA)
- **BA1**: Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes, or ExAC

### Strong Benign (BS)
- **BS1**: Allele frequency is greater than expected for disorder
- **BS2**: Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder with full penetrance expected at an early age
- **BS3**: Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing
- **BS4**: Lack of segregation in affected members of a family

### Supporting Benign (BP)
- **BP1**: Missense variant in a gene for which primarily truncating variants are known to cause disease
- **BP2**: Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern
- **BP3**: In-frame deletions/insertions in a repetitive region without a known function
- **BP4**: Multiple lines of computational evidence suggest no impact on gene or gene product
- **BP5**: Variant found in a case with an alternate molecular basis for disease
- **BP6**: Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation
- **BP7**: A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved

## Combining Evidence

| Classification | Rule |
|----------------|------|
| **Pathogenic** | (i) 1 Very Strong (PVS1) AND (a) ≥1 Strong (PS) OR (b) ≥2 Moderate (PM) OR (c) 1 Moderate (PM) AND 1 Supporting (PP) OR (d) ≥2 Supporting (PP); OR (ii) ≥2 Strong (PS) |
| **Likely Pathogenic** | (i) 1 Very Strong (PVS1) AND 1 Moderate (PM) OR (ii) 1 Strong (PS) AND (a) ≥1 Moderate (PM) OR (b) ≥2 Supporting (PP) OR (iii) ≥2 Moderate (PM) OR (iv) 1 Moderate (PM) AND ≥2 Supporting (PP) |
| **Likely Benign** | (i) Strong (BS1–BS4) AND Supporting (BP1–BP7) OR (ii) ≥2 Supporting (BP1–BP7) |
| **Benign** | 1 Stand-alone (BA1) OR ≥2 Strong (BS1–BS4) |

## Scoring Implementation

For computational implementation, a weighted scoring system can be used:

| Evidence Level | Weight |
|----------------|--------|
| PVS1 | +8 |
| PS1–PS4 | +4 |
| PM1–PM6 | +2 |
| PP1–PP5 | +1 |
| BA1 | -8 |
| BS1–BS4 | -4 |
| BP1–BP7 | -1 |

**Score Thresholds:**
- Pathogenic: ≥ 10
- Likely Pathogenic: 6–9
- Uncertain Significance: 0–5
- Likely Benign: -5 to -1
- Benign: ≤ -6

## Important Notes

1. **PS4 exception**: The OR must be calculated using appropriate statistical methods (e.g., Fisher's exact test)
2. **PM2 exception**: May be used for very rare variants (MAF < 0.005%) even in the presence of phenocopies
3. **BS2 exception**: Adult-onset conditions may have reduced penetrance; exercise caution
4. **PP3/PP4**: Must be used cautiously; verify with functional studies when possible

## Updates and Modifications

- 2018: Sequence Variant Interpretation (SVI) Working Group recommendations for PP2/BP1, PS2/PM6, and PVS1
- 2020: Recommendations for TP53, PTEN, and mismatch repair gene variants
- 2023: Continued refinement of criteria for specific genes and variant types

## Resources

- ACMG Standards and Guidelines: https://www.acmg.net/PDFLibrary/Standards-Guidelines-for-Interpretation-of-Sequence-Variants.pdf
- ClinGen Variant Curation Expert Panels: https://clinicalgenome.org/working-groups/variant-curation-expert-panels/
- InterVar: http://wintervar.wglab.org/
- Varsome: https://varsome.com/about-acmg-annotations

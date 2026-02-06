# Efficiency Benchmarks

## Benchmark Datasets

### 1. Doench 2014 Dataset

**Size**: 1,841 gRNAs targeting human CD33, CD13, and GFP genes

**Cell Lines**: HL-60, KBM-7, K562

**Readout**: Flow cytometry (knockout efficiency)

**Key Findings**:
- GC content optimal range: 40-60%
- Position 20 (NGG-proximal) prefers G
- Poly-T tracts reduce efficiency

### 2. Doench 2016 Dataset

**Size**: 2,389 gRNAs across 9 genes

**Improvements**:
- Multiple cell types (A375, K562, iPSC)
- Diverse genomic contexts
- Higher throughput screening

**Performance Metrics**:
- Top 5% guides: >80% cutting efficiency
- Bottom 20% guides: <10% efficiency
- Score threshold for "high activity": >0.6

### 3. Wang 2014 (Dropout Screens)

**Publication**: Wang T et al., "Genetic screens in human cells using the CRISPR-Cas9 system", Science 2014

**Method**: Genome-scale knockout screens

**Cell Lines**: A375, KBM7, K562, Raji, Jiyoye

**Validation**: 6,000+ gRNAs with deep sequencing

### 4. Hart 2015 (Pan-Cancer)

**Publication**: Hart T et al., "High-Resolution CRISPR Screens Reveal Fitness Genes and Genotype-Specific Cancer Liabilities", Cell 2015

**Focus**: Essential genes across cancer types

**Cell Lines**: 12 cancer cell lines

## Performance Statistics

### Efficiency Distribution

```
Efficiency Range    |  Percentage of Guides
--------------------|----------------------
> 80% (High)        |  15%
60-80% (Good)       |  25%
40-60% (Moderate)   |  30%
20-40% (Low)        |  20%
< 20% (Poor)        |  10%
```

### GC Content Impact

| GC Content | Average Efficiency | Success Rate (>50%) |
|------------|-------------------|---------------------|
| < 30%      | 22%               | 12%                 |
| 30-40%     | 45%               | 35%                 |
| 40-60%     | 68%               | 62%                 |
| 60-70%     | 52%               | 48%                 |
| > 70%      | 31%               | 25%                 |

### Position-Specific Effects

| Position | Nucleotide | Efficiency Boost |
|----------|------------|------------------|
| 20       | G          | +15%             |
| 19       | C          | +12%             |
| 18       | G          | +8%              |
| 1-3      | G          | -5% (penalty)    |

## Cas9 Variant Performance

### SpCas9 Variants

| Variant | On-Target | Off-Target | Best Use Case |
|---------|-----------|------------|---------------|
| SpCas9 (WT) | 100% | Baseline | General use |
| SpCas9-HF1 | 85% | 30% | High specificity |
| eSpCas9 | 90% | 40% | Balanced |
| HypaCas9 | 95% | 50% | Moderate specificity |
| Sniper-Cas9 | 95% | 45% | HDR applications |

### xCas9 & SpCas9-NG

| PAM | Variant | Efficiency vs NGG |
|-----|---------|-------------------|
| NGN | xCas9 | 70% |
| NG | SpCas9-NG | 85% |
| NAA | xCas9 | 60% |
| NAG | xCas9 | 65% |

## Predictive Model Performance

### Correlation with Empirical Data

| Model | Pearson r | Spearman ρ | RMSE |
|-------|-----------|------------|------|
| Doench '14 | 0.58 | 0.61 | 0.28 |
| Doench '16 | 0.71 | 0.74 | 0.22 |
| DeepCRISPR | 0.82 | 0.85 | 0.16 |
| CRISPRon | 0.75 | 0.78 | 0.19 |
| Azimuth | 0.72 | 0.75 | 0.21 |

### AUROC for High-Efficiency Prediction

| Model | AUROC | Optimal Threshold |
|-------|-------|-------------------|
| Doench '16 | 0.78 | 0.55 |
| DeepCRISPR | 0.86 | 0.60 |
| CRISPRon | 0.81 | 0.58 |
| Azimuth | 0.79 | 0.56 |

## Experimental Validation Rates

### Top-Ranked Guides (Top 5 by Score)

| Model | Success Rate (>50% efficiency) |
|-------|-------------------------------|
| Random Selection | 35% |
| Doench '16 | 72% |
| DeepCRISPR | 85% |
| Combined Score | 88% |

### Bottom-Ranked Guides (Bottom 20% by Score)

| Model | Success Rate |
|-------|-------------|
| Doench '16 | 12% |
| DeepCRISPR | 8% |

## Cell Type Effects

### Efficiency Variation by Cell Type

| Cell Type | Average Efficiency | Key Factors |
|-----------|-------------------|-------------|
| K562 | 65% | High Cas9 expression |
| HEK293T | 60% | Good transfection |
| iPSC | 45% | Variable Cas9 |
| Primary T cells | 40% | Hard to transfect |
| Neurons | 35% | Post-mitotic, delivery |

### Chromatin Accessibility Impact

| Chromatin State | Efficiency Multiplier |
|-----------------|----------------------|
| Open (DNase+) | 1.0x (baseline) |
| Closed (H3K9me3+) | 0.3-0.5x |
| Promoter | 1.2x |
| Enhancer | 1.1x |

## Guide RNA Design Rules

### High-Efficiency Guide Checklist

- [ ] GC content: 40-60%
- [ ] No Poly-T (>3 consecutive T's)
- [ ] Position 20: G preferred
- [ ] Position 19: C preferred
- [ ] No strong secondary structure (ΔG > -5 kcal/mol)
- [ ] Avoid runs of 4+ same nucleotide
- [ ] Check for common SNPs in target

### Low-Efficiency Red Flags

1. GC < 30% or > 70%
2. Homopolymer runs (AAAA, GGGG)
3. Position 20 = A or T
4. Predicted hairpin structure
5. Targeting repeat regions
6. Multiple mismatches in seed region

## Cost-Benefit Analysis

| Validation Level | Cost per Guide | Prediction Confidence |
|------------------|----------------|----------------------|
| In silico only | $0 | 60% |
| In vitro (Digenome) | $50 | 80% |
| In vivo (GUIDE-seq) | $500 | 95% |
| Functional test | $200 | 100% |

## Recommendations

1. **Initial Design**: Use DeepCRISPR for top candidates
2. **Library Construction**: Use Doench '16 for speed
3. **Critical Applications**: Validate with GUIDE-seq
4. **High-Throughput**: Accept 70% in silico prediction accuracy

## References

1. Doench JG et al. (2014) Nature Biotechnology 32:1262-1267
2. Doench JG et al. (2016) Nature Biotechnology 34:184-191
3. Wang T et al. (2014) Science 343:80-84
4. Hart T et al. (2015) Cell 163:1515-1526
5. Chuai G et al. (2018) Genome Biology 19:80

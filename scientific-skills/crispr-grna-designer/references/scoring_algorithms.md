# CRISPR Scoring Algorithms Reference

## Overview

This document summarizes the key algorithms for predicting gRNA efficiency and specificity.

## On-Target Efficiency Prediction

### 1. Doench et al. 2014 (Azimuth/Rule Set 2)

**Publication**: Doench et al., "Rational design of highly active sgRNAs for CRISPR-Cas9-mediated gene inactivation", Nature Biotechnology 2014

**Features Used**:
- Position-specific nucleotide preferences (20 positions)
- Melting temperature of guide RNA
- GC content
- Self-complementary structure
- Position-dependent dinucleotide features

**Performance**: ~0.6 Pearson correlation with empirical data

**Implementation Notes**:
```python
score = intercept + sum(position_weights[i] * features[i])
```

### 2. Doench et al. 2016 (Rule Set 3)

**Improvements**:
- L2-regularized logistic regression
- Trained on larger dataset (n=2,389)
- Includes chromatin accessibility features

**Performance**: ~0.71 Pearson correlation

### 3. DeepCRISPR

**Publication**: Chuai et al., "DeepCRISPR: optimized CRISPR guide RNA design by deep learning", Genome Biology 2018

**Architecture**:
- Convolutional Neural Network (CNN)
- Hybrid input: sequence + epigenetic features
- 5 convolutional layers + 2 fully connected layers

**Features**:
- One-hot encoded sequence (20bp)
- Chromatin accessibility (DNase-seq)
- Histone modifications (H3K4me3, H3K27ac)

**Performance**: ~0.86 AUROC

### 4. CRISPRon

**Publication**: Hsu et al., "CRISPRon: a logistic regression model for predicting gRNA activity"

**Key Innovation**: Accounts for chromatin state and DNA accessibility

**Input Features**:
- Guide sequence (20mer + PAM)
- Chromatin accessibility (ATAC-seq/DNase-seq)
- DNA methylation levels

### 5. Elevation (Microsoft Research)

**Publication**: Listgarten et al., "Prediction of off-target activities for the end-to-end design of CRISPR guide RNAs"

**Two-stage model**:
1. **Elevation-AGG**: Predicts activity of all guides
2. **Elevation-CFD**: Predicts off-target effects

## Off-Target Prediction

### 1. CFD (Cutting Frequency Determination)

**Method**: Quantifies effect of each mismatch position on cleavage frequency

**Key Insight**: Mismatches near PAM (seed region) have greater impact

**Calculation**:
```
CFD_score = product(mismatch_penalties[position])
```

**Position weights**:
- Positions 18-20 (PAM-proximal): High penalty (0.1-0.2 per mismatch)
- Positions 1-12 (PAM-distal): Lower penalty (0.5-0.8 per mismatch)

### 2. MIT Score

**Publication**: Hsu et al., "DNA targeting specificity of RNA-guided Cas9 nucleases", Nature Biotechnology 2013

**Formula**:
```
score = 1 / (1 + exp(-(intercept + sum(mismatch_scores))))
```

**Limitation**: Doesn't account for chromatin context

### 3. CCTop

**Publication**: Stemmer et al., "CCTop: An intuitive, flexible and reliable CRISPR/Cas9 target prediction tool"

**Features**:
- Mismatch position weighting
- Seed region emphasis (positions 12-20)
- Bulge RNA/DNA handling

### 4. CRISPOR

**Publication**: Concordet & Haeussler, "CRISPOR: intuitive guide selection for CRISPR/Cas9 genome editing experiments and screens"

**Integration**:
- Multiple efficiency scores (Doench '16, Moreno-Mateos, etc.)
- Off-target prediction with genome alignment
- Common SNP annotation

## Comparison Table

| Algorithm | Type | Correlation | Speed | Chromatin | Best For |
|-----------|------|-------------|-------|-----------|----------|
| Doench '14 | Linear | 0.60 | Fast | No | Quick screening |
| Doench '16 | Logistic | 0.71 | Fast | No | General use |
| DeepCRISPR | CNN | 0.86 | Slow | Yes | High-accuracy |
| CRISPRon | Logistic | 0.75 | Medium | Yes | Cell-specific |
| Azimuth | Regression | 0.72 | Fast | No | Python pipelines |

## Position-Specific Scoring Matrices

### Nucleotide Preferences (Doench '16)

| Position | G | A | C | T |
|----------|---|---|---|---|
| 20 (PAM-prox) | +0.20 | -0.10 | -0.05 | -0.05 |
| 19 | +0.10 | -0.05 | +0.15 | -0.10 |
| 18 | +0.15 | -0.05 | +0.05 | -0.05 |
| 1-17 | See full matrix | | | |

### Mismatch Penalties (CFD)

| Position | Weight |
|----------|--------|
| 20 | 0.10 |
| 19 | 0.15 |
| 18 | 0.20 |
| 17 | 0.25 |
| 16 | 0.30 |
| 15-13 | 0.40 |
| 12-1 | 0.60 |

## Recommendations

1. **Screening Phase**: Use Doench '16 for speed
2. **Validation Phase**: Use DeepCRISPR for top candidates
3. **Off-target**: Always use CFD or CCTop scoring
4. **Cell-specific**: Include chromatin data when available

## References

1. Doench JG et al. (2014) Nature Biotechnology 32:1262-1267
2. Doench JG et al. (2016) Nature Biotechnology 34:184-191
3. Chuai G et al. (2018) Genome Biology 19:80
4. Hsu PD et al. (2013) Nature Biotechnology 31:827-832
5. Listgarten J et al. (2018) Nature Biomedical Engineering 2:38-47

# Off-Target Databases

## Validated Off-Target Datasets

### 1. GUIDE-seq

**Method**: Genome-wide, unbiased identification of DSBs enabled by sequencing

**Publication**: Tsai et al., "GUIDE-seq enables genome-wide profiling of off-target cleavage by CRISPR-Cas nucleases", Nature Biotechnology 2014

**Key Features**:
- dsODN integration at DSB sites
- Detects DSBs with >0.1% frequency
- Gold standard for off-target validation

**Datasets**:
- `guide_seq_human_hg38.bed`: 50+ cell lines, 1,200+ guides
- `guide_seq_mouse_mm10.bed`: mESC, MEF datasets

**Access**: https://github.com/tsailabSJ/guideseq

### 2. Digenome-seq

**Method**: In vitro Cas9 digestion + whole-genome sequencing

**Publication**: Kim et al., "Digenome-seq: genome-wide profiling of CRISPR-Cas9 off-target effects in human cells", Nature Methods 2015

**Advantages**:
- Cell-free system (no cloning bias)
- Detects low-frequency off-targets
- Cost-effective for pre-screening

**Limitations**:
- May miss chromatin-protected sites
- In vitro may not reflect in vivo activity

### 3. CIRCLE-seq

**Method**: Circularization for in vitro reporting of CLeavage Effects by sequencing

**Publication**: Tsai et al., "CIRCLE-seq: a highly sensitive in vitro method for genome-wide identification of CRISPR-Cas9 off-targets", Nature Protocols 2018

**Improvement over Digenome-seq**:
- Higher sensitivity (detects 0.01% frequency)
- Reduced background noise
- Validation rate >90%

### 4. SITE-seq

**Method**: Selective enrichment and profiling of target Edges by sequencing

**Publication**: Cameron et al., "Mapping the genomic landscape of CRISPR-Cas9 cleavage", Nature Methods 2017

## Computational Databases

### 1. Cas-OFFinder

**Publication**: Bae et al., "Cas-OFFinder: a fast and versatile algorithm that searches for potential off-target sites of Cas9 RNA-guided endonucleases"

**Features**:
- Supports bulge sequences (DNA/RNA bulges)
- Multiple PAM sequences
- GPU acceleration available

**URL**: http://www.rgenome.net/cas-offinder/

### 2. CHOPCHOP Database

**URL**: https://chopchop.cbu.uib.no/

**Pre-computed**:
- Human (hg19/hg38)
- Mouse (mm9/mm10)
- Zebrafish (danRer10/11)

### 3. GT-Scan

**Features**:
- Whole-genome off-target analysis
- GPU-accelerated search
- Visual genome browser integration

## Off-Target Annotation

### Genomic Context Classification

| Category | Definition | Risk Level |
|----------|------------|------------|
| Exonic | Within protein-coding exon | HIGH |
| Intronic | Within gene intron | MEDIUM |
| UTR | 5' or 3' UTR | MEDIUM |
| Promoter | <2kb from TSS | HIGH |
| Intergenic | No known gene feature | LOW |
| Repeat | In transposable element | LOW |

### Population Variation

**gnomAD Integration**:
- Filter common SNPs near target site
- Flag guides targeting polymorphic regions
- Population-specific allele frequencies

**ClinVar Overlap**:
- Off-targets in pathogenic variant regions
- Disease-associated genes

## Benchmark Results

### Off-Target Detection Sensitivity

| Method | Detection Limit | False Positive Rate | Cost |
|--------|-----------------|---------------------|------|
| GUIDE-seq | 0.1% | <5% | $$$$ |
| Digenome-seq | 0.01% | ~15% | $$$ |
| CIRCLE-seq | 0.001% | <10% | $$$ |
| SITE-seq | 0.05% | ~8% | $$$ |
| WGS | 0.5% | ~20% | $$$$$ |

### Computational Prediction Accuracy

| Tool | Precision | Recall | F1 Score |
|------|-----------|--------|----------|
| CFD | 0.45 | 0.72 | 0.55 |
| MIT | 0.38 | 0.65 | 0.48 |
| CCTop | 0.52 | 0.68 | 0.59 |
| CRISPOR | 0.55 | 0.70 | 0.62 |

## Data Files in This Directory

```
references/off_target_databases/
├── guide_seq/
│   ├── human_hg38_guides.bed
│   ├── mouse_mm10_guides.bed
│   └── metadata.json
├── digenome_seq/
│   └── digenome_benchmarks.tsv
├── cfd_scores/
│   ├── mismatch_penalties.csv
│   └── pam_scores.csv
└── gnomad/
    └── common_variants_flanking_sgrnas.vcf
```

## Recommended Workflow

1. **In Silico Screen**: Use CFD/CCTop to filter high-risk guides
2. **In Vitro Validation**: Digenome-seq or CIRCLE-seq for top candidates
3. **In Vivo Confirmation**: GUIDE-seq in target cell type
4. **Functional Test**: Amplicon sequencing at predicted off-target sites

## Key Insights

1. **Seed Region Critical**: Mismatches in positions 12-20 often tolerated
2. **PAM Proximity**: Position 20 (NGG) most sensitive to mismatch
3. **Chromatin Effect**: Off-targets in open chromatin more likely active
4. **Cell Type Matters**: Same guide can have different off-targets in different cells

## References

1. Tsai SQ et al. (2014) Nature Biotechnology 32:687-697
2. Kim D et al. (2015) Nature Methods 12:237-243
3. Tsai SQ et al. (2017) Nature Protocols 12:551-567
4. Bae S et al. (2014) Bioinformatics 30:1473-1475
5. Cameron P et al. (2017) Nature Methods 14:600-606

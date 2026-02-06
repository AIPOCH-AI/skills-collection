---
name: microbiome-diversity-reporter
description: Interpret Alpha and Beta diversity metrics from 16S rRNA sequencing results and generate visualization reports for microbiome analysis.
---

# Microbiome Diversity Reporter

---

## Overview

This tool is used to analyze and interpret diversity metrics in microbiome 16S rRNA sequencing data, including:

- **Alpha Diversity**: Species diversity within a single sample
- **Beta Diversity**: Species composition differences between samples

---

## Usage

### Command Line

```bash
# Analyze Alpha diversity for a single sample
python scripts/main.py --input otu_table.tsv --metric shannon --output alpha_report.html

# Analyze Beta diversity (PCoA)
python scripts/main.py --input otu_table.tsv --beta --metadata metadata.tsv --output beta_report.html

# Generate full report (Alpha + Beta)
python scripts/main.py --input otu_table.tsv --full --metadata metadata.tsv --output diversity_report.html
```

### Parameter Description

| Parameter | Description | Required |
|------|------|------|
| `--input` | OTU/ASV table path (TSV format) | Yes |
| `--metadata` | Sample metadata (TSV format) | Required for Beta diversity |
| `--metric` | Alpha diversity metric: shannon, simpson, chao1, observed_otus | No (default: shannon) |
| `--alpha` | Calculate Alpha diversity only | No |
| `--beta` | Calculate Beta diversity only | No |
| `--full` | Generate full report (Alpha + Beta) | No |
| `--output` | Output report path | No (default: stdout) |
| `--format` | Output format: html, json, markdown | No (default: html) |

---

## Input Format

### OTU Table (TSV)
```
#OTU ID	Sample1	Sample2	Sample3
OTU_1	100	50	200
OTU_2	50	100	0
OTU_3	25	25	50
```

### Metadata (TSV)
```
SampleID	Group	Age	Gender
Sample1	Control	25	M
Sample2	Treatment	30	F
Sample3	Treatment	28	M
```

---

## Output

Generates HTML/JSON/Markdown reports containing:

1. **Alpha Diversity Results**
   - Diversity index values
   - Rarefaction curves
   - Box plots (by group)

2. **Beta Diversity Results**
   - PCoA scatter plots
   - NMDS plots
   - Distance matrix heatmaps
   - PERMANOVA statistical tests

3. **Statistical Summary**
   - Sample information statistics
   - Species richness
   - Diversity index distribution

---

## Dependencies

- Python 3.8+
- numpy
- pandas
- scipy
- scikit-bio
- matplotlib
- seaborn
- plotly (for interactive charts)

---

## Example Output

```json
{
  "alpha_diversity": {
    "shannon": {
      "Sample1": 2.45,
      "Sample2": 1.89,
      "Sample3": 2.12
    },
    "statistics": {
      "mean": 2.15,
      "std": 0.28
    }
  },
  "beta_diversity": {
    "method": "braycurtis",
    "pcoa": {
      "variance_explained": [0.45, 0.25, 0.15]
    }
  }
}
```

---

## References

1. Shannon, C.E. (1948) A mathematical theory of communication
2. Simpson, E.H. (1949) Measurement of diversity
3. Chao, A. (1984) Non-parametric estimation of classes
4. Lozupone et al. (2005) UniFrac: a phylogenetic metric

---
name: circos-plot-generator
description: Generate Circos plots for genomics data visualization, including genomic variations and cell-cell communication networks
---

# Circos Plot Generator

Generate Circos plots for genomics data visualization, including genomic variations and cell-cell communication networks.

## Overview

This skill simplifies the creation of Circos plots by generating complex configuration files automatically. It supports:
- Genomic variation visualization (SNPs, CNVs, structural variants)
- Cell-cell communication networks
- Chromosome ideograms with custom annotations
- Link tracks for showing connections

## Usage

```bash
# Generate a basic Circos configuration
python scripts/main.py --config config.yaml --output ./output/

# Generate from CSV data
python scripts/main.py --data data.csv --type variation --output ./output/

# Generate cell-cell communication plot
python scripts/main.py --data cell_comm.csv --type cell-comm --output ./output/
```

## Input Formats

### Genomic Variation Data (CSV)
```csv
chrom,start,end,type,value
chr1,1000000,2000000,SNP,0.5
chr2,500000,1500000,CNV,-0.8
```

### Cell-Cell Communication Data (CSV)
```csv
source,target,weight,type
CellType_A,CellType_B,0.8,Ligand-Receptor
CellType_B,CellType_C,0.6,Secreted
```

## Output

Generates:
- `circos.conf` - Main configuration file
- `data/` - Data files for tracks
- `circos.png` / `circos.svg` - Rendered plot (if Circos is installed)

## Dependencies

- Python 3.8+
- Optional: Circos (for rendering)
  - Installation: `conda install -c bioconda circos`

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--type` | Plot type: `variation`, `cell-comm`, `custom` | `variation` |
| `--title` | Plot title | `Circos Plot` |
| `--width` | Image width | 800 |
| `--height` | Image height | 800 |
| `--color-scheme` | Color scheme name | `default` |

## Examples

### Example 1: Genomic Variations
```bash
python scripts/main.py \
  --data variants.csv \
  --type variation \
  --title "Sample Variations" \
  --output ./plots/
```

### Example 2: Cell Communication
```bash
python scripts/main.py \
  --data cell_chat.csv \
  --type cell-comm \
  --title "Cell Interactions" \
  --color-scheme nature \
  --output ./cell_plots/
```

## Customization

Create a YAML config file for advanced customization:

```yaml
title: My Custom Plot
type: variation
chromosomes:
  - name: chr1
    size: 248956422
  - name: chr2
    size: 242193529
tracks:
  - type: histogram
    file: data.tsv
    color: blue
  - type: link
    file: links.tsv
    color: red
```

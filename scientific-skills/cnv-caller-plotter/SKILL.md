---
name: cnv-caller-plotter
description: Call copy number variations from WGS data and generate genome-wide CNV plots
trigger: cnv, copy number, wgs, genome
tier: C
---

# CNV Caller & Plotter

Detect copy number variations from whole genome sequencing data and visualize genome-wide copy number profiles.

## Usage

```bash
python scripts/main.py --input sample.bam --reference hg38.fa --output cnv_results/
```

## Parameters

- `--input`: BAM or VCF file path
- `--reference`: Reference genome FASTA
- `--output`: Output directory
- `--bin-size`: Bin size for segmentation (default: 1000)
- `--plot-format`: Output plot format (png/pdf/svg)

## Output

- CNV calls (BED format)
- Genome-wide copy number plot
- Segment summary statistics

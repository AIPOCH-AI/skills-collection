---
name: metagenomic-krona-chart
description: Generate interactive Krona charts (sunburst plots) for metagenomic samples to visualize taxonomic abundance hierarchies. Supports Kraken2, Bracken, Centrifuge output formats.
---

# Metagenomic Krona Chart

## Function Description

Generate interactive sunburst charts (Krona Chart) to display taxonomic abundance hierarchies in metagenomic samples. Supports parsing data from common classification tool outputs such as Kraken2, Bracken, and Centrifuge, and generates interactive HTML visualization charts.

## Output Example

```
skills/metagenomic-krona-chart/
├── SKILL.md
├── scripts/
│   └── main.py
├── example/
│   ├── input.tsv
│   └── output.html
└── README.md
```

## Usage

### Basic Usage

```bash
python scripts/main.py -i input.tsv -o krona_chart.html
```

### Parameter Description

| Parameter | Description | Default Value |
|------|------|--------|
| `-i, --input` | Input file path (TSV format) | Required |
| `-o, --output` | Output HTML file path | krona_chart.html |
| `-t, --type` | Input format type (kraken2/bracken/custom) | auto |
| `--max-depth` | Maximum display hierarchy depth | 7 |
| `--min-percent` | Minimum display percentage threshold | 0.01 |
| `--title` | Chart title | Metagenomic Krona Chart |

### Input Format

#### Kraken2/Bracken Report Format
```
100.00  1000000 0   U   0   unclassified
 99.00  990000  0   R   1   root
 95.00  950000  0   D   2   Bacteria
 50.00  500000  0   P   1234    Proteobacteria
...
```

#### Custom Format (TSV)
```
taxon_id	name	rank	parent_id	reads	percent
2	Bacteria	domain	1	950000	95.0
1234	Proteobacteria	phylum	2	500000	50.0
```

## Dependency Requirements

- Python 3.8+
- plotly >= 5.0.0
- pandas >= 1.3.0

```bash
pip install plotly pandas
```

## Output Features

- Interactive sunburst chart with zoom and click support
- Color-coded different taxonomic levels
- Hover to display detailed information (reads, percentage)
- Center displays total reads
- Responsive design, adapts to different screens

## Notes

1. Input files need to contain taxonomic hierarchy information
2. For large datasets, use `--min-percent` to filter low-abundance taxa
3. Output is a standalone HTML file that can be viewed offline

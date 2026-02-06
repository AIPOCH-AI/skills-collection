---
name: phylogenetic-tree-styler
description: Beautify phylogenetic trees with taxonomy color blocks, bootstrap values, and timeline annotations. Supports Newick format with customizable styling options.
---

# Phylogenetic Tree Styler

## Features
Beautify phylogenetic trees, add taxonomy color blocks, Bootstrap values, and timelines.

## Usage

```bash
python3 scripts/main.py --input <input_tree.nwk> --output <output.png> [options]
```

### Parameters

| Parameter | Description | Default |
|------|------|--------|
| `-i`, `--input` | Input Newick format phylogenetic tree file | Required |
| `-o`, `--output` | Output image file path | tree_styled.png |
| `-f`, `--format` | Output format: png, pdf, svg | png |
| `-w`, `--width` | Image width (pixels) | 1200 |
| `-h`, `--height` | Image height (pixels) | 800 |
| `--show-bootstrap` | Show Bootstrap values | False |
| `--bootstrap-threshold` | Only show Bootstrap values above this threshold | 50 |
| `--taxonomy-file` | Species taxonomy information file (CSV format: name,domain,phylum,class,order,family,genus) | None |
| `--show-timeline` | Show timeline | False |
| `--root-age` | Root node age (million years ago) | None |
| `--branch-color` | Branch color | black |
| `--leaf-color` | Leaf node label color | black |

## Examples

### Basic Beautification
```bash
python3 scripts/main.py -i tree.nwk -o tree_basic.png
```

### Show Bootstrap Values
```bash
python3 scripts/main.py -i tree.nwk -o tree_bootstrap.png --show-bootstrap --bootstrap-threshold 70
```

### Add Taxonomy Color Blocks
```bash
python3 scripts/main.py -i tree.nwk -o tree_taxonomy.png --taxonomy-file taxonomy.csv
```

### Add Timeline
```bash
python3 scripts/main.py -i tree.nwk -o tree_timeline.png --show-timeline --root-age 500
```

### Comprehensive Usage
```bash
python3 scripts/main.py -i tree.nwk -o tree_full.png \
    --show-bootstrap --bootstrap-threshold 70 \
    --taxonomy-file taxonomy.csv \
    --show-timeline --root-age 500
```

## Taxonomy Information File Format

taxonomy.csv example:
```csv
name,domain,phylum,class
Species_A,Bacteria,Proteobacteria,Gammaproteobacteria
Species_B,Bacteria,Firmicutes,Bacilli
Species_C,Archaea,Euryarchaeota,Methanobacteria
```

## Dependencies

- Python 3.8+
- ete3
- matplotlib
- numpy
- pandas

Install dependencies:
```bash
pip install ete3 matplotlib numpy pandas
```

## Input Format

Supports standard Newick format (.nwk or .newick):
```
((A:0.1,B:0.2)95:0.3,(C:0.4,D:0.5)88:0.6);
```

Bootstrap values can be placed at node label positions (like the 95, 88 above).

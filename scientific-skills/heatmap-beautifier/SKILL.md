---
name: heatmap-beautifier
description: Professional heatmap beautification tool with automatic clustering and
  annotation tracks
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Heatmap Beautifier

ID: 147

Professional beautification tool for gene expression heatmaps, automatically adds clustering trees, color annotation tracks, and intelligently optimizes label layout.

## Features

- **Automatic Clustering**: Automatically adds row/column clustering trees based on hierarchical clustering
- **Annotation Tracks**: Supports multiple color annotation tracks (sample grouping, gene classification, etc.)
- **Smart Labels**: Automatically calculates optimal font size to avoid row/column label overlap
- **Flexible Color Schemes**: Built-in multiple professional scientific research color schemes
- **Export Options**: Supports PDF, PNG, SVG, and other formats

## Dependency Installation

```bash
pip install seaborn matplotlib scipy pandas numpy
```

## Usage

### Basic Usage

```python
from skills.heatmap_beautifier.scripts.main import HeatmapBeautifier

# Initialize
hb = HeatmapBeautifier()

# Load data and generate heatmap
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap.pdf"
)
```

### Heatmap with Annotation Tracks

```python
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap_annotated.pdf",
    # Row annotations (gene classification)
    row_annotations={
        "Gene Type": gene_type_dict,  # {"gene1": "Kinase", "gene2": "Transcription Factor", ...}
        "Pathway": pathway_dict
    },
    # Column annotations (sample grouping)
    col_annotations={
        "Condition": condition_dict,  # {"sample1": "Control", "sample2": "Treatment", ...}
        "Time": time_dict
    },
    # Custom colors
    annotation_colors={
        "Condition": {"Control": "#2ecc71", "Treatment": "#e74c3c"},
        "Gene Type": {"Kinase": "#3498db", "Transcription Factor": "#9b59b6"}
    }
)
```

### Full Parameter Example

```python
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap.pdf",
    title="Gene Expression Heatmap",
    cmap="RdBu_r",                    # Color map
    center=0,                         # Color center value
    vmin=-2, vmax=2,                  # Value range
    row_cluster=True,                 # Row clustering
    col_cluster=True,                 # Column clustering
    standard_scale=None,              # Standardization: "row", "col", None
    z_score=None,                     # Z-score: 0 (row), 1 (col), None
    # Label optimization
    max_row_label_fontsize=10,
    max_col_label_fontsize=10,
    rotate_col_labels=45,             # Column label rotation angle
    hide_row_labels=False,
    hide_col_labels=False,
    # Size
    figsize=(12, 10),
    dpi=300
)
```

## Input Data Format

### Expression Matrix (CSV)

```csv
,sample1,sample2,sample3,sample4
Gene_A,2.5,-1.2,0.8,-0.5
Gene_B,-0.8,1.5,-2.1,0.3
Gene_C,1.2,0.5,-0.7,1.8
...
```

- First column: Gene names (row index)
- First row: Sample names (column names)
- Data: Expression values (e.g., log2 fold change, TPM, FPKM, etc.)

### Annotation File Format

Annotation dictionary format: `{item_name: category_value}`

Example:
```python
condition_dict = {
    "sample1": "Control",
    "sample2": "Control", 
    "sample3": "Treatment",
    "sample4": "Treatment"
}
```

## Color Schemes

Built-in color schemes:
- `"RdBu_r"` - Red-Blue (classic differential expression)
- `"viridis"` - Yellow-Purple (continuous data)
- `"RdYlBu_r"` - Red-Yellow-Blue
- `"coolwarm"` - Cool-Warm
- `"seismic"` - Seismic
- `"bwr"` - Blue-White-Red

## Command Line Usage

```bash
# Basic usage
python -m skills.heatmap_beautifier.scripts.main \
    --input expression_matrix.csv \
    --output heatmap.pdf

# With clustering and annotations
python -m skills.heatmap_beautifier.scripts.main \
    --input expression_matrix.csv \
    --output heatmap.pdf \
    --row-cluster \
    --col-cluster \
    --row-annotations row_annot.json \
    --col-annotations col_annot.json \
    --title "Gene Expression"
```

## Output Description

Generated heatmap includes:
1. **Main Heatmap**: Expression matrix visualization
2. **Left Clustering Tree**: Row (gene) hierarchical clustering
3. **Top Clustering Tree**: Column (sample) hierarchical clustering  
4. **Left Annotation Bar**: Row annotations (e.g., gene types)
5. **Top Annotation Bar**: Column annotations (e.g., sample groups)
6. **Color Scale**: Color bar corresponding to expression values

## Notes

1. **Data Preprocessing**: It is recommended to perform log2 transformation or standardization on data first
2. **Memory Usage**: Large datasets (>5000 rows) may take longer
3. **Label Visibility**: When there are too many rows/columns, some labels will be automatically hidden
4. **Clustering Distance**: Default uses Euclidean distance and Ward method

## Author

Bioinformatics Visualization Team

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

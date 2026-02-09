---
name: spatial-transcriptomics-mapper
description: Map spatial transcriptomics data from 10x Genomics Visium/Xenium onto
  tissue images
version: 1.0.0
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Spatial Transcriptomics Mapper (ID: 196)

## Description

Spatial Transcriptomics analysis tool for processing 10x Genomics Visium or Xenium data, projecting gene expression data back onto tissue section images to draw "gene-space" distribution maps. Supports gene expression visualization, spatial clustering analysis, and morphological feature correlation.

## Features

- **Visium Data Processing**: Supports Space Ranger output (filtered_feature_bc_matrix.h5, spatial/tissue_positions_list.csv, spatial/tissue_lowres_image.png)
- **Xenium Data Processing**: Supports Xenium Explorer output (.h5, transcripts.parquet, nucleus_boundaries.parquet)
- **Gene Expression Mapping**: Projects expression of specified genes onto tissue images
- **Spatial Clustering Visualization**: Displays spatial distribution of Seurat/Scanpy clustering results
- **Multi-gene Joint Analysis**: Supports combined visualization of multiple genes
- **High-resolution Output**: Supports high-resolution image export

## Installation

```bash
# Required dependencies
pip install scanpy squidpy matplotlib seaborn pillow numpy pandas h5py

# Optional: For Xenium data processing
pip install pyarrow dask

# Optional: For advanced image processing
pip install opencv-python scikit-image
```

## Quick Start - Test Data

Generate sample Visium data to test the tool:

```bash
# Generate test data
python scripts/generate_test_data.py \
  --platform visium \
  --output ./test_data/visium_sample \
  --n-spots 500 \
  --n-genes 1000

# Run analysis on test data
python scripts/main.py \
  --platform visium \
  --data-dir ./test_data/visium_sample \
  --gene GENE_0000 \
  --output ./test_output/
```

## Usage

### Basic - Visium Data

```bash
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/spaceranger/outs/ \
  --gene PIK3CA \
  --output ./output/
```

### Basic - Xenium Data

```bash
python scripts/main.py \
  --platform xenium \
  --data-dir /path/to/xenium/outs/ \
  --gene PIK3CA \
  --output ./output/
```

### Multiple Genes

```bash
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --genes PIK3CA,PTEN,EGFR \
  --mode overlay \
  --output ./output/
```

### With Clustering Results

```bash
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --cluster-file ./clusters.csv \
  --output ./output/
```

## Input File Structure

### Visium (Space Ranger output)
```
outs/
├── filtered_feature_bc_matrix.h5    # Gene expression matrix
├── raw_feature_bc_matrix.h5         # Raw counts (optional)
├── spatial/
│   ├── tissue_positions_list.csv    # Spot positions
│   ├── tissue_lowres_image.png      # Low-res H&E image
│   ├── tissue_hires_image.png       # High-res H&E image
│   └── scalefactors_json.json       # Scale factors
└── web_summary.html
```

### Xenium
```
outs/
├── cell_feature_matrix.h5           # Cell x gene matrix
├── transcripts.parquet              # Transcript coordinates
├── nucleus_boundaries.parquet       # Cell boundaries
├── cell_boundaries.parquet
├── morphology_focus.ome.tif         # Morphology image
└── experiment.xenium
```

## Output Files

- `{gene}_spatial_map.png`: Single gene spatial expression map
- `{gene}_heatmap.png`: Gene expression heatmap
- `multi_gene_overlay.png`: Multi-gene overlay map (if using --mode overlay)
- `cluster_spatial_map.png`: Cluster spatial distribution map
- `combined_report.html`: Comprehensive HTML report

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--platform` | str | required | Platform type: visium or xenium |
| `--data-dir` | str | required | Data directory path |
| `--gene` | str | optional | Single gene name |
| `--genes` | list | optional | Multiple genes, comma-separated |
| `--mode` | str | single | Mode: single/overlay/multi |
| `--cluster-file` | str | optional | Clustering result CSV file path |
| `--output` | str | ./output | Output directory |
| `--dpi` | int | 300 | Output image DPI |
| `--cmap` | str | viridis | Color map scheme |
| `--spot-size` | float | 1.0 | Visium spot size factor |
| `--alpha` | float | 0.8 | Transparency (0-1) |
| `--min-count` | int | 0 | Minimum expression filter |
| --crop | str | optional | Crop region (x1,y1,x2,y2) |

## Examples

### Example 1: Single Gene Visualization
```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./visium_sample/outs/ \
  --gene EPCAM \
  --cmap Reds \
  --output ./results/
```

### Example 2: Tumor Marker Combination
```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./breast_cancer/outs/ \
  --genes PIK3CA,ERBB2,ESR1,PGR \
  --mode multi \
  --cmap plasma \
  --output ./tumor_markers/
```

### Example 3: Xenium Subcellular Resolution
```bash
python scripts/main.py \
  --platform xenium \
  --data-dir ./xenium_lung/outs/ \
  --genes SFTPB,SFTPC,SCGB1A1 \
  --dpi 600 \
  --output ./xenium_results/
```

### Example 4: Spatial Clustering Visualization
```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./sample/outs/ \
  --cluster-file ./seurat_clusters.csv \
  --output ./clusters/
```

## API Usage

```python
from skills.spatial_transcriptomics_mapper.scripts.main import SpatialMapper

# Initialize
mapper = SpatialMapper(
    platform="visium",
    data_dir="/path/to/data",
    output_dir="./output"
)

# Load data
mapper.load_data()

# Plot single gene
mapper.plot_gene_spatial(
    gene="PIK3CA",
    cmap="viridis",
    save_path="./output/pik3ca.png"
)

# Plot multiple genes
mapper.plot_multi_genes(
    genes=["PIK3CA", "PTEN", "EGFR"],
    mode="grid",
    save_path="./output/multi.png"
)

# Get spatial statistics
stats = mapper.get_spatial_stats(gene="PIK3CA")
```

## Notes

- Visium data uses low-resolution images by default to improve processing speed, can use --hires parameter to enable high resolution
- For large Xenium datasets, it is recommended to use --crop parameter to specify region of interest
- Color map reference: https://matplotlib.org/stable/tutorials/colors/colormaps.html
- For large samples, consider using --downsample parameter to reduce resolution

## References

- 10x Genomics Visium: https://www.10xgenomics.com/products/spatial-gene-expression
- 10x Genomics Xenium: https://www.10xgenomics.com/platforms/xenium
- Scanpy: https://scanpy.readthedocs.io/
- Squidpy: https://squidpy.readthedocs.io/

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

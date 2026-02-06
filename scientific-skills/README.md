# Pseudotime Trajectory Visualization

Visualize single-cell developmental trajectories showing how cells differentiate from stem cells to mature cells.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate example data (optional)
python examples/generate_example_data.py example_data.h5ad

# Run analysis
python scripts/main.py --input example_data.h5ad --output ./results

# With specific parameters
python scripts/main.py \
    --input data.h5ad \
    --start-cell-type Stem \
    --method diffusion \
    --genes SOX2,NANOG,POU5F1 \
    --plot-genes \
    --output ./results
```

## Features

- **Diffusion Pseudotime (DPT)**: Robust trajectory inference using diffusion maps
- **PAGA**: Partition-based graph abstraction for trajectory visualization
- **Gene Expression Trends**: Track marker gene expression along pseudotime
- **Lineage Assignment**: Automatic or user-defined lineage branching
- **Publication-Ready Plots**: High-resolution figures in multiple formats

## Output Files

```
results/
├── trajectory_plot.png           # Main trajectory visualization
├── paga_graph.png                # PAGA connectivity graph (if method=paga)
├── gene_expression_heatmap.png   # Gene dynamics heatmap
├── gene_trends/
│   ├── SOX2_trend.png           # Individual gene plots
│   └── ...
├── pseudotime_values.csv         # Cell-level pseudotime data
├── analysis_report.json          # Analysis metadata
└── trajectory_data.h5ad          # Updated AnnData object
```

## Input Data Format

The tool expects a preprocessed AnnData (.h5ad) file:

```python
import scanpy as sc

# Load your data
adata = sc.read_h5ad('your_data.h5ad')

# Required annotations:
# - adata.obs['leiden'] or other cluster labels
# - adata.obs['cell_type'] (optional, for root detection)

# Preprocessing steps (if not done):
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)

# Save for analysis
adata.write('preprocessed_data.h5ad')
```

## Command Line Options

```
--input, -i              Input AnnData file (required)
--output, -o             Output directory (default: ./trajectory_output)
--embedding              Embedding for viz: umap, tsne, pca, diffmap (default: umap)
--method                 Trajectory method: diffusion, paga (default: diffusion)
--start-cell             Root cell ID for trajectory origin
--start-cell-type        Cell type to use as starting point
--n-lineages             Expected number of lineage branches
--cluster-key            Column name for clusters (default: leiden)
--cell-type-key          Column name for cell types (default: cell_type)
--genes                  Comma-separated gene names to plot
--plot-genes             Generate gene expression plots
--format                 Output format: png, pdf, svg (default: png)
--dpi                    Figure resolution (default: 300)
```

## Examples

### Basic Usage
```bash
python scripts/main.py --input data.h5ad --output ./results
```

### Specify Root Cell Type
```bash
python scripts/main.py \
    --input data.h5ad \
    --start-cell-type "Progenitor" \
    --output ./results
```

### Visualize Marker Genes
```bash
python scripts/main.py \
    --input data.h5ad \
    --genes SOX2,OCT4,NANOG,NESTIN \
    --plot-genes \
    --output ./results
```

### Use PAGA Method
```bash
python scripts/main.py \
    --input data.h5ad \
    --method paga \
    --embedding umap \
    --output ./results
```

### Generate PDF Figures
```bash
python scripts/main.py \
    --input data.h5ad \
    --format pdf \
    --dpi 600 \
    --output ./results
```

## Troubleshooting

**Issue**: "No root cell detected"  
**Solution**: Specify `--start-cell` or `--start-cell-type` explicitly

**Issue**: Memory error with large datasets  
**Solution**: Subsample cells or increase system RAM

**Issue**: Trajectory doesn't match biology  
**Solution**: Verify root cell selection and try different methods

## References

- Haghverdi et al. (2016) - Diffusion pseudotime robustly reconstructs lineage branching
- Wolf et al. (2019) - PAGA: graph abstraction reconciles clustering with trajectory inference

## License

MIT License

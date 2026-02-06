---
name: pseudotime-trajectory-viz
description: Visualize single-cell developmental trajectories (pseudotime) to show
  how cells differentiate from stem cells to mature cells. Includes trajectory inference,
  pseudotime calculation, and publication-ready visualizations.
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Pseudotime Trajectory Visualization

Visualize single-cell developmental trajectories showing cellular differentiation processes using pseudotime analysis.

## Function

- Infer developmental trajectories from single-cell RNA-seq data
- Calculate pseudotime values representing cellular differentiation progress
- Visualize trajectory trees and lineage branching
- Overlay gene expression dynamics along pseudotime
- Identify lineage-specific marker genes
- Generate publication-ready trajectory plots

## Technical Difficulty

**High** - Requires understanding of single-cell analysis, dimensionality reduction, trajectory inference algorithms, and Python visualization libraries.

## Usage

```bash
# Basic trajectory analysis from AnnData file
python scripts/main.py --input data.h5ad --output ./results

# Specify starting cells and lineage inference method
python scripts/main.py --input data.h5ad --start-cell stem_cell_cluster --method diffusion --output ./results

# Visualize specific gene expression along trajectories
python scripts/main.py --input data.h5ad --genes SOX2,OCT4,NANOG --plot-genes --output ./results

# Full analysis with custom parameters
python scripts/main.py --input data.h5ad \
    --embedding umap \
    --method slingshot \
    --start-cell-type progenitor \
    --n-lineages 3 \
    --genes MARKER1,MARKER2,MARKER3 \
    --output ./results \
    --format pdf
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | path | required | Input AnnData (.h5ad) file path |
| `--output` | path | ./trajectory_output | Output directory for results |
| `--embedding` | enum | umap | Embedding for visualization: `umap`, `tsne`, `pca`, `diffmap` |
| `--method` | enum | diffusion | Trajectory inference: `diffusion`, `slingshot`, `paga`, `palantir` |
| `--start-cell` | string | auto | Root cell ID or cluster name for trajectory origin |
| `--start-cell-type` | string | - | Cell type annotation to use as starting point |
| `--n-lineages` | int | auto | Number of expected lineage branches |
| `--cluster-key` | string | leiden | AnnData obs key for cell clusters |
| `--cell-type-key` | string | cell_type | AnnData obs key for cell type annotations |
| `--genes` | string | - | Comma-separated gene names to plot along pseudotime |
| `--plot-genes` | flag | false | Generate gene expression heatmaps along trajectories |
| `--plot-branch` | flag | true | Show lineage branch probabilities |
| `--format` | enum | png | Output format: `png`, `pdf`, `svg` |
| `--dpi` | int | 300 | Figure resolution |
| `--n-pcs` | int | 30 | Number of principal components for analysis |
| `--n-neighbors` | int | 15 | Number of neighbors for graph construction |
| `--diffmap-components` | int | 5 | Number of diffusion components to compute |

## Input Format

Required AnnData (.h5ad) structure:
```
AnnData object with n_obs × n_vars = n_cells × n_genes
    obs: 'leiden', 'cell_type'  # Cluster and cell type annotations
    var: 'highly_variable'       # Highly variable gene marker
    obsm: 'X_umap', 'X_pca'      # Pre-computed embeddings (optional)
    layers: 'spliced', 'unspliced'  # For RNA velocity (optional)
```

## Output Files

```
output_directory/
├── trajectory_plot.{format}          # Main trajectory visualization
├── pseudotime_distribution.{format}  # Pseudotime value distribution
├── lineage_tree.{format}             # Branching lineage structure
├── gene_expression_heatmap.{format}  # Gene dynamics heatmap (if --plot-genes)
├── gene_trends/
│   ├── {gene_name}_trend.{format}    # Individual gene expression trends
│   └── ...
├── pseudotime_values.csv             # Cell-level pseudotime values
├── lineage_assignments.csv           # Cell lineage assignments
└── analysis_report.json              # Analysis parameters and statistics
```

## Output Format Example

### analysis_report.json
```json
{
  "analysis_date": "2026-02-06T06:00:00",
  "method": "diffusion",
  "n_cells": 5000,
  "n_lineages": 3,
  "root_cell": "cell_1234",
  "pseudotime_range": [0.0, 1.0],
  "lineages": {
    "lineage_1": {
      "cell_count": 1500,
      "terminal_state": "mature_type_A",
      "mean_pseudotime": 0.75
    },
    "lineage_2": {
      "cell_count": 1200,
      "terminal_state": "mature_type_B",
      "mean_pseudotime": 0.68
    }
  }
}
```

### pseudotime_values.csv
```csv
cell_id,cluster,cell_type,pseudotime,lineage,branch_probability
cell_001,0,progenitor,0.05,lineage_1,0.95
cell_002,1,intermediate,0.42,lineage_1,0.88
...
```

## Dependencies

- Python 3.9+
- `scanpy>=1.9.0` - Single-cell analysis framework
- `scvelo>=0.2.5` - RNA velocity analysis
- `palantir` - Trajectory inference and pseudotime
- `scikit-learn` - Dimensionality reduction and clustering
- `matplotlib>=3.5.0` - Plotting
- `seaborn` - Statistical visualization
- `pandas`, `numpy` - Data manipulation
- `anndata` - Single-cell data structure

Optional:
- `slingshot` (R) via `rpy2` - Alternative trajectory method

## Implementation Notes

1. **Preprocessing**: Assumes input data is already normalized and log-transformed
2. **Root Detection**: If start cell not specified, uses cell cycle or marker gene expression to infer progenitors
3. **Diffusion Pseudotime**: Default method using diffusion maps for robust trajectory inference
4. **Palantir**: Used for soft lineage assignments and fate probability estimation
5. **Memory**: Large datasets (>50k cells) may require 16GB+ RAM

## Methods

### Diffusion Pseudotime (DPT)
- Uses diffusion maps to capture non-linear cell relationships
- Robust to noise and dataset size
- Good for complex branching trajectories

### Slingshot
- Principal curve-based approach
- Simultaneous inference of multiple lineages
- Requires R installation with rpy2 bridge

### PAGA (Partition-based Graph Abstraction)
- Connects clusters based on transcriptome similarity
- Provides coarse-grained trajectory overview
- Fast and scalable

### Palantir
- Diffusion-based fate probability estimation
- Soft lineage assignments
- Best for fate bias analysis

## Limitations

- Requires high-quality single-cell data with good cell type coverage
- Assumes differentiation is the main source of variation
- May not capture rare transitional states with few cells
- Circular or cyclic processes not well represented by linear pseudotime
- RNA velocity requires spliced/unspliced counts in AnnData layers

## Safety & Best Practices

- **Validate trajectories** with known marker genes and biological knowledge
- **Multiple methods** recommended for critical analyses
- **Batch effects** should be corrected before trajectory inference
- **Cell cycle** effects may confound differentiation trajectories
- **Do not overinterpret** precise pseudotime values as absolute time

## Example Workflow

```python
# Preprocess data with scanpy (before using this tool)
import scanpy as sc

adata = sc.read_h5ad('raw_data.h5ad')
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)
adata.write('data.h5ad')

# Then run this skill
# python scripts/main.py --input data.h5ad --start-cell-type progenitor
```

## References

- Haghverdi et al. (2016) - Diffusion pseudotime
- Street et al. (2018) - Slingshot
- Wolf et al. (2019) - PAGA
- Setty et al. (2019) - Palantir
- La Manno et al. (2018) - RNA velocity

## Version

- Created: 2026-02-06
- Status: Functional
- Version: 1.0.0

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

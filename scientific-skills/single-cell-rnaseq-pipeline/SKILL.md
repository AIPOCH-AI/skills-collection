---
name: single-cell-rnaseq-pipeline
description: Generate single-cell RNA-seq analysis code templates for Seurat and Scanpy,
  supporting QC, clustering, visualization, and downstream analysis. Trigger when
  users need scRNA-seq analysis pipelines, preprocessing workflows, or batch correction
  code.
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

# Single-Cell RNA-seq Pipeline

## Overview

Generate comprehensive single-cell RNA-seq analysis code templates for **Seurat (R)** and **Scanpy (Python)**. This skill provides ready-to-use code frameworks for preprocessing, quality control, normalization, clustering, marker identification, visualization, and advanced analyses like batch correction and trajectory inference.

**Technical Difficulty**: High

## When to Use

- Building scRNA-seq analysis pipelines from raw count matrices
- Need standardized QC and preprocessing workflows
- Performing batch correction across multiple samples/datasets
- Running dimensionality reduction and clustering
- Identifying cell type-specific marker genes
- Creating publication-ready visualizations (UMAP, violin plots, heatmaps)
- Conducting trajectory inference (pseudotime analysis)
- Comparing cell populations between conditions

## Core Features

### Seurat (R) Templates
1. **Data Loading**: 10x Genomics, H5AD, Cell Ranger outputs
2. **QC Metrics**: Mitochondrial content, gene counts, doublet detection
3. **Normalization**: Log-normalization, SCTransform
4. **Integration**: Harmony, RPCA, CCA for batch correction
5. **Clustering**: Graph-based clustering with optimization
6. **Visualization**: UMAP, t-SNE, feature plots, dot plots
7. **Marker Analysis**: Wilcoxon tests, conserved markers
8. **Differential Expression**: FindAllMarkers, FindConservedMarkers
9. **Cell Typing**: Reference-based annotation with SingleR/Azimuth

### Scanpy (Python) Templates
1. **Data Loading**: AnnData, 10x, CSV, loom files
2. **QC Workflow**: Comprehensive filtering and metrics
3. **Normalization**: Log1p, scran, Combat batch correction
4. **Integration**: scVI, Scanorama, BBKNN
5. **Clustering**: Leiden/Louvain with resolution sweep
6. **Visualization**: UMAP, PAGA, embeddings
7. **Marker Analysis**: rank_genes_groups, filter markers
8. **Trajectory**: PAGA, diffusion pseudotime (DPT)
9. **CellChat/CellPhoneDB**: Cell-cell communication

## Usage

### Generate Seurat Template

```bash
python scripts/main.py --tool seurat --output seurat_analysis.R --species human
```

### Generate Scanpy Template

```bash
python scripts/main.py --tool scanpy --output scanpy_analysis.py --species mouse
```

### Generate Both Templates

```bash
python scripts/main.py --tool both --output scrna_pipeline --species human --batch-correction harmony --trajectory true
```

### Command-Line Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --tool | string | Yes | Analysis tool: `seurat`, `scanpy`, or `both` |
| --output | string | Yes | Output file or directory path |
| --species | string | No | Species: `human` or `mouse` (default: human) |
| --batch-correction | string | No | Method: `harmony`, `rpca`, `cca`, `scanorama`, `scvi` |
| --trajectory | bool | No | Include trajectory analysis (default: false) |
| --cell-communication | bool | No | Include cell-cell communication (default: false) |
| --de-analysis | bool | No | Include differential expression (default: false) |
| --spatial | bool | No | Include spatial transcriptomics (default: false) |

## Output Structure

```
output/
├── seurat/
│   ├── 01_load_and_qc.R
│   ├── 02_normalize_integrate.R
│   ├── 03_cluster_annotate.R
│   ├── 04_visualize.R
│   └── 05_de_analysis.R (if --de-analysis)
├── scanpy/
│   ├── 01_load_qc.py
│   ├── 02_normalize_integrate.py
│   ├── 03_cluster_annotate.py
│   ├── 04_visualize.py
│   └── 05_trajectory.py (if --trajectory)
└── README.md
```

## Technical Details

### Supported Input Formats
- 10x Genomics Cell Ranger outputs (barcodes.tsv, features.tsv, matrix.mtx)
- H5AD (AnnData h5 format)
- Seurat RDS objects
- CSV/TSV count matrices
- HDF5 files

### QC Parameters (Default)
| Metric | Human | Mouse |
|--------|-------|-------|
| min_genes | 200 | 200 |
| max_genes | 25000 | 25000 |
| min_cells | 3 | 3 |
| max_mt_percent | 20% | 20% |
| doublet_threshold | Auto | Auto |

### Clustering Resolution Guidelines
- **0.4-0.6**: Broad cell types
- **0.8-1.2**: Subtypes
- **1.5-2.0**: Fine populations

### Batch Correction Recommendations
| Scenario | Seurat | Scanpy |
|----------|--------|--------|
| Small batches (<5) | Harmony | Harmony |
| Large batches | RPCA | Scanorama |
| Complex variation | CCA | scVI |

## Code Examples

### Seurat Quick Start

```r
# Load data
seurat_obj <- CreateSeuratObject(counts = raw_data, project = "Sample")

# QC
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")
seurat_obj <- subset(seurat_obj, subset = nFeature_RNA > 200 & percent.mt < 20)

# Normalize
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = "vst", nfeatures = 2000)

# Scale and PCA
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))

# Cluster
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = 1.0)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = "umap", label = TRUE)
FeaturePlot(seurat_obj, features = c("CD3E", "CD14", "CD79A"))
```

### Scanpy Quick Start

```python
import scanpy as sc

# Load data
adata = sc.read_10x_mtx("filtered_gene_bc_matrices/")

# QC
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20, :]

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA and UMAP
sc.pp.scale(adata)
sc.tl.pca(adata, svd_solver='arpack')
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=1.0)

# Visualize
sc.pl.umap(adata, color=['leiden', 'total_counts'])
sc.pl.dotplot(adata, var_names=['CD3E', 'CD14', 'CD79A'], groupby='leiden')
```

## References

- `references/seurat_template.R` - Complete Seurat analysis template
- `references/scanpy_template.py` - Complete Scanpy analysis template
- `references/batch_correction_guide.md` - Batch correction comparison
- `requirements.txt` - Python dependencies

## Dependencies

### Seurat (R)
```r
install.packages(c("Seurat", "SeuratObject", "tidyverse", "patchwork"))
# Optional
remotes::install_github("satijalab/seurat-wrappers")
remotes::install_github("immunogenomics/harmony")
BiocManager::install("SingleR")
```

### Scanpy (Python)
```bash
pip install scanpy leidenalg scvi-tools cellchatpy
```

## Testing

Run basic validation:
```bash
cd scripts
python test_main.py
```

## Error Handling

All errors return semantic messages:

```json
{
  "status": "error",
  "error": {
    "type": "invalid_parameter",
    "message": "Unsupported batch correction method: 'xyz'",
    "suggestion": "Use one of: harmony, rpca, cca, scanorama, scvi"
  }
}
```

## Safety & Compliance

- No external API calls
- All code templates are self-contained
- No hardcoded credentials or paths
- Templates use relative paths for data
- Default parameters are conservative for safety

## Citation

If using generated templates in publications:
- Seurat: Satija Lab, Nature Biotechnology 2015
- Scanpy: Wolf et al., Genome Biology 2018
- scVI: Lopez et al., Nature Methods 2018
- Harmony: Korsunsky et al., Nature Methods 2019

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

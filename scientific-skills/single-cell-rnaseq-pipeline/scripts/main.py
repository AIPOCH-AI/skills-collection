#!/usr/bin/env python3
"""
Single-Cell RNA-seq Pipeline Generator
Generate comprehensive scRNA-seq analysis code templates for Seurat (R) and Scanpy (Python)
Version: 1.0.0
"""

import sys
import json
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configuration
REFERENCE_DIR = Path(__file__).parent.parent / "references"
OUTPUT_DIR = Path.cwd()

# Valid parameters
VALID_TOOLS = ["seurat", "scanpy", "both"]
VALID_SPECIES = ["human", "mouse"]
VALID_BATCH_METHODS = ["harmony", "rpca", "cca", "scanorama", "scvi", "bbknn", "combat"]

# Mitochondrial gene patterns
MT_PATTERNS = {
    "human": "^MT-",
    "mouse": "^mt-"
}

# Species-specific markers
MARKER_GENES = {
    "human": {
        "T_cells": ["CD3D", "CD3E", "CD4", "CD8A", "CD8B"],
        "B_cells": ["CD79A", "CD79B", "CD19", "MS4A1"],
        "Monocytes": ["CD14", "LYZ", "S100A8", "S100A9"],
        "NK_cells": ["NKG7", "GNLY", "KLRD1"],
        "DCs": ["FCER1A", "CLEC10A", "CD1C"],
        "Platelets": ["PPBP", "PF4"]
    },
    "mouse": {
        "T_cells": ["Cd3d", "Cd3e", "Cd4", "Cd8a", "Cd8b1"],
        "B_cells": ["Cd79a", "Cd79b", "Cd19", "Ms4a1"],
        "Monocytes": ["Cd14", "Lyz2", "S100a8", "S100a9"],
        "NK_cells": ["Nkg7", "Gnly", "Klrd1"],
        "DCs": ["Fcgr3", "Cd74", "Cd86"],
        "Platelets": ["Ppbp", "Pf4"]
    }
}


def validate_args(args) -> Tuple[bool, str]:
    """Validate command-line arguments."""
    if args.tool not in VALID_TOOLS:
        return False, f"Invalid tool '{args.tool}'. Use: {VALID_TOOLS}"
    
    if args.species not in VALID_SPECIES:
        return False, f"Invalid species '{args.species}'. Use: {VALID_SPECIES}"
    
    if args.batch_correction and args.batch_correction not in VALID_BATCH_METHODS:
        return False, f"Invalid batch correction '{args.batch_correction}'. Use: {VALID_BATCH_METHODS}"
    
    return True, ""


def generate_seurat_template(species: str, batch_correction: Optional[str], 
                             trajectory: bool, cell_comm: bool, de_analysis: bool) -> str:
    """Generate complete Seurat analysis R script."""
    
    mt_pattern = MT_PATTERNS[species]
    markers = MARKER_GENES[species]
    
    batch_code = ""
    if batch_correction == "harmony":
        batch_code = """
# Batch correction with Harmony
seurat_obj <- RunHarmony(seurat_obj, group.by.vars = "batch", assay.use = "RNA")
seurat_obj <- RunUMAP(seurat_obj, reduction = "harmony", dims = 1:30)
seurat_obj <- FindNeighbors(seurat_obj, reduction = "harmony", dims = 1:30)
"""
    elif batch_correction == "rpca":
        batch_code = """
# Batch correction with RPCA (Reciprocal PCA)
seurat_list <- SplitObject(seurat_obj, split.by = "batch")
seurat_list <- lapply(seurat_list, function(x) {
    x <- NormalizeData(x)
    x <- FindVariableFeatures(x, selection.method = "vst", nfeatures = 2000)
})
features <- SelectIntegrationFeatures(object.list = seurat_list)
seurat_list <- lapply(seurat_list, function(x) {
    x <- ScaleData(x, features = features)
    x <- RunPCA(x, features = features)
})
anchors <- FindIntegrationAnchors(object.list = seurat_list, anchor.features = features, reduction = "rpca")
seurat_obj <- IntegrateData(anchorset = anchors)
DefaultAssay(seurat_obj) <- "integrated"
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))
"""
    elif batch_correction == "cca":
        batch_code = """
# Batch correction with CCA
seurat_list <- SplitObject(seurat_obj, split.by = "batch")
seurat_list <- lapply(seurat_list, function(x) {
    x <- NormalizeData(x)
    x <- FindVariableFeatures(x, selection.method = "vst", nfeatures = 2000)
})
anchors <- FindIntegrationAnchors(object.list = seurat_list, dims = 1:30)
seurat_obj <- IntegrateData(anchorset = anchors, dims = 1:30)
DefaultAssay(seurat_obj) <- "integrated"
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))
"""
    
    de_code = """
# Find all markers for each cluster
all_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
top10 <- all_markers %>% group_by(cluster) %>% top_n(n = 10, wt = avg_log2FC)

# Visualize top markers
top_features <- unique(top10$gene)[1:min(12, length(unique(top10$gene)))]
FeaturePlot(seurat_obj, features = top_features, ncol = 4)
ggsave("plots/top_markers_featureplot.pdf", width = 16, height = 12)
""" if de_analysis else ""
    
    trajectory_code = """
# Trajectory inference with Monocle3
library(monocle3)
seurat_cds <- as.cell_data_set(seurat_obj)
seurat_cds <- cluster_cells(cds = seurat_cds, reduction_method = "UMAP")
seurat_cds <- learn_graph(seurat_cds, use_partition = TRUE)
plot_cells(seurat_cds, color_cells_by = "cluster", label_groups_by_cluster = FALSE)
ggsave("plots/trajectory.pdf", width = 10, height = 8)
""" if trajectory else ""
    
    template = f'''# Single-Cell RNA-seq Analysis Pipeline - Seurat
# Generated: {datetime.now().isoformat()}
# Species: {species.capitalize()}
# Batch Correction: {batch_correction or "None"}

# ============================================================
# Step 1: Load Libraries
# ============================================================
library(Seurat)
library(SeuratObject)
library(dplyr)
library(ggplot2)
library(patchwork)

# Optional libraries
# library(harmony)  # For batch correction
# library(SingleR)  # For cell type annotation
# library(monocle3) # For trajectory analysis

# ============================================================
# Step 2: Load Data
# ============================================================
# Option 1: Load 10x Genomics data
data_dir <- "path/to/filtered_gene_bc_matrices"
seurat_obj <- CreateSeuratObject(
    counts = Read10X(data.dir = data_dir),
    project = "Sample",
    min.cells = 3,
    min.features = 200
)

# Option 2: Load from RDS
# seurat_obj <- readRDS("path/to/seurat_object.rds")

# Add metadata (optional)
# seurat_obj$batch <- "batch1"  # For batch correction
# seurat_obj$condition <- "control"  # For differential analysis

cat("Initial cells:", ncol(seurat_obj), "\\n")
cat("Initial genes:", nrow(seurat_obj), "\\n")

# ============================================================
# Step 3: Quality Control
# ============================================================
# Calculate mitochondrial percentage
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "{mt_pattern}")

# Visualize QC metrics
VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3)
ggsave("plots/qc_violin_before_filtering.pdf", width = 12, height = 5)

FeatureScatter(seurat_obj, feature1 = "nCount_RNA", feature2 = "percent.mt")
FeatureScatter(seurat_obj, feature1 = "nCount_RNA", feature2 = "nFeature_RNA")
ggsave("plots/qc_scatter.pdf", width = 12, height = 5)

# Filter cells
seurat_obj <- subset(seurat_obj, 
    subset = nFeature_RNA > 200 & 
             nFeature_RNA < 25000 &
             percent.mt < 20)

cat("Cells after QC:", ncol(seurat_obj), "\\n")

# ============================================================
# Step 4: Normalization
# ============================================================
# Option 1: Log-normalization
seurat_obj <- NormalizeData(seurat_obj, normalization.method = "LogNormalize", scale.factor = 10000)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = "vst", nfeatures = 2000)

# Option 2: SCTransform (recommended for complex datasets)
# seurat_obj <- SCTransform(seurat_obj, vars.to.regress = "percent.mt")

# Visualize variable features
top10 <- head(VariableFeatures(seurat_obj), 10)
plot1 <- VariableFeaturePlot(seurat_obj)
plot2 <- LabelPoints(plot = plot1, points = top10, repel = TRUE)
plot1 + plot2
ggsave("plots/variable_features.pdf", width = 12, height = 5)

# ============================================================
# Step 5: Scaling and PCA
# ============================================================
seurat_obj <- ScaleData(seurat_obj, features = rownames(seurat_obj))
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))

# Visualize PCA
print(seurat_obj[["pca"]], dims = 1:5, nfeatures = 5)
VizDimLoadings(seurat_obj, dims = 1:2, reduction = "pca")
ggsave("plots/pca_loadings.pdf", width = 10, height = 8)

DimPlot(seurat_obj, reduction = "pca")
ggsave("plots/pca_plot.pdf", width = 8, height = 6)

DimHeatmap(seurat_obj, dims = 1, cells = 500, balanced = TRUE)
ggsave("plots/pca_heatmap.pdf", width = 8, height = 8)

# Determine dimensionality
ElbowPlot(seurat_obj, ndims = 50)
ggsave("plots/elbow_plot.pdf", width = 8, height = 6)

# ============================================================
# Step 6: Batch Correction (Optional)
# ============================================================
{batch_code}

# ============================================================
# Step 7: Clustering
# ============================================================
# Find neighbors and clusters
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = seq(0.2, 1.2, by = 0.2))

# Set default clustering resolution
Idents(seurat_obj) <- "RNA_snn_res.0.8"

# Run UMAP
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize clusters
DimPlot(seurat_obj, reduction = "umap", label = TRUE)
ggsave("plots/umap_clusters.pdf", width = 10, height = 8)

DimPlot(seurat_obj, reduction = "umap", split.by = "batch")
ggsave("plots/umap_by_batch.pdf", width = 14, height = 6)

# ============================================================
# Step 8: Marker Identification
# ============================================================
# Find markers for all clusters
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
top_markers <- markers %>% group_by(cluster) %>% top_n(n = 5, wt = avg_log2FC)

# Known cell type markers
known_markers <- c(
    {", ".join([f'"{g}"' for g in markers["T_cells"][:3]])},
    {", ".join([f'"{g}"' for g in markers["B_cells"][:3]])},
    {", ".join([f'"{g}"' for g in markers["Monocytes"][:3]])}
)

FeaturePlot(seurat_obj, features = known_markers, ncol = 3)
ggsave("plots/cell_type_markers.pdf", width = 12, height = 10)

DotPlot(seurat_obj, features = known_markers) + RotatedAxis()
ggsave("plots/dotplot_markers.pdf", width = 10, height = 6)

VlnPlot(seurat_obj, features = known_markers[1:6], ncol = 3)
ggsave("plots/violin_markers.pdf", width = 12, height = 8)

{de_code}
{trajectory_code}

# ============================================================
# Step 9: Cell Type Annotation (Manual)
# ============================================================
# Based on marker expression, assign cell types
seurat_obj$cell_type <- "Unknown"
seurat_obj$cell_type[seurat_obj$seurat_clusters %in% c(0)] <- "CD4 T"
seurat_obj$cell_type[seurat_obj$seurat_clusters %in% c(1)] <- "CD8 T"
seurat_obj$cell_type[seurat_obj$seurat_clusters %in% c(2)] <- "B cells"
seurat_obj$cell_type[seurat_obj$seurat_clusters %in% c(3)] <- "Monocytes"
seurat_obj$cell_type[seurat_obj$seurat_clusters %in% c(4)] <- "NK cells"

# Visualize annotated cells
DimPlot(seurat_obj, reduction = "umap", group.by = "cell_type", label = TRUE)
ggsave("plots/umap_cell_types.pdf", width = 10, height = 8)

# ============================================================
# Step 10: Save Results
# ============================================================
saveRDS(seurat_obj, file = "seurat_analysis_object.rds")
write.csv(markers, file = "cluster_markers.csv", row.names = FALSE)

cat("Analysis complete!\\n")
cat("Final object:", ncol(seurat_obj), "cells,", nrow(seurat_obj), "genes\\n")
'''
    
    return template


def generate_scanpy_template(species: str, batch_correction: Optional[str],
                             trajectory: bool, cell_comm: bool, de_analysis: bool) -> str:
    """Generate complete Scanpy analysis Python script."""
    
    mt_pattern = MT_PATTERNS[species]
    markers = MARKER_GENES[species]
    
    batch_code = ""
    if batch_correction == "harmony":
        batch_code = """
# Batch correction with Harmony
import harmonypy as hm
sc.external.pp.harmony_integrate(adata, key='batch')
adata.obsm['X_pca'] = adata.obsm['X_pca_harmony']
"""
    elif batch_correction == "scanorama":
        batch_code = """
# Batch correction with Scanorama
import scanorama
adata_list = [adata[adata.obs['batch'] == b].copy() for b in adata.obs['batch'].unique()]
integrated = scanorama.integrate_scanpy(adata_list)
adata.obsm['X_scanorama'] = np.concatenate([a.obsm['X_scanorama'] for a in adata_list])
sc.pp.neighbors(adata, use_rep='X_scanorama')
"""
    elif batch_correction == "scvi":
        batch_code = """
# Batch correction with scVI
import scvi
scvi.model.SCVI.setup_anndata(adata, batch_key='batch')
vae = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
vae.train()
adata.obsm["X_scVI"] = vae.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI")
"""
    elif batch_correction == "bbknn":
        batch_code = """
# Batch correction with BBKNN
import bbknn
bbknn.bbknn(adata, batch_key='batch')
"""
    elif batch_correction == "combat":
        batch_code = """
# Batch correction with ComBat
sc.pp.combat(adata, key='batch')
"""
    
    de_code = """
# Differential expression analysis
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save='_markers.pdf')

# Get marker dataframe
marker_df = sc.get.rank_genes_groups_df(adata, group=None)
marker_df.to_csv('scanpy_markers.csv', index=False)
""" if de_analysis else ""
    
    trajectory_code = """
# Trajectory inference with PAGA
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, plot=False)
sc.tl.umap(adata, init_pos='paga')
sc.pl.umap(adata, color=['leiden', 'paga'], save='_trajectory.pdf')

# Diffusion pseudotime
sc.tl.diffmap(adata)
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == '0')[0]
sc.tl.dpt(adata)
sc.pl.umap(adata, color='dpt_pseudotime', save='_pseudotime.pdf')
""" if trajectory else ""
    
    cell_comm_code = """
# Cell-cell communication analysis with CellChat
# Requires R and CellChat
# import cellchatpy as cc
# cellchat = cc.CellChat(adata, cell_type_column='cell_type')
# cellchat.run_analysis()
""" if cell_comm else ""
    
    template = f'''"""
Single-Cell RNA-seq Analysis Pipeline - Scanpy
Generated: {datetime.now().isoformat()}
Species: {species.capitalize()}
Batch Correction: {batch_correction or "None"}
"""

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Settings
sc.settings.verbosity = 3  # verbosity level: errors (0), warnings (1), info (2), hints (3)
sc.settings.set_figure_params(dpi=80, facecolor='white')

# Create output directories
Path("plots").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# ============================================================
# Step 1: Load Data
# ============================================================
# Option 1: Load 10x Genomics data
adata = sc.read_10x_mtx(
    "path/to/filtered_gene_bc_matrices/",
    var_names='gene_symbols',
    cache=True
)

# Option 2: Load H5AD file
# adata = sc.read_h5ad("path/to/data.h5ad")

# Option 3: Load from CSV
# adata = sc.read_csv("path/to/count_matrix.csv").T

print(f"Initial shape: {{adata.shape}}")

# Add metadata (optional)
# adata.obs['batch'] = 'batch1'
# adata.obs['condition'] = 'control'

# ============================================================
# Step 2: Quality Control
# ============================================================
# Calculate QC metrics
adata.var['mt'] = adata.var_names.str.startswith('{mt_pattern.split("-")[0]}-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Visualize QC before filtering
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True, save='_qc_before.pdf')

sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', save='_counts_vs_mt.pdf')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts', save='_counts_vs_genes.pdf')

# Filter cells and genes
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Filter by mitochondrial percentage and counts
adata = adata[adata.obs.n_genes_by_counts < 25000, :]
adata = adata[adata.obs.pct_counts_mt < 20, :]
adata = adata[adata.obs.total_counts < 100000, :]

print(f"Shape after QC: {{adata.shape}}")

# ============================================================
# Step 3: Normalization
# ============================================================
# Normalize to 10,000 counts per cell
sc.pp.normalize_total(adata, target_sum=1e4)

# Log transform
sc.pp.log1p(adata)

# Identify highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)

# Visualize highly variable genes
sc.pl.highly_variable_genes(adata, save='_hvg.pdf')

print(f"Highly variable genes: {{np.sum(adata.var.highly_variable)}}")

# ============================================================
# Step 4: Scaling and PCA
# ============================================================
# Scale data
sc.pp.scale(adata, max_value=10)

# Run PCA
sc.tl.pca(adata, svd_solver='arpack')

# Visualize PCA
sc.pl.pca(adata, color='CST3', save='_pca_example.pdf')
sc.pl.pca_variance_ratio(adata, log=True, save='_pca_variance.pdf')

# ============================================================
# Step 5: Batch Correction (Optional)
# ============================================================
{batch_code}

# ============================================================
# Step 6: Neighborhood Graph and Clustering
# ============================================================
# Compute neighborhood graph
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Run UMAP
sc.tl.umap(adata)

# Clustering with Leiden algorithm
sc.tl.leiden(adata, resolution=0.8)

# Visualize clusters
sc.pl.umap(adata, color=['leiden'], save='_clusters.pdf')
sc.pl.umap(adata, color=['total_counts', 'n_genes_by_counts'], save='_qc_umap.pdf')

# ============================================================
# Step 7: Marker Identification
# ============================================================
# Find markers for each cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save='_markers_heatmap.pdf')

# Known cell type markers
marker_genes = {{
    'T_cells': {markers["T_cells"][:4]},
    'B_cells': {markers["B_cells"][:4]},
    'Monocytes': {markers["Monocytes"][:4]},
    'NK_cells': {markers["NK_cells"][:3]},
}}

# Visualize known markers
sc.pl.umap(adata, color=marker_genes['T_cells'][:3], save='_tcell_markers.pdf')
sc.pl.umap(adata, color=marker_genes['B_cells'][:3], save='_bcell_markers.pdf')

# Dot plot of markers
all_markers = [g for genes in marker_genes.values() for g in genes]
sc.pl.dotplot(adata, all_markers, groupby='leiden', save='_markers_dotplot.pdf')

# Stacked violin plot
sc.pl.stacked_violin(adata, all_markers[:8], groupby='leiden', rotation=90, 
                     save='_markers_violin.pdf')

{de_code}
{trajectory_code}
{cell_comm_code}

# ============================================================
# Step 8: Cell Type Annotation (Manual)
# ============================================================
# Based on marker expression, assign cell types
cluster_to_celltype = {{
    '0': 'CD4 T',
    '1': 'CD8 T', 
    '2': 'B cells',
    '3': 'Monocytes',
    '4': 'NK cells',
}}

adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_to_celltype)
adata.obs['cell_type'] = adata.obs['cell_type'].fillna('Unknown')

# Visualize annotated cells
sc.pl.umap(adata, color='cell_type', legend_loc='on data', 
           frameon=False, save='_cell_types.pdf')

# ============================================================
# Step 9: Summary Statistics
# ============================================================
print("\\n=== Analysis Summary ===")
print(f"Final dataset: {{adata.shape[0]}} genes x {{adata.shape[1]}} cells")
print(f"Number of clusters: {{adata.obs['leiden'].nunique()}}")
print("\\nCell type distribution:")
print(adata.obs['cell_type'].value_counts())

# ============================================================
# Step 10: Save Results
# ============================================================
adata.write('scanpy_analysis.h5ad')
print("\\nResults saved to: scanpy_analysis.h5ad")
'''
    
    return template


def generate_readme(params: dict) -> str:
    """Generate README for the generated templates."""
    
    readme = f"""# Single-Cell RNA-seq Analysis Pipeline

Generated: {datetime.now().isoformat()}

## Configuration

| Parameter | Value |
|-----------|-------|
| Species | {params['species'].capitalize()} |
| Batch Correction | {params.get('batch_correction', 'None')} |
| Trajectory Analysis | {params.get('trajectory', False)} |
| Cell Communication | {params.get('cell_comm', False)} |
| DE Analysis | {params.get('de_analysis', False)} |

## Directory Structure

```
.
├── seurat_analysis.R      # Complete Seurat pipeline
├── scanpy_analysis.py     # Complete Scanpy pipeline  
├── README.md              # This file
└── data/                  # Output directory
    └── plots/             # Generated plots
```

## Quick Start

### Seurat (R)

```bash
Rscript seurat_analysis.R
```

### Scanpy (Python)

```bash
python scanpy_analysis.py
```

## Prerequisites

### R (Seurat)
```r
install.packages(c("Seurat", "dplyr", "ggplot2", "patchwork"))
```

### Python (Scanpy)
```bash
pip install scanpy leidenalg python-igraph
```

## Data Input

Update the data path in the scripts:
- **Seurat**: Modify `data_dir <- "path/to/filtered_gene_bc_matrices"`
- **Scanpy**: Modify `sc.read_10x_mtx("path/to/filtered_gene_bc_matrices/")`

## Expected Output

- Processed Seurat/Scanpy objects
- UMAP visualizations with clusters
- Marker gene plots
- Cell type annotations
- Quality control plots

## Notes

1. Adjust QC thresholds based on your data quality
2. Modify marker genes for your specific tissue/cell types
3. Clustering resolution can be tuned (0.4-1.2 typical range)
4. For large datasets, consider downsampling for initial exploration

## Troubleshooting

- **Memory issues**: Increase `min.cells` and `min.features` filters
- **Poor clustering**: Adjust PCA dimensions (try 20-50) or resolution
- **Batch effects**: Use batch correction methods provided
- **Cell type annotation**: Update marker genes based on your tissue
"""
    
    return readme


def save_templates(tool: str, output_path: str, species: str, batch_correction: Optional[str],
                   trajectory: bool, cell_comm: bool, de_analysis: bool) -> List[str]:
    """Save generated templates to files."""
    
    created_files = []
    output = Path(output_path)
    
    params = {
        'species': species,
        'batch_correction': batch_correction,
        'trajectory': trajectory,
        'cell_comm': cell_comm,
        'de_analysis': de_analysis
    }
    
    if tool in ["seurat", "both"]:
        seurat_code = generate_seurat_template(species, batch_correction, 
                                               trajectory, cell_comm, de_analysis)
        
        if tool == "both":
            seurat_path = output / "seurat_analysis.R"
        else:
            seurat_path = output if str(output).endswith('.R') else output / "seurat_analysis.R"
        
        seurat_path.parent.mkdir(parents=True, exist_ok=True)
        with open(seurat_path, 'w') as f:
            f.write(seurat_code)
        created_files.append(str(seurat_path))
    
    if tool in ["scanpy", "both"]:
        scanpy_code = generate_scanpy_template(species, batch_correction,
                                               trajectory, cell_comm, de_analysis)
        
        if tool == "both":
            scanpy_path = output / "scanpy_analysis.py"
        else:
            scanpy_path = output if str(output).endswith('.py') else output / "scanpy_analysis.py"
        
        scanpy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(scanpy_path, 'w') as f:
            f.write(scanpy_code)
        created_files.append(str(scanpy_path))
    
    if tool == "both":
        readme_path = output / "README.md"
    else:
        readme_path = output.parent / "README.md" if output.suffix else output / "README.md"
    
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    with open(readme_path, 'w') as f:
        f.write(generate_readme(params))
    created_files.append(str(readme_path))
    
    return created_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate single-cell RNA-seq analysis code templates"
    )
    parser.add_argument(
        "--tool", "-t",
        required=True,
        choices=VALID_TOOLS,
        help="Analysis tool to generate templates for"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file or directory path"
    )
    parser.add_argument(
        "--species", "-s",
        default="human",
        choices=VALID_SPECIES,
        help="Species (default: human)"
    )
    parser.add_argument(
        "--batch-correction", "-b",
        choices=VALID_BATCH_METHODS,
        help="Batch correction method"
    )
    parser.add_argument(
        "--trajectory",
        action="store_true",
        help="Include trajectory analysis code"
    )
    parser.add_argument(
        "--cell-communication",
        action="store_true",
        help="Include cell-cell communication code"
    )
    parser.add_argument(
        "--de-analysis",
        action="store_true",
        help="Include differential expression analysis code"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    is_valid, error_msg = validate_args(args)
    if not is_valid:
        error_output = {
            "status": "error",
            "error": {
                "type": "invalid_parameter",
                "message": error_msg,
                "suggestion": "Check --help for valid options"
            }
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)
    
    try:
        # Generate and save templates
        created_files = save_templates(
            tool=args.tool,
            output_path=args.output,
            species=args.species,
            batch_correction=args.batch_correction,
            trajectory=args.trajectory,
            cell_comm=args.cell_communication,
            de_analysis=args.de_analysis
        )
        
        # Build success response
        output = {
            "status": "success",
            "data": {
                "tool": args.tool,
                "species": args.species,
                "batch_correction": args.batch_correction,
                "features": {
                    "trajectory": args.trajectory,
                    "cell_communication": args.cell_communication,
                    "de_analysis": args.de_analysis
                },
                "created_files": created_files,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "message": f"Successfully generated {args.tool} template(s)"
        }
        
        print(json.dumps(output, indent=2))
        sys.exit(0)
        
    except Exception as e:
        error_output = {
            "status": "error",
            "error": {
                "type": "generation_error",
                "message": "Failed to generate templates",
                "suggestion": "Check output path permissions and disk space"
            }
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()

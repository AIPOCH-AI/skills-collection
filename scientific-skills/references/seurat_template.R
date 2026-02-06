# Seurat Template Reference

## Complete Seurat Workflow Example

```r
# ============================================
# Complete Seurat scRNA-seq Analysis Pipeline
# ============================================

# 1. Setup
library(Seurat)
library(dplyr)
library(ggplot2)

# 2. Load Data (10x Genomics)
seurat_obj <- CreateSeuratObject(
    counts = Read10X(data.dir = "filtered_gene_bc_matrices/"),
    project = "Sample",
    min.cells = 3,
    min.features = 200
)

# 3. QC
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")
seurat_obj <- subset(seurat_obj, 
    subset = nFeature_RNA > 200 & 
             nFeature_RNA < 25000 &
             percent.mt < 20)

# 4. Normalize
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = "vst", nfeatures = 2000)

# 5. Scale and PCA
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))

# 6. Cluster
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.8)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# 7. Visualize
DimPlot(seurat_obj, reduction = "umap", label = TRUE)

# 8. Markers
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
```

## Key Functions

| Function | Purpose |
|----------|---------|
| `CreateSeuratObject()` | Create Seurat object from counts |
| `PercentageFeatureSet()` | Calculate gene set percentages (e.g., MT genes) |
| `NormalizeData()` | Log-normalization |
| `FindVariableFeatures()` | Identify highly variable genes |
| `ScaleData()` | Z-score normalization |
| `RunPCA()` | Principal component analysis |
| `RunHarmony()` | Batch correction (requires harmony package) |
| `FindNeighbors()` | Build SNN graph |
| `FindClusters()` | Graph-based clustering |
| `RunUMAP()` | UMAP dimensionality reduction |
| `FindAllMarkers()` | Identify cluster markers |

## Common Parameters

### QC Thresholds
```r
# Conservative (high quality cells only)
min_genes = 500
max_mt = 10

# Standard
min_genes = 200
max_mt = 20

# Permissive (poor quality data)
min_genes = 100
max_mt = 30
```

### Clustering Resolution
```r
resolution = 0.4  # Broad cell types
resolution = 0.8  # Subtypes
resolution = 1.2  # Fine populations
```

### PCA Dimensions
```r
dims = 1:10   # Simple datasets
dims = 1:30   # Standard
dims = 1:50   # Complex datasets
```

# Batch Correction Methods Comparison

## Overview

Batch correction is essential when combining data from multiple experiments, donors, or sequencing runs. This guide compares available methods for single-cell RNA-seq data.

## Method Comparison

| Method | Best For | Seurat | Scanpy | Speed | Accuracy |
|--------|----------|--------|--------|-------|----------|
| **Harmony** | Small batches (<5), simple variation | ✅ | ✅ | Fast | High |
| **RPCA** | Large datasets, many batches | ✅ | ❌ | Medium | Very High |
| **CCA** | Complex variation, different tissues | ✅ | ❌ | Slow | Very High |
| **Scanorama** | Integration across platforms | ✅ | ✅ | Fast | High |
| **scVI** | Deep learning approach, large data | ✅ | ✅ | Slow | Very High |
| **BBKNN** | Graph-based, fast alternative | ✅ | ✅ | Very Fast | Medium |
| **ComBat** | Simple linear correction | ❌ | ✅ | Fast | Medium |

## Recommendations by Scenario

### Small Study (<5 batches)
```
Recommended: Harmony
Reason: Fast, accurate, preserves biological variation
```

### Large Study (>10 batches)
```
Recommended: RPCA (Seurat) or scVI (Scanpy)
Reason: Scalable, handles complex batch structures
```

### Cross-Platform Integration
```
Recommended: Scanorama or scVI
Reason: Designed for platform-specific technical effects
```

### Different Tissues/Conditions
```
Recommended: CCA or scVI
Reason: Preserves cell type differences while removing technical effects
```

### Quick Exploration
```
Recommended: BBKNN
Reason: Fastest method, good for initial analysis
```

## Quality Control After Integration

1. **Visual inspection**: Check UMAP by batch
2. **kBET**: Quantify batch mixing per cell type
3. **LISI**: Local Inverse Simpson's Index
4. **Silhouette score**: Cluster cohesion
5. **Marker preservation**: Check if known markers still identify cell types

## Code Examples

### Seurat - Harmony
```r
library(harmony)
seurat_obj <- RunHarmony(seurat_obj, group.by.vars = "batch")
seurat_obj <- RunUMAP(seurat_obj, reduction = "harmony", dims = 1:30)
```

### Seurat - RPCA
```r
seurat_list <- SplitObject(seurat_obj, split.by = "batch")
seurat_list <- lapply(seurat_list, NormalizeData)
seurat_list <- lapply(seurat_list, FindVariableFeatures)
features <- SelectIntegrationFeatures(seurat_list)
seurat_list <- lapply(seurat_list, ScaleData)
seurat_list <- lapply(seurat_list, RunPCA, features = features)
anchors <- FindIntegrationAnchors(seurat_list, reduction = "rpca")
seurat_integrated <- IntegrateData(anchorset = anchors)
```

### Scanpy - Harmony
```python
import scanpy.external as sce
sce.pp.harmony_integrate(adata, key='batch')
adata.obsm['X_pca'] = adata.obsm['X_pca_harmony']
```

### Scanpy - scVI
```python
import scvi
scvi.model.SCVI.setup_anndata(adata, batch_key='batch')
vae = scvi.model.SCVI(adata, n_layers=2, n_latent=30)
vae.train()
adata.obsm["X_scVI"] = vae.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI")
```

## Common Pitfalls

1. **Over-correction**: Removes biological signal along with batch effects
   - Solution: Compare before/after correction marker expression

2. **Under-correction**: Batches remain separated
   - Solution: Try stronger methods (scVI, CCA)

3. **Confounding**: Batch and condition are correlated
   - Solution: Use methods that model condition (scVI)

4. **Cell type imbalance**: Different proportions across batches
   - Solution: Subsample abundant cell types before integration

## References

- Harmony: Korsunsky et al. (2019) Nature Methods
- RPCA: Stuart & Butler et al. (2019) Cell
- Scanorama: Hie et al. (2019) Nature Biotechnology
- scVI: Lopez et al. (2018) Nature Methods

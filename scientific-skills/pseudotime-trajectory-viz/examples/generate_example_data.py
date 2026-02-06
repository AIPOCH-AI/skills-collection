#!/usr/bin/env python3
"""
Generate example single-cell data for pseudotime trajectory analysis testing.

This script creates a synthetic AnnData object simulating a differentiation
process from stem cells to mature cell types.
"""

import numpy as np
import scanpy as sc
import anndata
import pandas as pd


def generate_trajectory_data(n_cells=1000, n_genes=2000, random_state=42):
    """
    Generate synthetic single-cell data with a differentiation trajectory.
    
    Parameters:
    -----------
    n_cells : int
        Number of cells to generate
    n_genes : int
        Number of genes
    random_state : int
        Random seed
        
    Returns:
    --------
    AnnData object with trajectory structure
    """
    np.random.seed(random_state)
    
    print(f"Generating synthetic data: {n_cells} cells, {n_genes} genes")
    
    # Define cell types along trajectory
    cell_types = ['Stem', 'Progenitor', 'Intermediate', 'Mature_A', 'Mature_B']
    proportions = [0.15, 0.25, 0.25, 0.2, 0.15]
    
    # Assign cell types
    cell_type_assignments = np.random.choice(
        cell_types, size=n_cells, p=proportions
    )
    
    # Create pseudotime based on cell type
    pseudotime_map = {
        'Stem': (0.0, 0.2),
        'Progenitor': (0.15, 0.4),
        'Intermediate': (0.35, 0.6),
        'Mature_A': (0.55, 0.9),
        'Mature_B': (0.55, 0.9)
    }
    
    pseudotime = np.array([
        np.random.uniform(*pseudotime_map[ct]) 
        for ct in cell_type_assignments
    ])
    
    # Define marker genes
    marker_genes = {
        'Stem': ['SOX2', 'NANOG', 'POU5F1'],
        'Progenitor': ['NES', 'PAX6', 'SOX1'],
        'Intermediate': ['NEUROD1', 'NEUROG2', 'ASCL1'],
        'Mature_A': ['RBFOX3', 'MAP2', 'TUBB3'],
        'Mature_B': ['GFAP', 'S100B', 'ALDH1L1']
    }
    
    # Generate gene names
    gene_names = []
    for genes in marker_genes.values():
        gene_names.extend(genes)
    # Fill rest with generic names
    while len(gene_names) < n_genes:
        gene_names.append(f'GENE_{len(gene_names)}')
    gene_names = gene_names[:n_genes]
    
    # Generate expression matrix
    X = np.zeros((n_cells, n_genes))
    
    for i, gene in enumerate(gene_names):
        # Base expression
        base_expr = np.random.exponential(0.5, n_cells)
        
        # Add cell type specific expression
        for ct, markers in marker_genes.items():
            if gene in markers:
                mask = cell_type_assignments == ct
                # Higher expression in this cell type
                base_expr[mask] += np.random.exponential(3, mask.sum())
        
        # Add pseudotime trend for some genes
        if np.random.random() < 0.1:  # 10% of genes have pseudotime trend
            trend = pseudotime * np.random.normal(2, 1)
            base_expr += trend
        
        X[:, i] = base_expr
    
    # Add noise
    X += np.random.normal(0, 0.5, X.shape)
    X = np.clip(X, 0, None)
    
    # Convert to sparse
    from scipy.sparse import csr_matrix
    X_sparse = csr_matrix(X)
    
    # Create AnnData
    adata = anndata.AnnData(
        X=X_sparse,
        obs=pd.DataFrame({
            'cell_type': cell_type_assignments,
            'pseudotime_true': pseudotime
        }, index=[f'cell_{i:04d}' for i in range(n_cells)]),
        var=pd.DataFrame(index=gene_names)
    )
    
    # Preprocess
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=500)
    sc.pp.scale(adata)
    sc.tl.pca(adata, svd_solver='arpack')
    sc.pp.neighbors(adata, n_neighbors=15, n_pcs=20)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.5)
    
    print(f"Generated AnnData: {adata.n_obs} cells × {adata.n_vars} genes")
    print(f"Cell types: {adata.obs['cell_type'].value_counts().to_dict()}")
    print(f"Clusters: {adata.obs['leiden'].nunique()}")
    
    return adata


if __name__ == '__main__':
    import sys
    
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'example_data.h5ad'
    
    adata = generate_trajectory_data()
    adata.write(output_path)
    print(f"\nSaved example data to: {output_path}")
    print("\nTo run trajectory analysis:")
    print(f"  python scripts/main.py --input {output_path} --start-cell-type Stem --output ./example_results")

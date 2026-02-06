#!/usr/bin/env python3
"""
Generate sample test data for Volcano Plot Labeler
"""

import numpy as np
import pandas as pd

def generate_test_data(n_genes=5000, seed=42, output_path='test_data.csv'):
    """
    Generate synthetic differential expression data for testing.
    
    Parameters:
    -----------
    n_genes : int
        Number of genes to generate
    seed : int
        Random seed for reproducibility
    output_path : str
        Output CSV path
    """
    np.random.seed(seed)
    
    # Generate gene names
    gene_names = [f"GENE_{i:05d}" for i in range(n_genes)]
    
    # Generate log2 fold changes (mostly near 0, some extreme)
    log2fc = np.random.normal(0, 1.5, n_genes)
    
    # Make some genes highly significant
    significant_indices = np.random.choice(n_genes, size=50, replace=False)
    log2fc[significant_indices[:25]] = np.random.uniform(2, 5, 25)  # Upregulated
    log2fc[significant_indices[25:]] = np.random.uniform(-5, -2, 25)  # Downregulated
    
    # Generate p-values (smaller p-values for more extreme fold changes)
    base_pvalues = np.random.uniform(0, 1, n_genes)
    # Adjust p-values based on effect size
    for i in significant_indices:
        base_pvalues[i] = np.random.uniform(1e-10, 0.001)
    
    # Adjusted p-values (padj)
    padj = np.minimum(base_pvalues * n_genes, 1.0)  # Simple Bonferroni-like correction
    padj = np.maximum(padj, 1e-300)  # Avoid zeros
    
    # Create dataframe
    df = pd.DataFrame({
        'gene_name': gene_names,
        'log2FoldChange': log2fc,
        'pvalue': base_pvalues,
        'padj': padj
    })
    
    df.to_csv(output_path, index=False)
    print(f"Generated {n_genes} genes in {output_path}")
    print(f"Top 5 upregulated genes:")
    print(df.nlargest(5, 'log2FoldChange')[['gene_name', 'log2FoldChange', 'padj']])
    print(f"\nTop 5 downregulated genes:")
    print(df.nsmallest(5, 'log2FoldChange')[['gene_name', 'log2FoldChange', 'padj']])
    
    return df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate test data for volcano plot')
    parser.add_argument('-n', '--n-genes', type=int, default=5000)
    parser.add_argument('-o', '--output', default='test_data.csv')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    
    generate_test_data(args.n_genes, args.seed, args.output)

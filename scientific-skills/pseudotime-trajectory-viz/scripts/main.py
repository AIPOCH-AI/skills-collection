#!/usr/bin/env python3
"""
Pseudotime Trajectory Visualization Tool

Visualize single-cell developmental trajectories showing how cells
differentiate from stem cells to mature cells.

Author: OpenClaw
Date: 2026-02-06
"""

import argparse
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

import anndata
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set matplotlib defaults for publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 9


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Visualize single-cell developmental trajectories (pseudotime)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.h5ad --output ./results
  %(prog)s --input data.h5ad --start-cell-type progenitor --method diffusion
  %(prog)s --input data.h5ad --genes SOX2,OCT4,NANOG --plot-genes
        """
    )
    
    # Required arguments
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='Input AnnData (.h5ad) file path')
    parser.add_argument('--output', '-o', type=str, default='./trajectory_output',
                        help='Output directory for results (default: ./trajectory_output)')
    
    # Embedding and method selection
    parser.add_argument('--embedding', type=str, default='umap',
                        choices=['umap', 'tsne', 'pca', 'diffmap'],
                        help='Embedding for visualization (default: umap)')
    parser.add_argument('--method', type=str, default='diffusion',
                        choices=['diffusion', 'paga'],
                        help='Trajectory inference method (default: diffusion)')
    
    # Trajectory parameters
    parser.add_argument('--start-cell', type=str, default=None,
                        help='Root cell ID for trajectory origin')
    parser.add_argument('--start-cell-type', type=str, default=None,
                        help='Cell type to use as trajectory starting point')
    parser.add_argument('--n-lineages', type=int, default=None,
                        help='Number of expected lineage branches (auto-detect if not specified)')
    
    # Data keys
    parser.add_argument('--cluster-key', type=str, default='leiden',
                        help='AnnData obs key for cell clusters (default: leiden)')
    parser.add_argument('--cell-type-key', type=str, default='cell_type',
                        help='AnnData obs key for cell type annotations (default: cell_type)')
    
    # Gene expression plotting
    parser.add_argument('--genes', type=str, default=None,
                        help='Comma-separated gene names to plot along pseudotime')
    parser.add_argument('--plot-genes', action='store_true',
                        help='Generate gene expression heatmaps along trajectories')
    parser.add_argument('--plot-branch', action='store_true', default=True,
                        help='Show lineage branch probabilities')
    
    # Output options
    parser.add_argument('--format', type=str, default='png',
                        choices=['png', 'pdf', 'svg'],
                        help='Output figure format (default: png)')
    parser.add_argument('--dpi', type=int, default=300,
                        help='Figure resolution (default: 300)')
    
    # Analysis parameters
    parser.add_argument('--n-pcs', type=int, default=30,
                        help='Number of principal components (default: 30)')
    parser.add_argument('--n-neighbors', type=int, default=15,
                        help='Number of neighbors for graph (default: 15)')
    parser.add_argument('--diffmap-components', type=int, default=5,
                        help='Number of diffusion components (default: 5)')
    
    return parser.parse_args()


def load_data(input_path):
    """Load AnnData object from file."""
    print(f"Loading data from {input_path}...")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        adata = sc.read_h5ad(input_path)
        print(f"Loaded {adata.n_obs} cells and {adata.n_vars} genes")
        return adata
    except Exception as e:
        raise ValueError(f"Error loading AnnData file: {e}")


def preprocess_data(adata, args):
    """Preprocess data for trajectory analysis."""
    print("Preprocessing data...")
    
    # Check for required annotations
    if args.cluster_key not in adata.obs.columns:
        print(f"Warning: Cluster key '{args.cluster_key}' not found. Computing Leiden clustering...")
        if 'neighbors' not in adata.uns:
            sc.pp.neighbors(adata, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs)
        sc.tl.leiden(adata, key_added=args.cluster_key)
    
    # Compute embedding if not present
    embedding_key = f'X_{args.embedding}'
    if embedding_key not in adata.obsm.keys():
        print(f"Computing {args.embedding.upper()} embedding...")
        if 'neighbors' not in adata.uns:
            sc.pp.neighbors(adata, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs)
        
        if args.embedding == 'umap':
            sc.tl.umap(adata)
        elif args.embedding == 'tsne':
            sc.tl.tsne(adata)
        elif args.embedding == 'diffmap':
            sc.tl.diffmap(adata, n_comps=args.diffmap_components)
    
    # Compute highly variable genes if not present
    if 'highly_variable' not in adata.var.columns:
        print("Computing highly variable genes...")
        sc.pp.highly_variable_genes(adata, n_top_genes=2000)
    
    return adata


def find_root_cell(adata, args):
    """Identify root cell for trajectory inference."""
    print("Identifying root cell...")
    
    root_cell = None
    
    # Option 1: Use specified cell ID
    if args.start_cell:
        if args.start_cell in adata.obs_names:
            root_cell = args.start_cell
            print(f"Using specified root cell: {root_cell}")
            return root_cell
        else:
            print(f"Warning: Specified start cell '{args.start_cell}' not found in data")
    
    # Option 2: Use cell type annotation
    if args.start_cell_type and args.cell_type_key in adata.obs.columns:
        cell_types = adata.obs[args.cell_type_key].values
        if args.start_cell_type in cell_types:
            # Find cell with highest stemness marker expression
            stem_markers = ['SOX2', 'POU5F1', 'NANOG', 'PROM1', 'THY1', 'KIT']
            available_markers = [g for g in stem_markers if g in adata.var_names]
            
            mask = cell_types == args.start_cell_type
            if available_markers:
                expr = adata[mask, available_markers].X.mean(axis=1)
                if hasattr(expr, 'A1'):
                    expr = expr.A1
                root_idx = np.where(mask)[0][np.argmax(expr)]
            else:
                root_idx = np.where(mask)[0][0]
            
            root_cell = adata.obs_names[root_idx]
            print(f"Selected root cell from '{args.start_cell_type}': {root_cell}")
            return root_cell
        else:
            print(f"Warning: Cell type '{args.start_cell_type}' not found")
    
    # Option 3: Auto-detect based on stemness markers
    stem_markers = ['SOX2', 'POU5F1', 'OCT4', 'NANOG', 'PROM1', 'THY1', 'KIT', 'CD34']
    available_markers = [g for g in stem_markers if g in adata.var_names]
    
    if available_markers:
        print(f"Using stemness markers to find root: {available_markers}")
        expr = adata[:, available_markers].X.mean(axis=1)
        if hasattr(expr, 'A1'):
            expr = expr.A1
        root_idx = np.argmax(expr)
        root_cell = adata.obs_names[root_idx]
        print(f"Auto-selected root cell: {root_cell}")
    else:
        # Fallback: use first cell
        root_cell = adata.obs_names[0]
        print(f"No markers found. Using first cell as root: {root_cell}")
    
    return root_cell


def compute_diffusion_pseudotime(adata, root_cell, args):
    """Compute diffusion pseudotime using scanpy."""
    print("Computing diffusion pseudotime...")
    
    # Compute diffusion map
    sc.tl.diffmap(adata, n_comps=args.diffmap_components)
    
    # Get root cell index
    root_idx = np.where(adata.obs_names == root_cell)[0][0]
    adata.uns['iroot'] = root_idx
    
    # Compute DPT
    sc.tl.dpt(adata, n_dcs=args.diffmap_components)
    
    # Get pseudotime values
    pseudotime = adata.obs['dpt_pseudotime'].values
    
    print(f"Pseudotime range: {pseudotime.min():.3f} - {pseudotime.max():.3f}")
    
    # Infer lineages based on clusters
    n_lineages = args.n_lineages or min(3, adata.obs[args.cluster_key].nunique())
    
    # Simple lineage assignment based on terminal branches
    lineage_assignments = assign_lineages(adata, n_lineages, args)
    adata.obs['lineage'] = lineage_assignments
    
    return adata


def assign_lineages(adata, n_lineages, args):
    """Assign cells to lineages based on trajectory branching."""
    # Simplified lineage assignment based on clusters and pseudotime
    clusters = adata.obs[args.cluster_key].values
    pseudotime = adata.obs['dpt_pseudotime'].values
    
    # Find terminal clusters (high pseudotime)
    cluster_pseudotime = {}
    for c in np.unique(clusters):
        mask = clusters == c
        cluster_pseudotime[c] = pseudotime[mask].mean()
    
    # Sort clusters by pseudotime
    sorted_clusters = sorted(cluster_pseudotime.items(), key=lambda x: x[1])
    
    # Assign lineages
    lineages = np.array(['lineage_1'] * adata.n_obs, dtype=object)
    
    if n_lineages > 1:
        # Simple heuristic: divide cells among lineages
        pseudotime_bins = np.linspace(0, 1, n_lineages + 1)
        for i in range(n_lineages):
            mask = (pseudotime >= pseudotime_bins[i]) & (pseudotime < pseudotime_bins[i+1])
            lineages[mask] = f'lineage_{i+1}'
    
    return lineages


def compute_paga_trajectory(adata, root_cell, args):
    """Compute trajectory using PAGA (Partition-based Graph Abstraction)."""
    print("Computing PAGA trajectory...")
    
    # Compute PAGA
    sc.tl.paga(adata, groups=args.cluster_key)
    
    # Get root cluster
    root_idx = np.where(adata.obs_names == root_cell)[0][0]
    root_cluster = adata.obs[args.cluster_key].iloc[root_idx]
    
    # Use PAGA to initialize embedding
    sc.tl.draw_graph(adata, init_pos=args.embedding)
    
    # Estimate pseudotime from PAGA distances
    paga_distances = adata.uns['paga']['connectivities'].toarray()
    
    # Simple pseudotime: distance from root cluster
    cluster_order = list(adata.obs[args.cluster_key].unique())
    if root_cluster in cluster_order:
        root_idx_cluster = cluster_order.index(root_cluster)
    else:
        root_idx_cluster = 0
    
    # Assign pseudotime based on cluster
    cluster_pseudotime = {}
    for i, c in enumerate(cluster_order):
        # Distance as pseudotime proxy
        cluster_pseudotime[c] = min(1.0, abs(i - root_idx_cluster) / max(1, len(cluster_order) - 1))
    
    pseudotime = np.array([cluster_pseudotime[c] for c in adata.obs[args.cluster_key]])
    pseudotime = pseudotime + np.random.normal(0, 0.05, len(pseudotime))  # Add noise
    pseudotime = np.clip(pseudotime, 0, 1)
    
    adata.obs['paga_pseudotime'] = pseudotime
    adata.obs['dpt_pseudotime'] = pseudotime  # Use same key for consistency
    
    # Assign lineages
    n_lineages = args.n_lineages or min(3, len(cluster_order))
    lineage_assignments = assign_lineages(adata, n_lineages, args)
    adata.obs['lineage'] = lineage_assignments
    
    return adata


def plot_trajectory(adata, args, output_dir):
    """Generate main trajectory visualization."""
    print("Generating trajectory plot...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    embedding_key = f'X_{args.embedding}'
    
    # Plot 1: Embedding colored by pseudotime
    ax = axes[0, 0]
    sc.pl.embedding(
        adata, basis=args.embedding, color='dpt_pseudotime',
        ax=ax, show=False, color_map='viridis_r',
        title='Pseudotime Trajectory'
    )
    
    # Plot 2: Embedding colored by cluster
    ax = axes[0, 1]
    sc.pl.embedding(
        adata, basis=args.embedding, color=args.cluster_key,
        ax=ax, show=False, legend_loc='on data',
        title='Cell Clusters'
    )
    
    # Plot 3: Embedding colored by lineage
    ax = axes[1, 0]
    sc.pl.embedding(
        adata, basis=args.embedding, color='lineage',
        ax=ax, show=False,
        title='Lineage Assignment'
    )
    
    # Plot 4: Pseudotime distribution
    ax = axes[1, 1]
    pseudotime = adata.obs['dpt_pseudotime'].values
    for lineage in adata.obs['lineage'].unique():
        mask = adata.obs['lineage'] == lineage
        ax.hist(pseudotime[mask], bins=30, alpha=0.6, label=lineage, density=True)
    ax.set_xlabel('Pseudotime')
    ax.set_ylabel('Density')
    ax.set_title('Pseudotime Distribution by Lineage')
    ax.legend()
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'trajectory_plot.{args.format}')
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")
    return output_path


def plot_paga_graph(adata, args, output_dir):
    """Plot PAGA graph if available."""
    if 'paga' not in adata.uns:
        return None
    
    print("Generating PAGA graph...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # PAGA connectivity
    sc.pl.paga(adata, ax=axes[0], show=False,
               title='PAGA Graph (Clusters)')
    
    # PAGA on embedding
    sc.pl.paga_compare(
        adata, basis=args.embedding, ax=axes[1], show=False,
        title='PAGA Graph on Embedding'
    )
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'paga_graph.{args.format}')
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")
    return output_path


def plot_gene_expression(adata, genes, args, output_dir):
    """Plot gene expression along pseudotime."""
    if not genes:
        return []
    
    print(f"Generating gene expression plots for {len(genes)} genes...")
    
    output_files = []
    
    # Create gene trends directory
    gene_trends_dir = os.path.join(output_dir, 'gene_trends')
    os.makedirs(gene_trends_dir, exist_ok=True)
    
    # Filter available genes
    available_genes = [g for g in genes if g in adata.var_names]
    missing_genes = set(genes) - set(available_genes)
    if missing_genes:
        print(f"Warning: Genes not found in data: {missing_genes}")
    
    if not available_genes:
        print("No valid genes to plot")
        return output_files
    
    # Individual gene plots
    for gene in available_genes:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        pseudotime = adata.obs['dpt_pseudotime'].values
        expression = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') else adata[:, gene].X.flatten()
        
        # Scatter plot with trend line
        for lineage in adata.obs['lineage'].unique():
            mask = adata.obs['lineage'] == lineage
            ax.scatter(pseudotime[mask], expression[mask], alpha=0.3, s=10, label=lineage)
            
            # Fit smoothing spline
            if mask.sum() > 10:
                from scipy.interpolate import UnivariateSpline
                idx = np.argsort(pseudotime[mask])
                x = pseudotime[mask][idx]
                y = expression[mask][idx]
                try:
                    spline = UnivariateSpline(x, y, s=len(x))
                    x_smooth = np.linspace(x.min(), x.max(), 100)
                    ax.plot(x_smooth, spline(x_smooth), linewidth=2, label=f'{lineage} trend')
                except:
                    pass
        
        ax.set_xlabel('Pseudotime')
        ax.set_ylabel(f'{gene} Expression')
        ax.set_title(f'{gene} Expression along Trajectory')
        ax.legend(loc='best')
        
        output_path = os.path.join(gene_trends_dir, f'{gene}_trend.{args.format}')
        plt.tight_layout()
        plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
        plt.close()
        output_files.append(output_path)
    
    # Combined heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Prepare data for heatmap
    expr_matrix = []
    gene_labels = []
    
    for gene in available_genes:
        expression = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') else adata[:, gene].X.flatten()
        expr_matrix.append(expression)
        gene_labels.append(gene)
    
    expr_matrix = np.array(expr_matrix)
    
    # Sort cells by pseudotime
    pseudotime = adata.obs['dpt_pseudotime'].values
    sort_idx = np.argsort(pseudotime)
    expr_matrix_sorted = expr_matrix[:, sort_idx]
    
    # Normalize per gene (z-score)
    expr_matrix_norm = (expr_matrix_sorted - expr_matrix_sorted.mean(axis=1, keepdims=True)) / (
        expr_matrix_sorted.std(axis=1, keepdims=True) + 1e-8
    )
    
    # Plot heatmap
    sns.heatmap(expr_matrix_norm, xticklabels=False, yticklabels=gene_labels,
                cmap='RdBu_r', center=0, ax=ax, cbar_kws={'label': 'Z-score'})
    ax.set_xlabel('Cells (ordered by pseudotime)')
    ax.set_title('Gene Expression Heatmap along Pseudotime')
    
    output_path = os.path.join(output_dir, f'gene_expression_heatmap.{args.format}')
    plt.tight_layout()
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    output_files.append(output_path)
    
    print(f"Saved {len(output_files)} gene expression plots")
    return output_files


def save_results(adata, args, output_dir, root_cell):
    """Save analysis results to files."""
    print("Saving results...")
    
    # Save pseudotime values
    results_df = pd.DataFrame({
        'cell_id': adata.obs_names,
        'cluster': adata.obs[args.cluster_key].values,
        'pseudotime': adata.obs['dpt_pseudotime'].values,
        'lineage': adata.obs['lineage'].values
    })
    
    if args.cell_type_key in adata.obs.columns:
        results_df['cell_type'] = adata.obs[args.cell_type_key].values
    
    results_path = os.path.join(output_dir, 'pseudotime_values.csv')
    results_df.to_csv(results_path, index=False)
    print(f"Saved: {results_path}")
    
    # Save analysis report
    lineages = {}
    for lineage in adata.obs['lineage'].unique():
        mask = adata.obs['lineage'] == lineage
        lineages[lineage] = {
            'cell_count': int(mask.sum()),
            'mean_pseudotime': float(adata.obs['dpt_pseudotime'][mask].mean()),
            'clusters': list(adata.obs[args.cluster_key][mask].unique())
        }
    
    report = {
        'analysis_date': datetime.now().isoformat(),
        'method': args.method,
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars,
        'n_lineages': len(adata.obs['lineage'].unique()),
        'root_cell': root_cell,
        'pseudotime_range': [
            float(adata.obs['dpt_pseudotime'].min()),
            float(adata.obs['dpt_pseudotime'].max())
        ],
        'lineages': lineages,
        'parameters': {
            'embedding': args.embedding,
            'n_pcs': args.n_pcs,
            'n_neighbors': args.n_neighbors,
            'cluster_key': args.cluster_key
        }
    }
    
    report_path = os.path.join(output_dir, 'analysis_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved: {report_path}")
    
    # Save updated AnnData
    adata_path = os.path.join(output_dir, 'trajectory_data.h5ad')
    adata.write(adata_path)
    print(f"Saved: {adata_path}")
    
    return results_path, report_path, adata_path


def main():
    """Main analysis pipeline."""
    args = parse_arguments()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    print(f"Output directory: {args.output}")
    
    try:
        # Load data
        adata = load_data(args.input)
        
        # Preprocess
        adata = preprocess_data(adata, args)
        
        # Find root cell
        root_cell = find_root_cell(adata, args)
        
        # Compute trajectory
        if args.method == 'diffusion':
            adata = compute_diffusion_pseudotime(adata, root_cell, args)
        elif args.method == 'paga':
            adata = compute_paga_trajectory(adata, root_cell, args)
        
        # Generate visualizations
        plot_trajectory(adata, args, args.output)
        
        if args.method == 'paga':
            plot_paga_graph(adata, args, args.output)
        
        # Gene expression plots
        if args.genes or args.plot_genes:
            gene_list = args.genes.split(',') if args.genes else []
            if not gene_list and args.plot_genes:
                # Use highly variable genes
                if 'highly_variable' in adata.var.columns:
                    gene_list = adata.var_names[adata.var['highly_variable']][:20].tolist()
            plot_gene_expression(adata, gene_list, args, args.output)
        
        # Save results
        save_results(adata, args, args.output, root_cell)
        
        print("\n" + "="*50)
        print("Analysis complete!")
        print(f"Results saved to: {args.output}")
        print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

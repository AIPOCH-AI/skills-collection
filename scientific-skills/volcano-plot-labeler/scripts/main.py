#!/usr/bin/env python3
"""
Volcano Plot Labeler

Automatically identifies and labels the Top 10 most significant genes
in volcano plots using a repulsion algorithm to prevent label overlap.

Author: OpenClaw
Skill ID: 148
"""

import argparse
import sys
import warnings
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import LineCollection
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Please install: pip install pandas matplotlib numpy")
    sys.exit(1)


def calculate_significance_score(log2fc, pvalue):
    """
    Calculate combined significance score for ranking genes.
    Score = |log2FC| * -log10(pvalue)
    
    Parameters:
    -----------
    log2fc : float or array
        Log2 fold change value(s)
    pvalue : float or array
        P-value(s)
    
    Returns:
    --------
    float or array
        Significance score(s)
    """
    # Handle zero p-values
    pvalue = np.maximum(pvalue, 1e-300)
    return np.abs(log2fc) * (-np.log10(pvalue))


def repulsion_algorithm(label_positions, gene_positions, 
                        box_widths, box_heights,
                        iterations=100, repulsion_force=0.05,
                        spring_force=0.01, boundary_margin=0.05):
    """
    Apply repulsion algorithm to prevent label overlap.
    
    Uses force-directed positioning:
    - Repulsive force between overlapping labels
    - Spring force pulling label toward its gene point
    - Boundary forces to keep labels within plot area
    
    Parameters:
    -----------
    label_positions : np.ndarray (N, 2)
        Initial label positions (x, y)
    gene_positions : np.ndarray (N, 2)
        Gene point positions (x, y)
    box_widths : np.ndarray (N,)
        Width of each label box
    box_heights : np.ndarray (N,)
        Height of each label box
    iterations : int
        Number of optimization iterations
    repulsion_force : float
        Strength of repulsion between overlapping boxes
    spring_force : float
        Strength of spring pulling label to gene point
    boundary_margin : float
        Margin from plot boundaries (relative to data range)
    
    Returns:
    --------
    np.ndarray (N, 2)
        Optimized label positions
    """
    positions = label_positions.copy().astype(float)
    n_labels = len(positions)
    
    if n_labels == 0:
        return positions
    
    # Calculate data bounds
    x_min, x_max = gene_positions[:, 0].min(), gene_positions[:, 0].max()
    y_min, y_max = gene_positions[:, 1].min(), gene_positions[:, 1].max()
    
    # Add some padding
    x_range = x_max - x_min
    y_range = y_max - y_min
    x_min -= x_range * boundary_margin
    x_max += x_range * boundary_margin
    y_min -= y_range * boundary_margin
    y_max += y_range * boundary_margin
    
    for iteration in range(iterations):
        forces = np.zeros_like(positions)
        
        # Calculate repulsive forces between all label pairs
        for i in range(n_labels):
            for j in range(i + 1, n_labels):
                dx = positions[i, 0] - positions[j, 0]
                dy = positions[i, 1] - positions[j, 1]
                
                # Check for overlap considering box sizes
                overlap_x = (box_widths[i] + box_widths[j]) / 2 - abs(dx)
                overlap_y = (box_heights[i] + box_heights[j]) / 2 - abs(dy)
                
                if overlap_x > 0 and overlap_y > 0:
                    # Boxes overlap - calculate repulsion
                    if abs(dx) < 1e-10:
                        dx = 1e-10
                    if abs(dy) < 1e-10:
                        dy = 1e-10
                    
                    # Normalize direction
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist > 0:
                        # Stronger repulsion when overlap is larger
                        overlap_factor = min(overlap_x, overlap_y)
                        force_magnitude = repulsion_force * (1 + overlap_factor)
                        
                        fx = (dx / dist) * force_magnitude
                        fy = (dy / dist) * force_magnitude
                        
                        forces[i, 0] += fx
                        forces[i, 1] += fy
                        forces[j, 0] -= fx
                        forces[j, 1] -= fy
        
        # Calculate spring forces (pull toward gene point)
        for i in range(n_labels):
            dx = gene_positions[i, 0] - positions[i, 0]
            dy = gene_positions[i, 1] - positions[i, 1]
            
            forces[i, 0] += dx * spring_force
            forces[i, 1] += dy * spring_force
        
        # Apply boundary constraints
        for i in range(n_labels):
            half_width = box_widths[i] / 2
            half_height = box_heights[i] / 2
            
            # Left boundary
            if positions[i, 0] - half_width < x_min:
                forces[i, 0] += (x_min - (positions[i, 0] - half_width)) * 0.1
            # Right boundary
            if positions[i, 0] + half_width > x_max:
                forces[i, 0] -= ((positions[i, 0] + half_width) - x_max) * 0.1
            # Bottom boundary
            if positions[i, 1] - half_height < y_min:
                forces[i, 1] += (y_min - (positions[i, 1] - half_height)) * 0.1
            # Top boundary
            if positions[i, 1] + half_height > y_max:
                forces[i, 1] -= ((positions[i, 1] + half_height) - y_max) * 0.1
        
        # Apply forces with damping
        damping = 1.0 - (iteration / iterations) * 0.5  # Reduce damping over time
        positions += forces * damping
    
    return positions


def label_volcano_plot(df, 
                       log2fc_col='log2FoldChange',
                       pvalue_col='padj',
                       gene_col='gene_name',
                       top_n=10,
                       pvalue_threshold=0.05,
                       log2fc_threshold=1.0,
                       figsize=(10, 10),
                       repulsion_iterations=100,
                       repulsion_force=0.05,
                       label_fontsize=10,
                       label_color='black',
                       arrow_color='gray',
                       arrow_linewidth=0.8,
                       point_size=20,
                       alpha=0.6,
                       colors=None,
                       title=None,
                       save_path=None,
                       dpi=300):
    """
    Create a volcano plot with automatically labeled top significant genes.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input data containing log2FC, p-values, and gene names
    log2fc_col : str
        Column name for log2 fold change values
    pvalue_col : str
        Column name for p-values (adjusted or raw)
    gene_col : str
        Column name for gene identifiers
    top_n : int
        Number of top genes to label
    pvalue_threshold : float
        P-value threshold for significance
    log2fc_threshold : float
        Log2FC threshold for significance
    figsize : tuple
        Figure size (width, height)
    repulsion_iterations : int
        Number of iterations for repulsion algorithm
    repulsion_force : float
        Strength of repulsion force
    label_fontsize : int
        Font size for gene labels
    label_color : str
        Color for label text
    arrow_color : str
        Color for leader lines
    arrow_linewidth : float
        Width of leader lines
    point_size : int
        Size of scatter points
    alpha : float
        Transparency of points
    colors : dict
        Custom colors for {'up', 'down', 'not_sig'}
    title : str
        Plot title
    save_path : str
        Path to save the figure (optional)
    dpi : int
        DPI for saved figure
    
    Returns:
    --------
    matplotlib.figure.Figure
        The generated figure
    """
    # Default colors
    if colors is None:
        colors = {
            'up': '#D62728',      # Red
            'down': '#1F77B4',    # Blue
            'not_sig': '#7F7F7F'  # Gray
        }
    
    # Create a copy to avoid modifying original
    data = df.copy()
    
    # Handle missing values
    data = data.dropna(subset=[log2fc_col, pvalue_col])
    
    # Replace zero p-values with small number
    data[pvalue_col] = data[pvalue_col].replace(0, 1e-300)
    
    # Calculate -log10(pvalue)
    data['-log10(pvalue)'] = -np.log10(data[pvalue_col])
    
    # Calculate significance score
    data['significance_score'] = calculate_significance_score(
        data[log2fc_col].values, 
        data[pvalue_col].values
    )
    
    # Classify genes
    data['group'] = 'not_sig'
    up_mask = (data[log2fc_col] >= log2fc_threshold) & (data[pvalue_col] < pvalue_threshold)
    down_mask = (data[log2fc_col] <= -log2fc_threshold) & (data[pvalue_col] < pvalue_threshold)
    data.loc[up_mask, 'group'] = 'up'
    data.loc[down_mask, 'group'] = 'down'
    
    # Get top N significant genes
    top_genes = data.nlargest(top_n, 'significance_score')
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot points
    for group in ['up', 'down', 'not_sig']:
        group_data = data[data['group'] == group]
        ax.scatter(group_data[log2fc_col], 
                   group_data['-log10(pvalue)'],
                   c=colors[group],
                   s=point_size,
                   alpha=alpha,
                   edgecolors='none',
                   label=group.replace('_', ' ').title())
    
    # Add threshold lines
    ax.axhline(-np.log10(pvalue_threshold), color='gray', linestyle='--', 
               linewidth=1, alpha=0.5)
    ax.axvline(-log2fc_threshold, color='gray', linestyle='--', 
               linewidth=1, alpha=0.5)
    ax.axvline(log2fc_threshold, color='gray', linestyle='--', 
               linewidth=1, alpha=0.5)
    
    # Prepare label positions
    label_positions = []
    gene_positions = []
    labels = []
    
    # Get renderer for text size calculations
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    
    box_widths = []
    box_heights = []
    
    for _, row in top_genes.iterrows():
        x = row[log2fc_col]
        y = row['-log10(pvalue)']
        gene_name = str(row[gene_col])
        
        gene_positions.append([x, y])
        labels.append(gene_name)
        
        # Calculate text extent
        text = ax.text(x, y, gene_name, fontsize=label_fontsize, 
                       ha='center', va='center')
        bbox = text.get_window_extent(renderer=renderer)
        # Convert from display to data coordinates
        inv_transform = ax.transData.inverted()
        bbox_data = bbox.transformed(inv_transform)
        
        width = bbox_data.width * 1.2  # Add padding
        height = bbox_data.height * 1.4
        
        box_widths.append(width)
        box_heights.append(height)
        label_positions.append([x, y])
        
        text.remove()
    
    # Apply repulsion algorithm if there are labels
    if len(label_positions) > 0:
        label_positions = np.array(label_positions)
        gene_positions = np.array(gene_positions)
        box_widths = np.array(box_widths)
        box_heights = np.array(box_heights)
        
        optimized_positions = repulsion_algorithm(
            label_positions, gene_positions,
            box_widths, box_heights,
            iterations=repulsion_iterations,
            repulsion_force=repulsion_force
        )
        
        # Draw labels and leader lines
        for i, (gene_pos, label_pos, label) in enumerate(
            zip(gene_positions, optimized_positions, labels)):
            
            # Draw leader line
            if not np.allclose(gene_pos, label_pos, rtol=1e-3):
                ax.annotate('', xy=gene_pos, xytext=label_pos,
                           arrowprops=dict(arrowstyle='-', color=arrow_color,
                                         lw=arrow_linewidth))
            
            # Draw label with background
            ax.text(label_pos[0], label_pos[1], label,
                   fontsize=label_fontsize,
                   color=label_color,
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3',
                            facecolor='white',
                            edgecolor='none',
                            alpha=0.9))
    
    # Labels and title
    ax.set_xlabel('Log2 Fold Change', fontsize=12)
    ax.set_ylabel('-Log10 Adjusted P-value', fontsize=12)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Legend
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Adjust limits to accommodate labels
    all_x = list(data[log2fc_col]) + list(optimized_positions[:, 0] if len(label_positions) > 0 else [])
    all_y = list(data['-log10(pvalue)']) + list(optimized_positions[:, 1] if len(label_positions) > 0 else [])
    
    x_margin = (max(all_x) - min(all_x)) * 0.15
    y_margin = (max(all_y) - min(all_y)) * 0.15
    
    ax.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
    ax.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Saved to: {save_path}")
    
    return fig


def main():
    parser = argparse.ArgumentParser(
        description='Generate labeled volcano plot with repulsion algorithm'
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input CSV/TSV file with differential expression results')
    parser.add_argument('--output', '-o', required=True,
                       help='Output figure path')
    parser.add_argument('--log2fc-col', default='log2FoldChange',
                       help='Column name for log2 fold change')
    parser.add_argument('--pvalue-col', default='padj',
                       help='Column name for p-value')
    parser.add_argument('--gene-col', default='gene_name',
                       help='Column name for gene names')
    parser.add_argument('--top-n', type=int, default=10,
                       help='Number of top genes to label')
    parser.add_argument('--pvalue-threshold', type=float, default=0.05,
                       help='P-value threshold')
    parser.add_argument('--log2fc-threshold', type=float, default=1.0,
                       help='Log2FC threshold')
    parser.add_argument('--figsize', nargs=2, type=float, default=[10, 10],
                       help='Figure size (width height)')
    parser.add_argument('--repulsion-iterations', type=int, default=100,
                       help='Iterations for repulsion algorithm')
    parser.add_argument('--repulsion-force', type=float, default=0.05,
                       help='Repulsion force strength')
    parser.add_argument('--label-fontsize', type=int, default=10,
                       help='Label font size')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Output DPI')
    parser.add_argument('--title',
                       help='Plot title')
    
    args = parser.parse_args()
    
    # Load data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    if args.input.endswith('.tsv') or args.input.endswith('.txt'):
        df = pd.read_csv(args.input, sep='\t')
    else:
        df = pd.read_csv(args.input)
    
    print(f"Loaded {len(df)} genes from {args.input}")
    
    # Validate columns
    required_cols = [args.log2fc_col, args.pvalue_col, args.gene_col]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Generate plot
    fig = label_volcano_plot(
        df,
        log2fc_col=args.log2fc_col,
        pvalue_col=args.pvalue_col,
        gene_col=args.gene_col,
        top_n=args.top_n,
        pvalue_threshold=args.pvalue_threshold,
        log2fc_threshold=args.log2fc_threshold,
        figsize=tuple(args.figsize),
        repulsion_iterations=args.repulsion_iterations,
        repulsion_force=args.repulsion_force,
        label_fontsize=args.label_fontsize,
        title=args.title,
        save_path=args.output,
        dpi=args.dpi
    )
    
    print(f"Generated volcano plot with top {args.top_n} labeled genes")


if __name__ == '__main__':
    main()

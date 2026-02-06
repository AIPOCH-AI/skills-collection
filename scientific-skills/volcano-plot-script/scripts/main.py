#!/usr/bin/env python3
"""
Volcano Plot Generator

Generate publication-ready volcano plots from DEG analysis results.
Supports both Python (matplotlib/seaborn) and R (ggplot2) outputs.

Author: Auto-generated
Date: 2025-02-05
"""

import argparse
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate volcano plots from DEG analysis results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input deg_results.csv --output volcano.png
  python main.py --input results.tsv --log2fc-col logFC --pvalue-col FDR --top-n 20
  python main.py --input data.csv --label-genes markers.txt --output plot.pdf
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='Input file (CSV/TSV) with DEG results')
    parser.add_argument('--output', '-o', default='volcano_plot.png',
                        help='Output plot file (png/pdf/svg)')
    parser.add_argument('--log2fc-col', default='log2FoldChange',
                        help='Column name for log2 fold change (default: log2FoldChange)')
    parser.add_argument('--pvalue-col', default='padj',
                        help='Column name for adjusted p-value (default: padj)')
    parser.add_argument('--gene-col', default='gene',
                        help='Column name for gene identifiers (default: gene)')
    parser.add_argument('--log2fc-thresh', type=float, default=1.0,
                        help='Log2 fold change threshold for significance (default: 1.0)')
    parser.add_argument('--pvalue-thresh', type=float, default=0.05,
                        help='P-value threshold for significance (default: 0.05)')
    parser.add_argument('--label-genes', type=str,
                        help='File containing list of genes to label (one per line)')
    parser.add_argument('--top-n', type=int, default=10,
                        help='Label top N most significant genes (default: 10)')
    parser.add_argument('--color-up', default='#E74C3C',
                        help='Color for upregulated genes (default: #E74C3C)')
    parser.add_argument('--color-down', default='#3498DB',
                        help='Color for downregulated genes (default: #3498DB)')
    parser.add_argument('--color-ns', default='#95A5A6',
                        help='Color for non-significant genes (default: #95A5A6)')
    parser.add_argument('--figsize', type=str, default='10,8',
                        help='Figure size as width,height (default: 10,8)')
    parser.add_argument('--dpi', type=int, default=300,
                        help='DPI for output image (default: 300)')
    parser.add_argument('--title', type=str, default='Volcano Plot',
                        help='Plot title')
    parser.add_argument('--xlabel', type=str, default='Log2 Fold Change',
                        help='X-axis label')
    parser.add_argument('--ylabel', type=str, default='-Log10 Adjusted P-value',
                        help='Y-axis label')
    parser.add_argument('--no-labels', action='store_true',
                        help='Do not label any genes')
    parser.add_argument('--export-r', action='store_true',
                        help='Also export an R script')
    parser.add_argument('--sig-genes-output', type=str,
                        help='Export significant genes to CSV file')
    
    return parser.parse_args()


def load_data(filepath):
    """Load DEG results from file."""
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    # Detect file type and read
    if filepath.suffix.lower() == '.tsv' or filepath.suffix.lower() == '.txt':
        df = pd.read_csv(filepath, sep='\t')
    elif filepath.suffix.lower() == '.csv':
        df = pd.read_csv(filepath)
    else:
        # Try auto-detection
        try:
            df = pd.read_csv(filepath, sep='\t')
        except:
            df = pd.read_csv(filepath)
    
    return df


def validate_columns(df, log2fc_col, pvalue_col, gene_col):
    """Validate that required columns exist."""
    missing = []
    
    if log2fc_col not in df.columns:
        missing.append(f"log2FC column '{log2fc_col}'")
    if pvalue_col not in df.columns:
        missing.append(f"p-value column '{pvalue_col}'")
    if gene_col not in df.columns:
        # Try common alternatives
        alternatives = ['Gene', 'gene_name', 'GeneSymbol', 'symbol', 'SYMBOL', 
                       'gene_id', 'ID', 'id', 'ensembl', 'ENSEMBL']
        for alt in alternatives:
            if alt in df.columns:
                print(f"Note: Using '{alt}' as gene column")
                gene_col = alt
                break
        else:
            missing.append(f"gene column '{gene_col}'")
    
    if missing:
        print(f"Error: Missing columns: {', '.join(missing)}")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)
    
    return gene_col


def process_data(df, log2fc_col, pvalue_col, log2fc_thresh, pvalue_thresh):
    """Process data and classify genes."""
    # Make a copy to avoid modifying original
    data = df.copy()
    
    # Handle zero or negative p-values
    data[pvalue_col] = data[pvalue_col].replace(0, np.nan)
    data = data.dropna(subset=[pvalue_col, log2fc_col])
    
    # Calculate -log10(p-value)
    data['negLog10_pvalue'] = -np.log10(data[pvalue_col])
    
    # Classify genes
    conditions = [
        (data[pvalue_col] < pvalue_thresh) & (data[log2fc_col] > log2fc_thresh),
        (data[pvalue_col] < pvalue_thresh) & (data[log2fc_col] < -log2fc_thresh),
    ]
    choices = ['up', 'down']
    
    data['regulation'] = np.select(conditions, choices, default='ns')
    
    return data


def get_genes_to_label(data, gene_col, label_genes_file, top_n, no_labels):
    """Determine which genes to label."""
    if no_labels:
        return []
    
    genes_to_label = []
    
    # Load custom gene list if provided
    if label_genes_file and Path(label_genes_file).exists():
        with open(label_genes_file, 'r') as f:
            genes_to_label = [line.strip() for line in f if line.strip()]
    
    # Add top N significant genes
    if top_n > 0:
        # Sort by p-value
        top_genes = data.nsmallest(top_n, data.columns[data.columns.str.contains('pvalue|padj|fdr', case=False)][0])
        genes_to_label.extend(top_genes[gene_col].tolist())
    
    # Remove duplicates
    genes_to_label = list(set(genes_to_label))
    
    # Filter to only genes present in data
    genes_to_label = [g for g in genes_to_label if g in data[gene_col].values]
    
    return genes_to_label


def create_volcano_plot(data, gene_col, log2fc_col, pvalue_col, genes_to_label, args):
    """Create the volcano plot."""
    # Parse figure size
    figsize = tuple(map(float, args.figsize.split(',')))
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=args.dpi)
    
    # Separate data by regulation
    up_data = data[data['regulation'] == 'up']
    down_data = data[data['regulation'] == 'down']
    ns_data = data[data['regulation'] == 'ns']
    
    # Plot points
    ax.scatter(ns_data[log2fc_col], ns_data['negLog10_pvalue'], 
               c=args.color_ns, s=15, alpha=0.6, edgecolors='none', label='Not significant')
    ax.scatter(down_data[log2fc_col], down_data['negLog10_pvalue'], 
               c=args.color_down, s=20, alpha=0.8, edgecolors='none', label='Downregulated')
    ax.scatter(up_data[log2fc_col], up_data['negLog10_pvalue'], 
               c=args.color_up, s=20, alpha=0.8, edgecolors='none', label='Upregulated')
    
    # Add threshold lines
    ax.axhline(-np.log10(args.pvalue_thresh), color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(-args.log2fc_thresh, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(args.log2fc_thresh, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    # Label genes
    if genes_to_label:
        label_data = data[data[gene_col].isin(genes_to_label)]
        
        # Simple label placement - adjust as needed
        for _, row in label_data.iterrows():
            ax.annotate(row[gene_col], 
                       xy=(row[log2fc_col], row['negLog10_pvalue']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3, edgecolor='none'))
    
    # Set labels and title
    ax.set_xlabel(args.xlabel, fontsize=12)
    ax.set_ylabel(args.ylabel, fontsize=12)
    ax.set_title(args.title, fontsize=14, fontweight='bold')
    
    # Add legend
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
    
    # Count statistics
    n_up = len(up_data)
    n_down = len(down_data)
    n_ns = len(ns_data)
    
    # Add stats text box
    stats_text = f"Up: {n_up}\nDown: {n_down}\nNot Sig: {n_ns}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, (n_up, n_down, n_ns)


def export_r_script(args, output_path):
    """Export equivalent R script."""
    r_script = f'''# Volcano Plot Script (R/ggplot2)
# Generated by volcano-plot-script

library(ggplot2)
library(dplyr)

# Read data
data <- read.csv("{args.input}")

# Parameters
log2fc_col <- "{args.log2fc_col}"
pvalue_col <- "{args.pvalue_col}"
gene_col <- "{args.gene_col}"
log2fc_thresh <- {args.log2fc_thresh}
pvalue_thresh <- {args.pvalue_thresh}

# Process data
data$negLog10_pvalue <- -log10(data[[pvalue_col]])

data <- data %>%
  mutate(regulation = case_when(
    .data[[pvalue_col]] < pvalue_thresh & .data[[log2fc_col]] > log2fc_thresh ~ "up",
    .data[[pvalue_col]] < pvalue_thresh & .data[[log2fc_col]] < -log2fc_thresh ~ "down",
    TRUE ~ "ns"
  ))

# Create plot
p <- ggplot(data, aes(x=.data[[log2fc_col]], y=negLog10_pvalue, color=regulation)) +
  geom_point(alpha=0.6, size=1.5) +
  scale_color_manual(values=c("up"="{args.color_up}", 
                              "down"="{args.color_down}", 
                              "ns"="{args.color_ns}"),
                     labels=c("up"="Upregulated", 
                              "down"="Downregulated", 
                              "ns"="Not significant")) +
  geom_hline(yintercept=-log10(pvalue_thresh), linetype="dashed", color="gray") +
  geom_vline(xintercept=c(-log2fc_thresh, log2fc_thresh), linetype="dashed", color="gray") +
  labs(x="{args.xlabel}", y="{args.ylabel}", title="{args.title}") +
  theme_minimal() +
  theme(legend.position="bottom")

# Save plot
ggsave("{output_path}", p, width=10, height=8, dpi={args.dpi})
print(paste("Plot saved to:", "{output_path}"))
'''
    
    r_output_path = output_path.with_suffix('.R')
    with open(r_output_path, 'w') as f:
        f.write(r_script)
    
    print(f"R script exported to: {r_output_path}")


def export_significant_genes(data, output_path, gene_col):
    """Export significant genes to CSV."""
    sig_genes = data[data['regulation'].isin(['up', 'down'])]
    sig_genes.to_csv(output_path, index=False)
    print(f"Significant genes exported to: {output_path}")


def main():
    """Main function."""
    args = parse_arguments()
    
    print(f"Loading data from: {args.input}")
    df = load_data(args.input)
    print(f"Loaded {len(df)} genes")
    
    # Validate columns
    gene_col = validate_columns(df, args.log2fc_col, args.pvalue_col, args.gene_col)
    
    # Process data
    print("Processing data...")
    data = process_data(df, args.log2fc_col, args.pvalue_col, 
                        args.log2fc_thresh, args.pvalue_thresh)
    
    # Get genes to label
    genes_to_label = get_genes_to_label(data, gene_col, args.label_genes, 
                                        args.top_n, args.no_labels)
    
    # Create plot
    print("Creating volcano plot...")
    fig, stats = create_volcano_plot(data, gene_col, args.log2fc_col, 
                                      args.pvalue_col, genes_to_label, args)
    
    # Save plot
    output_path = Path(args.output)
    fig.savefig(output_path, dpi=args.dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path}")
    
    # Print summary
    print(f"\\nSummary:")
    print(f"  Upregulated: {stats[0]} genes (log2FC > {args.log2fc_thresh}, p < {args.pvalue_thresh})")
    print(f"  Downregulated: {stats[1]} genes (log2FC < -{args.log2fc_thresh}, p < {args.pvalue_thresh})")
    print(f"  Not significant: {stats[2]} genes")
    
    # Export R script if requested
    if args.export_r:
        export_r_script(args, output_path)
    
    # Export significant genes if requested
    if args.sig_genes_output:
        export_significant_genes(data, args.sig_genes_output, gene_col)
    
    print("\\nDone!")


if __name__ == '__main__':
    main()

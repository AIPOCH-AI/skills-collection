#!/usr/bin/env python3
"""
GO/KEGG Enrichment Analysis Pipeline

Automated pipeline for Gene Ontology and KEGG pathway enrichment analysis.
Supports multiple organisms, ID types, and generates comprehensive visualizations.

Author: AI Assistant
Technical Difficulty: High
"""

import argparse
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd


# Organism mapping configuration
ORGANISM_CONFIG = {
    "human": {
        "scientific_name": "Homo sapiens",
        "kegg_code": "hsa",
        "orgdb": "org.Hs.eg.db",
        "tax_id": "9606"
    },
    "mouse": {
        "scientific_name": "Mus musculus", 
        "kegg_code": "mmu",
        "orgdb": "org.Mm.eg.db",
        "tax_id": "10090"
    },
    "rat": {
        "scientific_name": "Rattus norvegicus",
        "kegg_code": "rno", 
        "orgdb": "org.Rn.eg.db",
        "tax_id": "10116"
    },
    "zebrafish": {
        "scientific_name": "Danio rerio",
        "kegg_code": "dre",
        "orgdb": "org.Dr.eg.db",
        "tax_id": "7955"
    },
    "fly": {
        "scientific_name": "Drosophila melanogaster",
        "kegg_code": "dme",
        "orgdb": "org.Dm.eg.db",
        "tax_id": "7227"
    },
    "yeast": {
        "scientific_name": "Saccharomyces cerevisiae",
        "kegg_code": "sce",
        "orgdb": "org.Sc.sgd.db",
        "tax_id": "4932"
    }
}


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="GO/KEGG Enrichment Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic GO and KEGG analysis
  python main.py --genes gene_list.txt --organism human
  
  # KEGG only with custom cutoff
  python main.py --genes genes.txt --analysis kegg --pvalue-cutoff 0.01
  
  # GO only with specific ontologies
  python main.py --genes genes.txt --analysis go --go-ontologies BP,MF
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--genes", "-g",
        type=str,
        required=True,
        help="Path to gene list file (one gene per line)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--organism", "-o",
        type=str,
        default="human",
        choices=list(ORGANISM_CONFIG.keys()),
        help="Organism (default: human)"
    )
    parser.add_argument(
        "--id-type",
        type=str,
        default="symbol",
        choices=["symbol", "entrez", "ensembl", "refseq"],
        help="Gene ID type (default: symbol)"
    )
    parser.add_argument(
        "--background", "-b",
        type=str,
        default=None,
        help="Background gene list file (default: all genes)"
    )
    parser.add_argument(
        "--analysis", "-a",
        type=str,
        default="all",
        choices=["go", "kegg", "all"],
        help="Analysis type (default: all)"
    )
    parser.add_argument(
        "--go-ontologies",
        type=str,
        default="BP,MF,CC",
        help="GO ontologies to analyze, comma-separated (default: BP,MF,CC)"
    )
    parser.add_argument(
        "--pvalue-cutoff",
        type=float,
        default=0.05,
        help="P-value cutoff for significance (default: 0.05)"
    )
    parser.add_argument(
        "--qvalue-cutoff",
        type=float,
        default=0.2,
        help="Adjusted p-value (q-value) cutoff (default: 0.2)"
    )
    parser.add_argument(
        "--output", "-out",
        type=str,
        default="./enrichment_results",
        help="Output directory (default: ./enrichment_results)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="all",
        choices=["csv", "tsv", "excel", "all"],
        help="Output format (default: all)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top terms to visualize (default: 20)"
    )
    parser.add_argument(
        "--min-genes",
        type=int,
        default=10,
        help="Minimum genes in category (default: 10)"
    )
    parser.add_argument(
        "--max-genes",
        type=int,
        default=500,
        help="Maximum genes in category (default: 500)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> Tuple[bool, str]:
    """Validate input files and parameters."""
    # Check gene file exists
    if not os.path.exists(args.genes):
        return False, f"Gene list file not found: {args.genes}"
    
    # Check background file if provided
    if args.background and not os.path.exists(args.background):
        return False, f"Background file not found: {args.background}"
    
    # Check cutoffs are valid
    if not 0 < args.pvalue_cutoff <= 1:
        return False, "P-value cutoff must be between 0 and 1"
    if not 0 < args.qvalue_cutoff <= 1:
        return False, "Q-value cutoff must be between 0 and 1"
    
    # Check R is installed
    try:
        subprocess.run(["Rscript", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "R is not installed or not in PATH"
    
    return True, "Validation passed"


def read_gene_list(filepath: str) -> List[str]:
    """Read gene list from file."""
    genes = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle CSV/TSV format
                if ',' in line:
                    genes.append(line.split(',')[0])
                elif '\t' in line:
                    genes.append(line.split('\t')[0])
                else:
                    genes.append(line)
    return list(set(genes))  # Remove duplicates


def create_output_directories(base_path: str) -> Dict[str, str]:
    """Create output directory structure."""
    dirs = {
        'base': base_path,
        'go': os.path.join(base_path, 'go_enrichment'),
        'kegg': os.path.join(base_path, 'kegg_enrichment'),
        'visualization': os.path.join(base_path, 'visualization'),
        'pathview': os.path.join(base_path, 'kegg_enrichment', 'pathview')
    }
    
    for path in dirs.values():
        os.makedirs(path, exist_ok=True)
    
    return dirs


def generate_r_script(args: argparse.Namespace, 
                      gene_list: List[str],
                      output_dirs: Dict[str, str]) -> str:
    """Generate R script for enrichment analysis."""
    
    organism_config = ORGANISM_CONFIG[args.organism]
    gene_list_str = '", "'.join(gene_list)
    
    # Determine analysis components
    do_go = args.analysis in ["go", "all"]
    do_kegg = args.analysis in ["kegg", "all"]
    
    # Parse GO ontologies
    go_ontologies = args.go_ontologies.split(',')
    
    # Prepare background genes
    background_str = ""
    if args.background:
        bg_genes = read_gene_list(args.background)
        background_str = '", "'.join(bg_genes)
    
    r_script = f'''
# GO/KEGG Enrichment Analysis Script
# Auto-generated by go-kegg-enrichment pipeline

suppressMessages(library(clusterProfiler))
suppressMessages(library(org.Hs.eg.db))
suppressMessages(library(org.Mm.eg.db))
suppressMessages(library(org.Rn.eg.db))
suppressMessages(library(org.Dr.eg.db))
suppressMessages(library(org.Dm.eg.db))
suppressMessages(library(org.Sc.sgd.db))
suppressMessages(library(enrichplot))
suppressMessages(library(ggplot2))
suppressMessages(library(dplyr))
suppressMessages(library(readr))

# Configuration
organism <- "{args.organism}"
kegg_code <- "{organism_config['kegg_code']}"
orgdb <- "{organism_config['orgdb']}"
id_type <- "{args.id_type}"
pvalue_cutoff <- {args.pvalue_cutoff}
qvalue_cutoff <- {args.qvalue_cutoff}
top_n <- {args.top_n}
min_genes <- {args.min_genes}
max_genes <- {args.max_genes}

# Load gene list
genes <- c("{gene_list_str}")

# Load background if provided
{background_str and f'background <- c("{background_str}")' or 'background <- NULL'}

# ID type mapping
id_type_map <- list(
    symbol = "SYMBOL",
    entrez = "ENTREZID", 
    ensembl = "ENSEMBL",
    refseq = "REFSEQ"
)
keytype <- id_type_map[[id_type]]

# Convert gene IDs if needed
convert_ids <- function(genes, from_type, to_type, orgdb_pkg) {{
    if (from_type == to_type) return(genes)
    
    db <- get(orgdb_pkg)
    conv <- bitr(genes, fromType = from_type, toType = to_type, OrgDb = db)
    return(conv${to_type})
}}

# Convert to ENTREZID for analysis
genes_entrez <- convert_ids(genes, keytype, "ENTREZID", orgdb)
if (!is.null(background)) {{
    bg_entrez <- convert_ids(background, keytype, "ENTREZID", orgdb)
}} else {{
    bg_entrez <- NULL
}}

results_summary <- list()

# GO Enrichment Analysis
if ({str(do_go).lower()}) {{
    cat("\\n=== Running GO Enrichment Analysis ===\\n")
    
    ontologies <- c({', '.join([f'"{o.strip().upper()}"' for o in go_ontologies])})
    
    for (ont in ontologies) {{
        cat(paste("\\nProcessing", ont, "...\\n"))
        
        tryCatch({{
            ego <- enrichGO(
                gene = genes_entrez,
                OrgDb = get(orgdb),
                ont = ont,
                pAdjustMethod = "BH",
                pvalueCutoff = pvalue_cutoff,
                qvalueCutoff = qvalue_cutoff,
                readable = TRUE,
                minGSSize = min_genes,
                maxGSSize = max_genes,
                universe = bg_entrez
            )
            
            if (!is.null(ego) && nrow(ego@result) > 0) {{
                # Save results
                result_file <- file.path("{output_dirs['go']}", 
                                        paste0("GO_", ont, "_results.csv"))
                write.csv(ego@result, result_file, row.names = FALSE)
                cat(paste("Saved:", result_file, "\\n"))
                
                # Store summary
                results_summary[[paste0("GO_", ont)]] <- list(
                    total = nrow(ego@result),
                    significant = sum(ego@result$p.adjust < qvalue_cutoff),
                    top_terms = head(ego@result$Description, 5)
                )
                
                # Bar plot
                if (nrow(ego@result) > 0) {{
                    p <- barplot(ego, showCategory = top_n) +
                        ggtitle(paste("GO", ont, "Enrichment")) +
                        theme(axis.text.y = element_text(size = 8))
                    ggsave(file.path("{output_dirs['go']}", 
                                    paste0("GO_", ont, "_barplot.pdf")),
                           p, width = 10, height = 8)
                }}
                
                # Dot plot
                if (nrow(ego@result) > 0) {{
                    p <- dotplot(ego, showCategory = top_n) +
                        ggtitle(paste("GO", ont, "Enrichment"))
                    ggsave(file.path("{output_dirs['go']}", 
                                    paste0("GO_", ont, "_dotplot.pdf")),
                           p, width = 10, height = 8)
                }}
                
            }} else {{
                cat(paste("No significant", ont, "terms found\\n"))
                results_summary[[paste0("GO_", ont)]] <- list(
                    total = 0,
                    significant = 0,
                    top_terms = character(0)
                )
            }}
            
        }}, error = function(e) {{
            cat(paste("Error in GO", ont, ":", e$message, "\\n"))
            results_summary[[paste0("GO_", ont)]] <- list(
                total = 0,
                significant = 0,
                error = e$message
            )
        }})
    }}
}}

# KEGG Enrichment Analysis
if ({str(do_kegg).lower()}) {{
    cat("\\n=== Running KEGG Enrichment Analysis ===\\n")
    
    tryCatch({{
        kk <- enrichKEGG(
            gene = genes_entrez,
            organism = kegg_code,
            pAdjustMethod = "BH",
            pvalueCutoff = pvalue_cutoff,
            qvalueCutoff = qvalue_cutoff,
            minGSSize = min_genes,
            maxGSSize = max_genes,
            universe = bg_entrez
        )
        
        if (!is.null(kk) && nrow(kk@result) > 0) {{
            # Convert to gene symbols
            kk <- setReadable(kk, OrgDb = get(orgdb), keyType = "ENTREZID")
            
            # Save results
            result_file <- file.path("{output_dirs['kegg']}", "KEGG_results.csv")
            write.csv(kk@result, result_file, row.names = FALSE)
            cat(paste("Saved:", result_file, "\\n"))
            
            # Store summary
            results_summary[["KEGG"]] <- list(
                total = nrow(kk@result),
                significant = sum(kk@result$p.adjust < qvalue_cutoff),
                top_pathways = head(kk@result$Description, 5)
            )
            
            # Bar plot
            p <- barplot(kk, showCategory = top_n) +
                ggtitle("KEGG Pathway Enrichment") +
                theme(axis.text.y = element_text(size = 8))
            ggsave(file.path("{output_dirs['kegg']}", "KEGG_barplot.pdf"),
                   p, width = 10, height = 8)
            
            # Dot plot
            p <- dotplot(kk, showCategory = top_n) +
                ggtitle("KEGG Pathway Enrichment")
            ggsave(file.path("{output_dirs['kegg']}", "KEGG_dotplot.pdf"),
                   p, width = 10, height = 8)
            
            # Gene-Concept Network
            if (nrow(kk@result) >= 3) {{
                tryCatch({{
                    p <- cnetplot(kk, categorySize = "pvalue", 
                                 showCategory = min(5, nrow(kk@result)))
                    ggsave(file.path("{output_dirs['kegg']}", "KEGG_cnetplot.pdf"),
                           p, width = 12, height = 10)
                }}, error = function(e) {{
                    cat("Could not create cnetplot\\n")
                }})
            }}
            
        }} else {{
            cat("No significant KEGG pathways found\\n")
            results_summary[["KEGG"]] <- list(
                total = 0,
                significant = 0,
                top_pathways = character(0)
            )
        }}
        
    }}, error = function(e) {{
        cat(paste("Error in KEGG:", e$message, "\\n"))
        results_summary[["KEGG"]] <- list(
            total = 0,
            significant = 0,
            error = e$message
        )
    }})
}}

# Save summary
summary_file <- file.path("{output_dirs['base']}", "analysis_summary.json")
write(jsonlite::toJSON(results_summary, pretty = TRUE, auto_unbox = TRUE),
      summary_file)
cat(paste("\\nSummary saved to:", summary_file, "\\n"))

cat("\\n=== Analysis Complete ===\\n")
'''
    return r_script


def run_r_script(script_content: str, verbose: bool = False) -> Tuple[bool, str]:
    """Execute R script and capture output."""
    script_path = Path("temp_enrichment_analysis.R")
    
    try:
        # Write script to file
        script_path.write_text(script_content)
        
        # Execute R script
        cmd = ["Rscript", str(script_path)]
        if verbose:
            print(f"Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if verbose:
            print(result.stdout)
        
        if result.returncode != 0:
            return False, f"R script error:\n{result.stderr}"
        
        return True, result.stdout
        
    finally:
        # Cleanup
        if script_path.exists():
            script_path.unlink()


def generate_summary_report(output_dirs: Dict[str, str], 
                           args: argparse.Namespace) -> str:
    """Generate human-readable summary report."""
    
    report_lines = [
        "=" * 60,
        "GO/KEGG ENRICHMENT ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Organism: {ORGANISM_CONFIG[args.organism]['scientific_name']}",
        f"Gene ID Type: {args.id_type}",
        f"Analysis Type: {args.analysis}",
        f"P-value Cutoff: {args.pvalue_cutoff}",
        f"Q-value Cutoff: {args.qvalue_cutoff}",
        "",
        "-" * 60,
        "OUTPUT FILES",
        "-" * 60,
        "",
    ]
    
    # List generated files
    for root, dirs, files in os.walk(output_dirs['base']):
        level = root.replace(output_dirs['base'], '').count(os.sep)
        indent = '  ' * level
        subdir = os.path.basename(root)
        if subdir:
            report_lines.append(f"{indent}{subdir}/")
        
        subindent = '  ' * (level + 1)
        for file in sorted(files):
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.2f} MB"
            report_lines.append(f"{subindent}{file} ({size_str})")
    
    report_lines.extend([
        "",
        "-" * 60,
        "INTERPRETATION GUIDE",
        "-" * 60,
        "",
        "1. GO Enrichment Results:",
        "   - BP: Biological Process - what biological processes are affected",
        "   - MF: Molecular Function - what molecular functions are involved", 
        "   - CC: Cellular Component - where in the cell the genes act",
        "",
        "2. KEGG Pathway Results:",
        "   - Shows affected metabolic and signaling pathways",
        "   - Pathview diagrams show gene expression on pathway maps",
        "",
        "3. Key Statistics:",
        "   - GeneRatio: Proportion of input genes in the term",
        "   - BgRatio: Proportion of background genes in the term",
        "   - pvalue: Statistical significance",
        "   - p.adjust: Benjamini-Hochberg corrected p-value",
        "   - qvalue: FDR-corrected p-value",
        "",
        "=" * 60,
    ])
    
    return '\n'.join(report_lines)


def main():
    """Main entry point."""
    print("=" * 60)
    print("GO/KEGG Enrichment Analysis Pipeline")
    print("=" * 60)
    
    # Parse arguments
    args = parse_arguments()
    
    # Validate inputs
    valid, message = validate_inputs(args)
    if not valid:
        print(f"ERROR: {message}")
        sys.exit(1)
    
    if args.verbose:
        print(f"Validation: {message}")
    
    # Read gene list
    print(f"\nReading gene list from: {args.genes}")
    genes = read_gene_list(args.genes)
    print(f"Loaded {len(genes)} unique genes")
    
    if len(genes) == 0:
        print("ERROR: No genes found in input file")
        sys.exit(1)
    
    if len(genes) < 5:
        print("WARNING: Very few genes provided. Results may be limited.")
    
    # Create output directories
    print(f"\nCreating output directory: {args.output}")
    output_dirs = create_output_directories(args.output)
    
    # Generate and execute R script
    print("\nGenerating enrichment analysis script...")
    r_script = generate_r_script(args, genes, output_dirs)
    
    print("Running enrichment analysis (this may take a few minutes)...")
    print("-" * 40)
    
    success, output = run_r_script(r_script, args.verbose)
    print(output)
    
    if not success:
        print(f"\nERROR: Analysis failed\n{output}")
        sys.exit(1)
    
    print("-" * 40)
    
    # Generate summary report
    report = generate_summary_report(output_dirs, args)
    report_path = os.path.join(output_dirs['base'], 'REPORT.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    print("\n" + report)
    
    # Success message
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nResults available in: {os.path.abspath(args.output)}")
    print("\nNext steps:")
    print("  1. Review CSV files for detailed statistics")
    print("  2. Check PDF visualizations in each folder")
    print("  3. Read REPORT.txt for interpretation guidance")


if __name__ == "__main__":
    main()

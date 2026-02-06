#!/usr/bin/env python3
"""
CRISPR Screen Analyzer
Process CRISPR screening data to identify essential genes.
"""

import argparse
import pandas as pd
import numpy as np
from scipy import stats


class CRISPRScreenAnalyzer:
    """Analyze CRISPR screening data."""
    
    def __init__(self, counts_file, samplesheet):
        self.counts = pd.read_csv(counts_file, sep='\t', index_col=0)
        self.samples = pd.read_csv(samplesheet)
    
    def qc_metrics(self):
        """Calculate quality control metrics."""
        total_reads = self.counts.sum()
        
        # Gini index
        def gini(x):
            x = np.array(x, dtype=float)
            if np.sum(x) == 0:
                return 0
            x = np.sort(x)
            n = len(x)
            cumsum = np.cumsum(x)
            return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        
        gini_scores = self.counts.apply(gini, axis=0)
        zero_counts = (self.counts == 0).sum()
        
        return {
            "total_reads": total_reads.to_dict(),
            "gini_index": gini_scores.to_dict(),
            "zero_count_sgrnas": zero_counts.to_dict()
        }
    
    def calculate_lfc(self, control_samples, treatment_samples):
        """Calculate log fold changes."""
        control_mean = self.counts[control_samples].mean(axis=1)
        treatment_mean = self.counts[treatment_samples].mean(axis=1)
        lfc = np.log2((treatment_mean + 1) / (control_mean + 1))
        return lfc
    
    def rra_analysis(self, lfc, fdr_threshold=0.05):
        """Robust Rank Aggregation analysis."""
        z_scores = (lfc - lfc.mean()) / lfc.std()
        pvalues = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))
        
        # Simplified FDR
        sorted_p = np.sort(pvalues)
        n = len(pvalues)
        fdr = np.minimum.accumulate(sorted_p * n / np.arange(1, n + 1))
        
        results = pd.DataFrame({
            "sgrna": self.counts.index,
            "lfc": lfc,
            "pvalue": pvalues,
            "fdr": fdr
        })
        
        return results
    
    def identify_hits(self, results, fdr_threshold=0.05, lfc_threshold=1):
        """Identify hit sgRNAs and genes."""
        hits = results[
            (results["fdr"] < fdr_threshold) & 
            (np.abs(results["lfc"]) > lfc_threshold)
        ]
        return hits


def main():
    parser = argparse.ArgumentParser(description="CRISPR Screen Analyzer")
    parser.add_argument("--counts", "-c", required=True, help="sgRNA count matrix")
    parser.add_argument("--samples", "-s", required=True, help="Sample annotation")
    parser.add_argument("--control", help="Control samples")
    parser.add_argument("--treatment", "-t", help="Treatment samples")
    parser.add_argument("--output", "-o", default="crispr_results", help="Output directory")
    parser.add_argument("--fdr", type=float, default=0.05, help="FDR threshold")
    
    args = parser.parse_args()
    
    analyzer = CRISPRScreenAnalyzer(args.counts, args.samples)
    
    print("\n" + "="*70)
    print("CRISPR SCREEN ANALYZER")
    print("="*70)
    print(f"Loaded {analyzer.counts.shape[0]} sgRNAs x {analyzer.counts.shape[1]} samples")
    
    if args.control and args.treatment:
        control_samples = [s.strip() for s in args.control.split(",")]
        treatment_samples = [s.strip() for s in args.treatment.split(",")]
        
        lfc = analyzer.calculate_lfc(control_samples, treatment_samples)
        results = analyzer.rra_analysis(lfc)
        hits = analyzer.identify_hits(results, args.fdr)
        
        print(f"\nSignificant hits (FDR < {args.fdr}): {len(hits)} sgRNAs")
        
        results.to_csv(f"{args.output}_sgrna_results.csv", index=False)
        print(f"\nResults saved to: {args.output}_sgrna_results.csv")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

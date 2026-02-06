#!/usr/bin/env python3
"""
Sanger Chromatogram QA
Quality check Sanger sequencing traces for mutations.
"""

import argparse
import numpy as np


class SangerQA:
    """Quality check Sanger sequencing data."""
    
    def check_quality(self, trace_data):
        """Check chromatogram quality."""
        scores = {
            "average_quality": np.mean(trace_data.get("quality_scores", [])),
            "low_quality_bases": sum(1 for q in trace_data.get("quality_scores", []) if q < 20),
            "total_bases": len(trace_data.get("quality_scores", [])),
            "mixed_signal_regions": self.detect_mixed_signals(trace_data)
        }
        
        scores["percent_low_quality"] = (scores["low_quality_bases"] / scores["total_bases"] * 100) if scores["total_bases"] > 0 else 0
        
        return scores
    
    def detect_mixed_signals(self, trace_data):
        """Detect positions with mixed signals (heterozygous)."""
        # Simplified detection
        return 0  # Placeholder
    
    def check_for_mutations(self, sequence, reference):
        """Compare sequence to reference for mutations."""
        mutations = []
        
        min_len = min(len(sequence), len(reference))
        
        for i in range(min_len):
            if sequence[i] != reference[i] and sequence[i] != 'N':
                mutations.append({
                    "position": i + 1,
                    "ref": reference[i],
                    "alt": sequence[i],
                    "type": "SNV" if len(reference) == len(sequence) else "indel"
                })
        
        return mutations


def main():
    parser = argparse.ArgumentParser(description="Sanger Chromatogram QA")
    parser.add_argument("--ab1", help="AB1 trace file")
    parser.add_argument("--reference", "-r", help="Reference sequence")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    qa = SangerQA()
    
    if args.demo:
        # Demo data
        trace_data = {
            "quality_scores": [45, 42, 38, 35, 30, 25, 20, 15, 18, 22, 30, 40],
            "sequence": "ATCGATCGATCG"
        }
        reference = "ATCGATCGATCG"
        
        scores = qa.check_quality(trace_data)
        mutations = qa.check_for_mutations(trace_data["sequence"], reference)
        
        print(f"\n{'='*60}")
        print("SANGER QA REPORT")
        print(f"{'='*60}\n")
        
        print(f"Average quality: {scores['average_quality']:.1f}")
        print(f"Low quality bases: {scores['low_quality_bases']} ({scores['percent_low_quality']:.1f}%)")
        print(f"Mutations detected: {len(mutations)}")
        
        if mutations:
            for m in mutations:
                print(f"  Position {m['position']}: {m['ref']}>{m['alt']}")
        
        print(f"\n{'='*60}\n")
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()

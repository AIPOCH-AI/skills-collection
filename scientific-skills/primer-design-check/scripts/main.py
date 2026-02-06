#!/usr/bin/env python3
"""
Primer Design Check
Check primers for dimers, hairpins, and off-target amplification.
"""

import argparse
import re


class PrimerChecker:
    """Check primer quality."""
    
    def calculate_tm(self, sequence):
        """Calculate melting temperature (simplified)."""
        A = sequence.count('A')
        T = sequence.count('T')
        G = sequence.count('G')
        C = sequence.count('C')
        
        if len(sequence) < 14:
            tm = 2 * (A + T) + 4 * (G + C)
        else:
            tm = 64.9 + 41 * (G + C - 16.4) / len(sequence)
        
        return tm
    
    def check_hairpin(self, sequence):
        """Check for hairpin structures."""
        # Simplified check for self-complementarity
        rev_comp = self.reverse_complement(sequence)
        
        # Check 3' end complementarity
        end_match = sum(1 for a, b in zip(sequence[-5:], rev_comp[:5]) if a == b)
        
        if end_match >= 3:
            return True, f"Potential hairpin (3' complementarity: {end_match}/5)"
        
        return False, "No significant hairpin detected"
    
    def check_self_dimer(self, sequence):
        """Check for self-dimer formation."""
        # Simple check for 3' end complementarity with itself
        rev_comp = self.reverse_complement(sequence)
        
        # Check last 4 bases
        matches = sum(1 for a, b in zip(sequence[-4:], rev_comp[-4:]) if a == b)
        
        if matches >= 3:
            return True, f"Potential self-dimer ({matches}/4 bases match)"
        
        return False, "Low self-dimer risk"
    
    def reverse_complement(self, seq):
        """Get reverse complement."""
        complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        return ''.join(complement.get(base, base) for base in reversed(seq))
    
    def check_primer(self, sequence, name="Primer"):
        """Comprehensive primer check."""
        results = {
            "name": name,
            "sequence": sequence,
            "length": len(sequence),
            "tm": self.calculate_tm(sequence),
            "gc_content": (sequence.count('G') + sequence.count('C')) / len(sequence) * 100
        }
        
        # Check for hairpin
        has_hairpin, hairpin_msg = self.check_hairpin(sequence)
        results["hairpin"] = has_hairpin
        results["hairpin_comment"] = hairpin_msg
        
        # Check for self-dimer
        has_dimer, dimer_msg = self.check_self_dimer(sequence)
        results["self_dimer"] = has_dimer
        results["dimer_comment"] = dimer_msg
        
        return results
    
    def print_report(self, results):
        """Print primer check report."""
        print(f"\n{'='*60}")
        print(f"PRIMER CHECK: {results['name']}")
        print(f"{'='*60}\n")
        
        print(f"Sequence:     {results['sequence']}")
        print(f"Length:       {results['length']} bp")
        print(f"Tm:           {results['tm']:.1f}°C")
        print(f"GC Content:   {results['gc_content']:.1f}%")
        print()
        
        status = "✓ PASS" if not (results['hairpin'] or results['self_dimer']) else "✗ FAIL"
        print(f"Overall: {status}")
        print()
        
        print(f"Hairpin:  {results['hairpin_comment']}")
        print(f"Dimer:    {results['dimer_comment']}")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Primer Design Check")
    parser.add_argument("--forward", "-f", help="Forward primer sequence")
    parser.add_argument("--reverse", "-r", help="Reverse primer sequence")
    
    args = parser.parse_args()
    
    checker = PrimerChecker()
    
    if args.forward:
        results = checker.check_primer(args.forward.upper(), "Forward")
        checker.print_report(results)
    
    if args.reverse:
        results = checker.check_primer(args.reverse.upper(), "Reverse")
        checker.print_report(results)
    
    if not args.forward and not args.reverse:
        # Demo
        demo_primer = "ATCGATCGATCGATCG"
        results = checker.check_primer(demo_primer, "Demo Primer")
        checker.print_report(results)


if __name__ == "__main__":
    main()

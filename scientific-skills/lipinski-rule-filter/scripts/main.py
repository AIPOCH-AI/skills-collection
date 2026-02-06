#!/usr/bin/env python3
"""
Lipinski Rule Filter
Filter compounds by Lipinski's Rule of Five.
"""

import argparse
import sys


class LipinskiFilter:
    """Apply Lipinski's Rule of Five filter."""
    
    RULES = {
        "mw": ("Molecular Weight", 500, "<"),
        "logp": ("LogP", 5, "<"),
        "hbd": ("H-bond Donors", 5, "<"),
        "hba": ("H-bond Acceptors", 10, "<")
    }
    
    def check_compound(self, smiles, mw, logp, hbd, hba):
        """Check compound against Lipinski rules."""
        violations = 0
        details = []
        
        checks = [
            ("mw", mw),
            ("logp", logp),
            ("hbd", hbd),
            ("hba", hba)
        ]
        
        for key, value in checks:
            name, threshold, op = self.RULES[key]
            if key == "mw" and value >= threshold:
                violations += 1
                details.append(f"{name}: {value:.1f} (threshold: {threshold})")
            elif key == "logp" and value >= threshold:
                violations += 1
                details.append(f"{name}: {value:.1f} (threshold: {threshold})")
            elif key in ["hbd", "hba"] and value >= threshold:
                violations += 1
                details.append(f"{name}: {value} (threshold: {threshold})")
        
        passed = violations <= 1
        
        return {
            "smiles": smiles,
            "passed": passed,
            "violations": violations,
            "details": details,
            "properties": {"mw": mw, "logp": logp, "hbd": hbd, "hba": hba}
        }
    
    def filter_library(self, compounds, max_violations=1):
        """Filter compound library."""
        passed = []
        failed = []
        
        for compound in compounds:
            result = self.check_compound(
                compound.get("smiles", ""),
                compound.get("mw", 0),
                compound.get("logp", 0),
                compound.get("hbd", 0),
                compound.get("hba", 0)
            )
            
            if result["violations"] <= max_violations:
                passed.append(result)
            else:
                failed.append(result)
        
        return passed, failed


def main():
    parser = argparse.ArgumentParser(description="Lipinski Rule Filter")
    parser.add_argument("--smiles", "-s", help="SMILES string to check")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--violations", "-v", type=int, default=1, 
                        help="Max allowed violations")
    
    args = parser.parse_args()
    
    filter_tool = LipinskiFilter()
    
    if args.smiles:
        # Demo check with mock data
        result = filter_tool.check_compound(args.smiles, mw=180.2, logp=1.2, hbd=1, hba=3)
        print(f"\nCompound: {args.smiles}")
        print(f"Passed: {result['passed']}")
        print(f"Violations: {result['violations']}")
        if result['details']:
            print("Details:")
            for d in result['details']:
                print(f"  - {d}")
    else:
        print("Lipinski Rule of Five Filter")
        print("Rules:")
        print("  - MW < 500 Da")
        print("  - LogP < 5")
        print("  - H-bond donors < 5")
        print("  - H-bond acceptors < 10")
        print(f"\nMax violations allowed: {args.violations}")


if __name__ == "__main__":
    main()

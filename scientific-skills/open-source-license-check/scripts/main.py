#!/usr/bin/env python3
"""
Open Source License Check
Check bioinformatics software licenses for commercial use.
"""

import argparse
from pathlib import Path


class LicenseChecker:
    """Check software licenses."""
    
    LICENSE_DB = {
        "samtools": {"license": "MIT", "commercial": True, "copyleft": False},
        "bwa": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "bedtools": {"license": "MIT", "commercial": True, "copyleft": False},
        "bowtie2": {"license": "MIT", "commercial": True, "copyleft": False},
        "star": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "hisat2": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "salmon": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "kallisto": {"license": "BSD-2", "commercial": True, "copyleft": False},
        "deseq2": {"license": "LGPL-3.0", "commercial": True, "copyleft": True},
        "edger": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "limma": {"license": "GPL-3.0", "commercial": True, "copyleft": True},
        "ggplot2": {"license": "MIT", "commercial": True, "copyleft": False},
        "pandas": {"license": "BSD-3", "commercial": True, "copyleft": False},
        "numpy": {"license": "BSD-3", "commercial": True, "copyleft": False},
        "scipy": {"license": "BSD-3", "commercial": True, "copyleft": False},
        "scikit-learn": {"license": "BSD-3", "commercial": True, "copyleft": False},
        "tensorflow": {"license": "Apache-2.0", "commercial": True, "copyleft": False},
        "pytorch": {"license": "BSD-3", "commercial": True, "copyleft": False},
    }
    
    def check(self, software_name):
        """Check license for software."""
        name = software_name.lower().strip()
        if name in self.LICENSE_DB:
            return self.LICENSE_DB[name]
        return None
    
    def print_report(self, software_list):
        """Print license report."""
        print(f"\n{'='*70}")
        print(f"{'Software':<20} {'License':<15} {'Commercial':<12} {'Risk'}")
        print(f"{'='*70}")
        
        warnings = []
        for sw in software_list:
            info = self.check(sw)
            if info:
                status = "✅ Yes" if info["commercial"] else "❌ No"
                risk = "⚠️ Copyleft" if info["copyleft"] else "✓ Safe"
                print(f"{sw:<20} {info['license']:<15} {status:<12} {risk}")
                if info["copyleft"]:
                    warnings.append((sw, info["license"]))
            else:
                print(f"{sw:<20} {'Unknown':<15} {'?':<12} {'⚠️ Check manually'}")
        
        print(f"{'='*70}\n")
        
        if warnings:
            print("⚠️  WARNINGS - Copyleft licenses require source code sharing:")
            for sw, lic in warnings:
                print(f"  - {sw} ({lic}): Must open-source derivative works")
            print()


def main():
    parser = argparse.ArgumentParser(description="Open Source License Check")
    parser.add_argument("--software", "-s", help="Comma-separated software names")
    parser.add_argument("--check-requirements", "-r", help="Python requirements.txt file")
    
    args = parser.parse_args()
    
    checker = LicenseChecker()
    
    if args.software:
        software_list = [s.strip() for s in args.software.split(",")]
        checker.print_report(software_list)
    elif args.check_requirements:
        print(f"Checking {args.check_requirements}...")
        # Parse requirements file
        software_list = []
        with open(args.check_requirements) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    pkg = line.split("=")[0].split("[")[0].strip()
                    software_list.append(pkg)
        checker.print_report(software_list)
    else:
        # Demo mode
        print("Demo mode - checking common bioinformatics tools:")
        checker.print_report(["samtools", "bwa", "bedtools", "star", "kallisto"])


if __name__ == "__main__":
    main()

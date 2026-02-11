#!/usr/bin/env python3
"""
Lipinski Rule of Five Filter

Filter compound libraries based on Lipinski's Rule of Five for drug-likeness.
Uses RDKit to calculate molecular properties from SMILES strings.

Author: AIPOCH
Version: 2.0.0
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not available. Install with: pip install rdkit-pypi")


class LipinskiFilter:
    """
    Apply Lipinski's Rule of Five filter to compound libraries.
    
    Lipinski's Rules:
    1. Molecular Weight < 500 Da
    2. LogP < 5
    3. H-bond Donors < 5
    4. H-bond Acceptors < 10
    
    Compound passes if it violates ≤ 1 rule (default).
    """
    
    RULES = {
        "mw": ("Molecular Weight", 500, "<", "Da"),
        "logp": ("LogP", 5, "<", ""),
        "hbd": ("H-bond Donors", 5, "<", ""),
        "hba": ("H-bond Acceptors", 10, "<", "")
    }
    
    def calculate_properties(self, smiles: str) -> Optional[Dict]:
        """
        Calculate molecular properties from SMILES using RDKit.
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dictionary with mw, logp, hbd, hba or None if invalid
        """
        if not RDKIT_AVAILABLE:
            return None
            
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
            
        return {
            "mw": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "hbd": Lipinski.NumHDonors(mol),
            "hba": Lipinski.NumHAcceptors(mol)
        }
    
    def check_compound(self, smiles: str, name: str = "", 
                       max_violations: int = 1) -> Dict:
        """
        Check compound against Lipinski rules.
        
        Args:
            smiles: SMILES string
            name: Compound name/ID
            max_violations: Maximum allowed violations (default: 1)
            
        Returns:
            Dictionary with results
        """
        # Calculate properties
        props = self.calculate_properties(smiles)
        
        if props is None:
            return {
                "smiles": smiles,
                "name": name,
                "valid": False,
                "passed": False,
                "violations": -1,
                "details": ["Invalid SMILES"],
                "properties": {}
            }
        
        # Check rules
        violations = 0
        details = []
        
        checks = [
            ("mw", props["mw"]),
            ("logp", props["logp"]),
            ("hbd", props["hbd"]),
            ("hba", props["hba"])
        ]
        
        for key, value in checks:
            name_rule, threshold, op, unit = self.RULES[key]
            if key == "mw" and value >= threshold:
                violations += 1
                details.append(f"{name_rule}: {value:.1f} {unit} (threshold: <{threshold})")
            elif key == "logp" and value >= threshold:
                violations += 1
                details.append(f"{name_rule}: {value:.2f} (threshold: <{threshold})")
            elif key in ["hbd", "hba"] and value >= threshold:
                violations += 1
                details.append(f"{name_rule}: {int(value)} (threshold: <{threshold})")
        
        passed = violations <= max_violations
        
        return {
            "smiles": smiles,
            "name": name,
            "valid": True,
            "passed": passed,
            "violations": violations,
            "details": details,
            "properties": props
        }
    
    def filter_library(self, input_file: str, output_file: str = None,
                       max_violations: int = 1, 
                       separator: str = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter compound library from file.
        
        Supports CSV, TSV, or SMILES files.
        
        Args:
            input_file: Input file path
            output_file: Output file path (optional)
            max_violations: Maximum allowed violations
            separator: Field separator (auto-detect if None)
            
        Returns:
            Tuple of (passed_compounds, failed_compounds)
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Detect format
        suffix = input_path.suffix.lower()
        
        compounds = []
        
        if suffix == '.csv':
            compounds = self._read_csv(input_path)
        elif suffix == '.tsv' or suffix == '.txt':
            compounds = self._read_tsv(input_path)
        elif suffix == '.smi' or suffix == '.smiles':
            compounds = self._read_smiles(input_path)
        else:
            # Try auto-detect
            compounds = self._read_auto(input_path, separator)
        
        # Filter compounds
        passed = []
        failed = []
        
        print(f"Processing {len(compounds)} compounds...")
        
        for compound in compounds:
            result = self.check_compound(
                compound.get("smiles", ""),
                compound.get("name", ""),
                max_violations
            )
            
            if result["valid"] and result["passed"]:
                passed.append(result)
            else:
                failed.append(result)
        
        # Write output if specified
        if output_file:
            self._write_output(output_file, passed, failed)
        
        return passed, failed
    
    def _read_csv(self, filepath: Path) -> List[Dict]:
        """Read CSV file."""
        compounds = []
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                compounds.append({
                    "smiles": row.get("SMILES", row.get("smiles", "")),
                    "name": row.get("Name", row.get("name", ""))
                })
        return compounds
    
    def _read_tsv(self, filepath: Path) -> List[Dict]:
        """Read TSV file."""
        compounds = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                compounds.append({
                    "smiles": row.get("SMILES", row.get("smiles", "")),
                    "name": row.get("Name", row.get("name", ""))
                })
        return compounds
    
    def _read_smiles(self, filepath: Path) -> List[Dict]:
        """Read SMILES file (one SMILES per line)."""
        compounds = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    smiles = parts[0]
                    name = parts[1] if len(parts) > 1 else f"Compound_{i}"
                    compounds.append({"smiles": smiles, "name": name})
        return compounds
    
    def _read_auto(self, filepath: Path, separator: str = None) -> List[Dict]:
        """Auto-detect format and read."""
        # Try to detect delimiter
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if '\t' in first_line:
                return self._read_tsv(filepath)
            elif ',' in first_line:
                return self._read_csv(filepath)
            else:
                return self._read_smiles(filepath)
    
    def _write_output(self, output_file: str, 
                      passed: List[Dict], failed: List[Dict]):
        """Write results to output file."""
        output_path = Path(output_file)
        suffix = output_path.suffix.lower()
        
        # Write passed compounds
        passed_file = output_path.parent / f"{output_path.stem}_passed{suffix}"
        
        with open(passed_file, 'w', newline='', encoding='utf-8') as f:
            if suffix == '.csv':
                writer = csv.writer(f)
                writer.writerow(["SMILES", "Name", "MW", "LogP", "HBD", "HBA", "Violations"])
                for p in passed:
                    props = p["properties"]
                    writer.writerow([
                        p["smiles"], p["name"],
                        f"{props.get('mw', 0):.2f}",
                        f"{props.get('logp', 0):.2f}",
                        props.get('hbd', 0),
                        props.get('hba', 0),
                        p["violations"]
                    ])
            else:
                # SMILES format
                for p in passed:
                    f.write(f"{p['smiles']}\t{p['name']}\n")
        
        # Write report
        report_file = output_path.parent / f"{output_path.stem}_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Lipinski Rule of Five Filter Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total compounds: {len(passed) + len(failed)}\n")
            f.write(f"Passed: {len(passed)}\n")
            f.write(f"Failed: {len(failed)}\n\n")
            
            f.write("Failed Compounds:\n")
            f.write("-" * 60 + "\n")
            for fa in failed:
                f.write(f"\n{fa['name']}: {fa['smiles']}\n")
                f.write(f"  Violations: {fa['violations']}\n")
                for detail in fa['details']:
                    f.write(f"  - {detail}\n")
        
        print(f"\nOutput files:")
        print(f"  Passed compounds: {passed_file}")
        print(f"  Report: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Lipinski Rule of Five Filter - Drug-likeness filtering for compound libraries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single compound
  python main.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --name "Aspirin"
  
  # Filter compound library
  python main.py --input compounds.csv --output filtered.csv --violations 1
  
  # Read SMILES file
  python main.py --input library.smi --output results
        """
    )
    
    parser.add_argument(
        "--smiles", "-s",
        help="SMILES string to check"
    )
    parser.add_argument(
        "--name", "-n",
        default="",
        help="Compound name (use with --smiles)"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input file (CSV, TSV, or SMILES format)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file prefix for filtered results"
    )
    parser.add_argument(
        "--violations", "-v",
        type=int,
        default=1,
        help="Maximum allowed Lipinski rule violations (default: 1)"
    )
    
    args = parser.parse_args()
    
    filter_tool = LipinskiFilter()
    
    # Single compound mode
    if args.smiles:
        print("=" * 60)
        print("Lipinski Rule of Five Check")
        print("=" * 60)
        
        result = filter_tool.check_compound(args.smiles, args.name, args.violations)
        
        print(f"\nCompound: {result['name'] or 'Unknown'}")
        print(f"SMILES: {result['smiles']}")
        
        if not result['valid']:
            print("Status: ❌ INVALID SMILES")
            sys.exit(1)
        
        props = result['properties']
        print(f"\nProperties:")
        print(f"  Molecular Weight: {props['mw']:.2f} Da")
        print(f"  LogP: {props['logp']:.2f}")
        print(f"  H-bond Donors: {props['hbd']}")
        print(f"  H-bond Acceptors: {props['hba']}")
        
        print(f"\nLipinski Check:")
        if result['passed']:
            print(f"  ✅ PASSED ({result['violations']} violations)")
        else:
            print(f"  ❌ FAILED ({result['violations']} violations)")
        
        if result['details']:
            print("\n  Issues:")
            for detail in result['details']:
                print(f"    - {detail}")
        
        print("\n" + "=" * 60)
        sys.exit(0 if result['passed'] else 1)
    
    # Batch processing mode
    elif args.input:
        if not args.output:
            args.output = "filtered"
        
        print("=" * 60)
        print("Lipinski Rule of Five Filter")
        print("=" * 60)
        print(f"\nInput file: {args.input}")
        print(f"Max violations allowed: {args.violations}")
        
        try:
            passed, failed = filter_tool.filter_library(
                args.input,
                args.output,
                args.violations
            )
            
            print(f"\n{'='*60}")
            print("Summary:")
            print(f"  Total: {len(passed) + len(failed)}")
            print(f"  ✅ Passed: {len(passed)}")
            print(f"  ❌ Failed: {len(failed)}")
            print(f"{'='*60}")
            
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

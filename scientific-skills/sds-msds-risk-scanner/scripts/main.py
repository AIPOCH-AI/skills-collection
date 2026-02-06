#!/usr/bin/env python3
"""
SDS/MSDS Risk Scanner
Extract hazard codes and safety info from chemical safety datasheets.
"""

import argparse
import re


class SDSRiskScanner:
    """Scan SDS/MSDS for hazard information."""
    
    GHS_HAZARD_CLASSES = {
        "H300": "Fatal if swallowed",
        "H310": "Fatal in contact with skin",
        "H330": "Fatal if inhaled",
        "H314": "Causes severe skin burns and eye damage",
        "H318": "Causes serious eye damage",
        "H226": "Flammable liquid and vapor",
        "H315": "Causes skin irritation",
        "H319": "Causes serious eye irritation",
        "H335": "May cause respiratory irritation"
    }
    
    def extract_hazard_codes(self, sds_text):
        """Extract GHS hazard codes from SDS text."""
        codes = []
        
        # Pattern for H-codes
        pattern = r'H\d{3}[dfi]?'
        matches = re.findall(pattern, sds_text)
        
        for code in matches:
            description = self.GHS_HAZARD_CLASSES.get(code, "Unknown hazard")
            codes.append({"code": code, "description": description})
        
        return codes
    
    def extract_precautionary_statements(self, sds_text):
        """Extract P-statements from SDS text."""
        pattern = r'P\d{3}[abc]?'
        return re.findall(pattern, sds_text)
    
    def assess_risk_level(self, hazard_codes):
        """Assess overall risk level."""
        fatal_codes = ["H300", "H310", "H330"]
        corrosive_codes = ["H314", "H318"]
        
        has_fatal = any(c["code"] in fatal_codes for c in hazard_codes)
        has_corrosive = any(c["code"] in corrosive_codes for c in hazard_codes)
        
        if has_fatal:
            return "EXTREME - Handle with extreme caution"
        elif has_corrosive:
            return "HIGH - Use full PPE required"
        elif len(hazard_codes) > 3:
            return "MODERATE - Standard safety precautions"
        else:
            return "LOW - Basic safety measures"


def main():
    parser = argparse.ArgumentParser(description="SDS/MSDS Risk Scanner")
    parser.add_argument("--sds", "-s", help="SDS text file")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    scanner = SDSRiskScanner()
    
    if args.demo:
        # Demo SDS text
        sds_text = """
        Product: Chemical X
        Hazard Statements: H314, H318, H226
        Precautionary Statements: P280, P305+P351+P338
        """
        
        hazards = scanner.extract_hazard_codes(sds_text)
        risk_level = scanner.assess_risk_level(hazards)
        
        print(f"\n{'='*60}")
        print("SDS RISK SCAN REPORT")
        print(f"{'='*60}\n")
        
        print(f"Risk Level: {risk_level}")
        print("\nHazard Codes:")
        for h in hazards:
            print(f"  {h['code']}: {h['description']}")
        
        print(f"\n{'='*60}\n")
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()

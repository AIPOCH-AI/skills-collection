#!/usr/bin/env python3
"""
IHC/IF Optimizer
Optimize IHC/IF protocols for specific tissues and antigens.
"""

import argparse


class IHCIFOptimizer:
    """Optimize immunohistochemistry and immunofluorescence protocols."""
    
    TISSUE_RECOMMENDATIONS = {
        "brain": {
            "fixation": "4% PFA, 24 hours",
            "permeabilization": "0.3% Triton X-100, 30 min",
            "blocking": "10% normal serum, 1 hour",
            "notes": "Brain tissue is soft; avoid over-fixation"
        },
        "skin": {
            "fixation": "4% PFA, 12-16 hours",
            "permeabilization": "0.1% Triton X-100, 15 min",
            "blocking": "5% BSA, 30 min",
            "notes": "High autofluorescence; consider quenching"
        },
        "liver": {
            "fixation": "4% PFA, 16-20 hours",
            "permeabilization": "0.2% Triton X-100, 20 min",
            "blocking": "10% normal serum, 45 min",
            "notes": "High endogenous peroxidase; use H2O2 quench"
        },
        "kidney": {
            "fixation": "4% PFA, 16-20 hours",
            "permeabilization": "0.2% Triton X-100, 20 min",
            "blocking": "10% normal serum, 45 min",
            "notes": "Consider antigen retrieval for most targets"
        },
        "tumor": {
            "fixation": "4% PFA, 16-24 hours",
            "permeabilization": "0.3% Triton X-100, 30 min",
            "blocking": "10% normal serum + 5% BSA, 1 hour",
            "notes": "High variability; optimize for each tumor type"
        }
    }
    
    ANTIGEN_RETRIEVAL = {
        "high": {"method": "Citrate buffer (pH 6.0), 95°C, 20 min", "note": "For difficult antigens"},
        "medium": {"method": "EDTA (pH 8.0), 95°C, 15 min", "note": "Standard protocol"},
        "low": {"method": "Trypsin, 37°C, 10 min", "note": "For delicate antigens"},
        "none": {"method": "None required", "note": "Surface antigens or well-preserved epitopes"}
    }
    
    ANTIBODY_RECOMMENDATIONS = {
        "nuclear": {"dilution": "1:200-1:500", "incubation": "Overnight, 4°C", "retrieval": "high"},
        "cytoplasmic": {"dilution": "1:100-1:200", "incubation": "1-2 hours, RT", "retrieval": "medium"},
        "membrane": {"dilution": "1:50-1:100", "incubation": "1 hour, RT", "retrieval": "none"},
        "extracellular": {"dilution": "1:200-1:400", "incubation": "1-2 hours, RT", "retrieval": "low"}
    }
    
    def optimize_protocol(self, tissue, antigen_location, antigen_difficulty="medium"):
        """Generate optimized protocol."""
        tissue_rec = self.TISSUE_RECOMMENDATIONS.get(tissue.lower(), {})
        antibody_rec = self.ANTIBODY_RECOMMENDATIONS.get(antigen_location.lower(), {})
        
        # Determine antigen retrieval
        if antigen_difficulty == "high" or antibody_rec.get("retrieval") == "high":
            retrieval = self.ANTIGEN_RETRIEVAL["high"]
        elif antigen_difficulty == "low":
            retrieval = self.ANTIGEN_RETRIEVAL["low"]
        else:
            retrieval = self.ANTIGEN_RETRIEVAL.get(antibody_rec.get("retrieval", "medium"), self.ANTIGEN_RETRIEVAL["medium"])
        
        protocol = {
            "tissue": tissue,
            "fixation": tissue_rec.get("fixation", "4% PFA, 16-24 hours"),
            "antigen_retrieval": retrieval,
            "permeabilization": tissue_rec.get("permeabilization", "0.2% Triton X-100, 20 min"),
            "blocking": tissue_rec.get("blocking", "10% normal serum, 1 hour"),
            "primary_antibody": {
                "dilution": antibody_rec.get("dilution", "1:100"),
                "incubation": antibody_rec.get("incubation", "Overnight, 4°C")
            },
            "notes": tissue_rec.get("notes", "")
        }
        
        return protocol
    
    def print_protocol(self, protocol):
        """Print formatted protocol."""
        print(f"\n{'='*60}")
        print(f"OPTIMIZED IHC/IF PROTOCOL")
        print(f"Tissue: {protocol['tissue'].upper()}")
        print(f"{'='*60}\n")
        
        print("1. FIXATION")
        print(f"   {protocol['fixation']}")
        print()
        
        print("2. ANTIGEN RETRIEVAL")
        print(f"   Method: {protocol['antigen_retrieval']['method']}")
        print(f"   Note: {protocol['antigen_retrieval']['note']}")
        print()
        
        print("3. PERMEABILIZATION")
        print(f"   {protocol['permeabilization']}")
        print()
        
        print("4. BLOCKING")
        print(f"   {protocol['blocking']}")
        print()
        
        print("5. PRIMARY ANTIBODY")
        print(f"   Dilution: {protocol['primary_antibody']['dilution']}")
        print(f"   Incubation: {protocol['primary_antibody']['incubation']}")
        print()
        
        if protocol['notes']:
            print(f"SPECIAL NOTES:")
            print(f"   {protocol['notes']}")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="IHC/IF Optimizer")
    parser.add_argument("--tissue", "-t", required=True, help="Tissue type")
    parser.add_argument("--antigen-location", "-a", required=True,
                       choices=["nuclear", "cytoplasmic", "membrane", "extracellular"],
                       help="Antigen subcellular location")
    parser.add_argument("--difficulty", "-d", default="medium",
                       choices=["high", "medium", "low"],
                       help="Antigen detection difficulty")
    parser.add_argument("--list-tissues", action="store_true", help="List supported tissues")
    
    args = parser.parse_args()
    
    optimizer = IHCIFOptimizer()
    
    if args.list_tissues:
        print("\nSupported tissues:")
        for tissue in optimizer.TISSUE_RECOMMENDATIONS.keys():
            print(f"  - {tissue}")
        return
    
    protocol = optimizer.optimize_protocol(args.tissue, args.antigen_location, args.difficulty)
    optimizer.print_protocol(protocol)


if __name__ == "__main__":
    main()

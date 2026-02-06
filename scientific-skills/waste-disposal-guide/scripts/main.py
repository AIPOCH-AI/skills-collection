#!/usr/bin/env python3
"""
Waste Disposal Guide
Guide for proper chemical waste disposal.
"""

import argparse


class WasteDisposalGuide:
    """Chemical waste disposal guide."""
    
    WASTE_CATEGORIES = {
        "halogenated": {
            "color": "🟠 Orange",
            "name": "Halogenated Organic Waste",
            "accepts": ["chloroform", "dichloromethane", "dcm", "carbon tetrachloride", 
                       "trichloroethylene", "halothane", "iodine compounds"],
            "notes": "Keep separate from non-halogenated waste"
        },
        "non_halogenated": {
            "color": "🔴 Red",
            "name": "Non-Halogenated Organic Waste",
            "accepts": ["ethanol", "methanol", "acetone", "isopropanol", "ethyl acetate",
                       "hexane", "toluene", "xylene", "acetonitrile"],
            "notes": "Most common organic solvent waste"
        },
        "aqueous": {
            "color": "🔵 Blue",
            "name": "Aqueous Waste",
            "accepts": ["buffer solutions", "saline", "water-based", "pbs", "tris"],
            "notes": "Non-hazardous aqueous solutions only"
        },
        "acid": {
            "color": "🟡 Yellow",
            "name": "Acid Waste",
            "accepts": ["hydrochloric acid", "hcl", "sulfuric acid", "h2so4", 
                       "nitric acid", "hno3", "acetic acid", "trifluoroacetic acid"],
            "notes": "Keep acids separate from bases - never mix!"
        },
        "base": {
            "color": "⚪ White",
            "name": "Base/Alkali Waste",
            "accepts": ["sodium hydroxide", "naoh", "potassium hydroxide", "koh",
                       "ammonium hydroxide", "ammonia", "sodium carbonate"],
            "notes": "Keep bases separate from acids - never mix!"
        },
        "heavy_metal": {
            "color": "⚫ Gray",
            "name": "Heavy Metal Waste",
            "accepts": ["mercury", "lead", "cadmium", "chromium", "arsenic",
                       "silver", "copper salts"],
            "notes": "Requires special disposal - contact EHS"
        },
        "solid": {
            "color": "⬛ Black",
            "name": "Solid Waste",
            "accepts": ["gloves", "paper", "tips", "debris", "solid debris"],
            "notes": "Non-sharp solid waste only"
        }
    }
    
    def lookup(self, chemical):
        """Look up disposal category for chemical."""
        chemical_lower = chemical.lower().strip()
        
        for category, info in self.WASTE_CATEGORIES.items():
            if any(chemical_lower in accept or accept in chemical_lower 
                   for accept in info["accepts"]):
                return info
        
        return None
    
    def print_guide(self, chemical):
        """Print disposal guide."""
        result = self.lookup(chemical)
        
        print(f"\n{'='*60}")
        print(f"WASTE DISPOSAL GUIDE: {chemical}")
        print(f"{'='*60}")
        
        if result:
            print(f"\nContainer: {result['color']}")
            print(f"Category: {result['name']}")
            print(f"\n⚠️  Important: {result['notes']}")
        else:
            print("\n⚠️  Chemical not found in database")
            print("Contact EHS (Environmental Health & Safety) for guidance")
        
        print(f"{'='*60}\n")
    
    def list_categories(self):
        """List all waste categories."""
        print("\n" + "="*60)
        print("WASTE CONTAINER GUIDE")
        print("="*60)
        
        for key, info in self.WASTE_CATEGORIES.items():
            print(f"\n{info['color']} - {info['name']}")
            print(f"  Accepts: {', '.join(info['accepts'][:5])}...")
            print(f"  Note: {info['notes']}")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description="Waste Disposal Guide")
    parser.add_argument("--chemical", "-c", help="Chemical name to look up")
    parser.add_argument("--list-categories", "-l", action="store_true",
                       help="List all waste categories")
    parser.add_argument("--safety", "-s", action="store_true",
                       help="Show safety notes")
    
    args = parser.parse_args()
    
    guide = WasteDisposalGuide()
    
    if args.chemical:
        guide.print_guide(args.chemical)
    elif args.list_categories:
        guide.list_categories()
    elif args.safety:
        print("\n" + "="*60)
        print("SAFETY NOTES")
        print("="*60)
        print("\n⚠️  NEVER MIX:")
        print("  - Acids with Bases")
        print("  - Oxidizers with Organics")
        print("  - Unknown chemicals")
        print("\n✓  ALWAYS:")
        print("  - Label containers clearly")
        print("  - Keep containers closed")
        print("  - Contact EHS with questions")
        print("="*60 + "\n")
    else:
        # Show common chemicals
        print("\nCommon chemical waste lookup:")
        for chemical in ["chloroform", "ethanol", "hydrochloric acid", "gloves"]:
            guide.print_guide(chemical)


if __name__ == "__main__":
    main()

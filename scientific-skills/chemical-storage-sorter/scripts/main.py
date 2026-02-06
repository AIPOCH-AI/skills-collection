#!/usr/bin/env python3
"""
Chemical Storage Sorter
Sort chemicals by compatibility for safe lab storage.
"""

import argparse


class ChemicalStorageSorter:
    """Sort chemicals by compatibility groups."""
    
    COMPATIBILITY_GROUPS = {
        "acids": {
            "compatible": ["acids"],
            "incompatible": ["bases", "oxidizers", "cyanides", "sulfides"],
            "examples": ["HCl", "H2SO4", "HNO3", "acetic acid"]
        },
        "bases": {
            "compatible": ["bases"],
            "incompatible": ["acids", "oxidizers", "halogenated"],
            "examples": ["NaOH", "KOH", "ammonia", "Trizma"]
        },
        "flammables": {
            "compatible": ["flammables"],
            "incompatible": ["oxidizers", "acids"],
            "examples": ["ethanol", "methanol", "acetone", "hexane"]
        },
        "oxidizers": {
            "compatible": ["oxidizers"],
            "incompatible": ["flammables", "acids", "bases", "reducing"],
            "examples": ["H2O2", "KMnO4", "sodium hypochlorite", "nitric acid"]
        },
        "toxics": {
            "compatible": ["toxics"],
            "incompatible": ["acids", "oxidizers"],
            "examples": ["cyanide salts", "arsenic compounds", "mercury"]
        },
        "general": {
            "compatible": ["general", "salts", "buffers"],
            "incompatible": [],
            "examples": ["NaCl", "PBS", "sucrose", "glycerol"]
        }
    }
    
    def classify_chemical(self, name):
        """Classify chemical into storage group."""
        name_lower = name.lower()
        
        for group, data in self.COMPATIBILITY_GROUPS.items():
            for example in data["examples"]:
                if example.lower() in name_lower:
                    return group
        
        # Check keywords
        acid_keywords = ["acid", "hcl", "sulfuric", "nitric", "acetic"]
        base_keywords = ["hydroxide", "naoh", "koh", "ammonia", "amine"]
        flammable_keywords = ["ethanol", "methanol", "acetone", "ether", "hexane"]
        oxidizer_keywords = ["peroxide", "permanganate", "hypochlorite", "nitrate"]
        
        if any(k in name_lower for k in acid_keywords):
            return "acids"
        elif any(k in name_lower for k in base_keywords):
            return "bases"
        elif any(k in name_lower for k in flammable_keywords):
            return "flammables"
        elif any(k in name_lower for k in oxidizer_keywords):
            return "oxidizers"
        
        return "general"
    
    def check_compatibility(self, chemical1, chemical2):
        """Check if two chemicals can be stored together."""
        group1 = self.classify_chemical(chemical1)
        group2 = self.classify_chemical(chemical2)
        
        if group1 == group2:
            return True, f"Same group ({group1})"
        
        # Check if group2 is in group1's incompatible list
        incompatibles = self.COMPATIBILITY_GROUPS[group1]["incompatible"]
        if group2 in incompatibles:
            return False, f"INCOMPATIBLE: {group1} cannot be stored with {group2}"
        
        # Check reverse
        incompatibles = self.COMPATIBILITY_GROUPS[group2]["incompatible"]
        if group1 in incompatibles:
            return False, f"INCOMPATIBLE: {group2} cannot be stored with {group1}"
        
        return True, "Compatible with precautions"
    
    def sort_chemicals(self, chemical_list):
        """Sort chemicals into storage groups."""
        groups = {key: [] for key in self.COMPATIBILITY_GROUPS.keys()}
        
        for chem in chemical_list:
            group = self.classify_chemical(chem)
            groups[group].append(chem)
        
        return groups
    
    def print_storage_plan(self, groups):
        """Print storage plan."""
        print(f"\n{'='*60}")
        print("CHEMICAL STORAGE PLAN")
        print(f"{'='*60}\n")
        
        for group, chemicals in groups.items():
            if chemicals:
                print(f"\n{group.upper()} STORAGE:")
                print("-" * 40)
                for chem in chemicals:
                    print(f"  • {chem}")
                
                incompat = self.COMPATIBILITY_GROUPS[group]["incompatible"]
                if incompat:
                    print(f"  ⚠️  Keep away from: {', '.join(incompat)}")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Chemical Storage Sorter")
    parser.add_argument("--chemicals", "-c", help="Comma-separated chemical list")
    parser.add_argument("--check", help="Check compatibility with another chemical")
    parser.add_argument("--list-groups", "-l", action="store_true",
                       help="List storage groups")
    
    args = parser.parse_args()
    
    sorter = ChemicalStorageSorter()
    
    if args.list_groups:
        print("\nStorage Groups:")
        for group, data in sorter.COMPATIBILITY_GROUPS.items():
            print(f"\n{group.upper()}:")
            print(f"  Examples: {', '.join(data['examples'][:3])}")
        return
    
    if args.chemicals:
        chemicals = [c.strip() for c in args.chemicals.split(",")]
        groups = sorter.sort_chemicals(chemicals)
        sorter.print_storage_plan(groups)
    elif args.check:
        compatible, message = sorter.check_compatibility(args.chemicals or "", args.check)
        print(f"\nCompatibility check: {message}")
    else:
        # Demo
        demo_chemicals = ["HCl", "NaOH", "ethanol", "acetone", "PBS", "H2O2"]
        groups = sorter.sort_chemicals(demo_chemicals)
        sorter.print_storage_plan(groups)


if __name__ == "__main__":
    main()

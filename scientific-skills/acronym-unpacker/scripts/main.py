#!/usr/bin/env python3
"""
Acronym Unpacker
Medical acronym disambiguation tool.
"""

import argparse


class AcronymUnpacker:
    """Expand medical acronyms based on context."""
    
    ACRONYM_DB = {
        "PID": {
            "gynecology": [("Pelvic Inflammatory Disease", 0.9), ("Prolapsed Intervertebral Disc", 0.1)],
            "immunology": [("Primary Immunodeficiency", 0.95), ("Pelvic Inflammatory Disease", 0.05)],
            "general": [("Pelvic Inflammatory Disease", 0.6), ("Prolapsed Intervertebral Disc", 0.3), ("Primary Immunodeficiency", 0.1)]
        },
        "MI": {
            "cardiology": [("Myocardial Infarction", 0.95), ("Mitral Insufficiency", 0.05)],
            "general": [("Myocardial Infarction", 0.7), ("Mitral Insufficiency", 0.2), ("Mental Illness", 0.1)]
        },
        "COPD": {
            "pulmonology": [("Chronic Obstructive Pulmonary Disease", 1.0)],
            "general": [("Chronic Obstructive Pulmonary Disease", 1.0)]
        },
        "HTN": {
            "cardiology": [("Hypertension", 1.0)],
            "general": [("Hypertension", 1.0)]
        },
        "DM": {
            "endocrinology": [("Diabetes Mellitus", 0.95), ("Dermatomyositis", 0.05)],
            "dermatology": [("Dermatomyositis", 0.6), ("Diabetes Mellitus", 0.4)],
            "general": [("Diabetes Mellitus", 0.9), ("Dermatomyositis", 0.1)]
        }
    }
    
    def unpack(self, acronym, context="general"):
        """Expand acronym based on context."""
        acronym = acronym.upper().strip()
        context = context.lower().strip()
        
        if acronym not in self.ACRONYM_DB:
            return [(f"Unknown acronym: {acronym}", 0.0)]
        
        expansions = self.ACRONYM_DB[acronym]
        
        # Return context-specific or general
        if context in expansions:
            return expansions[context]
        elif "general" in expansions:
            return expansions["general"]
        else:
            # Return first available context
            return list(expansions.values())[0]
    
    def print_result(self, acronym, context, expansions):
        """Print expansion results."""
        print(f"\n{'='*60}")
        print(f"ACRONYM: {acronym}")
        print(f"Context: {context}")
        print(f"{'='*60}")
        
        for i, (expansion, confidence) in enumerate(expansions, 1):
            bar = "█" * int(confidence * 20)
            print(f"{i}. {expansion}")
            print(f"   Confidence: {confidence:.1%} {bar}")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Acronym Unpacker")
    parser.add_argument("acronym", help="Acronym to expand")
    parser.add_argument("--context", "-c", default="general",
                       help="Clinical context (e.g., cardiology, gynecology)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List known acronyms")
    
    args = parser.parse_args()
    
    unpacker = AcronymUnpacker()
    
    if args.list:
        print("\nKnown acronyms:")
        for acr in unpacker.ACRONYM_DB.keys():
            print(f"  - {acr}")
        return
    
    expansions = unpacker.unpack(args.acronym, args.context)
    unpacker.print_result(args.acronym, args.context, expansions)


if __name__ == "__main__":
    main()

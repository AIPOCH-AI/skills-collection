#!/usr/bin/env python3
"""Comparison Table Generator - Markdown table creator."""

import json

class ComparisonTableGen:
    """Generates comparison tables."""
    
    def generate(self, items: list, attributes: list) -> dict:
        """Generate comparison table."""
        
        # Header
        header = "| Feature | " + " | ".join(items) + " |"
        separator = "|" + "|".join(["---"] * (len(items) + 1)) + "|"
        
        # Rows
        rows = []
        for attr in attributes:
            row = f"| {attr} |" + " | " * len(items)
            rows.append(row)
        
        markdown = "\n".join([header, separator] + rows)
        
        return {
            "markdown_table": markdown,
            "items": items,
            "attributes": attributes
        }

def main():
    gen = ComparisonTableGen()
    result = gen.generate(["Drug A", "Drug B"], ["Mechanism", "Dose", "Side Effects"])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

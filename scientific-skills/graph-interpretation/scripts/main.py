#!/usr/bin/env python3
"""Graph Interpretation - Academic graph descriptions."""

import json

class GraphInterpretation:
    """Describes graphs academically."""
    
    def describe(self, graph_type: str, data_description: str) -> dict:
        """Generate description."""
        
        templates = {
            "bar": f"As shown in Figure 1, {data_description} demonstrated significant differences across groups.",
            "line": f"Figure 1 illustrates the trend of {data_description} over time.",
            "scatter": f"A scatter plot (Figure 1) reveals the relationship between {data_description}."
        }
        
        description = templates.get(graph_type, templates["bar"])
        
        return {
            "description": description,
            "caption_suggestion": f"Figure 1. {data_description.capitalize()}.",
            "graph_type": graph_type
        }

def main():
    interp = GraphInterpretation()
    result = interp.describe("bar", "treatment outcomes")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Concept Explainer - Medical concept analogies."""

import json

class ConceptExplainer:
    """Explains medical concepts using analogies."""
    
    ANALOGIES = {
        "thrombosis": {
            "analogy": "Like a traffic jam in a highway",
            "explanation": "Blood clots form when blood flow slows or stops, similar to how traffic jams occur when cars can't move freely."
        },
        "immune system": {
            "analogy": "Like a security system in a building",
            "explanation": "The immune system patrols the body looking for intruders (pathogens), just like security guards check for unauthorized visitors."
        },
        "antibiotic resistance": {
            "analogy": "Like weeds becoming resistant to weed killer",
            "explanation": "Bacteria evolve to survive antibiotics, similar to how weeds adapt to survive repeated herbicide use."
        }
    }
    
    def explain(self, concept: str, audience: str = "patient") -> dict:
        """Explain concept with analogy."""
        concept_lower = concept.lower()
        
        if concept_lower in self.ANALOGIES:
            data = self.ANALOGIES[concept_lower]
            return {
                "concept": concept,
                "explanation": data["explanation"],
                "analogy": data["analogy"],
                "audience": audience
            }
        
        return {
            "concept": concept,
            "explanation": f"{concept} is a medical condition/physiological process.",
            "analogy": "Analogy not available in database.",
            "audience": audience
        }

def main():
    explainer = ConceptExplainer()
    result = explainer.explain("thrombosis")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

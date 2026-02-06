#!/usr/bin/env python3
"""Visual Content Desc - Image description generator."""

import json

class VisualContentDesc:
    """Generates descriptions of medical images."""
    
    def describe(self, image_type: str, key_features: list) -> dict:
        """Generate image description."""
        
        features_text = ", ".join(key_features)
        
        description = f"This {image_type} shows {features_text}."
        alt_text = f"Medical {image_type}: {features_text}"
        
        return {
            "description": description,
            "alt_text": alt_text[:150],
            "figure_text": f"Figure shows {features_text}.",
            "image_type": image_type
        }

def main():
    describer = VisualContentDesc()
    result = describer.describe("microscopy", ["cellular structures", "stained nuclei", "tissue architecture"])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

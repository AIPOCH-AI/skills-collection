#!/usr/bin/env python3
"""
Variant Pathogenicity Predictor
Integrate REVEL, CADD, PolyPhen scores for variant classification.
"""

import argparse
import json


class VariantPathogenicityPredictor:
    """Predict variant pathogenicity."""
    
    def predict(self, variant_data):
        """Predict pathogenicity from multiple scores."""
        
        scores = {
            "REVEL": variant_data.get("REVEL", 0.5),
            "CADD": variant_data.get("CADD", 15),
            "PolyPhen": variant_data.get("PolyPhen", 0.5)
        }
        
        # Normalize CADD (higher = more damaging)
        cadd_norm = min(scores["CADD"] / 30, 1.0)
        
        # Composite score
        composite = (scores["REVEL"] * 0.4 + 
                    cadd_norm * 0.3 + 
                    scores["PolyPhen"] * 0.3)
        
        # Classification
        if composite >= 0.9:
            classification = "Pathogenic"
        elif composite >= 0.7:
            classification = "Likely Pathogenic"
        elif composite >= 0.3:
            classification = "Uncertain Significance"
        elif composite >= 0.1:
            classification = "Likely Benign"
        else:
            classification = "Benign"
        
        return {
            "composite_score": composite,
            "classification": classification,
            "individual_scores": scores
        }


def main():
    parser = argparse.ArgumentParser(description="Variant Pathogenicity Predictor")
    parser.add_argument("--revel", type=float, help="REVEL score")
    parser.add_argument("--cadd", type=float, help="CADD score")
    parser.add_argument("--polyphen", type=float, help="PolyPhen score")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    predictor = VariantPathogenicityPredictor()
    
    if args.demo:
        variant = {"REVEL": 0.85, "CADD": 25, "PolyPhen": 0.92}
    else:
        variant = {
            "REVEL": args.revel or 0.5,
            "CADD": args.cadd or 15,
            "PolyPhen": args.polyphen or 0.5
        }
    
    result = predictor.predict(variant)
    
    print(f"\n{'='*60}")
    print("VARIANT PATHOGENICITY PREDICTION")
    print(f"{'='*60}\n")
    
    print(f"Composite Score: {result['composite_score']:.3f}")
    print(f"Classification: {result['classification']}")
    print("\nIndividual Scores:")
    for tool, score in result['individual_scores'].items():
        print(f"  {tool}: {score}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

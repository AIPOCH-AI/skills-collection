#!/usr/bin/env python3
"""
Rare Disease HPO Mapper
Map patient symptoms to Human Phenotype Ontology terms.
"""

import argparse
from difflib import get_close_matches


class HPOMapper:
    """Map symptoms to HPO terms."""
    
    HPO_TERMS = {
        "HP:0001250": {"name": "Seizure", "synonyms": ["seizures", "epilepsy", "fits"]},
        "HP:0001263": {"name": "Global developmental delay", "synonyms": ["developmental delay", "DD"]},
        "HP:0004322": {"name": "Short stature", "synonyms": ["short", "small stature"]},
        "HP:0001638": {"name": "Cardiomyopathy", "synonyms": ["heart muscle disease"]},
        "HP:0000518": {"name": "Cataract", "synonyms": ["lens opacity"]},
        "HP:0001251": {"name": "Ataxia", "synonyms": ["coordination problems", "unsteady gait"]}
    }
    
    def find_hpo_term(self, symptom):
        """Find HPO term for symptom."""
        symptom_lower = symptom.lower()
        
        # Direct match
        for hpo_id, data in self.HPO_TERMS.items():
            if symptom_lower == data["name"].lower():
                return hpo_id, data
            
            for synonym in data["synonyms"]:
                if symptom_lower == synonym.lower():
                    return hpo_id, data
        
        # Fuzzy match
        all_names = []
        for data in self.HPO_TERMS.values():
            all_names.append(data["name"])
            all_names.extend(data["synonyms"])
        
        matches = get_close_matches(symptom_lower, all_names, n=1, cutoff=0.6)
        if matches:
            for hpo_id, data in self.HPO_TERMS.items():
                if matches[0] == data["name"] or matches[0] in data["synonyms"]:
                    return hpo_id, data
        
        return None, None
    
    def map_symptoms(self, symptoms):
        """Map list of symptoms to HPO terms."""
        mappings = []
        
        for symptom in symptoms:
            hpo_id, data = self.find_hpo_term(symptom)
            
            if hpo_id:
                mappings.append({
                    "symptom": symptom,
                    "hpo_id": hpo_id,
                    "hpo_name": data["name"],
                    "confidence": "high"
                })
            else:
                mappings.append({
                    "symptom": symptom,
                    "hpo_id": None,
                    "hpo_name": "Unknown",
                    "confidence": "none"
                })
        
        return mappings


def main():
    parser = argparse.ArgumentParser(description="Rare Disease HPO Mapper")
    parser.add_argument("--symptoms", "-s", required=True, help="Comma-separated symptoms")
    
    args = parser.parse_args()
    
    mapper = HPOMapper()
    
    symptoms = [s.strip() for s in args.symptoms.split(",")]
    
    mappings = mapper.map_symptoms(symptoms)
    
    print(f"\n{'='*60}")
    print("HPO MAPPING RESULTS")
    print(f"{'='*60}\n")
    
    for m in mappings:
        if m["hpo_id"]:
            print(f"✓ {m['symptom']} → {m['hpo_id']} ({m['hpo_name']})")
        else:
            print(f"✗ {m['symptom']} → No match found")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Drug Pronunciation Guide - Medical terminology pronunciation assistant."""

import json
from typing import Dict, List, Optional

class DrugPronunciation:
    """Provides pronunciation guides for drug names."""
    
    DRUG_DATABASE = {
        "metformin": {
            "ipa": "/mɛtˈfɔːrmɪn/",
            "syllables": ["met", "FOR", "min"],
            "emphasis": "FOR",
            "common_errors": ["MET-for-min", "met-FOR-meen"]
        },
        "atorvastatin": {
            "ipa": "/əˌtɔːrvəˈstætɪn/",
            "syllables": ["a", "TOR", "va", "sta", "tin"],
            "emphasis": "TOR",
            "common_errors": ["at-or-VAS-ta-tin"]
        },
        "lisinopril": {
            "ipa": "/laɪˈsɪnəprɪl/",
            "syllables": ["lye", "SIN", "oh", "pril"],
            "emphasis": "SIN",
            "common_errors": ["LI-sin-o-pril"]
        },
        "amlodipine": {
            "ipa": "/æmˈloʊdɪpin/",
            "syllables": ["am", "LOH", "di", "peen"],
            "emphasis": "LOH",
            "common_errors": ["AM-lo-dip-een"]
        },
        "omeprazole": {
            "ipa": "/oʊˈmɛprəzoʊl/",
            "syllables": ["oh", "MEP", "ra", "zole"],
            "emphasis": "MEP",
            "common_errors": ["OH-me-pray-zole"]
        },
        "phenytoin": {
            "ipa": "/ˈfɛnɪtɔɪn/",
            "syllables": ["FEN", "i", "toyn"],
            "emphasis": "FEN",
            "common_errors": ["fen-ee-TOY-in"]
        },
        "warfarin": {
            "ipa": "/ˈwɔːrfərɪn/",
            "syllables": ["WAR", "far", "in"],
            "emphasis": "WAR",
            "common_errors": ["war-FAR-in"]
        },
        "levothyroxine": {
            "ipa": "/ˌliːvoʊθaɪˈrɒksiːn/",
            "syllables": ["lee", "voh", "thy", "ROX", "een"],
            "emphasis": "ROX",
            "common_errors": ["LE-vo-thy-rox-een"]
        },
        "prednisone": {
            "ipa": "/ˈprɛdnɪsoʊn/",
            "syllables": ["PRED", "ni", "sone"],
            "emphasis": "PRED",
            "common_errors": ["pred-NI-sone"]
        },
        "gabapentin": {
            "ipa": "/ˌɡæbəˈpɛntɪn/",
            "syllables": ["ga", "ba", "PEN", "tin"],
            "emphasis": "PEN",
            "common_errors": ["GAB-a-pen-tin"]
        }
    }
    
    def get_pronunciation(self, drug_name: str, format_type: str = "detailed") -> Dict:
        """Get pronunciation guide for a drug."""
        drug_lower = drug_name.lower().strip()
        
        if drug_lower in self.DRUG_DATABASE:
            data = self.DRUG_DATABASE[drug_lower]
            return {
                "drug_name": drug_name,
                "ipa_transcription": data["ipa"],
                "syllable_breakdown": data["syllables"],
                "emphasis": data["emphasis"],
                "audio_ssml": self._generate_ssml(drug_name, data),
                "common_errors": data.get("common_errors", []),
                "tips": f"Emphasize the '{data['emphasis']}' syllable"
            }
        
        # Generic fallback
        return self._generate_generic_guide(drug_name)
    
    def _generate_ssml(self, name: str, data: Dict) -> str:
        """Generate SSML for audio synthesis."""
        syllables = "-".join(data["syllables"])
        return f'<speak><phoneme alphabet="ipa" ph="{data["ipa"]}">{name}</phoneme> is pronounced: {syllables}</speak>'
    
    def _generate_generic_guide(self, drug_name: str) -> Dict:
        """Generate generic pronunciation guide."""
        return {
            "drug_name": drug_name,
            "ipa_transcription": "See detailed guide",
            "syllable_breakdown": self._guess_syllables(drug_name),
            "emphasis": "First syllable",
            "note": "Drug not in database. Using generic rules.",
            "common_errors": []
        }
    
    def _guess_syllables(self, name: str) -> List[str]:
        """Basic syllable splitting."""
        # Simple vowel-based splitting
        import re
        pattern = r'[aeiouy]+[^aeiouy]*'
        matches = re.findall(pattern, name.lower())
        return matches if matches else [name]
    
    def search_drugs(self, prefix: str) -> List[str]:
        """Search drugs by prefix."""
        prefix_lower = prefix.lower()
        return [name for name in self.DRUG_DATABASE.keys() if name.startswith(prefix_lower)]

def main():
    import sys
    pronouncer = DrugPronunciation()
    
    drug = sys.argv[1] if len(sys.argv) > 1 else "metformin"
    result = pronouncer.get_pronunciation(drug)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

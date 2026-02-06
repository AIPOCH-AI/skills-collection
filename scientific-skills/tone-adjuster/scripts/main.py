#!/usr/bin/env python3
"""Tone Adjuster - Bidirectional medical text tone converter."""

import json
import re
from typing import Dict, List

class ToneAdjuster:
    """Adjusts tone of medical text."""
    
    JARGON_DICTIONARY = {
        "myocardial infarction": "heart attack",
        "cerebrovascular accident": "stroke",
        "hypertension": "high blood pressure",
        "hyperlipidemia": "high cholesterol",
        "malignancy": "cancer",
        "benign": "not cancerous",
        "idiopathic": "unknown cause",
        "iatrogenic": "caused by medical treatment",
        "acute": "sudden/severe",
        "chronic": "long-term",
        "exacerbation": "flare-up",
        "remission": "symptoms improved",
        "etiology": "cause",
        "pathogenesis": "how disease develops",
        "morbidity": "illness/complications",
        "mortality": "death rate"
    }
    
    def adjust(self, text: str, target_tone: str, level: str = "moderate") -> Dict:
        """Adjust text tone."""
        
        original_tone = self._assess_tone(text)
        
        if target_tone == "patient_friendly":
            converted = self._to_patient_friendly(text, level)
        elif target_tone == "academic":
            converted = self._to_academic(text)
        else:
            converted = text
        
        changes = self._identify_changes(text, converted)
        
        return {
            "converted_text": converted,
            "original_tone": original_tone,
            "target_tone": target_tone,
            "adjustment_level": level,
            "readability_score": self._calc_readability(converted),
            "changes_made": changes
        }
    
    def _to_patient_friendly(self, text: str, level: str) -> str:
        """Convert to patient-friendly language."""
        result = text
        
        # Replace jargon
        for medical, plain in self.JARGON_DICTIONARY.items():
            pattern = re.compile(medical, re.IGNORECASE)
            result = pattern.sub(plain, result)
        
        # Simplify sentence structure
        result = result.replace("utilize", "use")
        result = result.replace("demonstrate", "show")
        result = result.replace("indicate", "suggest")
        result = result.replace("approximately", "about")
        
        return result
    
    def _to_academic(self, text: str) -> str:
        """Convert to academic tone."""
        # Reverse the dictionary
        reverse_dict = {v: k for k, v in self.JARGON_DICTIONARY.items()}
        
        result = text
        for plain, medical in reverse_dict.items():
            pattern = re.compile(r'\b' + re.escape(plain) + r'\b', re.IGNORECASE)
            result = pattern.sub(medical, result)
        
        return result
    
    def _assess_tone(self, text: str) -> str:
        """Assess current tone."""
        jargon_count = sum(1 for term in self.JARGON_DICTIONARY if term.lower() in text.lower())
        
        if jargon_count > 3:
            return "academic"
        elif jargon_count > 0:
            return "mixed"
        return "patient-friendly"
    
    def _identify_changes(self, original: str, converted: str) -> List[str]:
        """Identify changes made."""
        changes = []
        
        for medical, plain in self.JARGON_DICTIONARY.items():
            if medical.lower() in original.lower() and plain.lower() in converted.lower():
                changes.append(f"'{medical}' → '{plain}'")
        
        return changes[:5]  # Limit to 5 changes
    
    def _calc_readability(self, text: str) -> float:
        """Simple readability estimate (Flesch-inspired)."""
        words = len(text.split())
        sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
        avg_words_per_sentence = words / sentences
        
        # Simple score: lower is more readable
        score = max(0, min(100, 100 - (avg_words_per_sentence - 10) * 5))
        return round(score, 1)

def main():
    import sys
    adjuster = ToneAdjuster()
    
    text = sys.argv[1] if len(sys.argv) > 1 else "The patient suffered an acute myocardial infarction."
    tone = sys.argv[2] if len(sys.argv) > 2 else "patient_friendly"
    
    result = adjuster.adjust(text, tone)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

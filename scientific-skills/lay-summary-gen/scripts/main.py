#!/usr/bin/env python3
"""Lay Summary Generator - Plain language medical summary creator."""

import json
import re
from typing import Dict, List

class LaySummaryGenerator:
    """Creates plain-language summaries of medical research."""
    
    JARGON = {
        "randomized controlled trial": "study where participants were randomly assigned to treatments",
        "placebo": "inactive substance for comparison",
        "double-blind": "neither participants nor researchers knew who got which treatment",
        "efficacy": "how well the treatment works",
        "adverse events": "side effects",
        "placebo-controlled": "compared against inactive treatment",
        "multicenter": "conducted at multiple hospitals",
        "inclusion criteria": "requirements to participate",
        "exclusion criteria": "factors preventing participation",
        "primary endpoint": "main result being measured",
        "secondary endpoint": "additional results measured"
    }
    
    def generate(self, abstract: str, target: str = "public", max_words: int = 250) -> Dict:
        """Generate lay summary."""
        
        # Replace jargon
        summary = abstract
        jargon_replaced = []
        
        for term, plain in self.JARGON.items():
            if term.lower() in summary.lower():
                summary = re.sub(term, plain, summary, flags=re.IGNORECASE)
                jargon_replaced.append({"term": term, "plain": plain})
        
        # Simplify structure
        summary = self._simplify_sentences(summary)
        
        # Extract key points
        takeaways = self._extract_takeaways(summary)
        
        # Count words
        word_count = len(summary.split())
        
        # Calculate reading level
        reading_level = self._estimate_reading_level(summary)
        
        return {
            "lay_summary": summary[:max_words * 6],  # Rough character limit
            "original_word_count": len(abstract.split()),
            "summary_word_count": word_count,
            "reading_level": reading_level,
            "target_audience": target,
            "key_takeaways": takeaways,
            "jargon_replaced": jargon_replaced
        }
    
    def _simplify_sentences(self, text: str) -> str:
        """Simplify sentence structures."""
        # Break long sentences
        text = text.replace(";", ".")
        text = text.replace(" furthermore", ". Also")
        text = text.replace(" however", ". But")
        text = text.replace(" moreover", ". Also")
        
        return text
    
    def _extract_takeaways(self, text: str) -> List[str]:
        """Extract key points."""
        sentences = text.split(".")
        takeaways = []
        
        for sent in sentences:
            sent = sent.strip()
            if any(word in sent.lower() for word in ["found", "showed", "result", "conclusion", "suggests"]):
                if len(sent) > 20:
                    takeaways.append(sent)
        
        return takeaways[:3]
    
    def _estimate_reading_level(self, text: str) -> str:
        """Estimate reading grade level."""
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        if avg_word_length < 4.5:
            return "Grade 6-8 (Easy)"
        elif avg_word_length < 5.5:
            return "Grade 9-10 (Average)"
        return "Grade 11+ (Advanced)"

def main():
    import sys
    gen = LaySummaryGenerator()
    
    abstract = sys.argv[1] if len(sys.argv) > 1 else "This RCT evaluated efficacy of Drug X in N=200 patients."
    result = gen.generate(abstract)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

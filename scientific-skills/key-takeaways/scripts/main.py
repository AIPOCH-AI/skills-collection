#!/usr/bin/env python3
"""Key Takeaways - Extracts core conclusions from documents."""

import json
import re

class KeyTakeaways:
    """Extracts key points from medical documents."""
    
    def extract(self, document: str, num_takeaways: int = 5) -> dict:
        """Extract key takeaways from document."""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', document)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Score sentences by importance indicators
        indicators = ['conclusion', 'found', 'result', 'demonstrated', 'showed', 'important', 'significant', 'key finding']
        scored = []
        
        for sent in sentences:
            score = sum(1 for ind in indicators if ind in sent.lower())
            if score > 0:
                scored.append((sent, score))
        
        # Sort by score and return top N
        scored.sort(key=lambda x: x[1], reverse=True)
        takeaways = [s[0] for s in scored[:num_takeaways]]
        
        return {
            "takeaways": takeaways,
            "source_word_count": len(document.split())
        }

def main():
    extractor = KeyTakeaways()
    text = "We studied 100 patients. The key finding was significant improvement. Results showed 80% success."
    result = extractor.extract(text, 3)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

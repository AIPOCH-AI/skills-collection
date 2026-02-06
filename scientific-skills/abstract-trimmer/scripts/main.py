#!/usr/bin/env python3
"""Abstract Trimmer - Compresses abstracts to word limits."""

import json
import re

class AbstractTrimmer:
    """Trims abstracts to meet word limits."""
    
    def trim(self, abstract: str, target_words: int) -> dict:
        """Trim abstract to target word count."""
        original_words = len(abstract.split())
        
        # Remove redundant phrases
        trimmed = abstract
        redundant = [
            r'\bin this study\b',
            r'\bit is important to note that\b',
            r'\bwe found that\b',
            r'\bthere was\b',
            r'\bit was observed that\b'
        ]
        
        for pattern in redundant:
            trimmed = re.sub(pattern, '', trimmed, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        trimmed = re.sub(r'\s+', ' ', trimmed).strip()
        
        words = trimmed.split()
        if len(words) > target_words:
            # Keep first and last sentences, trim middle
            sentences = trimmed.split('. ')
            if len(sentences) > 2:
                trimmed = f"{sentences[0]}. {' '.join(words[target_words//2:target_words])}... {sentences[-1]}"
            else:
                trimmed = ' '.join(words[:target_words])
        
        final_words = len(trimmed.split())
        
        return {
            "trimmed_abstract": trimmed,
            "original_words": original_words,
            "final_words": final_words,
            "reduction_percent": round((1 - final_words/original_words) * 100, 1)
        }

def main():
    trimmer = AbstractTrimmer()
    result = trimmer.trim("This study investigated the effects of drug X on patients. It is important to note that we found significant improvements.", 10)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

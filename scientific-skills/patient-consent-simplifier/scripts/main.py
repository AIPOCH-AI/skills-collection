#!/usr/bin/env python3
"""
Patient Consent Simplifier
Simplify informed consent forms to plain language.
"""

import argparse
import re


class ConsentSimplifier:
    """Simplify consent form language."""
    
    # Common legal/medical term replacements
    REPLACEMENTS = {
        "hereby": "now",
        "hereinafter": "from now on",
        "aforementioned": "mentioned above",
        "indemnify": "protect from harm",
        "liability": "legal responsibility",
        "thereto": "to it",
        "whereas": "because",
        "witnesseth": "shows that",
        "pursuant to": "under",
        "notwithstanding": "even if",
        "prospective": "future",
        "voluntary": "by choice",
        "confidentiality": "privacy",
        "randomization": "random assignment",
        "placebo": "inactive substance",
        "adverse event": "side effect",
        "investigational": "experimental"
    }
    
    def simplify(self, text):
        """Simplify consent form text."""
        simplified = text
        
        # Replace complex terms
        for term, replacement in self.REPLACEMENTS.items():
            simplified = re.sub(r'\b' + term + r'\b', replacement, simplified, flags=re.IGNORECASE)
        
        # Break long sentences (simple heuristic)
        sentences = simplified.split(". ")
        shortened = []
        for sent in sentences:
            if len(sent.split()) > 25:
                # Try to break at conjunctions
                sent = re.sub(r',\s*and\s+', ". Also, ", sent)
                sent = re.sub(r';\s*', ". ", sent)
            shortened.append(sent)
        
        simplified = ". ".join(shortened)
        
        # Calculate readability (simple word count heuristic)
        words = text.split()
        avg_sentence_len = len(words) / max(len(sentences), 1)
        
        return {
            "original": text,
            "simplified": simplified,
            "original_word_count": len(words),
            "simplified_word_count": len(simplified.split()),
            "avg_sentence_length": avg_sentence_len,
            "terms_replaced": len(self.REPLACEMENTS)
        }
    
    def calculate_grade_level(self, text):
        """Estimate Flesch-Kincaid grade level."""
        sentences = max(len(text.split(". ")), 1)
        words = len(text.split())
        syllables = sum(self._count_syllables(w) for w in text.split())
        
        if words == 0:
            return 0
        
        # Flesch-Kincaid Grade Level formula
        grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        return max(0, round(grade, 1))
    
    def _count_syllables(self, word):
        """Rough syllable count."""
        word = word.lower().strip(".,!?;")
        if not word:
            return 0
        vowels = "aeiouy"
        count = 0
        prev_was_vowel = False
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        if word.endswith("e"):
            count -= 1
        return max(1, count)


def main():
    parser = argparse.ArgumentParser(description="Patient Consent Simplifier")
    parser.add_argument("--input", "-i", help="Input consent form file")
    parser.add_argument("--text", "-t", help="Direct text input")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--target-grade", type=int, default=5, help="Target reading grade")
    
    args = parser.parse_args()
    
    simplifier = ConsentSimplifier()
    
    if args.input:
        with open(args.input) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # Demo text
        text = """You hereby authorize the investigators to conduct research procedures 
        as described in the aforementioned protocol. You understand that participation 
        is voluntary and you may withdraw at any time without prejudice."""
    
    result = simplifier.simplify(text)
    original_grade = simplifier.calculate_grade_level(text)
    simplified_grade = simplifier.calculate_grade_level(result["simplified"])
    
    print("\n" + "="*60)
    print("CONSENT FORM SIMPLIFICATION")
    print("="*60)
    print(f"\nOriginal Grade Level: {original_grade}")
    print(f"Simplified Grade Level: {simplified_grade}")
    print(f"Word Count: {result['original_word_count']} → {result['simplified_word_count']}")
    print("\n--- SIMPLIFIED VERSION ---\n")
    print(result["simplified"])
    print("\n" + "="*60)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result["simplified"])
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()

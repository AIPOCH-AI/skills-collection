#!/usr/bin/env python3
"""
Conference Abstract Adaptor
Adapt abstracts to meet specific conference word limits and formats.
"""

import argparse
import re


class AbstractAdaptor:
    """Adapt conference abstracts."""
    
    CONFERENCE_FORMATS = {
        "ASGCT": {"word_limit": 250, "sections": ["Background", "Methods", "Results", "Conclusion"]},
        "ASCO": {"word_limit": 260, "sections": ["Background", "Methods", "Results", "Conclusion"]},
        "SfN": {"word_limit": 2000, "sections": ["Abstract"]},  # Characters
        "AACR": {"word_limit": 300, "sections": ["Background", "Methods", "Results", "Conclusion"]},
        "ASM": {"word_limit": 300, "sections": ["Abstract"]}
    }
    
    def count_words(self, text):
        """Count words in text."""
        return len(text.split())
    
    def count_characters(self, text):
        """Count characters (excluding spaces)."""
        return len(text.replace(" ", "").replace("\n", ""))
    
    def compress_text(self, text, target_words):
        """Compress text to target word count."""
        words = text.split()
        if len(words) <= target_words:
            return text
        
        # Simple compression - truncate with ellipsis
        compressed = " ".join(words[:target_words])
        return compressed.rstrip(".,") + "..."
    
    def adapt_structure(self, abstract, conference):
        """Adapt abstract structure for conference."""
        format_info = self.CONFERENCE_FORMATS.get(conference, {"word_limit": 250})
        
        # Try to identify sections
        sections = {}
        current_section = "text"
        
        for line in abstract.split('\n'):
            line_lower = line.lower().strip()
            if line_lower.startswith(("background", "introduction")):
                current_section = "background"
                sections[current_section] = []
            elif line_lower.startswith(("methods", "material")):
                current_section = "methods"
                sections[current_section] = []
            elif line_lower.startswith(("results", "findings")):
                current_section = "results"
                sections[current_section] = []
            elif line_lower.startswith(("conclusion", "discussion")):
                current_section = "conclusion"
                sections[current_section] = []
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)
        
        return sections, format_info
    
    def format_for_conference(self, abstract, conference):
        """Format abstract for specific conference."""
        sections, format_info = self.adapt_structure(abstract, conference)
        word_limit = format_info["word_limit"]
        
        # Combine all text
        full_text = " ".join([" ".join(lines) for lines in sections.values()])
        
        # Check length
        word_count = self.count_words(full_text)
        char_count = self.count_characters(full_text)
        
        result = {
            "original_words": word_count,
            "original_chars": char_count,
            "target_words": word_limit,
            "conference": conference,
            "within_limit": word_count <= word_limit
        }
        
        if word_count > word_limit:
            result["compressed"] = self.compress_text(full_text, word_limit)
            result["compressed_words"] = self.count_words(result["compressed"])
        else:
            result["compressed"] = full_text
            result["compressed_words"] = word_count
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Conference Abstract Adaptor")
    parser.add_argument("--abstract", "-a", required=True, help="Abstract text file")
    parser.add_argument("--conference", "-c", required=True,
                       help="Target conference (ASGCT, ASCO, SfN, AACR, ASM)")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--list-conferences", "-l", action="store_true",
                       help="List supported conferences")
    
    args = parser.parse_args()
    
    adaptor = AbstractAdaptor()
    
    if args.list_conferences:
        print("\nSupported conferences:")
        for conf, info in adaptor.CONFERENCE_FORMATS.items():
            print(f"  {conf}: {info['word_limit']} words")
        return
    
    # Load abstract
    with open(args.abstract) as f:
        abstract = f.read()
    
    # Adapt
    result = adaptor.format_for_conference(abstract, args.conference)
    
    print(f"\n{'='*60}")
    print(f"CONFERENCE: {result['conference']}")
    print(f"Word Limit: {result['target_words']}")
    print(f"{'='*60}")
    print(f"Original: {result['original_words']} words")
    print(f"Adapted:  {result['compressed_words']} words")
    print(f"Status:   {'✓ Within limit' if result['within_limit'] else '⚠ Compressed to fit'}")
    print(f"{'='*60}\n")
    
    print("ADAPTED ABSTRACT:")
    print("-"*60)
    print(result['compressed'])
    print("-"*60)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result['compressed'])
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()

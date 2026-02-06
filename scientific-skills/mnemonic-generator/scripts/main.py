#!/usr/bin/env python3
"""
Mnemonic Generator
Create memory aids for anatomy and pharmacology.
"""

import argparse
import random


class MnemonicGenerator:
    """Generate medical mnemonics."""
    
    KNOWN_MNEMONICS = {
        "cranial_nerves": {
            "on_old_olympus": "On Old Olympus Towering Tops A Finn And German Viewed Some Hops",
            "explanation": "Olfactory, Optic, Oculomotor, Trochlear, Trigeminal, Abducens, Facial, Auditory, Glossopharyngeal, Vagus, Spinal Accessory, Hypoglossal"
        },
        "brachial_plexus": {
            "read_the_damn_cadaver": "Roots, Trunks, Divisions, Cords, Branches",
            "explanation": "5 Roots, 3 Trunks, 6 Divisions, 3 Cords, 5 Branches"
        }
    }
    
    def generate_acronym(self, items):
        """Generate acronym from list of items."""
        first_letters = [item[0].upper() for item in items]
        acronym = ''.join(first_letters)
        
        # Try to find words starting with these letters
        words = self._find_words(first_letters)
        
        return {
            "acronym": acronym,
            "suggested_phrase": ' '.join(words),
            "items": items
        }
    
    def _find_words(self, letters):
        """Find words starting with given letters."""
        word_bank = {
            'O': ['On', 'Old', 'Olympus', 'Octopus'],
            'T': ['Towering', 'Tall', 'Tiny', 'Top'],
            'A': ['A', 'And', 'All', 'Animals'],
            'F': ['Finn', 'Funny', 'Fast', 'First'],
            'G': ['German', 'Great', 'Good', 'Green'],
            'V': ['Viewed', 'Very', 'Vast', 'Victory'],
            'S': ['Some', 'Small', 'Smart', 'Silly'],
            'H': ['Hops', 'Happy', 'Hot', 'High']
        }
        
        words = []
        for letter in letters:
            if letter in word_bank:
                words.append(random.choice(word_bank[letter]))
            else:
                words.append(letter)
        
        return words
    
    def generate_story(self, items, topic):
        """Generate a story-based mnemonic."""
        story = f"Imagine a scene about {topic}.\n\n"
        
        for i, item in enumerate(items, 1):
            story += f"{i}. {item}\n"
        
        story += f"\nCreate a vivid mental image connecting these {len(items)} items."
        
        return story
    
    def print_mnemonic(self, mnemonic, mnemonic_type="acronym"):
        """Print formatted mnemonic."""
        print(f"\n{'='*60}")
        print("MNEMONIC GENERATOR")
        print(f"{'='*60}\n")
        
        if mnemonic_type == "acronym":
            print(f"ACRONYM: {mnemonic['acronym']}")
            print(f"\nSUGGESTED PHRASE:")
            print(f"  \"{mnemonic['suggested_phrase']}\"")
            print(f"\nITEMS:")
            for i, item in enumerate(mnemonic['items'], 1):
                letter = item[0].upper()
                print(f"  {letter} = {item}")
        else:
            print(mnemonic)
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Mnemonic Generator")
    parser.add_argument("--items", "-i", help="Comma-separated list of items")
    parser.add_argument("--topic", "-t", help="Topic for context")
    parser.add_argument("--type", choices=["acronym", "story"], default="acronym",
                       help="Mnemonic type")
    parser.add_argument("--list-known", action="store_true", help="List known mnemonics")
    
    args = parser.parse_args()
    
    generator = MnemonicGenerator()
    
    if args.list_known:
        print("\nKnown Medical Mnemonics:")
        for key, value in generator.KNOWN_MNEMONICS.items():
            print(f"\n{key.upper()}:")
            for name, mnemonic in value.items():
                if name != "explanation":
                    print(f"  {name}: {mnemonic}")
        return
    
    if args.items:
        items = [item.strip() for item in args.items.split(",")]
        
        if args.type == "acronym":
            mnemonic = generator.generate_acronym(items)
        else:
            mnemonic = generator.generate_story(items, args.topic or "medical topic")
        
        generator.print_mnemonic(mnemonic, args.type)
    else:
        # Demo
        items = ["Olfactory", "Optic", "Oculomotor", "Trochlear", "Trigeminal"]
        mnemonic = generator.generate_acronym(items)
        generator.print_mnemonic(mnemonic)


if __name__ == "__main__":
    main()

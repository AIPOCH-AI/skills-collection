#!/usr/bin/env python3
"""
Figure Reference Checker
Check figure reference consistency.
"""

import argparse
import re


class FigureChecker:
    """Check figure references."""
    
    def check_references(self, text):
        """Find figure references in text."""
        pattern = r'Fig\.?\s*(\d+)[A-Z]?'
        matches = re.findall(pattern, text)
        return set(matches)
    
    def validate(self, manuscript):
        """Validate figure references."""
        refs = self.check_references(manuscript)
        print(f"Found figure references: {sorted(refs)}")
        return refs


def main():
    parser = argparse.ArgumentParser(description="Figure Reference Checker")
    parser.add_argument("--manuscript", "-m", required=True, help="Manuscript text or file")
    args = parser.parse_args()
    
    checker = FigureChecker()
    checker.validate(args.manuscript)


if __name__ == "__main__":
    main()

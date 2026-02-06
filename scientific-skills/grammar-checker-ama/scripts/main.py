#!/usr/bin/env python3
"""
Grammar Checker (AMA)
Check grammar for AMA style medical writing.
"""

import argparse


class AMAChecker:
    """Check grammar for AMA style."""
    
    def check_passive_voice(self, text):
        """Detect passive voice constructions."""
        passive_indicators = ["was performed", "were analyzed", "is shown", "are demonstrated"]
        issues = []
        for indicator in passive_indicators:
            if indicator in text.lower():
                issues.append(f"Passive voice detected: '{indicator}'")
        return issues
    
    def check(self, text):
        """Run all grammar checks."""
        results = {
            "passive_voice": self.check_passive_voice(text),
            "suggestions": []
        }
        return results


def main():
    parser = argparse.ArgumentParser(description="Grammar Checker (AMA)")
    parser.add_argument("--text", "-t", required=True, help="Text to check")
    args = parser.parse_args()
    
    checker = AMAChecker()
    results = checker.check(args.text)
    
    print("AMA Grammar Check Results:")
    print("-" * 50)
    if results["passive_voice"]:
        print("\nPassive voice issues:")
        for issue in results["passive_voice"]:
            print(f"  - {issue}")
    else:
        print("\nNo passive voice issues found.")


if __name__ == "__main__":
    main()

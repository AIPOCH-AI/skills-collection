#!/usr/bin/env python3
"""
Journal Impact Factor Trend
Analyze journal IF trends over time.
"""

import argparse
from datetime import datetime


class JFTrendAnalyzer:
    """Analyze journal impact factor trends."""
    
    # Mock data - in real implementation would query Journal Citation Reports
    JOURNAL_DB = {
        "Nature Medicine": {
            "if_trend": [36.13, 36.13, 53.44, 58.70, 82.90],
            "quartile": ["Q1", "Q1", "Q1", "Q1", "Q1"],
            "category": "Medicine, Research & Experimental"
        },
        "Cell": {
            "if_trend": [31.40, 36.22, 41.58, 45.50, 64.50],
            "quartile": ["Q1", "Q1", "Q1", "Q1", "Q1"],
            "category": "Cell Biology"
        },
        "NEJM": {
            "if_trend": [74.70, 78.10, 91.25, 95.25, 120.70],
            "quartile": ["Q1", "Q1", "Q1", "Q1", "Q1"],
            "category": "Medicine, General & Internal"
        }
    }
    
    def analyze(self, journal_name, years=5):
        """Analyze journal trend."""
        if journal_name not in self.JOURNAL_DB:
            return None
        
        data = self.JOURNAL_DB[journal_name]
        recent_if = data["if_trend"][-years:]
        
        # Calculate trend
        growth = (recent_if[-1] - recent_if[0]) / recent_if[0] * 100
        
        if growth > 20:
            trend = "🚀 Rising star"
        elif growth > 5:
            trend = "📈 Growing"
        elif growth > -5:
            trend = "➡️ Stable"
        else:
            trend = "📉 Declining"
        
        return {
            "journal": journal_name,
            "category": data["category"],
            "current_if": recent_if[-1],
            "if_5yr_ago": recent_if[0],
            "growth": growth,
            "trend": trend,
            "quartile": data["quartile"][-1]
        }
    
    def print_report(self, result):
        """Print analysis report."""
        print(f"\n{'='*60}")
        print(f"Journal: {result['journal']}")
        print(f"Category: {result['category']}")
        print(f"{'='*60}")
        print(f"Current IF: {result['current_if']:.2f}")
        print(f"5 Years Ago: {result['if_5yr_ago']:.2f}")
        print(f"Growth: {result['growth']:+.1f}%")
        print(f"Trend: {result['trend']}")
        print(f"Current Quartile: {result['quartile']}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Journal Impact Factor Trend")
    parser.add_argument("--journal", "-j", help="Journal name")
    parser.add_argument("--journal-list", "-l", help="File with journal names")
    parser.add_argument("--years", type=int, default=5, help="Years to analyze")
    
    args = parser.parse_args()
    
    analyzer = JFTrendAnalyzer()
    
    if args.journal:
        result = analyzer.analyze(args.journal, args.years)
        if result:
            analyzer.print_report(result)
        else:
            print(f"Journal '{args.journal}' not found in database")
    elif args.journal_list:
        with open(args.journal_list) as f:
            for line in f:
                journal = line.strip()
                if journal:
                    result = analyzer.analyze(journal, args.years)
                    if result:
                        analyzer.print_report(result)
    else:
        # Demo mode
        print("Demo mode - analyzing sample journals:")
        for journal in ["Nature Medicine", "Cell", "NEJM"]:
            result = analyzer.analyze(journal, args.years)
            analyzer.print_report(result)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Grant Funding Scout
NIH funding trend analysis to identify high-priority research areas.
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime


class FundingScout:
    """Analyze funding trends and opportunities."""
    
    # Mock funding data
    FUNDING_DATA = {
        "AI/ML": {"trend": "rising", "funding_change": 45, "priority": "high"},
        "CRISPR": {"trend": "stable", "funding_change": 15, "priority": "high"},
        "Immunotherapy": {"trend": "rising", "funding_change": 35, "priority": "high"},
        "Microbiome": {"trend": "rising", "funding_change": 28, "priority": "medium"},
        "Single Cell": {"trend": "rising", "funding_change": 40, "priority": "high"},
        "Structural Biology": {"trend": "stable", "funding_change": 8, "priority": "medium"},
        "Traditional": {"trend": "declining", "funding_change": -5, "priority": "low"}
    }
    
    INSTITUTES = {
        "NCI": "National Cancer Institute",
        "NIGMS": "General Medical Sciences",
        "NHLBI": "Heart, Lung, and Blood",
        "NIAID": "Allergy and Infectious Diseases",
        "NIAMS": "Arthritis and Musculoskeletal",
        "NINDS": "Neurological Disorders"
    }
    
    def analyze_trends(self, field=None):
        """Analyze funding trends by field."""
        if field:
            return self.FUNDING_DATA.get(field, {})
        return self.FUNDING_DATA
    
    def identify_opportunities(self, research_area):
        """Identify funding opportunities."""
        area_lower = research_area.lower()
        
        opportunities = []
        
        # Match to trending areas
        for trend_area, data in self.FUNDING_DATA.items():
            if trend_area.lower() in area_lower or area_lower in trend_area.lower():
                opportunities.append({
                    "area": trend_area,
                    "trend": data["trend"],
                    "priority": data["priority"],
                    "funding_change": data["funding_change"]
                })
        
        # Suggest related areas
        if "ai" in area_lower or "machine" in area_lower:
            opportunities.append({
                "area": "AI/ML",
                "trend": "rising",
                "priority": "high",
                "note": "Cross-disciplinary opportunity"
            })
        
        if "cancer" in area_lower:
            opportunities.append({
                "area": "Immunotherapy",
                "trend": "rising",
                "priority": "high",
                "note": "Hot area in cancer research"
            })
        
        return opportunities
    
    def suggest_institutes(self, research_area):
        """Suggest relevant NIH institutes."""
        area_lower = research_area.lower()
        suggestions = []
        
        if "cancer" in area_lower:
            suggestions.append({"institute": "NCI", "fit": "excellent"})
        if "heart" in area_lower or "cardio" in area_lower:
            suggestions.append({"institute": "NHLBI", "fit": "excellent"})
        if "immune" in area_lower or "infect" in area_lower:
            suggestions.append({"institute": "NIAID", "fit": "excellent"})
        if "brain" in area_lower or "neuro" in area_lower:
            suggestions.append({"institute": "NINDS", "fit": "excellent"})
        
        if not suggestions:
            suggestions.append({"institute": "NIGMS", "fit": "general"})
        
        return suggestions
    
    def print_report(self, research_area, opportunities, institutes):
        """Print funding scout report."""
        print(f"\n{'='*60}")
        print(f"FUNDING SCOUT REPORT: {research_area.upper()}")
        print(f"{'='*60}\n")
        
        print("FUNDING OPPORTUNITIES:")
        print("-"*60)
        for opp in opportunities:
            trend_icon = "📈" if opp["trend"] == "rising" else "➡️" if opp["trend"] == "stable" else "📉"
            print(f"{trend_icon} {opp['area']}")
            print(f"   Priority: {opp['priority'].upper()}")
            if 'funding_change' in opp:
                print(f"   Funding change: {opp['funding_change']:+.0f}%")
            if 'note' in opp:
                print(f"   Note: {opp['note']}")
            print()
        
        print("-"*60)
        print("\nSUGGESTED INSTITUTES:")
        print("-"*60)
        for inst in institutes:
            full_name = self.INSTITUTES.get(inst["institute"], "")
            print(f"  {inst['institute']}: {full_name}")
            print(f"     Fit: {inst['fit']}")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Grant Funding Scout")
    parser.add_argument("--area", "-a", required=True, help="Research area")
    parser.add_argument("--trends", "-t", action="store_true", help="Show all trends")
    parser.add_argument("--output", "-o", help="Output JSON file")
    
    args = parser.parse_args()
    
    scout = FundingScout()
    
    if args.trends:
        print("\nCurrent Funding Trends:")
        print("-"*60)
        for area, data in scout.FUNDING_DATA.items():
            trend_icon = "📈" if data["trend"] == "rising" else "➡️" if data["trend"] == "stable" else "📉"
            print(f"{trend_icon} {area}: {data['funding_change']:+.0f}% ({data['priority']})")
        return
    
    opportunities = scout.identify_opportunities(args.area)
    institutes = scout.suggest_institutes(args.area)
    
    scout.print_report(args.area, opportunities, institutes)
    
    if args.output:
        result = {
            "research_area": args.area,
            "opportunities": opportunities,
            "suggested_institutes": institutes
        }
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()

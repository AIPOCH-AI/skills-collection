#!/usr/bin/env python3
"""
KOL Profiler
Analyze physician academic influence and collaboration networks.
"""

import argparse
import json
from collections import defaultdict


class KOLProfiler:
    """Profile Key Opinion Leaders in medicine."""
    
    def __init__(self):
        self.publications = defaultdict(list)
        self.collaborations = defaultdict(set)
    
    def add_publication(self, author, publication):
        """Add publication to author's record."""
        self.publications[author].append(publication)
    
    def calculate_metrics(self, author):
        """Calculate academic metrics for KOL."""
        pubs = self.publications.get(author, [])
        
        total_pubs = len(pubs)
        total_citations = sum(p.get("citations", 0) for p in pubs)
        
        # h-index calculation (simplified)
        citations = sorted([p.get("citations", 0) for p in pubs], reverse=True)
        h_index = 0
        for i, c in enumerate(citations, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        return {
            "name": author,
            "total_publications": total_pubs,
            "total_citations": total_citations,
            "h_index": h_index,
            "average_citations": total_citations / total_pubs if total_pubs > 0 else 0
        }
    
    def identify_collaborators(self, author):
        """Identify frequent collaborators."""
        return list(self.collaborations.get(author, set()))
    
    def profile_kol(self, author):
        """Generate complete KOL profile."""
        metrics = self.calculate_metrics(author)
        collaborators = self.identify_collaborators(author)
        
        # Determine influence tier
        if metrics["h_index"] >= 50:
            tier = "Tier 1 (Global Leader)"
        elif metrics["h_index"] >= 30:
            tier = "Tier 2 (National Expert)"
        elif metrics["h_index"] >= 15:
            tier = "Tier 3 (Regional Expert)"
        else:
            tier = "Emerging"
        
        return {
            **metrics,
            "tier": tier,
            "collaborators": collaborators,
            "collaboration_network_size": len(collaborators)
        }
    
    def print_profile(self, profile):
        """Print KOL profile."""
        print(f"\n{'='*60}")
        print(f"KOL PROFILE: {profile['name']}")
        print(f"{'='*60}\n")
        
        print(f"Influence Tier: {profile['tier']}")
        print(f"Total Publications: {profile['total_publications']}")
        print(f"Total Citations: {profile['total_citations']}")
        print(f"h-index: {profile['h_index']}")
        print(f"Average Citations per Paper: {profile['average_citations']:.1f}")
        print()
        
        if profile['collaborators']:
            print(f"Collaboration Network ({profile['collaboration_network_size']} collaborators):")
            for collab in profile['collaborators'][:10]:
                print(f"  • {collab}")
            if len(profile['collaborators']) > 10:
                print(f"  ... and {len(profile['collaborators']) - 10} more")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="KOL Profiler")
    parser.add_argument("--author", "-a", required=True, help="Author name to profile")
    parser.add_argument("--data", "-d", help="Publication data JSON file")
    parser.add_argument("--demo", action="store_true", help="Show demo profile")
    
    args = parser.parse_args()
    
    profiler = KOLProfiler()
    
    if args.demo or not args.data:
        # Demo data
        demo_pubs = [
            {"title": "Paper 1", "citations": 150},
            {"title": "Paper 2", "citations": 80},
            {"title": "Paper 3", "citations": 65},
            {"title": "Paper 4", "citations": 45},
            {"title": "Paper 5", "citations": 30}
        ]
        for pub in demo_pubs:
            profiler.add_publication(args.author, pub)
        
        profiler.collaborations[args.author] = {"Dr. Smith", "Dr. Jones", "Dr. Lee"}
    else:
        with open(args.data) as f:
            data = json.load(f)
        for pub in data.get("publications", []):
            profiler.add_publication(args.author, pub)
    
    profile = profiler.profile_kol(args.author)
    profiler.print_profile(profile)


if __name__ == "__main__":
    main()

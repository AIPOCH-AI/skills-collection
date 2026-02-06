#!/usr/bin/env python3
"""
Citation Chasing & Mapping
Trace citation networks to discover related research.
"""

import argparse
import json
from collections import defaultdict


class CitationNetwork:
    """Map and analyze citation networks."""
    
    def __init__(self):
        self.papers = {}
        self.citations = defaultdict(list)
    
    def add_paper(self, paper_id, title, year, citations=None):
        """Add paper to network."""
        self.papers[paper_id] = {
            "title": title,
            "year": year,
            "citations": citations or []
        }
    
    def find_citing_papers(self, paper_id):
        """Find papers that cite this paper."""
        citing = []
        for pid, data in self.papers.items():
            if paper_id in data.get("citations", []):
                citing.append(pid)
        return citing
    
    def find_related_papers(self, paper_id, depth=2):
        """Find papers related through citation network."""
        related = set()
        to_check = {paper_id}
        
        for d in range(depth):
            new_related = set()
            for pid in to_check:
                # Papers this paper cites
                if pid in self.papers:
                    new_related.update(self.papers[pid].get("citations", []))
                # Papers that cite this paper
                new_related.update(self.find_citing_papers(pid))
            
            related.update(new_related)
            to_check = new_related - {paper_id}
        
        return related
    
    def identify_key_papers(self):
        """Identify highly cited papers (potential foundational works)."""
        citation_counts = defaultdict(int)
        
        for data in self.papers.values():
            for cited in data.get("citations", []):
                citation_counts[cited] += 1
        
        sorted_papers = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_papers[:10]
    
    def export_network(self, output_file):
        """Export citation network to JSON."""
        network = {
            "nodes": [
                {"id": pid, "title": data["title"], "year": data["year"]}
                for pid, data in self.papers.items()
            ],
            "edges": [
                {"source": pid, "target": cited}
                for pid, data in self.papers.items()
                for cited in data.get("citations", [])
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(network, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Citation Chasing & Mapping")
    parser.add_argument("--paper-id", "-p", help="Starting paper ID")
    parser.add_argument("--depth", "-d", type=int, default=2, help="Search depth")
    parser.add_argument("--network-file", "-n", help="Citation network JSON file")
    parser.add_argument("--output", "-o", default="network.json", help="Output file")
    
    args = parser.parse_args()
    
    network = CitationNetwork()
    
    # Load or create demo network
    if args.network_file:
        with open(args.network_file) as f:
            data = json.load(f)
        for node in data.get("nodes", []):
            network.add_paper(node["id"], node.get("title", ""), node.get("year", 2020))
        for edge in data.get("edges", []):
            if edge["source"] in network.papers:
                network.papers[edge["source"]]["citations"].append(edge["target"])
    else:
        # Demo network
        network.add_paper("paper1", "Original CRISPR Paper", 2012, ["paper2", "paper3"])
        network.add_paper("paper2", "CRISPR Applications", 2013, ["paper4"])
        network.add_paper("paper3", "CRISPR Improvements", 2014, ["paper4", "paper5"])
        network.add_paper("paper4", "Therapeutic Applications", 2015, [])
        network.add_paper("paper5", "Clinical Trials", 2016, [])
    
    if args.paper_id:
        print(f"\nAnalyzing citation network for: {args.paper_id}")
        print(f"Search depth: {args.depth}")
        
        related = network.find_related_papers(args.paper_id, args.depth)
        print(f"\nFound {len(related)} related papers:")
        for pid in related:
            if pid in network.papers:
                print(f"  - {pid}: {network.papers[pid]['title']} ({network.papers[pid]['year']})")
    
    # Identify key papers
    print("\nMost cited papers (foundational works):")
    key_papers = network.identify_key_papers()
    for pid, count in key_papers[:5]:
        title = network.papers.get(pid, {}).get("title", "Unknown")
        print(f"  {pid}: {count} citations - {title[:50]}...")
    
    # Export
    network.export_network(args.output)
    print(f"\nNetwork exported to: {args.output}")


if __name__ == "__main__":
    main()

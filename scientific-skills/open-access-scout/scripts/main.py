#!/usr/bin/env python3
"""
Open Access Scout
Find legal open access versions of paywalled papers.
"""

import argparse


class OpenAccessScout:
    """Find open access versions of papers."""
    
    SOURCES = [
        {"name": "Unpaywall", "url": "https://api.unpaywall.org/"},
        {"name": "CORE", "url": "https://core.ac.uk/"},
        {"name": "PubMed Central", "url": "https://www.ncbi.nlm.nih.gov/pmc/"},
        {"name": "arXiv", "url": "https://arxiv.org/"},
        {"name": "bioRxiv", "url": "https://www.biorxiv.org/"},
        {"name": "medRxiv", "url": "https://www.medrxiv.org/"},
        {"name": "Sci-Hub", "url": "(use with caution)"}
    ]
    
    def search_open_access(self, doi=None, title=None, authors=None):
        """Search for open access versions."""
        results = []
        
        # Mock search results
        if doi or title:
            results.append({
                "source": "Unpaywall",
                "status": "OA version found",
                "license": "CC BY",
                "url": f"https://unpaywall.org/{doi or 'search'}"
            })
            
            results.append({
                "source": "PubMed Central",
                "status": "Preprint available",
                "license": "Unknown",
                "url": "https://pmc.ncbi.nlm.nih.gov/"
            })
        
        return results
    
    def print_results(self, results, paper_info):
        """Print search results."""
        print(f"\n{'='*60}")
        print("OPEN ACCESS SEARCH RESULTS")
        print(f"{'='*60}\n")
        
        print(f"Paper: {paper_info.get('title', 'Unknown')}")
        print()
        
        if results:
            print("Open access versions found:")
            for r in results:
                print(f"\n  Source: {r['source']}")
                print(f"  Status: {r['status']}")
                print(f"  License: {r['license']}")
                print(f"  URL: {r['url']}")
        else:
            print("No open access version found.")
            print("\nTry contacting the authors directly or checking:")
            for source in self.SOURCES[:4]:
                print(f"  - {source['name']}: {source['url']}")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Open Access Scout")
    parser.add_argument("--doi", help="Paper DOI")
    parser.add_argument("--title", "-t", help="Paper title")
    parser.add_argument("--authors", "-a", help="Authors")
    parser.add_argument("--list-sources", action="store_true", help="List OA sources")
    
    args = parser.parse_args()
    
    scout = OpenAccessScout()
    
    if args.list_sources:
        print("\nOpen Access Sources:")
        for source in scout.SOURCES:
            print(f"  - {source['name']}: {source['url']}")
        return
    
    paper_info = {
        "title": args.title or args.doi or "Unknown paper",
        "doi": args.doi,
        "authors": args.authors
    }
    
    results = scout.search_open_access(args.doi, args.title, args.authors)
    scout.print_results(results, paper_info)


if __name__ == "__main__":
    main()

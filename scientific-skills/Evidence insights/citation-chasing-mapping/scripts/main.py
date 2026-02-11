#!/usr/bin/env python3
"""
Citation Chasing & Mapping
Trace citation networks using Semantic Scholar API to discover related research.
Supports automatic DOI/Title/PMID lookup with multi-hop citation tracing.
"""

import argparse
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


@dataclass
class Paper:
    """Represents a paper with its metadata."""
    paper_id: str
    title: str
    year: int
    authors: List[str] = field(default_factory=list)
    venue: str = ""
    citation_count: int = 0
    reference_count: int = 0
    doi: str = ""
    pmid: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


class SemanticScholarClient:
    """Client for Semantic Scholar API."""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, delay: float = 0.5):
        """
        Initialize client.
        
        Args:
            delay: Delay between API requests (seconds) to respect rate limits
        """
        self.delay = delay
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: str = "") -> dict:
        """Make API request with rate limiting."""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            url += f"?{params}"
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                self.last_request_time = time.time()
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  ⚠️  Paper not found in Semantic Scholar")
                return {}
            elif e.code == 429:
                print(f"  ⚠️  Rate limit reached. Waiting...")
                time.sleep(5)
                return self._make_request(endpoint, params)
            else:
                print(f"  ⚠️  API error: {e.code}")
                return {}
        except Exception as e:
            print(f"  ⚠️  Request failed: {e}")
            return {}
    
    def search_paper(self, query: str, limit: int = 5) -> List[dict]:
        """Search for papers by title or keywords."""
        print(f"🔍 Searching for: {query}")
        params = f"query={urllib.parse.quote(query)}&limit={limit}&fields=paperId,title,year,authors,venue,citationCount,referenceCount,externalIds"
        response = self._make_request("/paper/search", params)
        return response.get("data", [])
    
    def get_paper_by_id(self, paper_id: str) -> Optional[dict]:
        """Get paper details by Semantic Scholar ID, DOI, or PMID."""
        # Try different ID formats
        if paper_id.startswith("10."):
            # DOI
            endpoint = f"/paper/DOI:{paper_id}"
        elif paper_id.isdigit() and len(paper_id) > 5:
            # PMID
            endpoint = f"/paper/PMID:{paper_id}"
        else:
            # Semantic Scholar ID
            endpoint = f"/paper/{paper_id}"
        
        params = "fields=paperId,title,year,authors,venue,citationCount,referenceCount,externalIds"
        return self._make_request(endpoint, params)
    
    def get_citations(self, paper_id: str, limit: int = 100) -> List[dict]:
        """Get papers that cite this paper (descendants)."""
        params = f"limit={limit}&fields=paperId,title,year,authors,venue,citationCount,referenceCount"
        response = self._make_request(f"/paper/{paper_id}/citations", params)
        if response is None or not isinstance(response, dict):
            return []
        data = response.get("data", [])
        if data is None:
            return []
        return [item.get("citingPaper", {}) for item in data if item]
    
    def get_references(self, paper_id: str, limit: int = 100) -> List[dict]:
        """Get papers cited by this paper (ancestors)."""
        params = f"limit={limit}&fields=paperId,title,year,authors,venue,citationCount,referenceCount"
        response = self._make_request(f"/paper/{paper_id}/references", params)
        if response is None or not isinstance(response, dict):
            return []
        data = response.get("data", [])
        if data is None:
            return []
        return [item.get("citedPaper", {}) for item in data if item]


class CitationNetwork:
    """Map and analyze citation networks."""
    
    def __init__(self):
        self.papers: Dict[str, Paper] = {}
        self.edges: Set[Tuple[str, str]] = set()  # (source, target) citations
        self.references: Dict[str, Set[str]] = defaultdict(set)  # paper -> papers it cites
        self.cited_by: Dict[str, Set[str]] = defaultdict(set)  # paper -> papers citing it
    
    def add_paper(self, paper_data: dict) -> Optional[str]:
        """Add paper from API response."""
        paper_id = paper_data.get("paperId")
        if not paper_id or paper_id in self.papers:
            return paper_id
        
        # Extract authors
        authors = []
        for author in paper_data.get("authors", [])[:3]:  # Limit to first 3
            if isinstance(author, dict):
                authors.append(author.get("name", ""))
            else:
                authors.append(str(author))
        
        # Get external IDs
        external_ids = paper_data.get("externalIds", {})
        
        paper = Paper(
            paper_id=paper_id,
            title=paper_data.get("title", "Unknown"),
            year=paper_data.get("year", 0),
            authors=authors,
            venue=paper_data.get("venue", ""),
            citation_count=paper_data.get("citationCount", 0),
            reference_count=paper_data.get("referenceCount", 0),
            doi=external_ids.get("DOI", ""),
            pmid=external_ids.get("PubMed", "")
        )
        
        self.papers[paper_id] = paper
        return paper_id
    
    def add_citation(self, citing_id: str, cited_id: str):
        """Add citation relationship."""
        if citing_id and cited_id:
            self.edges.add((citing_id, cited_id))
            self.references[citing_id].add(cited_id)
            self.cited_by[cited_id].add(citing_id)
    
    def find_related_papers(self, paper_id: str, depth: int = 2) -> Set[str]:
        """Find papers related through citation network (both directions)."""
        related = set()
        to_check = {paper_id}
        seen = {paper_id}
        
        for d in range(depth):
            new_related = set()
            for pid in to_check:
                # Papers this paper cites (ancestors)
                new_related.update(self.references.get(pid, set()))
                # Papers that cite this paper (descendants)
                new_related.update(self.cited_by.get(pid, set()))
            
            # Filter out already seen papers
            new_related = new_related - seen
            related.update(new_related)
            seen.update(new_related)
            to_check = new_related
        
        return related
    
    def identify_key_papers(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Identify highly cited papers."""
        citation_counts = [(pid, len(self.cited_by.get(pid, set()))) 
                          for pid in self.papers.keys()]
        return sorted(citation_counts, key=lambda x: x[1], reverse=True)[:top_n]
    
    def export_knowledge_graph(self, output_file: str, paper_id: Optional[str] = None):
        """Export knowledge graph in standard format."""
        graph = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_papers": len(self.papers),
                "total_citations": len(self.edges),
                "center_paper": paper_id
            },
            "nodes": [],
            "edges": []
        }
        
        # Add nodes (papers)
        for pid, paper in self.papers.items():
            node = {
                "id": pid,
                "label": paper.title[:100] + "..." if len(paper.title) > 100 else paper.title,
                "title": paper.title,
                "year": paper.year,
                "authors": ", ".join(paper.authors) if paper.authors else "Unknown",
                "venue": paper.venue,
                "citation_count": paper.citation_count,
                "reference_count": paper.reference_count,
                "doi": paper.doi,
                "pmid": paper.pmid,
                "is_center": pid == paper_id
            }
            graph["nodes"].append(node)
        
        # Add edges (citations)
        for source, target in self.edges:
            edge = {
                "source": source,
                "target": target,
                "relationship": "cites"
            }
            graph["edges"].append(edge)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        return graph
    
    def print_summary(self, center_paper_id: Optional[str] = None):
        """Print network summary."""
        print("\n" + "="*70)
        print("📊 CITATION NETWORK SUMMARY")
        print("="*70)
        print(f"Total papers in network: {len(self.papers)}")
        print(f"Total citation relationships: {len(self.edges)}")
        
        if center_paper_id and center_paper_id in self.papers:
            center = self.papers[center_paper_id]
            print(f"\n🎯 Center paper: {center.title}")
            print(f"   Year: {center.year}")
            print(f"   Authors: {', '.join(center.authors) if center.authors else 'Unknown'}")
            print(f"   Citations: {center.citation_count}")
            print(f"   References: {center.reference_count}")
            
            # Direct neighbors
            direct_citations = len(self.cited_by.get(center_paper_id, set()))
            direct_refs = len(self.references.get(center_paper_id, set()))
            print(f"\n📈 Network connections:")
            print(f"   - Directly cited by: {direct_citations} papers")
            print(f"   - Directly cites: {direct_refs} papers")
        
        # Key papers
        print("\n🏆 Most cited papers in network:")
        key_papers = self.identify_key_papers(5)
        for rank, (pid, count) in enumerate(key_papers, 1):
            paper = self.papers.get(pid)
            if paper:
                title = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title
                print(f"   {rank}. [{paper.year}] {title}")
                print(f"      Citations in network: {count} | Total: {paper.citation_count}")


def build_network_from_api(
    client: SemanticScholarClient,
    network: CitationNetwork,
    start_paper_id: str,
    depth: int = 2,
    max_per_level: int = 20
) -> bool:
    """
    Build citation network by querying API.
    
    Args:
        client: Semantic Scholar API client
        network: CitationNetwork to populate
        start_paper_id: Starting paper ID
        depth: How many hops to traverse
        max_per_level: Max papers to fetch per level (to avoid explosion)
    
    Returns:
        True if successful
    """
    print(f"\n🌐 Building citation network (depth={depth})...")
    
    # Get center paper
    print(f"\n📄 Fetching center paper...")
    center_data = client.get_paper_by_id(start_paper_id)
    if not center_data:
        print(f"❌ Could not find paper: {start_paper_id}")
        return False
    
    center_id = network.add_paper(center_data)
    if not center_id:
        print("❌ Failed to add center paper to network")
        return False
    
    print(f"   ✓ Found: {center_data.get('title', 'Unknown')[:80]}")
    
    # BFS to build network
    to_process: List[Tuple[str, int]] = [(center_id, 0)]  # (paper_id, current_depth)
    processed: Set[str] = {center_id}
    
    while to_process:
        current_id, current_depth = to_process.pop(0)
        
        if current_depth >= depth:
            continue
        
        print(f"\n📍 Processing depth {current_depth+1}/{depth}: {current_id[:20]}...")
        
        # Get citations (descendants)
        print(f"   ↳ Fetching papers that cite this...")
        citations = client.get_citations(current_id, limit=max_per_level)
        for citation in citations:
            if citation and citation.get("paperId"):
                cited_id = network.add_paper(citation)
                if cited_id:
                    network.add_citation(cited_id, current_id)  # cited_id cites current_id
                    if cited_id not in processed and current_depth + 1 < depth:
                        to_process.append((cited_id, current_depth + 1))
                        processed.add(cited_id)
        print(f"      Found {len(citations)} citing papers")
        
        # Get references (ancestors)
        print(f"   ↳ Fetching papers this cites...")
        references = client.get_references(current_id, limit=max_per_level)
        for reference in references:
            if reference and reference.get("paperId"):
                ref_id = network.add_paper(reference)
                if ref_id:
                    network.add_citation(current_id, ref_id)  # current_id cites ref_id
                    if ref_id not in processed and current_depth + 1 < depth:
                        to_process.append((ref_id, current_depth + 1))
                        processed.add(ref_id)
        print(f"      Found {len(references)} referenced papers")
        
        time.sleep(0.5)  # Be nice to the API
    
    return True


def load_offline_network(network_file: str) -> Optional[CitationNetwork]:
    """Load network from offline JSON file."""
    try:
        with open(network_file, 'r') as f:
            data = json.load(f)
        
        network = CitationNetwork()
        
        # Load nodes
        for node in data.get("nodes", []):
            paper_data = {
                "paperId": node.get("id"),
                "title": node.get("title", ""),
                "year": node.get("year", 2020),
                "authors": [{"name": node.get("authors", "Unknown")}],
                "venue": node.get("venue", ""),
                "citationCount": node.get("citation_count", 0),
                "referenceCount": 0
            }
            network.add_paper(paper_data)
        
        # Load edges
        for edge in data.get("edges", []):
            network.add_citation(edge.get("source"), edge.get("target"))
        
        return network
    except Exception as e:
        print(f"❌ Error loading network file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Citation Chasing & Mapping - Trace citation networks using Semantic Scholar API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query by DOI (auto-fetch from Semantic Scholar)
  python main.py --doi "10.1038/nature14236" --depth 2
  
  # Query by title
  python main.py --title "Deep learning for protein structure prediction" --depth 1
  
  # Query by PMID
  python main.py --pmid 27669175 --depth 2
  
  # Use offline network file (legacy mode)
  python main.py --network-file network.json --paper-id paper1
  
  # Demo mode
  python main.py --demo
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--doi", help="Paper DOI to query")
    input_group.add_argument("--title", help="Paper title to search")
    input_group.add_argument("--pmid", help="PubMed ID to query")
    input_group.add_argument("--network-file", "-n", help="Offline network JSON file (legacy mode)")
    input_group.add_argument("--demo", action="store_true", help="Run demo with example data")
    
    # Analysis options
    parser.add_argument("--depth", "-d", type=int, default=2, 
                       help="Citation search depth (1-3, default: 2)")
    parser.add_argument("--max-per-level", type=int, default=20,
                       help="Max papers to fetch per level (default: 20)")
    parser.add_argument("--delay", type=float, default=0.5,
                       help="API request delay in seconds (default: 0.5)")
    
    # Output options
    parser.add_argument("--output", "-o", default="citation_network.json",
                       help="Output knowledge graph file (default: citation_network.json)")
    parser.add_argument("--format", choices=["json", "cytoscape", "gexf"], default="json",
                       help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Create network
    network = CitationNetwork()
    center_paper_id = None
    
    # Check input
    if not any([args.doi, args.title, args.pmid, args.network_file, args.demo]):
        parser.print_help()
        print("\n❌ Error: Please provide one of --doi, --title, --pmid, --network-file, or --demo")
        return
    
    # Demo mode
    if args.demo:
        print("🎮 Running DEMO mode with example CRISPR network...")
        # Add demo papers
        demo_papers = [
            ("paper1", "CRISPR-Cas9: A Programmable Dual-RNA-Guided DNA Endonuclease", 2012),
            ("paper2", "Multiplex Genome Engineering Using CRISPR-Cas Systems", 2013),
            ("paper3", "RNA-Guided Human Genome Engineering via Cas9", 2013),
            ("paper4", "CRISPR-Cas Systems for Editing, Regulating and Targeting Genomes", 2014),
            ("paper5", "A programmable dual-RNA-guided DNA endonuclease in adaptive bacterial immunity", 2012),
        ]
        
        for pid, title, year in demo_papers:
            network.add_paper({
                "paperId": pid,
                "title": title,
                "year": year,
                "authors": [{"name": "Demo Author"}],
                "citationCount": 100
            })
        
        # Add demo citations
        network.add_citation("paper2", "paper1")
        network.add_citation("paper3", "paper1")
        network.add_citation("paper4", "paper2")
        network.add_citation("paper4", "paper3")
        
        center_paper_id = "paper1"
        print("✓ Demo network created with 5 papers")
    
    # Offline network mode
    elif args.network_file:
        print(f"📁 Loading offline network from: {args.network_file}")
        loaded_network = load_offline_network(args.network_file)
        if loaded_network:
            network = loaded_network
            center_paper_id = args.paper_id if hasattr(args, 'paper_id') else None
            print(f"✓ Loaded {len(network.papers)} papers")
        else:
            return
    
    # API query mode
    else:
        # Initialize API client
        client = SemanticScholarClient(delay=args.delay)
        
        # Get starting paper ID
        start_id = None
        
        if args.doi:
            print(f"🔍 Looking up DOI: {args.doi}")
            start_id = args.doi
            center_paper_id = None  # Will be set after fetching
        
        elif args.pmid:
            print(f"🔍 Looking up PMID: {args.pmid}")
            start_id = args.pmid
            center_paper_id = None
        
        elif args.title:
            print(f"🔍 Searching by title: {args.title}")
            results = client.search_paper(args.title, limit=5)
            if results:
                print(f"\n📝 Found {len(results)} matches:")
                for i, paper in enumerate(results, 1):
                    title = paper.get("title", "Unknown")[:80]
                    year = paper.get("year", "?")
                    print(f"   {i}. [{year}] {title}")
                
                # Use first result
                start_id = results[0].get("paperId")
                center_paper_id = start_id
                print(f"\n✓ Using: {results[0].get('title', 'Unknown')[:80]}")
            else:
                print("❌ No papers found")
                return
        
        # Build network
        if start_id:
            success = build_network_from_api(
                client, network, start_id, 
                depth=args.depth,
                max_per_level=args.max_per_level
            )
            if not success:
                return
            
            # Set center paper ID
            if not center_paper_id:
                # Find the paper that matches our query
                for pid, paper in network.papers.items():
                    if args.doi and paper.doi == args.doi:
                        center_paper_id = pid
                        break
                    elif args.pmid and paper.pmid == args.pmid:
                        center_paper_id = pid
                        break
                if not center_paper_id and network.papers:
                    center_paper_id = list(network.papers.keys())[0]
    
    # Print summary
    network.print_summary(center_paper_id)
    
    # Export knowledge graph
    print(f"\n💾 Exporting knowledge graph to: {args.output}")
    graph = network.export_knowledge_graph(args.output, center_paper_id)
    print(f"✓ Exported {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    
    # Print usage tips
    print("\n" + "="*70)
    print("💡 NEXT STEPS")
    print("="*70)
    print(f"1. View the network: open {args.output}")
    print("2. Visualize with Cytoscape: Import → Network from File")
    print("3. Or use online tools: https://arrows.app/")
    print("\n📊 Network analysis complete!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Emerging Topic Scout
Main script for monitoring bioRxiv/medRxiv preprints and identifying trending topics.

Usage:
    python main.py --sources biorxiv medrxiv --days 7 --output markdown
"""

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import feedparser
import requests
from textblob import TextBlob

# Constants
BIORXIV_RSS = "https://www.biorxiv.org/rss/recent.rss"
MEDRXIV_RSS = "https://www.medrxiv.org/rss/recent.rss"
BIORXIV_API = "https://api.biorxiv.org/details/biorxiv"
MEDRXIV_API = "https://api.medrxiv.org/details/medrxiv"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


@dataclass
class Paper:
    """Represents a preprint paper."""
    title: str
    authors: List[str]
    doi: str
    source: str  # biorxiv or medrxiv
    published: str
    abstract: str = ""
    url: str = ""
    categories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Topic:
    """Represents an emerging topic."""
    name: str
    keywords: List[str]
    trending_score: float
    velocity: str  # slow, moderate, rapid, explosive
    preprint_count: int
    cross_platform_mentions: int
    related_papers: List[Paper]
    emerging_since: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "topic": self.name,
            "keywords": self.keywords,
            "trending_score": round(self.trending_score, 3),
            "velocity": self.velocity,
            "preprint_count": self.preprint_count,
            "cross_platform_mentions": self.cross_platform_mentions,
            "related_papers": [p.to_dict() for p in self.related_papers],
            "emerging_since": self.emerging_since
        }


class PreprintFetcher:
    """Fetches preprints from bioRxiv and medRxiv."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "EmergingTopicScout/1.0 (Research Tool)"
        })
    
    def fetch_rss(self, url: str, source: str, days_back: int = 7) -> List[Paper]:
        """Fetch papers from RSS feed."""
        papers = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                try:
                    # Parse publication date
                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published:
                        pub_date = datetime(*published[:6])
                        if pub_date < cutoff_date:
                            continue
                        pub_str = pub_date.strftime("%Y-%m-%d")
                    else:
                        pub_str = datetime.now().strftime("%Y-%m-%d")
                    
                    # Extract DOI
                    doi = self._extract_doi(entry.get("id", ""))
                    if not doi:
                        doi = self._extract_doi(entry.get("link", ""))
                    
                    paper = Paper(
                        title=entry.get("title", "Untitled").strip(),
                        authors=self._parse_authors(entry.get("author", "")),
                        doi=doi or f"unknown-{hash(entry.get('title', ''))}",
                        source=source,
                        published=pub_str,
                        abstract=self._clean_abstract(entry.get("summary", "")),
                        url=entry.get("link", ""),
                        categories=[tag.term for tag in entry.get("tags", [])]
                    )
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"Warning: Error parsing entry: {e}", file=sys.stderr)
                    continue
                    
        except Exception as e:
            print(f"Error fetching RSS from {source}: {e}", file=sys.stderr)
        
        return papers
    
    def fetch_api(self, source: str, cursor: str = "0", limit: int = 100) -> List[Paper]:
        """Fetch papers from API (for detailed metadata)."""
        papers = []
        base_url = BIORXIV_API if source == "biorxiv" else MEDRXIV_API
        
        try:
            url = f"{base_url}/{cursor}/json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("collection", []):
                paper = Paper(
                    title=item.get("title", "Untitled"),
                    authors=item.get("authors", "").split("; ") if item.get("authors") else [],
                    doi=item.get("doi", ""),
                    source=source,
                    published=item.get("date", ""),
                    abstract=item.get("abstract", ""),
                    url=f"https://www.{source}.org/content/{item.get('doi', '')}",
                    categories=[item.get("category", "")] if item.get("category") else []
                )
                papers.append(paper)
            
            time.sleep(self.delay)
            
        except Exception as e:
            print(f"Error fetching API from {source}: {e}", file=sys.stderr)
        
        return papers
    
    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text."""
        doi_pattern = r'10\.\d{4,}/[^\s<>"\']+'
        match = re.search(doi_pattern, text)
        return match.group(0) if match else None
    
    def _parse_authors(self, author_str: str) -> List[str]:
        """Parse author string into list."""
        if not author_str:
            return []
        # Handle various formats
        authors = re.split(r',|;|\band\b', author_str)
        return [a.strip() for a in authors if a.strip()]
    
    def _clean_abstract(self, abstract: str) -> str:
        """Clean and truncate abstract."""
        # Remove HTML tags
        abstract = re.sub(r'<[^>]+>', '', abstract)
        # Truncate if too long
        if len(abstract) > 500:
            abstract = abstract[:497] + "..."
        return abstract.strip()


class TrendAnalyzer:
    """Analyzes trends and detects emerging topics."""
    
    # Common stop words and non-informative terms
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "can", "this",
        "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "using", "based", "new", "novel", "study", "analysis", "data", "results",
        "method", "methods", "approach", "model", "models", "effect", "effects",
        "high", "low", "large", "small", "different", "similar", "important",
        "significant", "potential", "specific", "cell", "cells", "gene", "genes",
        "protein", "proteins", "expression", "role", "human", "humans", "mice",
        "mouse", "rat", "rats", "patient", "patients", "disease", "diseases"
    }
    
    # Multi-word biomed terms that should be kept together
    COMPOUND_TERMS = [
        "machine learning", "deep learning", "artificial intelligence",
        "gene therapy", "cell therapy", "stem cell", "single cell",
        "spatial transcriptomics", "crispr", "gene editing", "base editing",
        "prime editing", "mrna vaccine", "long covid", "immune checkpoint",
        "microbiome", "gut microbiota", "brain computer interface",
        "organoid", "organ on chip", "liquid biopsy", "circulating tumor",
        "next generation sequencing", "whole genome", "whole exome",
        "protein structure", "alpha fold", "cryo em", "live imaging"
    ]
    
    def __init__(self):
        self.history_file = DATA_DIR / "history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[dict]:
        """Load historical trend data."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_history(self, topics: List[Topic]):
        """Save current scan to history."""
        entry = {
            "date": datetime.now().isoformat(),
            "topics": [t.to_dict() for t in topics]
        }
        self.history.append(entry)
        # Keep only last 30 days of history
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        self.history = [h for h in self.history if h.get("date", "") > cutoff]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def extract_keywords(self, papers: List[Paper]) -> Counter:
        """Extract keywords from paper titles and abstracts."""
        keyword_counts = Counter()
        
        for paper in papers:
            text = f"{paper.title} {paper.abstract}".lower()
            
            # First, find compound terms
            found_compounds = set()
            for term in self.COMPOUND_TERMS:
                if term in text:
                    keyword_counts[term] += 1
                    found_compounds.add(term)
            
            # Then extract n-grams from title (more weight)
            title_words = self._tokenize(paper.title.lower())
            for n in [2, 3]:
                for i in range(len(title_words) - n + 1):
                    phrase = " ".join(title_words[i:i+n])
                    if phrase not in found_compounds and self._is_valid_phrase(phrase):
                        keyword_counts[phrase] += 3  # Higher weight for title
            
            # Single words from title
            for word in title_words:
                if self._is_valid_word(word):
                    keyword_counts[word] += 1
        
        return keyword_counts
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Keep alphanumeric and some special chars
        text = re.sub(r'[^\w\s-]', ' ', text.lower())
        return [w.strip() for w in text.split() if w.strip()]
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word is valid for keyword extraction."""
        if len(word) < 3:
            return False
        if word in self.STOP_WORDS:
            return False
        if word.isdigit():
            return False
        return True
    
    def _is_valid_phrase(self, phrase: str) -> bool:
        """Check if phrase is valid."""
        words = phrase.split()
        if len(words) < 2:
            return False
        # At least one word should not be a stop word
        return any(w not in self.STOP_WORDS for w in words)
    
    def calculate_trending_score(
        self, 
        keyword: str, 
        count: int, 
        total_papers: int,
        papers: List[Paper]
    ) -> float:
        """Calculate trending score for a keyword."""
        if count < 2:
            return 0.0
        
        # Frequency component (normalized)
        freq_score = min(count / max(total_papers * 0.1, 10), 1.0)
        
        # Momentum component - recent papers
        recent_count = sum(
            1 for p in papers 
            if keyword in (p.title + p.abstract).lower()
        )
        momentum_score = recent_count / max(count, 1)
        
        # Novelty component - check against history
        novelty_score = 1.0
        for entry in self.history[-7:]:  # Check last 7 scans
            for topic in entry.get("topics", []):
                if keyword in [k.lower() for k in topic.get("keywords", [])]:
                    novelty_score *= 0.9  # Decrease novelty if seen before
        
        # Compound terms get a boost
        compound_bonus = 1.2 if " " in keyword else 1.0
        
        # Weighted combination
        score = (
            freq_score * 0.3 +
            momentum_score * 0.4 +
            novelty_score * 0.3
        ) * compound_bonus
        
        return min(score, 1.0)
    
    def determine_velocity(self, score: float, count: int) -> str:
        """Determine trend velocity."""
        if score > 0.9 and count > 10:
            return "explosive"
        elif score > 0.8:
            return "rapid"
        elif score > 0.6:
            return "moderate"
        else:
            return "slow"
    
    def find_related_papers(self, keyword: str, papers: List[Paper], max_papers: int = 5) -> List[Paper]:
        """Find papers related to a keyword."""
        keyword_lower = keyword.lower()
        related = []
        
        for paper in papers:
            text = (paper.title + " " + paper.abstract).lower()
            if keyword_lower in text:
                related.append(paper)
        
        # Sort by relevance (title matches are more relevant)
        related.sort(key=lambda p: (
            keyword_lower in p.title.lower(),
            len(p.authors) > 0,
            p.published
        ), reverse=True)
        
        return related[:max_papers]
    
    def cluster_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Cluster related keywords into topics."""
        clusters = defaultdict(list)
        assigned = set()
        
        # First, identify compound terms as cluster centers
        for kw in sorted(keywords, key=len, reverse=True):
            if " " in kw and kw not in assigned:
                clusters[kw].append(kw)
                assigned.add(kw)
                # Add single words that appear in compound
                for word in kw.split():
                    if word in keywords and word not in assigned:
                        clusters[kw].append(word)
                        assigned.add(word)
        
        # Add remaining single words as their own clusters if frequent enough
        for kw in keywords:
            if kw not in assigned:
                clusters[kw] = [kw]
        
        return dict(clusters)
    
    def analyze(
        self, 
        papers: List[Paper], 
        min_score: float = 0.6,
        max_topics: int = 20
    ) -> List[Topic]:
        """Analyze papers and identify emerging topics."""
        if not papers:
            return []
        
        print(f"Analyzing {len(papers)} papers...")
        
        # Extract keywords
        keyword_counts = self.extract_keywords(papers)
        print(f"Extracted {len(keyword_counts)} unique keywords")
        
        # Calculate trending scores
        scored_keywords = []
        for keyword, count in keyword_counts.most_common(200):
            score = self.calculate_trending_score(
                keyword, count, len(papers), papers
            )
            if score >= min_score:
                scored_keywords.append((keyword, score, count))
        
        # Cluster into topics
        top_keywords = [k for k, s, c in scored_keywords[:100]]
        clusters = self.cluster_keywords(top_keywords)
        
        # Create topics from clusters
        topics = []
        for cluster_name, keywords in list(clusters.items())[:max_topics]:
            # Get best score from cluster
            cluster_scores = [
                (s, c) for k, s, c in scored_keywords 
                if k in keywords
            ]
            if not cluster_scores:
                continue
            
            best_score = max(s for s, c in cluster_scores)
            total_mentions = sum(c for s, c in cluster_scores)
            
            # Find related papers
            related = self.find_related_papers(cluster_name, papers)
            
            topic = Topic(
                name=cluster_name.title(),
                keywords=keywords[:5],  # Top 5 keywords
                trending_score=best_score,
                velocity=self.determine_velocity(best_score, total_mentions),
                preprint_count=len(related),
                cross_platform_mentions=total_mentions,
                related_papers=related,
                emerging_since=datetime.now().strftime("%Y-%m-%d")
            )
            topics.append(topic)
        
        # Sort by trending score
        topics.sort(key=lambda t: t.trending_score, reverse=True)
        
        # Save to history
        self._save_history(topics)
        
        return topics


class OutputFormatter:
    """Formats output in various formats."""
    
    def format_json(self, topics: List[Topic], sources: List[str]) -> str:
        """Format output as JSON."""
        output = {
            "scan_date": datetime.now().isoformat(),
            "sources": sources,
            "hot_topics": [t.to_dict() for t in topics],
            "summary": {
                "total_topics": len(topics),
                "high_priority": sum(1 for t in topics if t.trending_score > 0.8),
                "rapid_growth": sum(1 for t in topics if t.velocity in ["rapid", "explosive"])
            }
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def format_markdown(self, topics: List[Topic], sources: List[str]) -> str:
        """Format output as Markdown."""
        lines = [
            "# Emerging Topics Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Sources:** {', '.join(sources)}",
            "",
            "## Summary",
            "",
            f"- **Total Topics Detected:** {len(topics)}",
            f"- **High Priority (Score > 0.8):** {sum(1 for t in topics if t.trending_score > 0.8)}",
            f"- **Rapid Growth:** {sum(1 for t in topics if t.velocity in ['rapid', 'explosive'])}",
            "",
            "---",
            ""
        ]
        
        # Group by priority
        high_priority = [t for t in topics if t.trending_score > 0.8]
        medium_priority = [t for t in topics if 0.6 <= t.trending_score <= 0.8]
        
        if high_priority:
            lines.extend(["## 🔥 High Priority Topics", ""])
            for i, topic in enumerate(high_priority, 1):
                lines.extend(self._format_topic_markdown(topic, i))
        
        if medium_priority:
            lines.extend(["## 📈 Medium Priority Topics", ""])
            for i, topic in enumerate(medium_priority, 1):
                lines.extend(self._format_topic_markdown(topic, i))
        
        return "\n".join(lines)
    
    def _format_topic_markdown(self, topic: Topic, index: int) -> List[str]:
        """Format a single topic as Markdown."""
        velocity_emoji = {
            "explosive": "🚀",
            "rapid": "📈",
            "moderate": "📊",
            "slow": "🐢"
        }.get(topic.velocity, "📊")
        
        lines = [
            f"### {index}. {topic.name}",
            "",
            f"**Trending Score:** {topic.trending_score:.3f}",
            f"**Growth Velocity:** {velocity_emoji} {topic.velocity.title()}",
            f"**Related Preprints:** {topic.preprint_count}",
            f"**Total Mentions:** {topic.cross_platform_mentions}",
            "",
            f"**Keywords:** {', '.join(topic.keywords)}",
            "",
            "#### Key Papers",
            ""
        ]
        
        for paper in topic.related_papers[:3]:
            author_str = paper.authors[0] + " et al." if paper.authors else "Unknown"
            lines.append(f"1. **{paper.title}**")
            lines.append(f"   - Authors: {author_str}")
            lines.append(f"   - Source: {paper.source} | Published: {paper.published}")
            if paper.doi.startswith("10."):
                lines.append(f"   - DOI: {paper.doi}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def format_csv(self, topics: List[Topic]) -> str:
        """Format output as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "Topic", "Trending Score", "Velocity", "Preprint Count",
            "Mentions", "Keywords", "Emerging Since"
        ])
        
        for topic in topics:
            writer.writerow([
                topic.name,
                topic.trending_score,
                topic.velocity,
                topic.preprint_count,
                topic.cross_platform_mentions,
                "; ".join(topic.keywords),
                topic.emerging_since or ""
            ])
        
        return output.getvalue()


def main():
    parser = argparse.ArgumentParser(
        description="Emerging Topic Scout - Monitor bioRxiv/medRxiv for trending research"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["biorxiv", "medrxiv", "all"],
        default=["biorxiv", "medrxiv"],
        help="Data sources to monitor"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.6,
        help="Minimum trending score (0-1)"
    )
    parser.add_argument(
        "--max-topics",
        type=int,
        default=20,
        help="Maximum number of topics to return"
    )
    parser.add_argument(
        "--output",
        choices=["json", "markdown", "csv"],
        default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        help="Comma-separated keywords to prioritize"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests (seconds)"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save output to file"
    )
    
    args = parser.parse_args()
    
    # Handle 'all' source
    sources = ["biorxiv", "medrxiv"] if "all" in args.sources else args.sources
    
    print(f"🔬 Emerging Topic Scout")
    print(f"Sources: {', '.join(sources)}")
    print(f"Lookback: {args.days} days")
    print("-" * 40)
    
    # Fetch papers
    fetcher = PreprintFetcher(delay=args.delay)
    all_papers = []
    
    source_urls = {
        "biorxiv": BIORXIV_RSS,
        "medrxiv": MEDRXIV_RSS
    }
    
    for source in sources:
        print(f"Fetching from {source}...")
        papers = fetcher.fetch_rss(source_urls[source], source, args.days)
        print(f"  Found {len(papers)} papers")
        all_papers.extend(papers)
    
    print(f"\nTotal papers to analyze: {len(all_papers)}")
    
    if not all_papers:
        print("No papers found. Try increasing --days or check network connection.")
        return
    
    # Analyze trends
    analyzer = TrendAnalyzer()
    topics = analyzer.analyze(
        all_papers,
        min_score=args.min_score,
        max_topics=args.max_topics
    )
    
    print(f"Identified {len(topics)} emerging topics")
    
    # Format output
    formatter = OutputFormatter()
    if args.output == "json":
        output = formatter.format_json(topics, sources)
    elif args.output == "csv":
        output = formatter.format_csv(topics)
    else:
        output = formatter.format_markdown(topics, sources)
    
    # Save or print
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nOutput saved to: {args.save}")
    else:
        print("\n" + "=" * 60)
        print(output)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Scan complete!")
    print(f"  Topics found: {len(topics)}")
    print(f"  High priority: {sum(1 for t in topics if t.trending_score > 0.8)}")


if __name__ == "__main__":
    main()

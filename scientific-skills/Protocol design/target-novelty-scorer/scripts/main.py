#!/usr/bin/env python3
"""
Target Novelty Scorer
Target novelty scoring tool based on literature mining

Usage:
    python main.py --target "PD-L1"
    python main.py --target "BRCA1" --years 10 --format json
"""

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


@dataclass
class NoveltyScore:
    """Novelty score data structure"""
    target: str
    novelty_score: float
    confidence: float
    breakdown: Dict[str, float]
    metadata: Dict
    interpretation: str


class PubMedSearcher:
    """PubMed literature searcher (simulated implementation)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search(self, query: str, years: int = 5) -> Dict:
        """
        Search PubMed literature
        
        Actual implementation should call NCBI E-utilities API
        Here using simulated data for demonstration
        """
        # Simulated search results
        current_year = datetime.now().year
        
        # Generate simulated data based on target name (actual implementation should call real API)
        np.random.seed(hash(query) % 2**32)
        
        total_papers = np.random.randint(100, 50000)
        recent_papers = int(total_papers * np.random.uniform(0.1, 0.5))
        clinical_trials = np.random.randint(0, min(200, total_papers // 100))
        
        # Generate year distribution
        year_distribution = {
            str(year): np.random.randint(recent_papers // years // 2, recent_papers // years * 2)
            for year in range(current_year - years, current_year + 1)
        }
        
        return {
            "query": query,
            "total_count": total_papers,
            "recent_count": recent_papers,
            "clinical_trials": clinical_trials,
            "year_distribution": year_distribution,
            "search_year": current_year,
            "years_analyzed": years
        }


class NoveltyScorer:
    """Target novelty scorer"""
    
    def __init__(self):
        self.searcher = PubMedSearcher()
        
        # Scoring weight configuration
        self.weights = {
            "research_heat": 0.25,      # Research heat 25%
            "uniqueness": 0.25,         # Uniqueness 25%
            "research_depth": 0.20,     # Research depth 20%
            "collaboration": 0.15,      # Collaboration network 15%
            "trend": 0.15               # Time trend 15%
        }
    
    def _score_research_heat(self, data: Dict) -> float:
        """
        Score: Research heat (0-25 points)
        Based on recent literature count and citations
        """
        total = data.get("total_count", 0)
        recent = data.get("recent_count", 0)
        
        # Literature quantity score (0-15 points)
        if total < 500:
            quantity_score = 12 + (total / 500) * 3  # Scarce: high score
        elif total < 5000:
            quantity_score = 8 + (5000 - total) / 4500 * 4
        elif total < 20000:
            quantity_score = 4 + (20000 - total) / 15000 * 4
        else:
            quantity_score = max(0, 4 - (total - 20000) / 50000)
        
        # Recent activity score (0-10 points)
        recent_ratio = recent / total if total > 0 else 0
        recency_score = min(10, recent_ratio * 20)
        
        return min(25, quantity_score + recency_score)
    
    def _score_uniqueness(self, data: Dict, target: str) -> float:
        """
        Score: Uniqueness (0-25 points)
        Distinctiveness from known hot targets
        """
        total = data.get("total_count", 0)
        
        # Hot target list (examples)
        hot_targets = ["p53", "KRAS", "EGFR", "HER2", "PD-L1", "PD-1", "VEGF"]
        
        # If itself is a hot target, uniqueness is lower
        if target.upper() in [t.upper() for t in hot_targets]:
            base_score = 5
        else:
            # Uniqueness based on literature count
            if total < 1000:
                base_score = 20 + min(5, (1000 - total) / 200)
            elif total < 5000:
                base_score = 15 + (5000 - total) / 4000 * 5
            elif total < 15000:
                base_score = 8 + (15000 - total) / 10000 * 7
            else:
                base_score = max(0, 8 - (total - 15000) / 20000 * 8)
        
        return min(25, base_score)
    
    def _score_research_depth(self, data: Dict) -> float:
        """
        Score: Research depth (0-20 points)
        Progress level of preclinical/clinical research
        """
        clinical_trials = data.get("clinical_trials", 0)
        total = data.get("total_count", 0)
        
        # Clinical trial count score
        if clinical_trials == 0:
            clinical_score = 8  # Early target, unknown potential
        elif clinical_trials < 10:
            clinical_score = 12 + clinical_trials * 0.5
        elif clinical_trials < 50:
            clinical_score = 16 + (clinical_trials - 10) * 0.1
        else:
            clinical_score = max(10, 20 - (clinical_trials - 50) * 0.05)
        
        # Basic research depth (based on total literature count)
        if total < 1000:
            basic_score = 2
        elif total < 5000:
            basic_score = 3
        else:
            basic_score = 4
        
        return min(20, clinical_score + basic_score)
    
    def _score_collaboration(self, data: Dict) -> float:
        """
        Score: Collaboration network (0-15 points)
        Diversity of research institutions/teams distribution
        """
        total = data.get("total_count", 0)
        
        # Estimated collaboration diversity based on literature count
        if total < 100:
            diversity_score = 5
        elif total < 1000:
            diversity_score = 8 + (total - 100) / 900 * 4
        elif total < 5000:
            diversity_score = 12 + (total - 1000) / 4000 * 3
        else:
            diversity_score = 15
        
        return min(15, diversity_score)
    
    def _score_trend(self, data: Dict) -> float:
        """
        Score: Time trend (0-15 points)
        Recent research growth trend
        """
        year_dist = data.get("year_distribution", {})
        
        if not year_dist or len(year_dist) < 2:
            return 7.5  # Neutral score
        
        # Calculate growth trend
        years = sorted(year_dist.keys())
        values = [year_dist[y] for y in years]
        
        if len(values) >= 2:
            # Simple linear trend
            early_avg = np.mean(values[:len(values)//2])
            recent_avg = np.mean(values[len(values)//2:])
            
            if early_avg > 0:
                growth_rate = (recent_avg - early_avg) / early_avg
            else:
                growth_rate = 0
            
            # Convert to 0-15 points
            if growth_rate > 1.0:  # Growth over 100%
                trend_score = 15
            elif growth_rate > 0.5:
                trend_score = 12 + (growth_rate - 0.5) * 6
            elif growth_rate > 0.2:
                trend_score = 9 + (growth_rate - 0.2) * 10
            elif growth_rate > 0:
                trend_score = 6 + growth_rate * 15
            elif growth_rate > -0.2:
                trend_score = max(0, 6 + growth_rate * 30)
            else:
                trend_score = max(0, 3 + (growth_rate + 0.2) * 15)
        else:
            trend_score = 7.5
        
        return min(15, max(0, trend_score))
    
    def calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence (0-1)"""
        total = data.get("total_count", 0)
        
        # More literature, higher confidence
        if total < 50:
            return 0.4
        elif total < 200:
            return 0.6
        elif total < 1000:
            return 0.75
        elif total < 5000:
            return 0.85
        else:
            return 0.90
    
    def generate_interpretation(self, score: float, data: Dict) -> str:
        """Generate score interpretation"""
        total = data.get("total_count", 0)
        clinical = data.get("clinical_trials", 0)
        
        if score >= 80:
            level = "Extremely High Novelty"
            desc = "This target has limited research but unique value, representing a highly promising innovative direction."
        elif score >= 65:
            level = "High Novelty"
            desc = "This target has some research foundation but still has significant exploration space, recommended for focused attention."
        elif score >= 50:
            level = "Medium Novelty"
            desc = "This target has moderate research heat, requiring further evaluation of its differentiation advantages."
        elif score >= 35:
            level = "Low Novelty"
            desc = "This target already has substantial research, with intense competition, requiring breakthroughs in specific niche areas."
        else:
            level = "Very Low Novelty"
            desc = "This target is a mature research direction with limited innovation space, requiring careful evaluation of input-output ratio."
        
        details = f"Total literature: {total}, Clinical trials: {clinical}."
        
        return f"[{level}] {desc} {details}"
    
    def score(self, target: str, years: int = 5) -> NoveltyScore:
        """
        Calculate target novelty score
        
        Args:
            target: Target name or gene symbol
            years: Analysis year range
            
        Returns:
            NoveltyScore object
        """
        # Search literature data
        search_result = self.searcher.search(target, years)
        
        # Calculate scores for each dimension
        breakdown = {
            "research_heat": self._score_research_heat(search_result),
            "uniqueness": self._score_uniqueness(search_result, target),
            "research_depth": self._score_research_depth(search_result),
            "collaboration": self._score_collaboration(search_result),
            "trend": self._score_trend(search_result)
        }
        
        # Calculate total score (weighted average)
        total_score = sum(
            breakdown[key] * self.weights[key] 
            for key in breakdown
        )
        
        # Normalize to 0-100
        novelty_score = round(total_score * 100 / 25, 1)
        
        # Calculate confidence
        confidence = self.calculate_confidence(search_result)
        
        # Build metadata
        metadata = {
            "total_papers": search_result["total_count"],
            "recent_papers": search_result["recent_count"],
            "clinical_trials": search_result["clinical_trials"],
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "years_analyzed": years
        }
        
        # Generate interpretation
        interpretation = self.generate_interpretation(novelty_score, search_result)
        
        return NoveltyScore(
            target=target,
            novelty_score=novelty_score,
            confidence=round(confidence, 2),
            breakdown={k: round(v * 100 / 25, 1) for k, v in breakdown.items()},
            metadata=metadata,
            interpretation=interpretation
        )


def format_text_output(result: NoveltyScore) -> str:
    """Format text output"""
    lines = [
        "=" * 60,
        f"Target Novelty Score Report: {result.target}",
        "=" * 60,
        "",
        f"Overall Score: {result.novelty_score}/100",
        f"Confidence: {result.confidence * 100:.0f}%",
        "",
        "Dimension Scores:",
        f"  - Research Heat:   {result.breakdown['research_heat']:.1f}/100",
        f"  - Uniqueness:     {result.breakdown['uniqueness']:.1f}/100",
        f"  - Research Depth:   {result.breakdown['research_depth']:.1f}/100",
        f"  - Collaboration Network:   {result.breakdown['collaboration']:.1f}/100",
        f"  - Time Trend:   {result.breakdown['trend']:.1f}/100",
        "",
        "Statistics:",
        f"  - Total Literature: {result.metadata['total_papers']:,}",
        f"  - Recent Literature: {result.metadata['recent_papers']:,}",
        f"  - Clinical Trials: {result.metadata['clinical_trials']}",
        f"  - Analysis Date: {result.metadata['analysis_date']}",
        "",
        f"Interpretation: {result.interpretation}",
        "",
        "=" * 60
    ]
    return "\n".join(lines)


def format_csv_output(result: NoveltyScore) -> str:
    """Format CSV output"""
    headers = [
        "target", "novelty_score", "confidence",
        "research_heat", "uniqueness", "research_depth",
        "collaboration", "trend", "total_papers",
        "recent_papers", "clinical_trials", "interpretation"
    ]
    
    values = [
        result.target,
        result.novelty_score,
        result.confidence,
        result.breakdown['research_heat'],
        result.breakdown['uniqueness'],
        result.breakdown['research_depth'],
        result.breakdown['collaboration'],
        result.breakdown['trend'],
        result.metadata['total_papers'],
        result.metadata['recent_papers'],
        result.metadata['clinical_trials'],
        f'"{result.interpretation}"'
    ]
    
    return ",".join(map(str, values))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Target Novelty Scoring Tool - Based on Literature Mining",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target "PD-L1"
  python main.py --target "BRCA1" --years 10 --format json
  python main.py --target "EGFR" --output report.json
        """
    )
    
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Target name or gene symbol (e.g.: PD-L1, BRCA1)"
    )
    parser.add_argument(
        "--db", "-d",
        choices=["pubmed", "pmc", "all"],
        default="pubmed",
        help="Data source (default: pubmed)"
    )
    parser.add_argument(
        "--years", "-y",
        type=int,
        default=5,
        help="Analysis year range (default: 5)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output mode"
    )
    
    args = parser.parse_args()
    
    # Execute scoring
    try:
        scorer = NoveltyScorer()
        result = scorer.score(args.target, args.years)
        
        # Format output
        if args.format == "json":
            output = json.dumps(asdict(result), ensure_ascii=False, indent=2)
        elif args.format == "csv":
            output = format_csv_output(result)
        else:
            output = format_text_output(result)
        
        # Output results
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        else:
            print(output)
        
        # Verbose mode
        if args.verbose and args.format == "text":
            print(f"\nRaw Data: {json.dumps(result.metadata, ensure_ascii=False)}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

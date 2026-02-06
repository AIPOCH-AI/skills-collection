#!/usr/bin/env python3
"""
Journal Matchmaker - Recommend journals based on abstract content.

Analyzes paper abstracts and matches them with suitable journals based on:
- Research field and scope alignment
- Impact factor requirements
- Journal aims and scope descriptions
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
import math


@dataclass
class Journal:
    """Represents a journal with its metadata."""
    name: str
    abbreviation: str
    impact_factor: float
    fields: List[str]
    scope: str
    publisher: str
    issn: Optional[str] = None
    open_access: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Recommendation:
    """Represents a journal recommendation with relevance score."""
    journal: Journal
    relevance_score: float
    match_reasons: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "journal": self.journal.to_dict(),
            "relevance_score": round(self.relevance_score, 3),
            "match_reasons": self.match_reasons
        }


class AbstractAnalyzer:
    """Analyzes paper abstracts to extract key information."""
    
    # Common stopwords to exclude from analysis
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'we', 'our', 'us', 'it', 'its', 'they', 'them', 'their',
        'paper', 'study', 'research', 'propose', 'proposed', 'present',
        'demonstrate', 'show', 'results', 'approach', 'method', 'methods'
    }
    
    # Field detection keywords
    FIELD_KEYWORDS = {
        'computer_science': [
            'algorithm', 'computational', 'software', 'hardware', 'programming',
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'data mining', 'computer vision', 'nlp',
            'natural language processing', 'cloud computing', 'distributed',
            'cybersecurity', 'blockchain', 'database', 'network'
        ],
        'artificial_intelligence': [
            'machine learning', 'deep learning', 'neural network', 'reinforcement learning',
            'transformer', 'llm', 'large language model', 'ai', 'artificial intelligence',
            'computer vision', 'nlp', 'natural language processing', 'generative',
            'gpt', 'bert', 'classification', 'prediction', 'optimization'
        ],
        'biology': [
            'gene', 'protein', 'cell', 'molecular', 'genome', 'dna', 'rna',
            'organism', 'species', 'ecosystem', 'evolution', 'biological',
            'biochemistry', 'microbiology', 'genetics', 'physiology'
        ],
        'medicine': [
            'patient', 'clinical', 'treatment', 'disease', 'diagnosis', 'therapy',
            'medical', 'health', 'healthcare', 'hospital', 'drug', 'medicine',
            'surgery', 'symptom', 'prognosis', 'epidemiology'
        ],
        'physics': [
            'quantum', 'particle', 'energy', 'thermodynamics', 'electromagnetic',
            'optics', 'mechanics', 'relativity', 'condensed matter', 'astrophysics',
            'nuclear', 'plasma', 'atomic', 'molecular'
        ],
        'chemistry': [
            'molecule', 'compound', 'reaction', 'catalysis', 'organic', 'inorganic',
            'analytical', 'physical chemistry', 'materials', 'polymer', 'nanotechnology',
            'spectroscopy', 'synthesis'
        ],
        'materials_science': [
            'material', 'nanomaterial', 'composite', 'polymer', 'ceramic', 'metal',
            'alloy', 'semiconductor', 'graphene', 'nanotechnology', 'fabrication',
            'characterization', 'properties'
        ],
        'engineering': [
            'system', 'design', 'control', 'automation', 'robotics', 'mechanical',
            'electrical', 'civil', 'aerospace', 'manufacturing', 'process',
            'simulation', 'modeling', 'optimization'
        ],
        'environmental_science': [
            'climate', 'environment', 'pollution', 'sustainability', 'ecosystem',
            'conservation', 'renewable', 'carbon', 'emission', 'biodiversity',
            'atmospheric', 'ocean', 'water'
        ],
        'economics': [
            'economic', 'market', 'finance', 'policy', 'trade', 'growth',
            'investment', 'banking', 'monetary', 'fiscal', 'development',
            'behavioral economics', 'econometrics'
        ],
        'psychology': [
            'cognitive', 'behavioral', 'mental', 'psychological', 'neuroscience',
            'perception', 'memory', 'learning', 'emotion', 'social psychology',
            'clinical psychology', 'development'
        ]
    }
    
    def __init__(self):
        self.field_scores = {}
    
    def extract_keywords(self, abstract: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """Extract important keywords from abstract using TF-IDF-like scoring."""
        # Clean and tokenize
        text = abstract.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter stopwords and short words
        words = [w for w in words if w not in self.STOPWORDS and len(w) > 2]
        
        # Calculate word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate TF scores
        tf_scores = {word: count / total_words for word, count in word_freq.items()}
        
        # Extract bigrams and trigrams for phrases
        phrases = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            phrases.append(bigram)
        
        phrase_freq = Counter(phrases)
        phrase_scores = {phrase: count / len(phrases) * 2 for phrase, count in phrase_freq.items()}
        
        # Combine and sort
        all_terms = {**tf_scores, **phrase_scores}
        sorted_terms = sorted(all_terms.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_terms[:top_n]
    
    def detect_field(self, abstract: str) -> List[Tuple[str, float]]:
        """Detect research field(s) from abstract content."""
        text = abstract.lower()
        field_scores = {}
        
        for field, keywords in self.FIELD_KEYWORDS.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                if count > 0:
                    score += count
                    matched_keywords.append(keyword)
            
            if score > 0:
                field_scores[field] = {
                    'score': score,
                    'keywords': matched_keywords
                }
        
        # Sort by score
        sorted_fields = sorted(
            [(f, data['score'], data['keywords']) for f, data in field_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_fields
    
    def extract_methods(self, abstract: str) -> List[str]:
        """Extract methodology mentions from abstract."""
        method_patterns = [
            r'using ([\w\s]+?)(?:method|approach|technique|algorithm)',
            r'(propose|present|develop) ([\w\s]+?)(?:method|approach|framework)',
            r'(?:based on|via|through) ([\w\s]+?)(?:analysis|learning|modeling)',
            r'([\w]+? learning)',
            r'([\w]+? network)',
        ]
        
        methods = []
        text = abstract.lower()
        
        for pattern in method_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[-1]
                match = match.strip()
                if len(match) > 3 and len(match) < 50:
                    methods.append(match)
        
        return list(set(methods))


class JournalDatabase:
    """Manages journal metadata database."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "references"
        self.data_dir = data_dir
        self.journals: List[Journal] = []
        self.load_journals()
    
    def load_journals(self):
        """Load journal database from JSON file."""
        journals_file = self.data_dir / "journals.json"
        
        if not journals_file.exists():
            # Create default journal database if not exists
            self._create_default_database()
        
        with open(journals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.journals = [
            Journal(
                name=j.get('name', ''),
                abbreviation=j.get('abbreviation', ''),
                impact_factor=j.get('impact_factor', 0.0),
                fields=j.get('fields', []),
                scope=j.get('scope', ''),
                publisher=j.get('publisher', ''),
                issn=j.get('issn'),
                open_access=j.get('open_access', False)
            )
            for j in data.get('journals', [])
        ]
    
    def _create_default_database(self):
        """Create a default journal database with high-impact journals."""
        journals_file = self.data_dir / "journals.json"
        default_journals = {
            "journals": [
                # Nature Family
                {"name": "Nature", "abbreviation": "Nature", "impact_factor": 64.8, "fields": ["multidisciplinary"], "scope": "Publishes the finest peer-reviewed research in all fields of science and technology", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Nature Medicine", "abbreviation": "Nat Med", "impact_factor": 58.7, "fields": ["medicine", "biology"], "scope": "Research and review articles in biomedical sciences", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Nature Methods", "abbreviation": "Nat Methods", "impact_factor": 48.0, "fields": ["biology", "methods"], "scope": "New methods and significant improvements to tried-and-tested techniques in the life sciences", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Nature Biotechnology", "abbreviation": "Nat Biotechnol", "impact_factor": 46.9, "fields": ["biology", "biotechnology"], "scope": "Biological research with commercial applications", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Nature Machine Intelligence", "abbreviation": "Nat Mach Intell", "impact_factor": 25.0, "fields": ["artificial_intelligence", "computer_science"], "scope": "Machine learning, robotics and AI research", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Nature Communications", "abbreviation": "Nat Commun", "impact_factor": 16.6, "fields": ["multidisciplinary"], "scope": "High-quality research across all natural sciences", "publisher": "Nature Publishing Group", "open_access": True},
                
                # Science Family
                {"name": "Science", "abbreviation": "Science", "impact_factor": 56.9, "fields": ["multidisciplinary"], "scope": "Original scientific research and cutting-edge research news", "publisher": "AAAS", "open_access": False},
                {"name": "Science Translational Medicine", "abbreviation": "Sci Transl Med", "impact_factor": 17.1, "fields": ["medicine", "biology"], "scope": "Translational medical research", "publisher": "AAAS", "open_access": False},
                {"name": "Science Advances", "abbreviation": "Sci Adv", "impact_factor": 13.6, "fields": ["multidisciplinary"], "scope": "Open access multidisciplinary research", "publisher": "AAAS", "open_access": True},
                
                # Cell Family
                {"name": "Cell", "abbreviation": "Cell", "impact_factor": 64.5, "fields": ["biology", "medicine"], "scope": "Research articles in cell biology and molecular biology", "publisher": "Cell Press", "open_access": False},
                {"name": "Cell Research", "abbreviation": "Cell Res", "impact_factor": 44.1, "fields": ["biology", "cell_biology"], "scope": "Cell biology and molecular cell biology", "publisher": "Nature Publishing Group", "open_access": False},
                
                # AI/ML Journals
                {"name": "IEEE Transactions on Pattern Analysis and Machine Intelligence", "abbreviation": "IEEE TPAMI", "impact_factor": 20.8, "fields": ["artificial_intelligence", "computer_science", "computer_vision"], "scope": "Pattern recognition, machine intelligence, computer vision", "publisher": "IEEE", "open_access": False},
                {"name": "International Journal of Computer Vision", "abbreviation": "IJCV", "impact_factor": 19.5, "fields": ["computer_vision", "artificial_intelligence"], "scope": "Computer vision theory and applications", "publisher": "Springer", "open_access": False},
                {"name": "IEEE Transactions on Neural Networks and Learning Systems", "abbreviation": "IEEE TNNLS", "impact_factor": 10.4, "fields": ["artificial_intelligence", "neural_networks"], "scope": "Neural networks and machine learning systems", "publisher": "IEEE", "open_access": False},
                {"name": "Neural Networks", "abbreviation": "Neural Netw", "impact_factor": 7.8, "fields": ["artificial_intelligence", "neural_networks"], "scope": "Neural network research and applications", "publisher": "Elsevier", "open_access": False},
                {"name": "Machine Learning", "abbreviation": "Mach Learn", "impact_factor": 5.0, "fields": ["artificial_intelligence", "machine_learning"], "scope": "Machine learning algorithms and theory", "publisher": "Springer", "open_access": False},
                {"name": "Journal of Machine Learning Research", "abbreviation": "JMLR", "impact_factor": 4.3, "fields": ["artificial_intelligence", "machine_learning"], "scope": "Machine learning research", "publisher": "JMLR", "open_access": True},
                
                # NLP/Computational Linguistics
                {"name": "Computational Linguistics", "abbreviation": "Comput Linguist", "impact_factor": 8.6, "fields": ["nlp", "computational_linguistics"], "scope": "Computational approaches to linguistics and NLP", "publisher": "MIT Press", "open_access": False},
                {"name": "Transactions of the Association for Computational Linguistics", "abbreviation": "TACL", "impact_factor": 6.0, "fields": ["nlp", "computational_linguistics"], "scope": "Computational linguistics research", "publisher": "ACL", "open_access": True},
                
                # Medical Journals
                {"name": "The Lancet", "abbreviation": "Lancet", "impact_factor": 168.9, "fields": ["medicine"], "scope": "General medical research and reviews", "publisher": "Elsevier", "open_access": False},
                {"name": "New England Journal of Medicine", "abbreviation": "NEJM", "impact_factor": 91.2, "fields": ["medicine"], "scope": "Medical research and clinical practice", "publisher": "NEJM Group", "open_access": False},
                {"name": "JAMA", "abbreviation": "JAMA", "impact_factor": 120.7, "fields": ["medicine"], "scope": "Medical sciences and public health", "publisher": "American Medical Association", "open_access": False},
                
                # Computer Science - General
                {"name": "Communications of the ACM", "abbreviation": "CACM", "impact_factor": 22.7, "fields": ["computer_science"], "scope": "Computing research and practice", "publisher": "ACM", "open_access": False},
                {"name": "IEEE Transactions on Computers", "abbreviation": "IEEE TC", "impact_factor": 3.7, "fields": ["computer_science", "hardware"], "scope": "Computer hardware and architecture", "publisher": "IEEE", "open_access": False},
                
                # Data Science
                {"name": "IEEE Transactions on Knowledge and Data Engineering", "abbreviation": "IEEE TKDE", "impact_factor": 8.9, "fields": ["data_mining", "computer_science", "artificial_intelligence"], "scope": "Knowledge and data engineering", "publisher": "IEEE", "open_access": False},
                {"name": "Data Mining and Knowledge Discovery", "abbreviation": "Data Min Knowl Disc", "impact_factor": 4.0, "fields": ["data_mining", "computer_science"], "scope": "Theory and practice of data mining", "publisher": "Springer", "open_access": False},
                
                # Environmental Science
                {"name": "Nature Climate Change", "abbreviation": "Nat Clim Chang", "impact_factor": 29.6, "fields": ["environmental_science", "climate"], "scope": "Climate change research", "publisher": "Nature Publishing Group", "open_access": False},
                {"name": "Environmental Science & Technology", "abbreviation": "Environ Sci Technol", "impact_factor": 11.4, "fields": ["environmental_science", "chemistry"], "scope": "Environmental science and engineering", "publisher": "ACS", "open_access": False},
                
                # Materials Science
                {"name": "Advanced Materials", "abbreviation": "Adv Mater", "impact_factor": 29.4, "fields": ["materials_science", "nanotechnology"], "scope": "Materials science and engineering", "publisher": "Wiley", "open_access": False},
                {"name": "Nature Materials", "abbreviation": "Nat Mater", "impact_factor": 47.9, "fields": ["materials_science", "physics"], "scope": "Materials science research", "publisher": "Nature Publishing Group", "open_access": False},
                
                # Physics
                {"name": "Physical Review Letters", "abbreviation": "Phys Rev Lett", "impact_factor": 8.0, "fields": ["physics"], "scope": "Brief reports of significant physics research", "publisher": "APS", "open_access": False},
                {"name": "Nature Physics", "abbreviation": "Nat Phys", "impact_factor": 19.6, "fields": ["physics"], "scope": "Pure and applied physics research", "publisher": "Nature Publishing Group", "open_access": False},
            ]
        }
        
        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(journals_file, 'w', encoding='utf-8') as f:
            json.dump(default_journals, f, indent=2, ensure_ascii=False)
    
    def filter_by_field(self, fields: List[str]) -> List[Journal]:
        """Filter journals by research field."""
        if not fields:
            return self.journals
        
        filtered = []
        for journal in self.journals:
            if any(f in journal.fields for f in fields):
                filtered.append(journal)
        return filtered
    
    def filter_by_impact_factor(self, min_if: float = 0.0, max_if: Optional[float] = None) -> List[Journal]:
        """Filter journals by impact factor range."""
        filtered = []
        for journal in self.journals:
            if journal.impact_factor >= min_if:
                if max_if is None or journal.impact_factor <= max_if:
                    filtered.append(journal)
        return filtered
    
    def get_all(self) -> List[Journal]:
        """Get all journals in database."""
        return self.journals


class JournalMatchmaker:
    """Main class for journal recommendation."""
    
    def __init__(self):
        self.analyzer = AbstractAnalyzer()
        self.database = JournalDatabase()
    
    def calculate_scope_similarity(self, abstract: str, journal: Journal) -> float:
        """Calculate similarity between abstract and journal scope."""
        # Extract keywords from abstract
        abstract_keywords = set([k[0] for k in self.analyzer.extract_keywords(abstract, 30)])
        
        # Extract keywords from journal scope
        scope_text = journal.scope.lower()
        scope_keywords = set(re.findall(r'\b\w+\b', scope_text))
        
        # Calculate Jaccard similarity
        if not abstract_keywords or not scope_keywords:
            return 0.0
        
        intersection = abstract_keywords & scope_keywords
        union = abstract_keywords | scope_keywords
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_field_match_score(self, detected_fields: List[Tuple[str, float, List[str]]], journal: Journal) -> float:
        """Calculate field match score."""
        if not detected_fields:
            return 0.5  # Neutral if no fields detected
        
        score = 0.0
        for field, field_score, _ in detected_fields[:3]:  # Top 3 fields
            if field in journal.fields:
                score += field_score * 0.3
        
        return min(score, 1.0)
    
    def calculate_method_match_score(self, methods: List[str], journal: Journal) -> float:
        """Calculate methodology match score."""
        if not methods:
            return 0.5
        
        journal_scope = journal.scope.lower()
        matches = sum(1 for m in methods if m.lower() in journal_scope)
        
        return min(matches / len(methods), 1.0)
    
    def recommend(self, abstract: str, field: Optional[str] = None, 
                  min_if: float = 0.0, max_if: Optional[float] = None,
                  count: int = 5) -> List[Recommendation]:
        """Generate journal recommendations for given abstract."""
        
        # Analyze abstract
        keywords = self.analyzer.extract_keywords(abstract, 20)
        detected_fields = self.analyzer.detect_field(abstract)
        methods = self.analyzer.extract_methods(abstract)
        
        # Determine target fields
        target_fields = []
        if field:
            target_fields = [field.lower().replace(' ', '_')]
        elif detected_fields:
            target_fields = [f[0] for f in detected_fields[:2]]
        
        # Filter journals
        candidates = self.database.get_all()
        candidates = self.database.filter_by_impact_factor(min_if, max_if)
        
        if target_fields:
            field_filtered = self.database.filter_by_field(target_fields)
            if field_filtered:
                candidates = [j for j in candidates if j in field_filtered]
        
        # Score each journal
        recommendations = []
        for journal in candidates:
            scores = {
                'scope_similarity': self.calculate_scope_similarity(abstract, journal),
                'field_match': self.calculate_field_match_score(detected_fields, journal),
                'method_match': self.calculate_method_match_score(methods, journal),
                'impact_factor': min(journal.impact_factor / 50.0, 1.0)  # Normalize IF
            }
            
            # Weighted total score
            total_score = (
                scores['scope_similarity'] * 0.35 +
                scores['field_match'] * 0.30 +
                scores['method_match'] * 0.20 +
                scores['impact_factor'] * 0.15
            )
            
            # Generate match reasons
            reasons = []
            if scores['field_match'] > 0.5:
                matched_fields = [f for f in target_fields if f in journal.fields]
                reasons.append(f"Field alignment: {', '.join(matched_fields[:2])}")
            if scores['scope_similarity'] > 0.1:
                reasons.append("Scope similarity detected")
            if journal.open_access:
                reasons.append("Open access journal")
            if journal.impact_factor >= 10:
                reasons.append(f"High impact factor ({journal.impact_factor})")
            
            recommendations.append(Recommendation(
                journal=journal,
                relevance_score=total_score,
                match_reasons=reasons if reasons else ["General multidisciplinary match"]
            ))
        
        # Sort by relevance score and return top N
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:count]
    
    def format_output(self, recommendations: List[Recommendation], output_format: str = 'table') -> str:
        """Format recommendations for output."""
        
        if output_format == 'json':
            return json.dumps([r.to_dict() for r in recommendations], indent=2, ensure_ascii=False)
        
        elif output_format == 'markdown':
            lines = ["# Journal Recommendations\n"]
            for i, rec in enumerate(recommendations, 1):
                j = rec.journal
                lines.append(f"## {i}. {j.name}")
                lines.append(f"- **Abbreviation**: {j.abbreviation}")
                lines.append(f"- **Impact Factor**: {j.impact_factor}")
                lines.append(f"- **Publisher**: {j.publisher}")
                lines.append(f"- **Open Access**: {'Yes' if j.open_access else 'No'}")
                lines.append(f"- **Relevance Score**: {rec.relevance_score:.3f}")
                lines.append(f"- **Match Reasons**: {', '.join(rec.match_reasons)}")
                lines.append(f"- **Scope**: {j.scope}\n")
            return '\n'.join(lines)
        
        else:  # table format
            lines = [
                "=" * 120,
                f"{'Rank':<6} {'Journal':<45} {'IF':<8} {'Score':<8} {'OA':<4} {'Key Match Reasons'}",
                "-" * 120
            ]
            
            for i, rec in enumerate(recommendations, 1):
                j = rec.journal
                reasons = ', '.join(rec.match_reasons[:2])
                oa = 'Yes' if j.open_access else 'No'
                lines.append(f"{i:<6} {j.name[:44]:<45} {j.impact_factor:<8.1f} {rec.relevance_score:<8.3f} {oa:<4} {reasons}")
            
            lines.append("=" * 120)
            lines.append(f"\nTotal: {len(recommendations)} recommendations")
            return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Journal Matchmaker - Recommend journals based on abstract content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --abstract "Your abstract text here"
  python main.py --abstract "abstract.txt" --file --min-if 5.0
  python main.py --abstract "..." --field "artificial_intelligence" --count 10
        """
    )
    
    parser.add_argument('--abstract', required=True, 
                        help='Paper abstract text or path to file containing abstract')
    parser.add_argument('--file', action='store_true',
                        help='Treat --abstract as file path')
    parser.add_argument('--field', 
                        help='Research field (e.g., artificial_intelligence, medicine, biology)')
    parser.add_argument('--min-if', type=float, default=0.0,
                        help='Minimum impact factor threshold (default: 0.0)')
    parser.add_argument('--max-if', type=float, default=None,
                        help='Maximum impact factor threshold (optional)')
    parser.add_argument('--count', type=int, default=5,
                        help='Number of recommendations (default: 5)')
    parser.add_argument('--format', choices=['table', 'json', 'markdown'], default='table',
                        help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # Read abstract
    if args.file:
        with open(args.abstract, 'r', encoding='utf-8') as f:
            abstract = f.read()
    else:
        abstract = args.abstract
    
    if len(abstract) < 50:
        print("Error: Abstract too short. Please provide a complete abstract (at least 50 characters).", file=sys.stderr)
        sys.exit(1)
    
    # Generate recommendations
    matchmaker = JournalMatchmaker()
    
    print("Analyzing abstract...")
    print(f"Length: {len(abstract)} characters")
    
    # Show detected fields
    analyzer = AbstractAnalyzer()
    detected_fields = analyzer.detect_field(abstract)
    if detected_fields:
        print(f"Detected fields: {', '.join([f[0] for f in detected_fields[:3]])}")
    
    print(f"\nSearching journals with IF >= {args.min_if}...\n")
    
    recommendations = matchmaker.recommend(
        abstract=abstract,
        field=args.field,
        min_if=args.min_if,
        max_if=args.max_if,
        count=args.count
    )
    
    if not recommendations:
        print("No matching journals found. Try relaxing your criteria.")
        sys.exit(0)
    
    # Output results
    output = matchmaker.format_output(recommendations, args.format)
    print(output)


if __name__ == '__main__':
    main()

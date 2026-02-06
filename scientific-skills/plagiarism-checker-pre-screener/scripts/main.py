#!/usr/bin/env python3
"""
Plagiarism Checker Pre-Screener
Checks text originality and provides paraphrasing suggestions for high-duplicate content.

Technical: Text similarity detection, paraphrasing suggestions, originality scoring
Difficulty: High
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import math


@dataclass
class Segment:
    """Represents a text segment for analysis."""
    index: int
    text: str
    similarity_score: float = 0.0
    flagged: bool = False
    paraphrase_suggestion: str = ""
    matches_with: List[int] = None
    
    def __post_init__(self):
        if self.matches_with is None:
            self.matches_with = []


class TextPreprocessor:
    """Handles text preprocessing and segmentation."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Normalize punctuation spacing
        text = re.sub(r'\s*([.!?;,])\s*', r'\1 ', text)
        return text.strip()
    
    @staticmethod
    def segment_by_sentence(text: str) -> List[str]:
        """Segment text into sentences."""
        # Handle both English and Chinese sentence delimiters
        pattern = r'(?<=[.!?。！？])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def segment_by_paragraph(text: str) -> List[str]:
        """Segment text into paragraphs."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple tokenization (supports English and basic CJK)."""
        # For English: split by non-alphanumeric
        # For CJK: each character is a token
        tokens = []
        words = re.findall(r'[\w]+|[^\w\s]', text.lower())
        return words
    
    @staticmethod
    def ngrams(tokens: List[str], n: int = 3) -> List[str]:
        """Generate n-grams from tokens."""
        if len(tokens) < n:
            return [' '.join(tokens)]
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


class SimilarityDetector:
    """Detects similarity between text segments using multiple algorithms."""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # Normalize
        total = len(tokens)
        return {k: v/total for k, v in tf.items()}
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        tokens1 = self.preprocessor.tokenize(text1)
        tokens2 = self.preprocessor.tokenize(text2)
        
        tf1 = self._compute_tf(tokens1)
        tf2 = self._compute_tf(tokens2)
        
        # Get all unique terms
        all_terms = set(tf1.keys()) | set(tf2.keys())
        
        # Compute dot product and magnitudes
        dot_product = sum(tf1.get(term, 0) * tf2.get(term, 0) for term in all_terms)
        magnitude1 = math.sqrt(sum(v**2 for v in tf1.values()))
        magnitude2 = math.sqrt(sum(v**2 for v in tf2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def ngram_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """Compute n-gram overlap similarity."""
        tokens1 = self.preprocessor.tokenize(text1)
        tokens2 = self.preprocessor.tokenize(text2)
        
        ngrams1 = set(self.preprocessor.ngrams(tokens1, n))
        ngrams2 = set(self.preprocessor.ngrams(tokens2, n))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Compute Jaccard similarity."""
        tokens1 = set(self.preprocessor.tokenize(text1))
        tokens2 = set(self.preprocessor.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def combined_similarity(self, text1: str, text2: str) -> float:
        """Combine multiple similarity metrics."""
        cos_sim = self.cosine_similarity(text1, text2)
        ngram_sim = self.ngram_similarity(text1, text2, n=3)
        jaccard_sim = self.jaccard_similarity(text1, text2)
        
        # Weighted combination
        return 0.5 * cos_sim + 0.3 * ngram_sim + 0.2 * jaccard_sim


class Paraphraser:
    """Provides paraphrasing suggestions for flagged text."""
    
    # Common synonym mappings
    SYNONYMS = {
        'important': ['significant', 'crucial', 'essential', 'vital', 'key'],
        'show': ['demonstrate', 'indicate', 'reveal', 'display', 'illustrate'],
        'use': ['utilize', 'employ', 'apply', 'adopt', 'implement'],
        'make': ['create', 'produce', 'generate', 'construct', 'form'],
        'find': ['discover', 'identify', 'locate', 'detect', 'determine'],
        'increase': ['rise', 'grow', 'expand', 'escalate', 'surge'],
        'decrease': ['decline', 'reduce', 'diminish', 'drop', 'fall'],
        'good': ['excellent', 'superior', 'favorable', 'positive', 'beneficial'],
        'bad': ['poor', 'inferior', 'unfavorable', 'negative', 'harmful'],
        'big': ['large', 'substantial', 'considerable', 'significant', 'major'],
        'small': ['minor', 'minimal', 'slight', 'modest', 'limited'],
    }
    
    # Academic style transformations
    ACADEMIC_PHRASES = {
        'a lot of': ['a substantial amount of', 'a considerable number of', 'numerous'],
        'many': ['a multitude of', 'a wide range of', 'various'],
        'some': ['certain', 'particular', 'specific'],
        'thing': ['aspect', 'factor', 'element', 'component'],
        'do': ['perform', 'conduct', 'carry out', 'execute'],
        'get': ['obtain', 'acquire', 'receive', 'gain'],
        'say': ['state', 'assert', 'claim', 'suggest', 'argue'],
    }
    
    def __init__(self, style: str = 'neutral'):
        self.style = style
    
    def _synonym_replace(self, text: str) -> str:
        """Replace words with synonyms."""
        words = text.split()
        new_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.SYNONYMS:
                # Get synonym with same case pattern
                synonym = self.SYNONYMS[clean_word][0]
                if word[0].isupper():
                    synonym = synonym.capitalize()
                new_words.append(synonym)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def _academic_transform(self, text: str) -> str:
        """Transform to academic style."""
        result = text
        for phrase, replacements in self.ACADEMIC_PHRASES.items():
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            result = pattern.sub(replacements[0], result)
        return result
    
    def _passive_voice(self, text: str) -> str:
        """Convert active to passive voice where appropriate."""
        # Simple patterns for common verbs
        patterns = [
            (r'\b(\w+)\s+(\w+ed)\s+(\w+)', r'\3 was \2 by \1'),
            (r'\bWe\s+(\w+)\s+', r'It was \1ed that '),
            (r'\bI\s+(\w+)\s+', r'It was \1ed that '),
        ]
        
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    def _restructure_sentence(self, text: str) -> str:
        """Restructure sentence while preserving meaning."""
        # Split by common conjunctions and restructure
        parts = re.split(r',\s*', text)
        if len(parts) > 1:
            # Rearrange clauses
            parts.reverse()
            return '. '.join(parts)
        return text
    
    def paraphrase(self, text: str) -> str:
        """Generate paraphrasing suggestion."""
        if self.style == 'academic':
            text = self._academic_transform(text)
        elif self.style == 'formal':
            text = self._passive_voice(text)
        
        # Apply synonym replacement
        text = self._synonym_replace(text)
        
        # Restructure
        text = self._restructure_sentence(text)
        
        return text


class PlagiarismChecker:
    """Main class for plagiarism checking."""
    
    def __init__(self, threshold: float = 0.70, segment_type: str = 'sentence'):
        self.threshold = threshold
        self.segment_type = segment_type
        self.preprocessor = TextPreprocessor()
        self.detector = SimilarityDetector()
    
    def _segment_text(self, text: str) -> List[str]:
        """Segment text based on configuration."""
        if self.segment_type == 'paragraph':
            return self.preprocessor.segment_by_paragraph(text)
        return self.preprocessor.segment_by_sentence(text)
    
    def analyze(self, text: str, paraphrase: bool = False, 
                style: str = 'neutral') -> Dict:
        """Analyze text for plagiarism."""
        # Clean text
        text = self.preprocessor.clean_text(text)
        
        # Segment text
        raw_segments = self._segment_text(text)
        
        # Create segment objects
        segments = [Segment(index=i, text=s) for i, s in enumerate(raw_segments)]
        
        # Initialize paraphraser if needed
        paraphraser = Paraphraser(style) if paraphrase else None
        
        # Compare each segment with every other segment
        for i, seg1 in enumerate(segments):
            max_similarity = 0.0
            matches = []
            
            for j, seg2 in enumerate(segments):
                if i != j:
                    sim = self.detector.combined_similarity(seg1.text, seg2.text)
                    if sim > max_similarity:
                        max_similarity = sim
                    if sim >= self.threshold:
                        matches.append(j)
            
            seg1.similarity_score = max_similarity
            seg1.flagged = max_similarity >= self.threshold
            seg1.matches_with = matches
            
            # Generate paraphrase if flagged and requested
            if paraphraser and seg1.flagged:
                seg1.paraphrase_suggestion = paraphraser.paraphrase(seg1.text)
        
        # Calculate overall originality score
        flagged_count = sum(1 for s in segments if s.flagged)
        total_segments = len(segments)
        originality_score = ((total_segments - flagged_count) / total_segments * 100) if total_segments > 0 else 100
        
        # Build result
        result = {
            'originality_score': round(originality_score, 2),
            'total_segments': total_segments,
            'flagged_segments': flagged_count,
            'threshold': self.threshold,
            'segment_type': self.segment_type,
            'segments': [
                {
                    'index': s.index,
                    'text': s.text,
                    'similarity_score': round(s.similarity_score, 4),
                    'flagged': s.flagged,
                    'matches_with': s.matches_with,
                    'paraphrase_suggestion': s.paraphrase_suggestion if paraphrase else None
                }
                for s in segments
            ],
            'summary': self._generate_summary(originality_score, flagged_count, total_segments)
        }
        
        return result
    
    def _generate_summary(self, originality_score: float, 
                          flagged: int, total: int) -> str:
        """Generate human-readable summary."""
        if originality_score >= 90:
            return f"Text shows very high originality ({originality_score:.1f}%). Minor patterns detected in {flagged}/{total} segments."
        elif originality_score >= 75:
            return f"Text shows good originality ({originality_score:.1f}%). {flagged}/{total} segments flagged for review."
        elif originality_score >= 50:
            return f"Text shows moderate similarity issues ({originality_score:.1f}%). {flagged}/{total} segments require revision."
        else:
            return f"Text shows significant similarity concerns ({originality_score:.1f}%). Extensive revision recommended - {flagged}/{total} segments flagged."


def read_file(filepath: str) -> str:
    """Read text from file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Handle common text formats
    suffix = path.suffix.lower()
    
    if suffix == '.txt' or suffix == '.md':
        return path.read_text(encoding='utf-8')
    else:
        # Try to read as text
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported file format: {suffix}")


def format_report(result: Dict, format_type: str = 'json') -> str:
    """Format analysis report."""
    if format_type == 'json':
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # Text format
    lines = [
        "=" * 60,
        "PLAGIARISM CHECK REPORT",
        "=" * 60,
        f"Originality Score: {result['originality_score']}%",
        f"Total Segments: {result['total_segments']}",
        f"Flagged Segments: {result['flagged_segments']}",
        f"Threshold: {result['threshold']}",
        "-" * 60,
        result['summary'],
        "=" * 60,
    ]
    
    for seg in result['segments']:
        if seg['flagged']:
            lines.append(f"\n⚠️  SEGMENT {seg['index']} (Similarity: {seg['similarity_score']:.2%})")
            lines.append(f"   Text: {seg['text'][:100]}...")
            if seg.get('paraphrase_suggestion'):
                lines.append(f"   Suggestion: {seg['paraphrase_suggestion'][:100]}...")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Plagiarism Checker Pre-Screener - Check text originality'
    )
    parser.add_argument('--input', '-i', type=str, help='Text to analyze')
    parser.add_argument('--file', '-f', type=str, help='Path to file to analyze')
    parser.add_argument('--threshold', '-t', type=float, default=0.70,
                        help='Similarity threshold (0.0-1.0), default 0.70')
    parser.add_argument('--paraphrase', '-p', action='store_true',
                        help='Enable paraphrasing suggestions')
    parser.add_argument('--style', '-s', type=str, default='neutral',
                        choices=['academic', 'formal', 'casual', 'neutral'],
                        help='Paraphrasing style')
    parser.add_argument('--segments', type=str, default='sentence',
                        choices=['sentence', 'paragraph'],
                        help='Analysis segment type')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file path (JSON format)')
    parser.add_argument('--format', type=str, default='text',
                        choices=['json', 'text'],
                        help='Output format')
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        try:
            text = read_file(args.file)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        text = args.input
    else:
        # Read from stdin
        text = sys.stdin.read()
        if not text.strip():
            parser.print_help()
            sys.exit(1)
    
    # Validate threshold
    if not 0 <= args.threshold <= 1:
        print("Error: Threshold must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    checker = PlagiarismChecker(
        threshold=args.threshold,
        segment_type=args.segments
    )
    
    result = checker.analyze(
        text=text,
        paraphrase=args.paraphrase,
        style=args.style
    )
    
    # Format and output
    output = format_report(result, args.format)
    
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Report saved to: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()

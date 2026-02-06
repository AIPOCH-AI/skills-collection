#!/usr/bin/env python3
"""
Graphical Abstract Wizard
Analyzes paper abstracts and generates graphical abstract layout recommendations.

Usage:
    python main.py -a "Your abstract text"
    cat abstract.txt | python main.py
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Concept:
    """Represents an extracted concept from the abstract."""
    term: str
    category: str  # 'method', 'material', 'result', 'concept'
    importance: int  # 1-5
    visual_symbol: str


@dataclass
class LayoutElement:
    """Represents a visual element in the layout."""
    name: str
    symbol: str
    position: str  # 'center', 'left', 'right', 'top', 'bottom'
    color: str
    description: str


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    abstract_summary: Dict[str, str]
    key_concepts: List[Concept]
    visual_elements: List[LayoutElement]
    layout_blueprint: str
    midjourney_prompt: str
    dalle_prompt: str


class AbstractAnalyzer:
    """Analyzes paper abstracts to extract key information."""
    
    # Domain keywords for concept extraction
    METHOD_KEYWORDS = [
        'approach', 'method', 'algorithm', 'technique', 'framework', 'model',
        'architecture', 'strategy', 'procedure', 'protocol', 'system',
        'using', 'via', 'by means of', 'based on', 'trained', 'optimized',
        'deep learning', 'machine learning', 'neural network', 'transformer'
    ]
    
    MATERIAL_KEYWORDS = [
        'protein', 'dna', 'rna', 'cell', 'tissue', 'organism', 'sample',
        'dataset', 'data', 'material', 'compound', 'molecule', 'catalyst',
        'electrode', 'membrane', 'polymer', 'nanoparticle', 'quantum',
        'battery', 'solar', 'fuel', 'carbon', 'graphene', 'crystal'
    ]
    
    RESULT_KEYWORDS = [
        'achieved', 'achieves', 'demonstrated', 'shows', 'results', 'found',
        'observed', 'improved', 'enhanced', 'increased', 'decreased',
        'accuracy', 'performance', 'efficiency', 'significant', 'outperforms',
        'state-of-the-art', 'breakthrough', 'discovery', 'validated'
    ]
    
    # Common stop words to filter out
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'this',
        'that', 'these', 'those', 'we', 'our', 'us', 'it', 'its', 'they',
        'their', 'them', 'i', 'me', 'my', 'he', 'him', 'his', 'she', 'her',
        'you', 'your', 'also', 'more', 'most', 'some', 'any', 'all', 'both',
        'each', 'few', 'many', 'much', 'such', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'now', 'then', 'here', 'there', 'when',
        'where', 'why', 'how', 'what', 'who', 'which', 'whom', 'whose', 'not',
        'no', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
        't', 'don', 'doesn', 'didn', 'wasn', 'weren', 'haven', 'hasn', 'hadn',
        'won', 'wouldn', 'couldn', 'shouldn', 'isn', 'aren', 'ain', 'll',
        're', 've', 'd', 'm', 'o', 'ma', 'needn', 'shan', 'shouldn', 'wasn',
        'weren', 'won', 'wouldn', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn',
        'hadn', 'hasn', 'haven', 'isn', 'let', 'mustn', 'needn', 'shouldn',
        'wasn', 'weren', 'won', 'yourselves', 'yours', 'yourself', 'you', 'y',
        'wouldn', 'would', 'will', 'weren', 'we', 'wasn', 'was', 've', 'us',
        'until', 'under', 'too', 'to', 'through', 'those', 'this', 'these',
        'theirs', 'themselves', 'the', 'than', 't', 'such', 'some', 'so',
        'shouldn', 'should', 'shan', 'she', 's', 'same', 're', 'ourselves',
        'ours', 'our', 'ourselves', 'out', 'own', 'or', 'on', 'once', 'of',
        'off', 'o', 'now', 'not', 'nor', 'no', 'needn', 'need', 'myself',
        'my', 'mustn', 'must', 'more', 'most', 'me', 'm', 'll', 'itself',
        'its', 'it', 'isn', 'into', 'in', 'if', 'himself', 'him', 'hers',
        'herself', 'her', 'he', 'haven', 'hasn', 'has', 'hadn', 'had', 'hadn',
        'had', 'hadn', 'further', 'from', 'for', 'few', 'each', 'doesn',
        'does', 'do', 'didn', 'did', 'don', 'do', 'down', 'during', 'don',
        'do', 'does', 'doing', 'did', 'couldn', 'could', 'can', 'cannot',
        'can', 'by', 'but', 'both', 'between', 'before', 'been', 'be', 'because',
        'been', 'be', 'at', 'as', 'aren', 'are', 'an', 'am', 'against', 'again',
        'after', 'above', 'about', 'your', 'yours', 'yourself', 'yourselves',
        'you', 'y', 'wouldn', 'would', 'will', 'weren', 'we', 'wasn', 'was',
        've', 'us', 'until', 'under', 'too', 'to', 'through', 'those', 'this',
        'these', 'theirs', 'themselves', 'the', 'than', 't', 'such', 'some',
        'so', 'shouldn', 'should', 'shan', 'she', 's', 'same', 're', 'ourselves',
        'ours', 'our', 'ourselves', 'out', 'own', 'or', 'on', 'once', 'of',
        'off', 'o', 'now', 'not', 'nor', 'no', 'needn', 'need', 'myself',
        'my', 'mustn', 'must', 'more', 'most', 'me', 'm', 'll', 'itself',
        'its', 'it', 'isn', 'into', 'in', 'if', 'himself', 'him', 'hers',
        'herself', 'her', 'he', 'haven', 'hasn', 'has', 'hadn', 'had',
        'having', 'has', 'hadn', 'had', 'hadn', 'further', 'from', 'for',
        'few', 'each', 'doesn', 'does', 'do', 'didn', 'did', 'don', 'do',
        'down', 'during', 'don', 'do', 'does', 'doing', 'did', 'couldn',
        'could', 'can', 'cannot', 'can', 'by', 'but', 'both', 'between',
        'before', 'been', 'be', 'because', 'been', 'be', 'at', 'as', 'aren',
        'are', 'an', 'am', 'against', 'again', 'after', 'above', 'about'
    }
    
    # Visual symbol mappings
    SYMBOL_MAP = {
        # Methods
        'neural network': '🧠', 'deep learning': '🤖', 'machine learning': '⚙️',
        'transformer': '🔀', 'cnn': '👁️', 'rnn': '🔄', 'llm': '💬',
        'algorithm': '📐', 'simulation': '💻', 'experiment': '🧪',
        'approach': '📋', 'method': '🔧', 'framework': '🏗️', 'model': '📊',
        'architecture': '🏛️', 'technique': '🔨', 'strategy': '♟️',
        # Materials
        'protein': '🧬', 'dna': '🧬', 'cell': '🦠', 'molecule': '⚛️',
        'quantum': '🔮', 'nanoparticle': '⚫', 'catalyst': '⚗️',
        'battery': '🔋', 'solar': '☀️', 'fuel': '⛽', 'carbon': '⚫',
        'graphene': '⬡', 'crystal': '💎',
        # Results
        'accuracy': '🎯', 'performance': '📈', 'improvement': '⬆️',
        'efficiency': '⚡', 'breakthrough': '💡', 'discovery': '🔍',
        'state-of-the-art': '🏆', 'validated': '✅',
        # General
        'data': '📊', 'analysis': '📋', 'prediction': '🔮', 'optimization': '🎯',
        'learning': '📚', 'network': '🕸️', 'structure': '🏗️', 'energy': '⚡',
        'geometric': '📐', 'constraint': '⛓️', 'benchmark': '📏'
    }
    
    COLOR_PALETTES = {
        'scientific': ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE'],
        'biomedical': ['#059669', '#10B981', '#34D399', '#6EE7B7', '#D1FAE5'],
        'tech': ['#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD', '#EDE9FE'],
        'energy': ['#DC2626', '#EF4444', '#F87171', '#FCA5A5', '#FEE2E2'],
        'minimal': ['#1F2937', '#4B5563', '#9CA3AF', '#D1D5DB', '#F3F4F6']
    }
    
    def __init__(self):
        self.abstract_text = ""
    
    def analyze(self, abstract: str) -> AnalysisResult:
        """Main analysis pipeline."""
        self.abstract_text = abstract.strip()
        
        # Extract components
        summary = self._extract_summary()
        concepts = self._extract_concepts()
        elements = self._generate_visual_elements(concepts)
        blueprint = self._generate_layout_blueprint(elements)
        
        # Generate prompts
        mj_prompt = self._generate_midjourney_prompt(concepts, elements)
        dalle_prompt = self._generate_dalle_prompt(concepts, elements)
        
        return AnalysisResult(
            abstract_summary=summary,
            key_concepts=concepts,
            visual_elements=elements,
            layout_blueprint=blueprint,
            midjourney_prompt=mj_prompt,
            dalle_prompt=dalle_prompt
        )
    
    def _extract_summary(self) -> Dict[str, str]:
        """Extract a brief summary of the abstract."""
        # Simple sentence extraction for key points
        sentences = re.split(r'[.!?]+', self.abstract_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        summary = {
            'topic': self._detect_topic(),
            'method': '',
            'result': '',
            'full_text': self.abstract_text[:500] + '...' if len(self.abstract_text) > 500 else self.abstract_text
        }
        
        # Try to identify method and result sentences
        for sent in sentences:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in self.METHOD_KEYWORDS) and not summary['method']:
                summary['method'] = sent[:200]
            if any(kw in sent_lower for kw in self.RESULT_KEYWORDS) and not summary['result']:
                summary['result'] = sent[:200]
        
        # Fallback to first and last sentences
        if not summary['method'] and sentences:
            summary['method'] = sentences[0][:200]
        if not summary['result'] and len(sentences) > 1:
            summary['result'] = sentences[-1][:200]
            
        return summary
    
    def _detect_topic(self) -> str:
        """Detect the main topic domain."""
        text_lower = self.abstract_text.lower()
        
        domain_scores = {
            'biomedical': sum(1 for kw in ['protein', 'dna', 'cell', 'drug', 'disease'] if kw in text_lower),
            'computer_vision': sum(1 for kw in ['image', 'vision', 'detection', 'segmentation'] if kw in text_lower),
            'nlp': sum(1 for kw in ['language', 'text', 'nlp', 'translation', 'sentiment'] if kw in text_lower),
            'robotics': sum(1 for kw in ['robot', 'autonomous', 'control', 'navigation'] if kw in text_lower),
            'energy': sum(1 for kw in ['battery', 'solar', 'catalyst', 'energy', 'fuel'] if kw in text_lower),
            'materials': sum(1 for kw in ['material', 'crystal', 'polymer', 'composite'] if kw in text_lower),
        }
        
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        return 'general_science'
    
    def _extract_concepts(self) -> List[Concept]:
        """Extract key concepts from the abstract."""
        concepts = []
        text_lower = self.abstract_text.lower()
        
        # Helper function to filter valid terms
        def is_valid_term(term: str) -> bool:
            term_lower = term.lower()
            # Must be longer than 2 chars, not a stop word, and not just numbers
            return (len(term) > 2 and 
                    term_lower not in self.STOP_WORDS and
                    not term.isdigit() and
                    not all(c in '.,;:!?()[]{}' for c in term))
        
        # Helper function to clean and validate term
        def clean_term(term: str) -> Optional[str]:
            # Remove punctuation and extra whitespace
            cleaned = term.strip(',.()[]{};:?!\"\'').strip()
            if is_valid_term(cleaned):
                return cleaned
            return None
        
        # Find method concepts with better context extraction
        for keyword in self.METHOD_KEYWORDS:
            if keyword in text_lower:
                # Find all occurrences
                pattern = re.compile(rf'[^.]*?\b{re.escape(keyword)}\b[^.]*?\.', re.IGNORECASE)
                matches = pattern.findall(self.abstract_text)
                
                for match in matches[:2]:  # Limit to first 2 matches
                    # Look for compound terms after the keyword
                    # Pattern: keyword + [optional words] + important term
                    words = match.split()
                    for i, word in enumerate(words):
                        word_clean = word.lower().strip(',.()[]')
                        if keyword in word_clean:
                            # Try to get the next meaningful term
                            for j in range(i + 1, min(i + 4, len(words))):
                                candidate = clean_term(words[j])
                                if candidate and len(candidate) > 3:
                                    # Check if it's a compound term (e.g., "neural network")
                                    if j + 1 < len(words):
                                        next_word = words[j + 1].lower().strip(',.()[]')
                                        compound = f"{candidate.lower()} {next_word}"
                                        if compound in self.SYMBOL_MAP:
                                            candidate = compound.title()
                                    
                                    symbol = self._get_symbol(candidate, 'method')
                                    concepts.append(Concept(
                                        term=candidate.title(),
                                        category='method',
                                        importance=4,
                                        visual_symbol=symbol
                                    ))
                                    break
        
        # Find material/subject concepts with importance weighting
        material_concepts = []
        for keyword in self.MATERIAL_KEYWORDS:
            if keyword in text_lower:
                # Check if it's a compound term
                for compound in ['protein structure', 'dna sequencing', 'cell membrane', 
                                'neural network', 'deep learning', 'quantum computing']:
                    if compound in text_lower:
                        parts = compound.split()
                        if parts[0] == keyword or parts[1] == keyword:
                            symbol = self._get_symbol(compound, 'material')
                            material_concepts.append(Concept(
                                term=compound.title(),
                                category='material',
                                importance=5,
                                visual_symbol=symbol
                            ))
                            break
                else:
                    symbol = self._get_symbol(keyword, 'material')
                    # Count occurrences for importance
                    count = text_lower.count(keyword)
                    importance = min(5, 3 + count // 2)
                    material_concepts.append(Concept(
                        term=keyword.title(),
                        category='material',
                        importance=importance,
                        visual_symbol=symbol
                    ))
        concepts.extend(material_concepts)
        
        # Find result concepts
        result_concepts = []
        for keyword in self.RESULT_KEYWORDS:
            if keyword in text_lower:
                symbol = self._get_symbol(keyword, 'result')
                # Check if followed by a metric or value
                pattern = re.compile(rf'\b{re.escape(keyword)}\b\s+(\d+(?:\.\d+)?\s*(?:%|percent|fold|x))', re.IGNORECASE)
                metric_match = pattern.search(self.abstract_text)
                
                if metric_match:
                    term = f"{keyword} {metric_match.group(1)}"
                    importance = 5
                else:
                    term = keyword.title()
                    importance = 4
                    
                result_concepts.append(Concept(
                    term=term,
                    category='result',
                    importance=importance,
                    visual_symbol=symbol
                ))
        concepts.extend(result_concepts)
        
        # Extract significant noun phrases using simple patterns
        # Pattern: adjective + noun combinations
        noun_patterns = [
            r'\b(\w{4,})\s+(?:approach|method|algorithm|technique|framework|model|system)\b',
            r'\b(\w{4,})\s+(?:prediction|classification|detection|analysis|optimization)\b',
            r'\b(\w{4,})\s+(?:performance|accuracy|efficiency|improvement)\b',
            r'\b(?:novel|new|improved|efficient|accurate)\s+(\w{4,})\b'
        ]
        
        for pattern in noun_patterns:
            matches = re.findall(pattern, self.abstract_text, re.IGNORECASE)
            for match in matches[:3]:  # Limit to first 3
                term = clean_term(match)
                if term and is_valid_term(term) and len(term) > 4:
                    # Avoid duplicates
                    if not any(c.term.lower() == term.lower() for c in concepts):
                        symbol = self._get_symbol(term, 'concept')
                        concepts.append(Concept(
                            term=term.title(),
                            category='concept',
                            importance=3,
                            visual_symbol=symbol
                        ))
        
        # Deduplicate by term (case-insensitive)
        seen = {}
        unique_concepts = []
        for c in concepts:
            term_key = c.term.lower()
            if term_key not in seen:
                seen[term_key] = c
                unique_concepts.append(c)
            else:
                # Update importance if this is a duplicate with higher importance
                if c.importance > seen[term_key].importance:
                    seen[term_key].importance = c.importance
        
        # Sort by importance descending
        unique_concepts.sort(key=lambda x: x.importance, reverse=True)
        
        return unique_concepts[:8]  # Limit to top 8 concepts
    
    def _get_symbol(self, term: str, category: str) -> str:
        """Get appropriate visual symbol for a term."""
        term_lower = term.lower()
        
        # Check direct mapping
        for key, symbol in self.SYMBOL_MAP.items():
            if key in term_lower:
                return symbol
        
        # Default symbols by category
        defaults = {
            'method': '⚙️',
            'material': '🔬',
            'result': '📊',
            'concept': '💡'
        }
        return defaults.get(category, '📌')
    
    def _generate_visual_elements(self, concepts: List[Concept]) -> List[LayoutElement]:
        """Generate visual layout elements from concepts."""
        elements = []
        
        # Select color palette based on topic
        topic = self._detect_topic()
        palette = self.COLOR_PALETTES.get(topic, self.COLOR_PALETTES['scientific'])
        
        # Sort by importance
        sorted_concepts = sorted(concepts, key=lambda x: x.importance, reverse=True)
        
        positions = ['center', 'left', 'right', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left']
        
        for i, concept in enumerate(sorted_concepts[:6]):
            position = positions[i] if i < len(positions) else 'floating'
            color = palette[i % len(palette)]
            
            elements.append(LayoutElement(
                name=concept.term,
                symbol=concept.visual_symbol,
                position=position,
                color=color,
                description=f"{concept.category.title()}: {concept.term}"
            ))
        
        # Always add a flow/connection element
        if elements:
            elements.append(LayoutElement(
                name='Flow',
                symbol='→',
                position='connecting',
                color=palette[2],
                description='Data/information flow between elements'
            ))
        
        return elements
    
    def _generate_layout_blueprint(self, elements: List[LayoutElement]) -> str:
        """Generate ASCII layout blueprint."""
        # Create a simple grid layout
        center = [e for e in elements if e.position == 'center']
        left = [e for e in elements if e.position == 'left']
        right = [e for e in elements if e.position == 'right']
        top = [e for e in elements if e.position == 'top']
        bottom = [e for e in elements if e.position == 'bottom']
        
        blueprint = """
┌─────────────────────────────────────────────────────────┐
│  {top:^55}  │
├──────────────────┬──────────────────┬───────────────────┤
│  {left:^16} │  {center:^16} │  {right:^17} │
├──────────────────┼──────────────────┼───────────────────┤
│  {bottom:^54} │
└──────────────────┴──────────────────┴───────────────────┘
""".format(
            top=' '.join(e.symbol for e in top) if top else '  ',
            left=' '.join(e.symbol for e in left) if left else 'Input',
            center=' '.join(e.symbol for e in center) if center else '⚙️',
            right=' '.join(e.symbol for e in right) if right else 'Output',
            bottom=' '.join(e.symbol for e in bottom) if bottom else '  '
        )
        
        return blueprint
    
    def _generate_midjourney_prompt(self, concepts: List[Concept], elements: List[LayoutElement]) -> str:
        """Generate Midjourney prompt."""
        topic = self._detect_topic()
        
        # Build concept string
        concept_terms = [c.term for c in concepts[:4]]
        concept_str = ', '.join(concept_terms) if concept_terms else 'scientific research'
        
        # Select style based on topic
        style_modifiers = {
            'biomedical': 'microscopic detail, cellular structures',
            'computer_vision': 'digital visualization, neural patterns',
            'nlp': 'text streams, linguistic patterns',
            'robotics': 'mechanical precision, futuristic',
            'energy': 'dynamic energy flows, molecular bonds',
            'materials': 'crystalline structures, surface textures',
        }
        style = style_modifiers.get(topic, 'clean scientific illustration')
        
        symbols = ' '.join([e.symbol for e in elements[:5]])
        
        prompt = f"""Scientific graphical abstract, {concept_str}, {style}, 
clean minimalist design, {symbols}, professional academic journal style, 
blue and white color scheme, high quality, vector art style, 
white background, centered composition --ar 16:9 --v 6 --style raw"""
        
        return ' '.join(prompt.split())  # Normalize whitespace
    
    def _generate_dalle_prompt(self, concepts: List[Concept], elements: List[LayoutElement]) -> str:
        """Generate DALL-E prompt."""
        topic = self._detect_topic()
        
        concept_terms = [c.term for c in concepts[:4]]
        concept_str = ', '.join(concept_terms) if concept_terms else 'scientific research'
        
        topic_descriptions = {
            'biomedical': 'biological and molecular visualization',
            'computer_vision': 'computer vision and image processing',
            'nlp': 'natural language processing and text analysis',
            'robotics': 'robotics and autonomous systems',
            'energy': 'energy research and sustainable technology',
            'materials': 'materials science and nanotechnology',
        }
        topic_desc = topic_descriptions.get(topic, 'scientific research')
        
        prompt = f"""A clean, professional scientific illustration for a research paper about {topic_desc}.
The image should visually represent {concept_str}.

Style requirements:
- Modern, minimalist academic style suitable for a journal cover
- Professional blue and white color scheme with subtle gradients
- Clean white or very light background
- Abstract geometric shapes showing data flow and connections
- High contrast, crisp lines
- No text or labels
- Vector art aesthetic
- Scientifically accurate but stylized representation
- Centered composition with clear visual hierarchy

The illustration should communicate innovation, precision, and scientific rigor."""
        
        return prompt


def format_output(result: AnalysisResult, format_type: str) -> str:
    """Format the analysis result for output."""
    
    if format_type == 'json':
        # Convert dataclasses to dict
        output = {
            'abstract_summary': result.abstract_summary,
            'key_concepts': [asdict(c) for c in result.key_concepts],
            'visual_elements': [asdict(e) for e in result.visual_elements],
            'layout_blueprint': result.layout_blueprint,
            'ai_prompts': {
                'midjourney': result.midjourney_prompt,
                'dalle': result.dalle_prompt
            }
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    elif format_type == 'text':
        lines = [
            "=" * 60,
            "GRAPHICAL ABSTRACT RECOMMENDATION",
            "=" * 60,
            "",
            "ABSTRACT SUMMARY:",
            f"  Topic: {result.abstract_summary.get('topic', 'N/A')}",
            f"  Method: {result.abstract_summary.get('method', 'N/A')[:100]}...",
            f"  Result: {result.abstract_summary.get('result', 'N/A')[:100]}...",
            "",
            "KEY CONCEPTS:",
        ]
        for c in result.key_concepts:
            lines.append(f"  {c.visual_symbol} {c.term} ({c.category}, importance: {c.importance})")
        
        lines.extend([
            "",
            "VISUAL ELEMENTS:",
        ])
        for e in result.visual_elements:
            lines.append(f"  [{e.position}] {e.symbol} {e.name} - {e.color}")
        
        lines.extend([
            "",
            "LAYOUT BLUEPRINT:",
            result.layout_blueprint,
            "",
            "MIDJOURNEY PROMPT:",
            result.midjourney_prompt,
            "",
            "DALL-E PROMPT:",
            result.dalle_prompt,
            "",
            "=" * 60,
        ])
        return '\n'.join(lines)
    
    else:  # markdown (default)
        lines = [
            "# 🎨 Graphical Abstract Recommendation",
            "",
            "## 📋 Abstract Summary",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Topic** | {result.abstract_summary.get('topic', 'N/A').replace('_', ' ').title()} |",
            f"| **Method** | {result.abstract_summary.get('method', 'N/A')[:150]}... |",
            f"| **Result** | {result.abstract_summary.get('result', 'N/A')[:150]}... |",
            "",
            "## 🔑 Key Concepts",
            "",
        ]
        
        for c in result.key_concepts:
            lines.append(f"- {c.visual_symbol} **{c.term}** ({c.category}) - Importance: {'⭐' * c.importance}")
        
        lines.extend([
            "",
            "## 🎯 Visual Elements",
            "",
            "| Element | Symbol | Position | Color |",
            "|---------|--------|----------|-------|",
        ])
        
        for e in result.visual_elements:
            color_preview = f"`{e.color}`"
            lines.append(f"| {e.name} | {e.symbol} | {e.position} | {color_preview} |")
        
        lines.extend([
            "",
            "## 📐 Layout Blueprint",
            "```",
            result.layout_blueprint,
            "```",
            "",
            "## 🎨 AI Art Prompts",
            "",
            "### Midjourney",
            "```",
            result.midjourney_prompt,
            "```",
            "",
            "### DALL-E",
            "```",
            result.dalle_prompt,
            "```",
            "",
            "---",
            "*Generated by Graphical Abstract Wizard (Skill ID: 158)*",
        ])
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Graphical Abstract Wizard - Generate visual layout recommendations from paper abstracts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -a "We propose a novel deep learning approach..."
  cat abstract.txt | python main.py -f json
  python main.py -a abstract.txt -s scientific -o output.md
        """
    )
    
    parser.add_argument(
        '--abstract', '-a',
        type=str,
        help='Paper abstract text (or path to file containing abstract)'
    )
    
    parser.add_argument(
        '--style', '-s',
        type=str,
        choices=['scientific', 'minimal', 'colorful', 'sketch'],
        default='scientific',
        help='Visual style preference (default: scientific)'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'markdown', 'text'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Get abstract text
    abstract_text = ""
    
    if args.abstract:
        # Check if it's a file path
        try:
            with open(args.abstract, 'r', encoding='utf-8') as f:
                abstract_text = f.read()
        except FileNotFoundError:
            # Treat as direct text
            abstract_text = args.abstract
        except IOError:
            abstract_text = args.abstract
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            abstract_text = sys.stdin.read()
    
    if not abstract_text.strip():
        print("Error: No abstract provided. Use -a flag or pipe text via stdin.", file=sys.stderr)
        sys.exit(1)
    
    # Analyze
    analyzer = AbstractAnalyzer()
    result = analyzer.analyze(abstract_text)
    
    # Format output
    output = format_output(result, args.format)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()

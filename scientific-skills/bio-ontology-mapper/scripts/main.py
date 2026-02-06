#!/usr/bin/env python3
"""
Bio-Ontology Mapper
Maps unstructured biomedical text to SNOMED CT and MeSH ontologies.

Author: AI Assistant
Date: 2026-02-05
Status: Requires human review
"""

import argparse
import json
import csv
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher


@dataclass
class MappingResult:
    """Represents a single ontology mapping result."""
    ontology: str
    concept_id: str
    term: str
    confidence: float
    semantic_tag: Optional[str] = None
    tree_numbers: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None


@dataclass
class MappingOutput:
    """Complete output for an input term."""
    input: str
    mappings: List[MappingResult]


class BioOntologyMapper:
    """
    Maps biomedical terms to SNOMED CT and MeSH ontologies.
    
    Uses a combination of:
    - Exact matching
    - Fuzzy string matching
    - Synonym expansion
    - Semantic type filtering
    """
    
    SNOMED_UMLS_URL = "https://uts-ws.nlm.nih.gov/rest"
    MESH_API_URL = "https://id.nlm.nih.gov/mesh"
    
    def __init__(self, 
                 threshold: float = 0.7,
                 use_api: bool = False,
                 references_dir: Optional[str] = None):
        """
        Initialize the mapper.
        
        Args:
            threshold: Minimum confidence score (0-1)
            use_api: Whether to use external APIs (requires credentials)
            references_dir: Path to reference files directory
        """
        self.threshold = threshold
        self.use_api = use_api
        self.references_dir = Path(references_dir) if references_dir else \
            Path(__file__).parent.parent / "references"
        
        # Load local reference data
        self._load_references()
        
        # API credentials from environment
        self.umls_api_key = os.getenv("UMLS_API_KEY")
    
    def _load_references(self):
        """Load reference synonym and sample mapping files."""
        self.synonyms = {}
        self.snomed_samples = {}
        self.mesh_samples = {}
        
        # Load synonyms
        syn_file = self.references_dir / "synonyms.json"
        if syn_file.exists():
            with open(syn_file, 'r', encoding='utf-8') as f:
                self.synonyms = json.load(f)
        
        # Load SNOMED samples
        snomed_file = self.references_dir / "snomed_sample.json"
        if snomed_file.exists():
            with open(snomed_file, 'r', encoding='utf-8') as f:
                self.snomed_samples = json.load(f)
        
        # Load MeSH samples
        mesh_file = self.references_dir / "mesh_sample.json"
        if mesh_file.exists():
            with open(mesh_file, 'r', encoding='utf-8') as f:
                self.mesh_samples = json.load(f)
    
    def _normalize_term(self, term: str) -> str:
        """Normalize input term for matching."""
        # Lowercase
        term = term.lower().strip()
        # Remove extra whitespace
        term = re.sub(r'\s+', ' ', term)
        # Remove punctuation except hyphen
        term = re.sub(r'[^\w\s-]', '', term)
        return term
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity (0-1)."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _expand_synonyms(self, term: str) -> List[str]:
        """Get expanded terms including synonyms."""
        variants = [term]
        norm = self._normalize_term(term)
        
        # Check direct synonym
        if norm in self.synonyms:
            variants.extend(self.synonyms[norm])
        
        # Check reverse lookup
        for key, syns in self.synonyms.items():
            if norm in [self._normalize_term(s) for s in syns]:
                variants.append(key)
        
        return list(set(variants))
    
    def _map_to_snomed(self, term: str) -> List[MappingResult]:
        """Map term to SNOMED CT concepts."""
        results = []
        variants = self._expand_synonyms(term)
        
        # Search in local samples
        for concept_id, data in self.snomed_samples.items():
            concept_term = data.get("term", "")
            concept_synonyms = data.get("synonyms", [])
            
            # Check all variants
            all_terms = [concept_term] + concept_synonyms
            for variant in variants:
                for ct in all_terms:
                    score = self._similarity(variant, ct)
                    if score >= self.threshold:
                        results.append(MappingResult(
                            ontology="SNOMED CT",
                            concept_id=concept_id,
                            term=concept_term,
                            confidence=round(score, 3),
                            semantic_tag=data.get("semantic_tag"),
                            synonyms=concept_synonyms if concept_synonyms else None
                        ))
                        break
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.confidence, reverse=True):
            key = (r.concept_id, r.term)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique[:5]  # Return top 5
    
    def _map_to_mesh(self, term: str) -> List[MappingResult]:
        """Map term to MeSH descriptors."""
        results = []
        variants = self._expand_synonyms(term)
        
        # Search in local samples
        for descriptor_id, data in self.mesh_samples.items():
            descriptor_term = data.get("term", "")
            entry_terms = data.get("entry_terms", [])
            
            # Check all variants
            all_terms = [descriptor_term] + entry_terms
            for variant in variants:
                for dt in all_terms:
                    score = self._similarity(variant, dt)
                    if score >= self.threshold:
                        results.append(MappingResult(
                            ontology="MeSH",
                            concept_id=descriptor_id,
                            term=descriptor_term,
                            confidence=round(score, 3),
                            tree_numbers=data.get("tree_numbers"),
                            synonyms=entry_terms if entry_terms else None
                        ))
                        break
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.confidence, reverse=True):
            key = (r.concept_id, r.term)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique[:5]  # Return top 5
    
    def map_term(self, term: str, ontology: str = "both") -> MappingOutput:
        """
        Map a single term to ontologies.
        
        Args:
            term: Input biomedical term
            ontology: Target ontology - 'snomed', 'mesh', or 'both'
        
        Returns:
            MappingOutput with all mappings
        """
        mappings = []
        
        if ontology in ("snomed", "both"):
            mappings.extend(self._map_to_snomed(term))
        
        if ontology in ("mesh", "both"):
            mappings.extend(self._map_to_mesh(term))
        
        # Sort by confidence
        mappings.sort(key=lambda x: x.confidence, reverse=True)
        
        return MappingOutput(input=term, mappings=mappings)
    
    def map_terms(self, terms: List[str], ontology: str = "both") -> List[MappingOutput]:
        """Map multiple terms."""
        return [self.map_term(t, ontology) for t in terms]
    
    def map_from_file(self, filepath: str, ontology: str = "both") -> List[MappingOutput]:
        """Map terms from a file (one per line)."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")
        
        # Detect format
        if path.suffix.lower() == '.csv':
            terms = self._read_csv(path)
        elif path.suffix.lower() == '.json':
            terms = self._read_json(path)
        else:
            # Plain text, one term per line
            with open(path, 'r', encoding='utf-8') as f:
                terms = [line.strip() for line in f if line.strip()]
        
        return self.map_terms(terms, ontology)
    
    def _read_csv(self, path: Path) -> List[str]:
        """Read terms from CSV."""
        terms = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            # Assume first column contains terms
            for row in reader:
                if row:
                    terms.append(row[0])
        return terms
    
    def _read_json(self, path: Path) -> List[str]:
        """Read terms from JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return [str(item) for item in data]
        elif isinstance(data, dict) and 'terms' in data:
            return data['terms']
        else:
            return [str(data)]


def format_output(results: List[MappingOutput], format_type: str) -> str:
    """Format results for output."""
    if format_type == 'json':
        # Convert dataclasses to dicts
        output = []
        for r in results:
            out = {
                "input": r.input,
                "mappings": [
                    {k: v for k, v in asdict(m).items() if v is not None}
                    for m in r.mappings
                ]
            }
            output.append(out)
        
        if len(output) == 1:
            return json.dumps(output[0], indent=2, ensure_ascii=False)
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    elif format_type in ('csv', 'tsv'):
        delimiter = '\t' if format_type == 'tsv' else ','
        lines = []
        lines.append(delimiter.join([
            'input', 'ontology', 'concept_id', 'term', 'confidence', 'semantic_tag'
        ]))
        
        for result in results:
            if result.mappings:
                for m in result.mappings:
                    lines.append(delimiter.join([
                        result.input,
                        m.ontology,
                        m.concept_id,
                        m.term,
                        str(m.confidence),
                        m.semantic_tag or ''
                    ]))
            else:
                lines.append(delimiter.join([result.input, 'NO_MATCH', '', '', '', '']))
        
        return '\n'.join(lines)
    
    else:
        raise ValueError(f"Unknown format: {format_type}")


def main():
    parser = argparse.ArgumentParser(
        description='Map biomedical terms to SNOMED CT and MeSH ontologies'
    )
    parser.add_argument('--term', type=str, help='Single term to map')
    parser.add_argument('--input', type=str, help='Input file path')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--ontology', choices=['snomed', 'mesh', 'both'],
                       default='both', help='Target ontology')
    parser.add_argument('--threshold', type=float, default=0.7,
                       help='Minimum confidence threshold (0-1)')
    parser.add_argument('--format', choices=['json', 'csv', 'tsv'],
                       default='json', help='Output format')
    parser.add_argument('--references', type=str,
                       help='Path to references directory')
    parser.add_argument('--use-api', action='store_true',
                       help='Use external APIs (requires credentials)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.term and not args.input:
        parser.error("Either --term or --input is required")
    
    if args.term and args.input:
        parser.error("Cannot use both --term and --input")
    
    # Initialize mapper
    mapper = BioOntologyMapper(
        threshold=args.threshold,
        use_api=args.use_api,
        references_dir=args.references
    )
    
    # Process
    if args.term:
        results = [mapper.map_term(args.term, args.ontology)]
    else:
        results = mapper.map_from_file(args.input, args.ontology)
    
    # Format output
    output = format_output(results, args.format)
    
    # Write or print
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()

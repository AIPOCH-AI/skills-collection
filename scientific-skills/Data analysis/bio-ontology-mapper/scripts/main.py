#!/usr/bin/env python3
"""
Bio-Ontology Mapper (with UMLS/MeSH API Integration)
Maps unstructured biomedical text to SNOMED CT and MeSH ontologies.
Uses official UMLS UTS API and MeSH API for accurate term mapping.
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional
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
    source: str = "local"


@dataclass
class MappingOutput:
    """Complete output for an input term."""
    input: str
    mappings: List[MappingResult]
    api_status: Dict[str, bool]


class UMLSClient:
    """Client for UMLS UTS API."""
    
    BASE_URL = "https://uts-ws.nlm.nih.gov/rest"
    
    def __init__(self, api_key: Optional[str] = None, delay: float = 0.5):
        self.api_key = api_key or os.getenv("UMLS_API_KEY")
        self.delay = delay
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Optional[Dict]:
        """Make UMLS API request with rate limiting."""
        if not self.api_key:
            return None
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}{endpoint}?{query_string}"
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'BioOntologyMapper/1.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                self.last_request_time = time.time()
                return json.loads(response.read().decode('utf-8'))
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"    UMLS auth failed: Invalid API key")
            elif e.code == 404:
                return {"result": []}
            else:
                print(f"    UMLS API error: {e.code}")
            return None
        except Exception as e:
            print(f"    UMLS request failed: {e}")
            return None
    
    def search(self, term: str, sabs: Optional[List[str]] = None, 
               page_size: int = 10) -> List[Dict]:
        """Search UMLS for concepts."""
        if not self.api_key:
            return []
        
        params = {
            "string": term,
            "apiKey": self.api_key,
            "pageSize": str(page_size)
        }
        
        if sabs:
            params["sabs"] = ",".join(sabs)
        
        response = self._make_request("/search/current", params)
        
        if response and "result" in response:
            return response["result"].get("results", [])
        return []
    
    def search_snomed(self, term: str) -> List[MappingResult]:
        """Search for SNOMED CT concepts."""
        results = []
        api_results = self.search(term, sabs=["SNOMEDCT_US"])
        
        for item in api_results[:5]:
            cui = item.get("ui", "")
            name = item.get("name", "")
            
            result = MappingResult(
                ontology="SNOMED CT",
                concept_id=cui,
                term=name,
                confidence=0.9,
                semantic_tag=item.get("semanticTypes", [{}])[0].get("name") if item.get("semanticTypes") else None,
                source="api"
            )
            results.append(result)
        
        return results


class MeSHClient:
    """Client for MeSH API."""
    
    BASE_URL = "https://id.nlm.nih.gov/mesh"
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.last_request_time = 0
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """Make MeSH API request with rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        try:
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'BioOntologyMapper/1.0'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                self.last_request_time = time.time()
                return json.loads(response.read().decode('utf-8'))
                
        except Exception as e:
            return None
    
    def search(self, term: str) -> List[Dict]:
        """Search MeSH descriptors."""
        encoded_term = urllib.parse.quote(term)
        url = f"{self.BASE_URL}/lookup/descriptor?label={encoded_term}"
        
        response = self._make_request(url)
        
        if response and isinstance(response, list):
            return response
        return []
    
    def search_descriptor(self, term: str) -> List[MappingResult]:
        """Search for MeSH descriptors."""
        results = []
        api_results = self.search(term)
        
        for item in api_results[:5]:
            if isinstance(item, dict):
                resource = item.get("resource", "")
                label = item.get("label", "")
                descriptor_id = resource.split('/')[-1] if resource else ""
                
                result = MappingResult(
                    ontology="MeSH",
                    concept_id=descriptor_id,
                    term=label,
                    confidence=0.95,
                    source="api"
                )
                results.append(result)
        
        return results


class BioOntologyMapper:
    """Maps biomedical terms to SNOMED CT and MeSH ontologies."""
    
    def __init__(self, threshold: float = 0.7, use_api: bool = True,
                 api_key: Optional[str] = None, references_dir: Optional[str] = None):
        self.threshold = threshold
        self.use_api = use_api
        self.references_dir = Path(references_dir) if references_dir else \
            Path(__file__).parent.parent / "references"
        
        self.umls_client = UMLSClient(api_key=api_key) if use_api else None
        self.mesh_client = MeSHClient() if use_api else None
        
        self._load_references()
    
    def _load_references(self):
        """Load local reference data."""
        self.synonyms = {}
        self.snomed_samples = {}
        self.mesh_samples = {}
        
        syn_file = self.references_dir / "synonyms.json"
        if syn_file.exists():
            with open(syn_file, 'r', encoding='utf-8') as f:
                self.synonyms = json.load(f)
        
        snomed_file = self.references_dir / "snomed_sample.json"
        if snomed_file.exists():
            with open(snomed_file, 'r', encoding='utf-8') as f:
                self.snomed_samples = json.load(f)
        
        mesh_file = self.references_dir / "mesh_sample.json"
        if mesh_file.exists():
            with open(mesh_file, 'r', encoding='utf-8') as f:
                self.mesh_samples = json.load(f)
    
    def _normalize_term(self, term: str) -> str:
        """Normalize input term."""
        term = term.lower().strip()
        term = re.sub(r'\s+', ' ', term)
        term = re.sub(r'[^\w\s-]', '', term)
        return term
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _expand_synonyms(self, term: str) -> List[str]:
        """Get expanded terms including synonyms."""
        variants = [term]
        norm = self._normalize_term(term)
        
        if norm in self.synonyms:
            variants.extend(self.synonyms[norm])
        
        return list(set(variants))
    
    def _map_to_snomed_local(self, term: str) -> List[MappingResult]:
        """Local SNOMED matching."""
        results = []
        variants = self._expand_synonyms(term)
        
        for concept_id, data in self.snomed_samples.items():
            concept_term = data.get("term", "")
            concept_synonyms = data.get("synonyms", [])
            
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
                            synonyms=concept_synonyms if concept_synonyms else None,
                            source="local"
                        ))
                        break
        
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.confidence, reverse=True):
            key = (r.concept_id, r.term)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique[:5]
    
    def _map_to_mesh_local(self, term: str) -> List[MappingResult]:
        """Local MeSH matching."""
        results = []
        variants = self._expand_synonyms(term)
        
        for descriptor_id, data in self.mesh_samples.items():
            descriptor_term = data.get("term", "")
            entry_terms = data.get("entry_terms", [])
            
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
                            synonyms=entry_terms if entry_terms else None,
                            source="local"
                        ))
                        break
        
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.confidence, reverse=True):
            key = (r.concept_id, r.term)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique[:5]
    
    def map_term(self, term: str, ontology: str = "both") -> MappingOutput:
        """Map a single term to ontologies."""
        mappings = []
        api_status = {"umls": False, "mesh": False}
        
        if ontology in ("snomed", "both"):
            if self.use_api and self.umls_client:
                api_results = self.umls_client.search_snomed(term)
                if api_results:
                    mappings.extend(api_results)
                    api_status["umls"] = True
            
            if not api_status["umls"]:
                local_results = self._map_to_snomed_local(term)
                mappings.extend(local_results)
        
        if ontology in ("mesh", "both"):
            if self.use_api and self.mesh_client:
                api_results = self.mesh_client.search_descriptor(term)
                if api_results:
                    mappings.extend(api_results)
                    api_status["mesh"] = True
            
            if not any(m.ontology == "MeSH" for m in mappings):
                local_results = self._map_to_mesh_local(term)
                mappings.extend(local_results)
        
        mappings.sort(key=lambda x: x.confidence, reverse=True)
        
        return MappingOutput(input=term, mappings=mappings, api_status=api_status)
    
    def map_terms(self, terms: List[str], ontology: str = "both") -> List[MappingOutput]:
        """Map multiple terms."""
        results = []
        for i, term in enumerate(terms, 1):
            print(f"[{i}/{len(terms)}] Processing: {term}")
            result = self.map_term(term, ontology)
            results.append(result)
            time.sleep(0.1)
        return results


def format_output(results: List[MappingOutput], format_type: str) -> str:
    """Format results for output."""
    if format_type == 'json':
        output = []
        for r in results:
            out = {
                "input": r.input,
                "api_status": r.api_status,
                "mappings": [asdict(m) for m in r.mappings]
            }
            output.append(out)
        
        if len(output) == 1:
            return json.dumps(output[0], indent=2)
        return json.dumps(output, indent=2)
    
    else:
        lines = []
        for r in results:
            if r.mappings:
                for m in r.mappings:
                    lines.append(f"{r.input}: {m.ontology} - {m.term} ({m.concept_id}) [{m.source}]")
            else:
                lines.append(f"{r.input}: No match found")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Map biomedical terms to SNOMED CT and MeSH ontologies'
    )
    parser.add_argument('--term', type=str, help='Single term to map')
    parser.add_argument('--input', type=str, help='Input file path')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--ontology', choices=['snomed', 'mesh', 'both'],
                       default='both')
    parser.add_argument('--threshold', type=float, default=0.7)
    parser.add_argument('--format', choices=['json', 'text'],
                       default='json')
    parser.add_argument('--use-api', action='store_true',
                       help='Use UMLS/MeSH APIs')
    parser.add_argument('--api-key', type=str,
                       help='UMLS API Key (or set UMLS_API_KEY env var)')
    
    args = parser.parse_args()
    
    if not args.term and not args.input:
        parser.error("Either --term or --input is required")
    
    api_key = args.api_key or os.getenv("UMLS_API_KEY")
    
    mapper = BioOntologyMapper(
        threshold=args.threshold,
        use_api=args.use_api,
        api_key=api_key
    )
    
    if args.term:
        print(f"Mapping: {args.term}")
        results = [mapper.map_term(args.term, args.ontology)]
    else:
        with open(args.input, 'r') as f:
            terms = [line.strip() for line in f if line.strip()]
        results = mapper.map_terms(terms, args.ontology)
    
    output = format_output(results, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()

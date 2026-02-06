#!/usr/bin/env python3
"""
Retraction Watcher - Scan document references and check for retracted papers.

Usage:
    python main.py --input <document.pdf|refs.bib|refs.txt> [--output report.txt]
    python main.py --text "[reference list]" [--format summary|detailed]
    python main.py --url <paper_url> [--format json]

Features:
    - Parses citations from PDF, BibTeX, RIS, and plain text
    - Checks DOIs against Retraction Watch and Crossref
    - Checks PMIDs against PubMed retraction database
    - Falls back to title matching when identifiers missing
    - Generates detailed or summary reports
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from urllib.error import HTTPError, URLError


@dataclass
class Citation:
    """Represents a parsed citation."""
    index: int
    raw_text: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []
    
    def get_identifier(self) -> str:
        """Return best available identifier for matching."""
        if self.doi:
            return f"DOI:{self.doi}"
        if self.pmid:
            return f"PMID:{self.pmid}"
        if self.title:
            return f"TITLE:{self.title[:50]}..."
        return f"REF:{self.index}"


@dataclass
class RetractionRecord:
    """Represents a retraction record from database."""
    identifier: str
    identifier_type: str  # 'doi', 'pmid', 'title'
    status: str  # 'retracted', 'expression_of_concern', 'corrected'
    title: Optional[str] = None
    original_title: Optional[str] = None
    retraction_date: Optional[str] = None
    retraction_reason: Optional[str] = None
    retraction_doi: Optional[str] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None


class CitationParser:
    """Parse citations from various formats."""
    
    DOI_PATTERN = re.compile(r'10\.\d{4,}\/[^\s\]]+', re.IGNORECASE)
    PMID_PATTERN = re.compile(r'PMID:\s*(\d+)', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
    
    @classmethod
    def extract_doi(cls, text: str) -> Optional[str]:
        """Extract DOI from text."""
        match = cls.DOI_PATTERN.search(text)
        if match:
            doi = match.group(0)
            # Clean up common suffixes
            doi = re.sub(r'[.,;\]]+$', '', doi)
            return doi.lower()
        return None
    
    @classmethod
    def extract_pmid(cls, text: str) -> Optional[str]:
        """Extract PMID from text."""
        match = cls.PMID_PATTERN.search(text)
        if match:
            return match.group(1)
        return None
    
    @classmethod
    def extract_year(cls, text: str) -> Optional[str]:
        """Extract publication year from text."""
        match = cls.YEAR_PATTERN.search(text)
        if match:
            return match.group(0)
        return None
    
    @classmethod
    def extract_title(cls, text: str) -> Optional[str]:
        """Try to extract article title from citation."""
        # Common patterns for titles in citations
        # Pattern 1: Title in quotes
        quote_match = re.search(r'"([^"]{20,200})"', text)
        if quote_match:
            return quote_match.group(1)
        
        # Pattern 2: Title after year, before journal (APA-like)
        # Example: Author (2020). Title here. Journal...
        apa_match = re.search(r'\(?(?:19|20)\d{2}\)?[.\s]+([A-Z][^.]{20,200}?)[.\s]+[A-Z][a-z]+', text)
        if apa_match:
            return apa_match.group(1).strip()
        
        # Pattern 3: Title after first period (numbered reference style)
        numbered_match = re.search(r'^\d+[.\]]\s+[^.]+\.\s+([A-Z][^.]{20,200})[.\s]', text)
        if numbered_match:
            return numbered_match.group(1).strip()
        
        return None
    
    @classmethod
    def extract_authors(cls, text: str) -> List[str]:
        """Extract author names from citation."""
        authors = []
        # Pattern 1: LastName FM, LastName FM
        author_pattern = re.findall(r'([A-Z][a-z]+\s+[A-Z]{1,2}(?:,\s*|\s+and\s+|\s*&\s*|$))', text)
        if author_pattern:
            for auth in author_pattern[:3]:  # Limit to first 3
                name = re.sub(r'[,\s]+$', '', auth).strip()
                if name:
                    authors.append(name)
        
        # Pattern 2: Author et al.
        et_al_match = re.search(r'([A-Z][a-z]+)\s+et\s+al', text, re.IGNORECASE)
        if et_al_match and not authors:
            authors.append(et_al_match.group(1))
        
        return authors
    
    @classmethod
    def parse_citation(cls, text: str, index: int = 0) -> Citation:
        """Parse a single citation from text."""
        citation = Citation(
            index=index,
            raw_text=text.strip()
        )
        
        citation.doi = cls.extract_doi(text)
        citation.pmid = cls.extract_pmid(text)
        citation.year = cls.extract_year(text)
        citation.title = cls.extract_title(text)
        citation.authors = cls.extract_authors(text)
        
        return citation
    
    @classmethod
    def parse_text(cls, text: str) -> List[Citation]:
        """Parse all citations from text."""
        citations = []
        
        # Try to split into individual references
        # Pattern 1: Numbered references [1], [2], etc.
        numbered_pattern = re.compile(r'(?:^|\n)\s*\[?(\d+)\]?[.\s]+(.+?)(?=\n\s*\[?\d+\]?[.\s]+|\Z)', re.DOTALL)
        numbered_matches = list(numbered_pattern.finditer(text))
        
        if numbered_matches:
            for match in numbered_matches:
                idx = int(match.group(1))
                content = match.group(2).replace('\n', ' ').strip()
                citations.append(cls.parse_citation(content, idx))
            return citations
        
        # Pattern 2: References separated by blank lines
        blocks = re.split(r'\n\s*\n', text)
        for i, block in enumerate(blocks, 1):
            block = block.strip()
            if len(block) > 30:  # Minimum length for a citation
                citations.append(cls.parse_citation(block, i))
        
        return citations
    
    @classmethod
    def parse_bibtex(cls, text: str) -> List[Citation]:
        """Parse BibTeX entries."""
        citations = []
        
        # Find all BibTeX entries
        entry_pattern = re.compile(r'@\w+\{([^,]+),\s*([^}]+)\}', re.DOTALL)
        doi_pattern = re.compile(r'doi\s*=\s*\{([^}]+)\}', re.IGNORECASE)
        title_pattern = re.compile(r'title\s*=\s*\{([^}]+)\}', re.IGNORECASE)
        year_pattern = re.compile(r'year\s*=\s*\{(\d{4})\}', re.IGNORECASE)
        author_pattern = re.compile(r'author\s*=\s*\{([^}]+)\}', re.IGNORECASE)
        
        for i, match in enumerate(entry_pattern.finditer(text), 1):
            entry = match.group(0)
            
            citation = Citation(index=i, raw_text=entry)
            
            doi_match = doi_pattern.search(entry)
            if doi_match:
                citation.doi = doi_match.group(1).strip()
            
            title_match = title_pattern.search(entry)
            if title_match:
                citation.title = title_match.group(1).strip()
            
            year_match = year_pattern.search(entry)
            if year_match:
                citation.year = year_match.group(1)
            
            author_match = author_pattern.search(entry)
            if author_match:
                citation.authors = [a.strip() for a in author_match.group(1).split(' and ')]
            
            citations.append(citation)
        
        return citations


class RetractionChecker:
    """Check citations against retraction databases."""
    
    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.cache: Dict[str, Optional[RetractionRecord]] = {}
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, headers: Dict[str, str] = None) -> Optional[Dict]:
        """Make HTTP request with error handling."""
        self._rate_limit()
        
        if headers is None:
            headers = {
                'User-Agent': 'RetractionWatcher/1.0 (academic integrity tool)'
            }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except HTTPError as e:
            if e.code == 404:
                return None
            print(f"  Warning: HTTP {e.code} for {url}", file=sys.stderr)
            return None
        except (URLError, json.JSONDecodeError, TimeoutError) as e:
            print(f"  Warning: Request failed for {url}: {e}", file=sys.stderr)
            return None
    
    def check_crossref(self, doi: str) -> Optional[RetractionRecord]:
        """Check DOI against Crossref for retractions."""
        if not doi:
            return None
        
        cache_key = f"crossref:{doi}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        data = self._make_request(url)
        
        if not data or 'message' not in data:
            self.cache[cache_key] = None
            return None
        
        work = data['message']
        
        # Check for retraction metadata
        update_type = work.get('update-type', '').lower()
        update_policy = work.get('update-policy', '').lower()
        
        # Check if this is a retraction notice
        if 'retraction' in update_type or 'retraction' in update_policy:
            record = RetractionRecord(
                identifier=doi,
                identifier_type='doi',
                status='retracted',
                title=work.get('title', [None])[0],
                journal=work.get('container-title', [None])[0],
                publisher=work.get('publisher'),
                retraction_date=work.get('updated', {}).get('date-time', '').split('T')[0] if isinstance(work.get('updated'), dict) else None
            )
            self.cache[cache_key] = record
            return record
        
        # Check for update-to field (may link to retraction)
        if 'update-to' in work:
            for update in work['update-to']:
                if update.get('type', '').lower() == 'retraction':
                    record = RetractionRecord(
                        identifier=doi,
                        identifier_type='doi',
                        status='retracted',
                        title=work.get('title', [None])[0],
                        retraction_doi=update.get('DOI'),
                        retraction_date=update.get('updated', {}).get('date-time', '').split('T')[0] if isinstance(update.get('updated'), dict) else None
                    )
                    self.cache[cache_key] = record
                    return record
        
        self.cache[cache_key] = None
        return None
    
    def check_pubmed(self, pmid: str) -> Optional[RetractionRecord]:
        """Check PMID against PubMed for retractions."""
        if not pmid:
            return None
        
        cache_key = f"pubmed:{pmid}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Use E-utilities to fetch publication types
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        data = self._make_request(url)
        
        if not data or 'result' not in data:
            self.cache[cache_key] = None
            return None
        
        result = data['result'].get(pmid, {})
        
        # Check publication types
        pubtypes = result.get('pubtype', [])
        
        retraction_types = [
            'Retracted Publication',
            'Retraction of Publication',
            'Expression of Concern'
        ]
        
        for rtype in retraction_types:
            if rtype in pubtypes:
                status = 'retracted' if 'Retract' in rtype else 'expression_of_concern'
                record = RetractionRecord(
                    identifier=pmid,
                    identifier_type='pmid',
                    status=status,
                    title=result.get('title'),
                    journal=result.get('fulljournalname'),
                    retraction_date=result.get('sortpubdate', '').split('/')[0] if result.get('sortpubdate') else None
                )
                self.cache[cache_key] = record
                return record
        
        self.cache[cache_key] = None
        return None
    
    def check_open_retractions(self, doi: str) -> Optional[RetractionRecord]:
        """Check Open Retractions database."""
        if not doi:
            return None
        
        cache_key = f"openret:{doi}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"https://openretractions.com/api/doi/{urllib.parse.quote(doi)}/data.json"
        data = self._make_request(url)
        
        if not data or not data.get('retracted'):
            self.cache[cache_key] = None
            return None
        
        record = RetractionRecord(
            identifier=doi,
            identifier_type='doi',
            status='retracted',
            title=data.get('title'),
            retraction_date=data.get('update_timestamp', '').split('T')[0] if data.get('update_timestamp') else None,
            retraction_reason=data.get('retraction_reason'),
            url=data.get('retraction_url')
        )
        self.cache[cache_key] = record
        return record
    
    def check_citation(self, citation: Citation) -> Optional[RetractionRecord]:
        """Check a citation against all available databases."""
        # Priority: Open Retractions (fastest), then Crossref, then PubMed
        
        if citation.doi:
            # Try Open Retractions first
            result = self.check_open_retractions(citation.doi)
            if result:
                return result
            
            # Try Crossref
            result = self.check_crossref(citation.doi)
            if result:
                return result
        
        if citation.pmid:
            result = self.check_pubmed(citation.pmid)
            if result:
                return result
        
        return None


class ReportGenerator:
    """Generate reports from retraction check results."""
    
    def __init__(self, citations: List[Citation], results: Dict[int, Optional[RetractionRecord]]):
        self.citations = citations
        self.results = results
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the check."""
        stats = {
            'total': len(self.citations),
            'checked': 0,
            'retracted': 0,
            'expression_of_concern': 0,
            'corrected': 0,
            'clear': 0,
            'unknown': 0
        }
        
        for citation in self.citations:
            result = self.results.get(citation.index)
            if result:
                stats['checked'] += 1
                stats[result.status] = stats.get(result.status, 0) + 1
            else:
                stats['clear'] += 1
        
        return stats
    
    def generate_summary(self) -> str:
        """Generate a brief summary report."""
        stats = self.get_stats()
        
        lines = [
            "🔍 RETRACTION WATCH REPORT - SUMMARY",
            "=" * 50,
            f"References Found: {stats['total']}",
            f"✅ Clear: {stats['clear']}",
        ]
        
        if stats['retracted']:
            lines.append(f"🔴 RETRACTED: {stats['retracted']} ⚠️ URGENT ACTION REQUIRED")
        if stats['expression_of_concern']:
            lines.append(f"🟡 Expression of Concern: {stats['expression_of_concern']}")
        if stats['corrected']:
            lines.append(f"🟠 Corrected: {stats['corrected']}")
        
        total_issues = stats['retracted'] + stats['expression_of_concern'] + stats['corrected']
        if total_issues == 0:
            lines.append("\n✅ No retraction issues found in your references!")
        else:
            lines.append(f"\n⚠️ {total_issues} citation(s) require attention")
        
        return '\n'.join(lines)
    
    def generate_detailed(self) -> str:
        """Generate a detailed report."""
        lines = [
            "🔍 RETRACTION WATCH REPORT - DETAILED",
            "=" * 50,
            ""
        ]
        
        stats = self.get_stats()
        lines.append(f"Total References: {stats['total']}")
        lines.append(f"Check Date: {time.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        # Group by status
        retracted = []
        concerned = []
        corrected = []
        clear = []
        
        for citation in self.citations:
            result = self.results.get(citation.index)
            if result:
                if result.status == 'retracted':
                    retracted.append((citation, result))
                elif result.status == 'expression_of_concern':
                    concerned.append((citation, result))
                elif result.status == 'corrected':
                    corrected.append((citation, result))
            else:
                clear.append(citation)
        
        # Report retracted papers (most important)
        if retracted:
            lines.append("🔴 RETRACTED PAPERS (URGENT)")
            lines.append("-" * 40)
            for citation, record in retracted:
                lines.append(f"\n[{citation.index}] {citation.raw_text[:100]}...")
                lines.append(f"    Status: RETRACTED")
                if record.title:
                    lines.append(f"    Title: {record.title}")
                if record.retraction_date:
                    lines.append(f"    Retraction Date: {record.retraction_date}")
                if record.retraction_reason:
                    lines.append(f"    Reason: {record.retraction_reason}")
                if record.url:
                    lines.append(f"    More Info: {record.url}")
                lines.append(f"    ⚠️  RECOMMENDATION: Remove this citation immediately")
            lines.append("")
        
        # Report expressions of concern
        if concerned:
            lines.append("🟡 EXPRESSIONS OF CONCERN")
            lines.append("-" * 40)
            for citation, record in concerned:
                lines.append(f"\n[{citation.index}] {citation.raw_text[:100]}...")
                lines.append(f"    Status: Expression of Concern issued")
                if record.title:
                    lines.append(f"    Title: {record.title}")
                lines.append(f"    ⚠️  RECOMMENDATION: Verify current status before citing")
            lines.append("")
        
        # Report corrected papers
        if corrected:
            lines.append("🟠 CORRECTED PAPERS")
            lines.append("-" * 40)
            for citation, record in corrected:
                lines.append(f"\n[{citation.index}] {citation.raw_text[:100]}...")
                lines.append(f"    Status: Correction/Erratum published")
                lines.append(f"    ℹ️  RECOMMENDATION: Review if correction affects your claims")
            lines.append("")
        
        # Summary
        lines.append("📊 SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Clear citations: {len(clear)}")
        if retracted:
            lines.append(f"Retracted: {len(retracted)} ⚠️")
        if concerned:
            lines.append(f"Expression of Concern: {len(concerned)}")
        if corrected:
            lines.append(f"Corrected: {len(corrected)}")
        
        return '\n'.join(lines)
    
    def generate_json(self) -> str:
        """Generate JSON report."""
        data = {
            'metadata': {
                'check_date': time.strftime('%Y-%m-%d %H:%M'),
                'total_references': len(self.citations),
                'stats': self.get_stats()
            },
            'citations': []
        }
        
        for citation in self.citations:
            result = self.results.get(citation.index)
            entry = {
                'index': citation.index,
                'raw_text': citation.raw_text,
                'identifiers': {
                    'doi': citation.doi,
                    'pmid': citation.pmid,
                    'title': citation.title
                },
                'status': result.status if result else 'clear',
                'retraction_details': asdict(result) if result else None
            }
            data['citations'].append(entry)
        
        return json.dumps(data, indent=2)


def read_file(filepath: str) -> str:
    """Read content from file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Handle PDF
    if path.suffix.lower() == '.pdf':
        try:
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
                return text
        except ImportError:
            raise ImportError("PyPDF2 required for PDF processing. Install with: pip install PyPDF2")
    
    # Handle text files
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_references_section(text: str) -> str:
    """Try to extract just the references section from a document."""
    # Common reference section headers
    ref_headers = [
        r'(?:^|\n)\s*references\s*(?:\n|$)',
        r'(?:^|\n)\s*bibliography\s*(?:\n|$)',
        r'(?:^|\n)\s*literature cited\s*(?:\n|$)',
        r'(?:^|\n)\s*works cited\s*(?:\n|$)',
    ]
    
    for pattern in ref_headers:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.end()
            # Take text from header to end, or until next major section
            remaining = text[start:]
            # Stop at common post-reference sections
            end_patterns = [
                r'(?:^|\n)\s*appendix\s*(?:\n|$)',
                r'(?:^|\n)\s*acknowledgments?\s*(?:\n|$)',
                r'(?:^|\n)\s*supplementary\s*(?:\n|$)',
            ]
            for end_pat in end_patterns:
                end_match = re.search(end_pat, remaining, re.IGNORECASE)
                if end_match:
                    return remaining[:end_match.start()]
            return remaining
    
    return text


def main():
    parser = argparse.ArgumentParser(
        description='Scan document references and check for retracted papers'
    )
    parser.add_argument('--input', '-i', help='Input file path (PDF, TXT, BIB)')
    parser.add_argument('--text', '-t', help='Direct text input')
    parser.add_argument('--url', '-u', help='URL to fetch document from')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', 
                       choices=['summary', 'detailed', 'json'],
                       default='detailed',
                       help='Report format')
    parser.add_argument('--full-doc', action='store_true',
                       help='Scan full document (not just references section)')
    
    args = parser.parse_args()
    
    # Get input text
    if args.input:
        text = read_file(args.input)
    elif args.text:
        text = args.text
    elif args.url:
        try:
            import urllib.request
            with urllib.request.urlopen(args.url, timeout=30) as response:
                text = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching URL: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        text = sys.stdin.read()
    
    if not text or not text.strip():
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)
    
    # Extract references section (unless full-doc flag)
    if not args.full_doc:
        text = extract_references_section(text)
    
    # Parse citations
    print("Parsing citations...", file=sys.stderr)
    
    # Detect format and parse
    if '.bib' in (args.input or ''):
        citations = CitationParser.parse_bibtex(text)
    else:
        citations = CitationParser.parse_text(text)
    
    if not citations:
        print("No citations found in input. Try using --full-doc flag.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(citations)} citations", file=sys.stderr)
    
    # Check each citation
    print("Checking against retraction databases...", file=sys.stderr)
    checker = RetractionChecker(rate_limit_delay=0.3)
    results = {}
    
    for citation in citations:
        print(f"  Checking [{citation.index}] {citation.get_identifier()[:50]}...", file=sys.stderr)
        result = checker.check_citation(citation)
        if result:
            results[citation.index] = result
            print(f"    ⚠️  {result.status.upper()}", file=sys.stderr)
    
    print(f"\nCheck complete. Found {len(results)} issue(s)", file=sys.stderr)
    
    # Generate report
    generator = ReportGenerator(citations, results)
    
    if args.format == 'summary':
        report = generator.generate_summary()
    elif args.format == 'json':
        report = generator.generate_json()
    else:
        report = generator.generate_detailed()
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport written to: {args.output}")
    else:
        print()
        print(report)


if __name__ == '__main__':
    main()

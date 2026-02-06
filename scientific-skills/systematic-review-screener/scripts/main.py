#!/usr/bin/env python3
"""
Systematic Review Abstract Screener
Automated screening of academic abstracts against inclusion/exclusion criteria.
Supports PRISMA workflow and generates screening reports.

Technical Difficulty: High - Manual verification required for final decisions.
"""

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml


@dataclass
class ScreeningResult:
    """Result of screening a single reference."""
    record_id: str
    title: str
    abstract: str
    authors: str = ""
    year: str = ""
    doi: str = ""
    pmid: str = ""
    
    # Screening outcomes
    include: bool = False
    confidence: float = 0.0
    decision_rationale: List[str] = field(default_factory=list)
    matched_criteria: Dict[str, Any] = field(default_factory=dict)
    exclusion_reasons: List[str] = field(default_factory=list)
    requires_review: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PRISMAData:
    """PRISMA 2020 flow diagram data structure."""
    identification: Dict[str, int] = field(default_factory=lambda: {
        "database_results": 0,
        "register_results": 0,
        "other_sources": 0,
        "duplicates_removed": 0
    })
    screening: Dict[str, int] = field(default_factory=lambda: {
        "records_screened": 0,
        "records_excluded": 0,
        "full_text_assessed": 0,
        "full_text_excluded": 0
    })
    included: Dict[str, int] = field(default_factory=lambda: {
        "qualitative_synthesis": 0,
        "quantitative_synthesis": 0
    })
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CriteriaMatcher:
    """Matches abstracts against inclusion/exclusion criteria."""
    
    def __init__(self, criteria: Dict[str, Any]):
        self.criteria = criteria
        self.confidence_threshold = criteria.get('confidence_threshold', 0.75)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        return text.lower().strip()
    
    def _fuzzy_match(self, text: str, keywords: List[str]) -> Tuple[bool, List[str], float]:
        """
        Check if any keywords appear in text.
        Returns: (matched, matched_keywords, confidence_score)
        """
        text_lower = self._normalize_text(text)
        matched = []
        total_score = 0.0
        
        for keyword in keywords:
            keyword_lower = self._normalize_text(keyword)
            
            # Exact match
            if keyword_lower in text_lower:
                matched.append(keyword)
                total_score += 1.0
            # Word boundary match
            elif re.search(r'\b' + re.escape(keyword_lower) + r'\b', text_lower):
                matched.append(keyword)
                total_score += 0.9
            # Fuzzy match (contains substring)
            elif keyword_lower.replace(' ', '') in text_lower.replace(' ', ''):
                matched.append(keyword)
                total_score += 0.7
        
        confidence = min(1.0, total_score / max(1, len(keywords))) if keywords else 0.0
        return len(matched) > 0, matched, confidence
    
    def screen(self, reference: Dict[str, str]) -> ScreeningResult:
        """
        Screen a single reference against criteria.
        
        Args:
            reference: Dictionary with title, abstract, and metadata
            
        Returns:
            ScreeningResult with decision and rationale
        """
        title = reference.get('title', '')
        abstract = reference.get('abstract', '')
        full_text = f"{title} {abstract}"
        
        result = ScreeningResult(
            record_id=reference.get('record_id', ''),
            title=title,
            abstract=abstract,
            authors=reference.get('authors', ''),
            year=reference.get('year', ''),
            doi=reference.get('doi', ''),
            pmid=reference.get('pmid', '')
        )
        
        exclusion_confidence = 0.0
        inclusion_confidence = 0.0
        
        # Check exclusion criteria first (hard exclusions)
        if 'study_type' in self.criteria:
            exclude_types = self.criteria['study_type'].get('exclude', [])
            matched, keywords, conf = self._fuzzy_match(full_text, exclude_types)
            if matched:
                result.exclude = True
                result.exclusion_reasons.append(f"Excluded study type: {', '.join(keywords)}")
                exclusion_confidence = max(exclusion_confidence, conf)
        
        # Check population exclusions
        if 'population' in self.criteria:
            exclude_pop = self.criteria['population'].get('exclude_keywords', [])
            matched, keywords, conf = self._fuzzy_match(full_text, exclude_pop)
            if matched:
                result.exclude = True
                result.exclusion_reasons.append(f"Excluded population: {', '.join(keywords)}")
                exclusion_confidence = max(exclusion_confidence, conf)
        
        # Check year range
        if 'year_range' in self.criteria and result.year:
            try:
                year = int(result.year)
                year_min = self.criteria['year_range'].get('min', 1900)
                year_max = self.criteria['year_range'].get('max', 2100)
                if year < year_min or year > year_max:
                    result.exclude = True
                    result.exclusion_reasons.append(f"Year {year} outside range [{year_min}-{year_max}]")
                    exclusion_confidence = 1.0
            except ValueError:
                pass
        
        # Check language
        if 'language' in self.criteria:
            allowed = self.criteria['language'].get('allowed', [])
            # Simple language detection from abstract
            lang_conf = self._detect_language_confidence(abstract)
            if allowed and lang_conf < 0.5:
                result.exclude = True
                result.exclusion_reasons.append(f"Language not in allowed list: {allowed}")
        
        # Check inclusion criteria (if not already excluded)
        if not result.exclusion_reasons:
            inclusion_scores = []
            
            # Study type inclusion
            if 'study_type' in self.criteria:
                include_types = self.criteria['study_type'].get('include', [])
                matched, keywords, conf = self._fuzzy_match(full_text, include_types)
                if matched:
                    result.matched_criteria['study_type'] = keywords
                    inclusion_scores.append(conf)
                    result.decision_rationale.append(f"Matched study types: {', '.join(keywords)}")
            
            # Population inclusion
            if 'population' in self.criteria:
                include_pop = self.criteria['population'].get('include_keywords', [])
                matched, keywords, conf = self._fuzzy_match(full_text, include_pop)
                if matched:
                    result.matched_criteria['population'] = keywords
                    inclusion_scores.append(conf)
                    result.decision_rationale.append(f"Matched population: {', '.join(keywords)}")
            
            # Intervention required
            if 'intervention' in self.criteria:
                required = self.criteria['intervention'].get('required', [])
                matched, keywords, conf = self._fuzzy_match(full_text, required)
                if matched:
                    result.matched_criteria['intervention'] = keywords
                    inclusion_scores.append(conf)
                    result.decision_rationale.append(f"Matched intervention: {', '.join(keywords)}")
                else:
                    # Missing required intervention
                    result.decision_rationale.append("No required intervention keywords found")
                    inclusion_scores.append(0.0)
            
            # Calculate overall confidence
            if inclusion_scores:
                inclusion_confidence = sum(inclusion_scores) / len(inclusion_scores)
            else:
                inclusion_confidence = 0.5  # Neutral if no criteria
            
            # Decision: include if reasonable confidence and no exclusions
            result.include = inclusion_confidence >= self.confidence_threshold
        
        # Final confidence calculation
        if result.exclusion_reasons:
            result.confidence = exclusion_confidence
            result.include = False
        else:
            result.confidence = inclusion_confidence
        
        # Flag for manual review if confidence below threshold
        if result.confidence < self.confidence_threshold:
            result.requires_review = True
        
        return result
    
    def _detect_language_confidence(self, text: str) -> float:
        """Simple heuristic for English language confidence."""
        if not text:
            return 0.0
        
        # Common English words check
        english_indicators = ['the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for', 'with']
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return 0.0
        
        indicator_count = sum(1 for word in words if word in english_indicators)
        return min(1.0, indicator_count / max(1, len(words) * 0.1))


class ReferenceParser:
    """Parse references from various input formats."""
    
    @staticmethod
    def parse_csv(filepath: Path) -> List[Dict[str, str]]:
        """Parse CSV or TSV file."""
        records = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            # Detect delimiter
            sample = f.read(1024)
            f.seek(0)
            delimiter = '\t' if '\t' in sample else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for idx, row in enumerate(reader):
                record = {
                    'record_id': str(idx),
                    'title': row.get('title', ''),
                    'abstract': row.get('abstract', ''),
                    'authors': row.get('authors', ''),
                    'year': row.get('year', ''),
                    'doi': row.get('doi', ''),
                    'pmid': row.get('pmid', '')
                }
                records.append(record)
        return records
    
    @staticmethod
    def parse_pubmed(filepath: Path) -> List[Dict[str, str]]:
        """Parse PubMed MEDLINE format."""
        records = []
        current_record = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()
                
                if line.startswith('PMID-'):
                    if current_record:
                        current_record['record_id'] = current_record.get('pmid', '')
                        records.append(current_record)
                    current_record = {'pmid': line[6:].strip()}
                elif line.startswith('TI  -'):
                    current_record['title'] = line[6:].strip()
                elif line.startswith('AB  -'):
                    current_record['abstract'] = line[6:].strip()
                elif line.startswith('AU  -'):
                    authors = current_record.get('authors', '')
                    current_record['authors'] = authors + line[6:].strip() + '; ' if authors else line[6:].strip()
                elif line.startswith('DP  -'):
                    year_match = re.search(r'(\d{4})', line[6:])
                    if year_match:
                        current_record['year'] = year_match.group(1)
                elif line.startswith('LID -') and '[doi]' in line:
                    doi_match = re.search(r'(10\.\S+)', line)
                    if doi_match:
                        current_record['doi'] = doi_match.group(1)
                elif line.startswith('      ') and current_record.get('abstract'):
                    # Continuation of abstract
                    current_record['abstract'] += ' ' + line.strip()
                elif line.startswith('      ') and current_record.get('title'):
                    # Continuation of title
                    current_record['title'] += ' ' + line.strip()
            
            # Add last record
            if current_record:
                current_record['record_id'] = current_record.get('pmid', '')
                records.append(current_record)
        
        return records
    
    @staticmethod
    def parse_endnote(filepath: Path) -> List[Dict[str, str]]:
        """Parse EndNote XML format."""
        records = []
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        for idx, record in enumerate(root.findall('.//record')):
            rec = {'record_id': str(idx)}
            
            # Title
            title_elem = record.find('.//titles/title/style')
            if title_elem is not None:
                rec['title'] = title_elem.text or ''
            
            # Abstract
            abstract_elem = record.find('.//abstract/style')
            if abstract_elem is not None:
                rec['abstract'] = abstract_elem.text or ''
            
            # Authors
            authors = []
            for author in record.findall('.//contributors/authors/author/style'):
                if author.text:
                    authors.append(author.text)
            rec['authors'] = '; '.join(authors)
            
            # Year
            year_elem = record.find('.//dates/year/style')
            if year_elem is not None and year_elem.text:
                rec['year'] = year_elem.text
            
            # DOI
            doi_elem = record.find('.//electronic-resource-num/style')
            if doi_elem is not None and doi_elem.text:
                rec['doi'] = doi_elem.text
            
            records.append(rec)
        
        return records


class ReportGenerator:
    """Generate screening reports in various formats."""
    
    @staticmethod
    def generate_prisma_data(results: List[ScreeningResult]) -> PRISMAData:
        """Generate PRISMA 2020 flow diagram data."""
        data = PRISMAData()
        
        total = len(results)
        included = sum(1 for r in results if r.include and not r.requires_review)
        excluded = sum(1 for r in results if not r.include and not r.requires_review)
        conflicts = sum(1 for r in results if r.requires_review)
        
        data.identification['database_results'] = total
        data.screening['records_screened'] = total
        data.screening['records_excluded'] = excluded
        data.included['qualitative_synthesis'] = included
        
        return data
    
    @staticmethod
    def save_csv(results: List[ScreeningResult], filepath: Path):
        """Save results to CSV."""
        if not results:
            return
        
        fieldnames = ['record_id', 'title', 'authors', 'year', 'doi', 'pmid', 
                     'include', 'confidence', 'requires_review', 
                     'decision_rationale', 'exclusion_reasons', 'matched_criteria']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                row = r.to_dict()
                # Convert lists/dicts to strings for CSV
                row['decision_rationale'] = '|'.join(row['decision_rationale'])
                row['exclusion_reasons'] = '|'.join(row['exclusion_reasons'])
                row['matched_criteria'] = json.dumps(row['matched_criteria'])
                writer.writerow(row)
    
    @staticmethod
    def save_json(results: List[ScreeningResult], filepath: Path):
        """Save results to JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
    
    @staticmethod
    def save_screening_log(results: List[ScreeningResult], prisma_data: PRISMAData, filepath: Path):
        """Save complete screening log with PRISMA data."""
        log = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(results),
            'included': sum(1 for r in results if r.include),
            'excluded': sum(1 for r in results if not r.include),
            'conflicts': sum(1 for r in results if r.requires_review),
            'prisma_data': prisma_data.to_dict(),
            'records': [r.to_dict() for r in results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Systematic Review Abstract Screener',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input references.csv --criteria criteria.yaml
  %(prog)s --input refs.xml --criteria criteria.yaml --output results/ --prisma
  %(prog)s --input refs.txt --criteria criteria.yaml --threshold 0.8 --conflict-only
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Input file (CSV, TSV, PubMed .txt, EndNote .xml)')
    parser.add_argument('--criteria', '-c', required=True,
                       help='Criteria YAML configuration file')
    parser.add_argument('--output', '-o', default='./output',
                       help='Output directory (default: ./output)')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'excel'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--threshold', '-t', type=float, default=0.75,
                       help='Confidence threshold (default: 0.75)')
    parser.add_argument('--prisma', '-p', action='store_true',
                       help='Generate PRISMA flow diagram data')
    parser.add_argument('--conflict-only', action='store_true',
                       help='Export only conflicts requiring review')
    parser.add_argument('--batch-size', '-b', type=int, default=100,
                       help='Processing batch size (default: 100)')
    
    return parser.parse_args()


def load_criteria(filepath: Path) -> Dict[str, Any]:
    """Load criteria from YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def detect_file_format(filepath: Path) -> str:
    """Detect input file format from extension and content."""
    suffix = filepath.suffix.lower()
    
    if suffix in ['.csv']:
        return 'csv'
    elif suffix in ['.tsv']:
        return 'tsv'
    elif suffix in ['.xml']:
        return 'xml'
    elif suffix in ['.txt']:
        # Check if PubMed format
        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            if 'PMID-' in sample:
                return 'pubmed'
    
    # Default to CSV
    return 'csv'


def main():
    """Main entry point."""
    args = parse_arguments()
    
    input_path = Path(args.input)
    criteria_path = Path(args.criteria)
    output_dir = Path(args.output)
    
    # Validate inputs
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if not criteria_path.exists():
        print(f"Error: Criteria file not found: {criteria_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load criteria
    print(f"Loading criteria from {criteria_path}...")
    criteria = load_criteria(criteria_path)
    criteria['confidence_threshold'] = args.threshold
    
    # Detect and parse input format
    file_format = detect_file_format(input_path)
    print(f"Detected format: {file_format}")
    
    print(f"Parsing references from {input_path}...")
    if file_format == 'pubmed':
        references = ReferenceParser.parse_pubmed(input_path)
    elif file_format == 'xml':
        references = ReferenceParser.parse_endnote(input_path)
    else:
        references = ReferenceParser.parse_csv(input_path)
    
    print(f"Loaded {len(references)} references")
    
    if not references:
        print("No references found. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    # Initialize screener
    matcher = CriteriaMatcher(criteria)
    
    # Process references
    print("Screening references...")
    results = []
    for i in range(0, len(references), args.batch_size):
        batch = references[i:i + args.batch_size]
        for ref in batch:
            result = matcher.screen(ref)
            results.append(result)
        
        if (i // args.batch_size + 1) % 10 == 0:
            print(f"  Processed {min(i + args.batch_size, len(references))}/{len(references)}...")
    
    print(f"Screening complete. {len(results)} records processed.")
    
    # Filter if conflict-only
    if args.conflict_only:
        results = [r for r in results if r.requires_review]
        print(f"Filtered to {len(results)} conflicts requiring review")
    
    # Generate PRISMA data if requested
    prisma_data = None
    if args.prisma:
        prisma_data = ReportGenerator.generate_prisma_data(results)
        prisma_path = output_dir / 'prisma_data.json'
        with open(prisma_path, 'w') as f:
            json.dump(prisma_data.to_dict(), f, indent=2)
        print(f"PRISMA data saved to {prisma_path}")
    
    # Split results
    included = [r for r in results if r.include and not r.requires_review]
    excluded = [r for r in results if not r.include and not r.requires_review]
    conflicts = [r for r in results if r.requires_review]
    
    # Save results
    print("\nSaving results...")
    
    if args.format == 'csv':
        if not args.conflict_only:
            ReportGenerator.save_csv(included, output_dir / 'screened_included.csv')
            ReportGenerator.save_csv(excluded, output_dir / 'screened_excluded.csv')
        ReportGenerator.save_csv(conflicts, output_dir / 'conflicts.csv')
    else:
        if not args.conflict_only:
            ReportGenerator.save_json(included, output_dir / 'screened_included.json')
            ReportGenerator.save_json(excluded, output_dir / 'screened_excluded.json')
        ReportGenerator.save_json(conflicts, output_dir / 'conflicts.json')
    
    # Save screening log
    if prisma_data is None:
        prisma_data = ReportGenerator.generate_prisma_data(results)
    ReportGenerator.save_screening_log(results, prisma_data, output_dir / 'screening_log.json')
    
    # Print summary
    print("\n" + "=" * 50)
    print("SCREENING SUMMARY")
    print("=" * 50)
    print(f"Total records:      {len(results)}")
    print(f"Included:           {len(included)} ({100*len(included)/len(results):.1f}%)")
    print(f"Excluded:           {len(excluded)} ({100*len(excluded)/len(results):.1f}%)")
    print(f"Conflicts (review): {len(conflicts)} ({100*len(conflicts)/len(results):.1f}%)")
    print("=" * 50)
    print(f"\nResults saved to: {output_dir}")
    
    if conflicts:
        print(f"\n⚠️  {len(conflicts)} records require manual review.")
        print(f"   Check: {output_dir}/conflicts.{args.format}")
    
    print("\n⚠️  IMPORTANT: This tool provides screening recommendations.")
    print("   Final inclusion decisions must be verified by human reviewers.")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Citation Formatter - Converts various citation formats to AMA style.
AMA 11th Edition standards.
"""

import re
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List


def parse_name(name_str: str) -> Dict[str, str]:
    """Parse author name into components."""
    name_str = name_str.strip()
    
    # Last, First M. format
    if ',' in name_str:
        parts = name_str.split(',')
        last = parts[0].strip()
        rest = parts[1].strip()
        first_middle = rest.split()
        first = first_middle[0] if first_middle else ''
        middle = first_middle[1] if len(first_middle) > 1 else ''
        return {'last': last, 'first': first, 'middle': middle}
    
    # First M. Last format (handles middle initial too)
    parts = name_str.split()
    if len(parts) == 1:
        return {'last': parts[0], 'first': '', 'middle': ''}
    elif len(parts) == 2:
        return {'last': parts[1], 'first': parts[0], 'middle': ''}
    else:
        # Check if middle part is initial (single letter or letter with period)
        if len(parts) >= 3:
            # First M Last or First Middle Last
            first = parts[0]
            last = parts[-1]
            # Everything in between is middle
            middle = ' '.join(parts[1:-1])
            return {'last': last, 'first': first, 'middle': middle}
        return {'last': parts[-1], 'first': parts[0], 'middle': ' '.join(parts[1:-1])}


def format_author_ama(name_dict: Dict[str, str]) -> str:
    """Format author name in AMA style: Lastname FM"""
    last = name_dict.get('last', '')
    first = name_dict.get('first', '')
    middle = name_dict.get('middle', '')
    
    initials = ''
    if first:
        initials += first[0].upper()
    if middle:
        # Take first letter of each middle name part
        for part in middle.split():
            if part:
                initials += part[0].upper()
    
    if initials:
        return f"{last} {initials}"
    return last


def detect_format(citation: str) -> str:
    """Detect the input citation format."""
    citation = citation.strip()
    
    # BibTeX
    if citation.startswith('@'):
        return 'bibtex'
    
    # Vancouver - numbered with periods OR Year;Vol(Issue):Pages pattern
    if re.match(r'^\d+\.\s', citation) or re.search(r'\d{4};\d+\(\d+\):\d', citation):
        return 'vancouver'
    
    # MLA - typically has "Print" or database name at end
    if 'Print.' in citation or re.search(r'\w+\s+\d+,\s+\d{4}\.\s+\w+\.', citation):
        return 'mla'
    
    # APA - year in parentheses
    if re.search(r'\(\d{4}[a-z]?\)', citation):
        return 'apa'
    
    return 'unknown'


def parse_apa(citation: str) -> Dict[str, Any]:
    """Parse APA format citation."""
    result = {'type': 'journal', 'authors': [], 'title': '', 'journal': '', 
              'year': '', 'volume': '', 'issue': '', 'pages': '', 'doi': ''}
    
    # Authors (before year) - handle "&" before year
    # Pattern: Author, A. A., Author, B. B., & Author, C. C. (Year)
    author_year_match = re.match(r'^(.+?)\s*\(\s*(\d{4})[a-z]?\s*\)', citation, re.DOTALL)
    if author_year_match:
        authors_str = author_year_match.group(1).strip()
        result['year'] = author_year_match.group(2)
        
        # Remove trailing punctuation from authors
        authors_str = re.sub(r'[,\s]+$', '', authors_str)
        
        # Split by commas, but handle the & or "and" before last author
        # Replace & with comma for easier splitting
        authors_str = authors_str.replace(' & ', ', ').replace(' and ', ', ')
        
        # Split by comma and parse each author
        author_parts = [p.strip() for p in authors_str.split(',') if p.strip()]
        
        # APA format: Last, F. M. - pairs of (Last, Initials)
        i = 0
        while i < len(author_parts):
            if i + 1 < len(author_parts):
                last = author_parts[i]
                initials = author_parts[i + 1]
                result['authors'].append({'last': last, 'first': initials, 'middle': ''})
                i += 2
            else:
                # Single part, try to parse
                result['authors'].append(parse_name(author_parts[i]))
                i += 1
    
    # Title (after year) - look for period then title then period
    # Find year end position
    year_end = citation.find(').')
    if year_end > 0:
        after_year = citation[year_end + 2:]
        # Title is typically the next sentence before the journal name
        title_match = re.match(r'\s*([^\.]+)\.\s*([A-Z][^\d\.]+)', after_year)
        if title_match:
            result['title'] = title_match.group(1).strip()
            result['journal'] = title_match.group(2).strip()
    
    # Journal, volume, issue, pages
    # Pattern: Journal, Vol(Issue), pages
    journal_pattern = r'([A-Z][^.]+?)\.?\s*(\d+)\s*\(\s*(\d+)\s*\),?\s*([\d\-–]+)'
    journal_match = re.search(journal_pattern, citation)
    if journal_match:
        if not result['journal']:
            result['journal'] = journal_match.group(1).strip()
        result['volume'] = journal_match.group(2)
        result['issue'] = journal_match.group(3)
        result['pages'] = journal_match.group(4)
    
    # DOI
    doi_match = re.search(r'doi[.:]?\s*(?:https?://doi\.org/)?(10\.\S+)', citation, re.IGNORECASE)
    if doi_match:
        result['doi'] = doi_match.group(1)
    
    return result


def parse_mla(citation: str) -> Dict[str, Any]:
    """Parse MLA format citation."""
    result = {'type': 'journal', 'authors': [], 'title': '', 'journal': '', 
              'year': '', 'volume': '', 'issue': '', 'pages': '', 'doi': ''}
    
    # MLA: Author. "Title." Journal, vol. X, no. Y, Year, pp. Z.
    
    # Authors (before quoted title)
    quote_match = citation.find('"')
    if quote_match > 0:
        authors_str = citation[:quote_match].strip().rstrip('.')
        for author in authors_str.split(' and '):
            if author.strip():
                result['authors'].append(parse_name(author.strip()))
    
    # Title (in quotes)
    title_match = re.search(r'"([^"]+)"', citation)
    if title_match:
        result['title'] = title_match.group(1).rstrip('.')
    
    # Year, volume, issue, pages
    year_match = re.search(r'(\d{4})[.,]?\s*(?:pp?\.?\s*)?([\d\-–]+)', citation)
    if year_match:
        result['year'] = year_match.group(1)
        result['pages'] = year_match.group(2)
    
    # Volume/issue
    vol_match = re.search(r'vol\.?\s*(\d+)', citation, re.IGNORECASE)
    if vol_match:
        result['volume'] = vol_match.group(1)
    
    issue_match = re.search(r'no\.?\s*(\d+)', citation, re.IGNORECASE)
    if issue_match:
        result['issue'] = issue_match.group(1)
    
    # Journal name (after title quotes, before vol/year)
    journal_match = re.search(r'"[^"]+"\.?\s*([^,\d]+)', citation)
    if journal_match:
        result['journal'] = journal_match.group(1).strip().rstrip('.')
    
    return result


def parse_vancouver(citation: str) -> Dict[str, Any]:
    """Parse Vancouver format citation."""
    result = {'type': 'journal', 'authors': [], 'title': '', 'journal': '', 
              'year': '', 'volume': '', 'issue': '', 'pages': '', 'doi': ''}
    
    # Remove numbering
    citation = re.sub(r'^\d+\.\s*', '', citation)
    
    # Authors (before title, usually end with et al or period)
    # Vancouver: Authors. Title. Journal. Year;Vol(Issue):Pages.
    
    parts = citation.split('. ')
    if len(parts) >= 1:
        authors_str = parts[0]
        for author in authors_str.split(', '):
            author = author.strip()
            if author and author.lower() != 'et al':
                # Vancouver authors are already in "Lastname FM" format
                # Just need to parse them
                name_parts = author.split()
                if len(name_parts) >= 1:
                    last = name_parts[0]
                    initials = ''.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    result['authors'].append({'last': last, 'first': initials, 'middle': ''})
    
    if len(parts) >= 2:
        result['title'] = parts[1].strip()
    
    # Journal info - pattern: Journal. Year;Vol(Issue):Pages
    journal_pattern = r'([A-Za-z\s]+)\.\s*(\d{4});\s*(\d+)\s*\((\d+)\):\s*([\d\-–]+)'
    journal_match = re.search(journal_pattern, citation)
    if journal_match:
        result['journal'] = journal_match.group(1).strip()
        result['year'] = journal_match.group(2)
        result['volume'] = journal_match.group(3)
        result['issue'] = journal_match.group(4)
        result['pages'] = journal_match.group(5)
    
    return result


def parse_bibtex(citation: str) -> Dict[str, Any]:
    """Parse BibTeX entry."""
    result = {'type': 'journal', 'authors': [], 'title': '', 'journal': '', 
              'year': '', 'volume': '', 'issue': '', 'pages': '', 'doi': ''}
    
    # Extract fields using regex
    def extract_field(field: str, text: str) -> str:
        pattern = rf'{field}\s*=\s*\{{([^}}]+)\}}'
        match = re.search(pattern, text)
        return match.group(1) if match else ''
    
    result['title'] = extract_field('title', citation)
    result['journal'] = extract_field('journal', citation)
    result['year'] = extract_field('year', citation)
    result['volume'] = extract_field('volume', citation)
    result['issue'] = extract_field('number', citation)
    result['pages'] = extract_field('pages', citation)
    result['doi'] = extract_field('doi', citation)
    
    # Parse authors
    authors_str = extract_field('author', citation)
    for author in authors_str.split(' and '):
        if author.strip():
            result['authors'].append(parse_name(author.strip()))
    
    # Detect type
    if '@book' in citation.lower():
        result['type'] = 'book'
    elif '@inproceedings' in citation.lower():
        result['type'] = 'conference'
    elif '@article' in citation.lower():
        result['type'] = 'journal'
    
    return result


def parse_free_text(citation: str) -> Dict[str, Any]:
    """Parse free-text/unstructured citation."""
    result = {'type': 'journal', 'authors': [], 'title': '', 'journal': '', 
              'year': '', 'volume': '', 'issue': '', 'pages': '', 'doi': ''}
    
    # Try to extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', citation)
    if year_match:
        result['year'] = year_match.group(0)
    
    # Try to extract DOI
    doi_match = re.search(r'10\.\d{4,}/\S+', citation)
    if doi_match:
        result['doi'] = doi_match.group(0)
    
    # Try to extract authors (look for pattern of names before year or title)
    # Common pattern: Lastname FM, Lastname2 FM2
    author_section = re.match(r'^((?:[A-Z][a-z]+\s+[A-Z][a-z]*\.?,?\s*)+)', citation)
    if author_section:
        authors_text = author_section.group(1)
        for author in re.split(r',\s*and\s*|,\s*&\s*|,\s*', authors_text):
            author = author.strip()
            if author and len(author) > 2:
                result['authors'].append(parse_name(author))
    
    # Try to find journal name (often in italics or capitalized)
    journal_pattern = r'([A-Z][A-Za-z\s]{3,30}\d?)\.?\s*(?:\d{4}|;|\d+\s*\()'
    journal_match = re.search(journal_pattern, citation)
    if journal_match:
        result['journal'] = journal_match.group(1).strip()
    
    # Volume and issue: ; Vol(Issue):
    vol_pattern = r';\s*(\d+)\s*\((\d+)\):'
    vol_match = re.search(vol_pattern, citation)
    if vol_match:
        result['volume'] = vol_match.group(1)
        result['issue'] = vol_match.group(2)
    
    # Pages
    pages_match = re.search(r':\s*([\d\-–]+)', citation)
    if pages_match:
        result['pages'] = pages_match.group(1)
    
    # Title (often between authors and journal, may be in quotes)
    if result['authors'] and result['journal']:
        # Extract text between author section and journal
        author_end = citation.find(str(result['authors'][-1].get('last', '')))
        journal_start = citation.find(result['journal'])
        if author_end > 0 and journal_start > author_end:
            title = citation[author_end:journal_start].strip()
            title = re.sub(r'^[A-Za-z]+\s+[A-Za-z\.]+[,\.\s]*', '', title)
            title = title.strip('. "')
            result['title'] = title
    
    return result


def to_ama(data: Dict[str, Any]) -> str:
    """Convert parsed citation data to AMA format."""
    
    # Format authors
    authors_formatted = []
    for author in data.get('authors', []):
        authors_formatted.append(format_author_ama(author))
    
    # Handle author display
    if len(authors_formatted) == 0:
        authors_str = ''
    elif len(authors_formatted) == 1:
        authors_str = authors_formatted[0]
    elif len(authors_formatted) == 2:
        authors_str = f"{authors_formatted[0]}, {authors_formatted[1]}"
    elif len(authors_formatted) == 3:
        authors_str = f"{authors_formatted[0]}, {authors_formatted[1]}, {authors_formatted[2]}"
    elif len(authors_formatted) == 4:
        authors_str = f"{authors_formatted[0]}, {authors_formatted[1]}, {authors_formatted[2]}, {authors_formatted[3]}"
    elif len(authors_formatted) == 5:
        authors_str = f"{authors_formatted[0]}, {authors_formatted[1]}, {authors_formatted[2]}, {authors_formatted[3]}, {authors_formatted[4]}"
    elif len(authors_formatted) == 6:
        authors_str = f"{authors_formatted[0]}, {authors_formatted[1]}, {authors_formatted[2]}, {authors_formatted[3]}, {authors_formatted[4]}, {authors_formatted[5]}"
    elif len(authors_formatted) > 6:
        authors_str = f"{authors_formatted[0]} et al"
    else:
        authors_str = ', '.join(authors_formatted)
    
    # Clean up journal name - remove extra spaces and capitalize properly
    journal = data.get('journal', '')
    if journal:
        journal = ' '.join(journal.split())  # Normalize whitespace
        # Check for common journal abbreviations
        journal_lower = journal.lower()
        abbrev_map = {
            'journal of the american medical association': 'JAMA',
            'jama': 'JAMA',
            'nature medicine': 'Nat Med',
            'new england journal of medicine': 'N Engl J Med',
            'british medical journal': 'BMJ',
            'bmj': 'BMJ',
            'annals of internal medicine': 'Ann Intern Med',
            'lancet': 'Lancet',
            'circulation': 'Circulation',
            'pediatrics': 'Pediatrics',
            'american journal of public health': 'Am J Public Health',
        }
        for key, val in abbrev_map.items():
            if key in journal_lower:
                journal = val
                break
        else:
            # Use title case for other journals
            journal = journal.title()
    
    # Build citation based on type
    citation_type = data.get('type', 'journal')
    
    if citation_type == 'book':
        book_title = data.get('title', '')
        year = data.get('year', '')
        return f"{authors_str}. {book_title}. {year}."
    
    # Journal article (default)
    title = data.get('title', '').rstrip('.')
    year = data.get('year', '')
    volume = data.get('volume', '')
    issue = data.get('issue', '')
    pages = data.get('pages', '')
    doi = data.get('doi', '')
    
    # Normalize page range separator: convert -- or - to en-dash (–)
    if pages:
        pages = pages.replace('--', '–').replace('-', '–')
    
    # Build parts
    parts = []
    if authors_str:
        parts.append(f"{authors_str}.")
    if title:
        parts.append(f"{title}.")
    if journal:
        parts.append(f"{journal}.")
    if year:
        year_part = f"{year}"
        if volume:
            year_part += f";{volume}"
            if issue:
                year_part += f"({issue})"
        parts.append(f"{year_part}.")
    if pages:
        parts.append(f"{pages}.")
    if doi:
        parts.append(f"doi:{doi}")
    
    return ' '.join(parts)


def format_citation(citation: str, format_type: str = 'auto') -> str:
    """
    Main function to format a citation to AMA style.
    
    Args:
        citation: Input citation string
        format_type: Input format type ('auto', 'apa', 'mla', 'vancouver', 'bibtex')
    
    Returns:
        AMA formatted citation string
    """
    if not citation or not citation.strip():
        return "Error: Empty citation provided"
    
    citation = citation.strip()
    
    # Auto-detect format
    if format_type == 'auto':
        format_type = detect_format(citation)
    
    # Parse based on format
    parsers = {
        'apa': parse_apa,
        'mla': parse_mla,
        'vancouver': parse_vancouver,
        'bibtex': parse_bibtex,
        'unknown': parse_free_text
    }
    
    parser = parsers.get(format_type, parse_free_text)
    
    try:
        parsed = parser(citation)
        return to_ama(parsed)
    except Exception as e:
        return f"Error parsing citation: {str(e)}"


def batch_format(input_file: str, output_file: str, format_type: str = 'auto'):
    """Format multiple citations from a file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            citations = [line.strip() for line in f if line.strip()]
        
        results = []
        for citation in citations:
            formatted = format_citation(citation, format_type)
            results.append(formatted)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')
        
        return len(results)
    except FileNotFoundError:
        print(f"Error: File not found - {input_file}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0


def interactive_mode():
    """Run in interactive mode."""
    print("Citation Formatter (AMA Style)")
    print("Enter 'quit' to exit\n")
    
    while True:
        try:
            citation = input("> ")
            if citation.lower() in ['quit', 'exit', 'q']:
                break
            
            result = format_citation(citation)
            print(f"\n{result}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(description='Format citations to AMA style')
    parser.add_argument('--input', '-i', help='Input file containing citations')
    parser.add_argument('--output', '-o', help='Output file for formatted citations')
    parser.add_argument('--format', '-f', default='auto', 
                        choices=['auto', 'apa', 'mla', 'vancouver', 'bibtex'],
                        help='Input format type')
    parser.add_argument('--interactive', '-I', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('citation', nargs='?', help='Single citation to format')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.input and args.output:
        count = batch_format(args.input, args.output, args.format)
        print(f"Formatted {count} citations to {args.output}")
    elif args.citation:
        result = format_citation(args.citation, args.format)
        print(result)
    else:
        # Read from stdin
        try:
            citation = sys.stdin.read().strip()
            if citation:
                result = format_citation(citation, args.format)
                print(result)
            else:
                parser.print_help()
        except:
            parser.print_help()


if __name__ == '__main__':
    main()

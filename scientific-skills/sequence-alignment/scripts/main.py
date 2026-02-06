#!/usr/bin/env python3
"""
Sequence Alignment using NCBI BLAST API
Supports nucleotide and protein sequence comparison
"""

import argparse
import json
import csv
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from xml.etree import ElementTree as ET


NCBI_BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
VALID_PROGRAMS = ['blastn', 'blastp', 'blastx', 'tblastn', 'tblastx']
VALID_DATABASES = ['nr', 'nt', 'swissprot', 'pdb', 'refseq_protein', 'refseq_rna', 'est', 'gss']


def submit_blast_request(sequence, program, database, evalue=10, max_hits=10):
    """
    Submit a BLAST search request to NCBI API
    
    Args:
        sequence: Query sequence (DNA or protein)
        program: BLAST program type
        database: Target database
        evalue: E-value threshold
        max_hits: Maximum number of hits
    
    Returns:
        Request ID (RID) for retrieving results
    """
    if program not in VALID_PROGRAMS:
        raise ValueError(f"Invalid program: {program}. Valid options: {VALID_PROGRAMS}")
    if database not in VALID_DATABASES:
        raise ValueError(f"Invalid database: {database}. Valid options: {VALID_DATABASES}")
    
    # Prepare parameters
    params = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': sequence,
        'EXPECT': str(evalue),
        'HITLIST_SIZE': str(max_hits),
        'FORMAT_TYPE': 'XML'
    }
    
    # Add program-specific parameters
    if program in ['blastn', 'tblastx']:
        params['ENTREZ_QUERY'] = 'all [filter]'
    
    data = urllib.parse.urlencode(params).encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    # Submit request with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(NCBI_BLAST_URL, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=60) as response:
                result = response.read().decode('utf-8')
            
            # Extract Request ID (RID)
            rid_start = result.find('RID = ')
            if rid_start == -1:
                raise RuntimeError("Failed to get RID from BLAST response")
            rid = result[rid_start + 6:].split('\n')[0].strip()
            
            # Extract estimated time
            time_start = result.find('RTOE = ')
            if time_start != -1:
                estimated_time = int(result[time_start + 7:].split('\n')[0].strip())
            else:
                estimated_time = 30
            
            return rid, estimated_time
            
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise RuntimeError(f"Failed to submit BLAST request after {max_retries} attempts: {e}")
    
    raise RuntimeError("Failed to submit BLAST request")


def check_blast_status(rid):
    """
    Check if BLAST search is complete
    
    Args:
        rid: Request ID
    
    Returns:
        True if complete, False otherwise
    """
    params = {'CMD': 'Get', 'RID': rid}
    data = urllib.parse.urlencode(params).encode('utf-8')
    
    try:
        req = urllib.request.Request(NCBI_BLAST_URL, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')
        
        # Check for status indicators
        if 'Status=WAITING' in result:
            return False
        elif 'Status=READY' in result or 'BlastOutput' in result:
            return True
        elif 'Status=FAILED' in result:
            raise RuntimeError("BLAST search failed on server")
        else:
            return False
    except urllib.error.URLError:
        return False


def retrieve_blast_results(rid):
    """
    Retrieve BLAST search results
    
    Args:
        rid: Request ID
    
    Returns:
        XML result string
    """
    params = {'CMD': 'Get', 'RID': rid, 'FORMAT_TYPE': 'XML'}
    data = urllib.parse.urlencode(params).encode('utf-8')
    
    req = urllib.request.Request(NCBI_BLAST_URL, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=60) as response:
        result = response.read().decode('utf-8')
    
    return result


def parse_blast_xml(xml_content):
    """
    Parse BLAST XML output into structured data
    
    Args:
        xml_content: XML string from BLAST
    
    Returns:
        Dictionary containing parsed results
    """
    results = {
        'query': '',
        'program': '',
        'database': '',
        'hits': []
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # Extract query info
        blast_query = root.find('.//BlastOutput_query-def')
        if blast_query is not None:
            results['query'] = blast_query.text or 'User Query'
        
        blast_program = root.find('.//BlastOutput_program')
        if blast_program is not None:
            results['program'] = blast_program.text
        
        blast_db = root.find('.//BlastOutput_db')
        if blast_db is not None:
            results['database'] = blast_db.text
        
        # Extract hits
        for hit in root.findall('.//Hit'):
            hit_data = {
                'id': '',
                'definition': '',
                'accession': '',
                'length': 0,
                'hsps': []
            }
            
            hit_id = hit.find('Hit_id')
            if hit_id is not None:
                hit_data['id'] = hit_id.text
            
            hit_def = hit.find('Hit_def')
            if hit_def is not None:
                hit_data['definition'] = hit_def.text
            
            hit_acc = hit.find('Hit_accession')
            if hit_acc is not None:
                hit_data['accession'] = hit_acc.text
            
            hit_len = hit.find('Hit_len')
            if hit_len is not None:
                hit_data['length'] = int(hit_len.text)
            
            # Extract HSPs (High-Scoring Segment Pairs)
            for hsp in hit.findall('.//Hsp'):
                hsp_data = {
                    'bit_score': 0.0,
                    'score': 0,
                    'evalue': 0.0,
                    'identity': 0,
                    'positive': 0,
                    'gaps': 0,
                    'align_len': 0,
                    'query_seq': '',
                    'midline': '',
                    'hit_seq': '',
                    'query_from': 0,
                    'query_to': 0,
                    'hit_from': 0,
                    'hit_to': 0
                }
                
                bit_score = hsp.find('Hsp_bit-score')
                if bit_score is not None:
                    hsp_data['bit_score'] = float(bit_score.text)
                
                score = hsp.find('Hsp_score')
                if score is not None:
                    hsp_data['score'] = int(score.text)
                
                evalue = hsp.find('Hsp_evalue')
                if evalue is not None:
                    hsp_data['evalue'] = float(evalue.text)
                
                identity = hsp.find('Hsp_identity')
                if identity is not None:
                    hsp_data['identity'] = int(identity.text)
                
                positive = hsp.find('Hsp_positive')
                if positive is not None:
                    hsp_data['positive'] = int(positive.text)
                
                gaps = hsp.find('Hsp_gaps')
                if gaps is not None:
                    hsp_data['gaps'] = int(gaps.text)
                
                align_len = hsp.find('Hsp_align-len')
                if align_len is not None:
                    hsp_data['align_len'] = int(align_len.text)
                
                query_seq = hsp.find('Hsp_qseq')
                if query_seq is not None:
                    hsp_data['query_seq'] = query_seq.text
                
                midline = hsp.find('Hsp_midline')
                if midline is not None:
                    hsp_data['midline'] = midline.text
                
                hit_seq = hsp.find('Hsp_hseq')
                if hit_seq is not None:
                    hsp_data['hit_seq'] = hit_seq.text
                
                query_from = hsp.find('Hsp_query-from')
                if query_from is not None:
                    hsp_data['query_from'] = int(query_from.text)
                
                query_to = hsp.find('Hsp_query-to')
                if query_to is not None:
                    hsp_data['query_to'] = int(query_to.text)
                
                hit_from = hsp.find('Hsp_hit-from')
                if hit_from is not None:
                    hsp_data['hit_from'] = int(hit_from.text)
                
                hit_to = hsp.find('Hsp_hit-to')
                if hit_to is not None:
                    hsp_data['hit_to'] = int(hit_to.text)
                
                hit_data['hsps'].append(hsp_data)
            
            results['hits'].append(hit_data)
    
    except ET.ParseError as e:
        raise RuntimeError(f"Failed to parse BLAST XML: {e}")
    
    return results


def format_text_output(results):
    """
    Format BLAST results as human-readable text
    
    Args:
        results: Parsed results dictionary
    
    Returns:
        Formatted string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("BLAST SEQUENCE ALIGNMENT RESULTS")
    lines.append("=" * 80)
    lines.append(f"Program: {results.get('program', 'N/A')}")
    lines.append(f"Database: {results.get('database', 'N/A')}")
    lines.append(f"Query: {results.get('query', 'N/A')}")
    lines.append("=" * 80)
    lines.append("")
    
    if not results['hits']:
        lines.append("No significant hits found.")
        return '\n'.join(lines)
    
    lines.append(f"Found {len(results['hits'])} hit(s):\n")
    
    for i, hit in enumerate(results['hits'], 1):
        lines.append(f"{'='*80}")
        lines.append(f"Hit #{i}")
        lines.append(f"{'='*80}")
        lines.append(f"ID:          {hit['id']}")
        lines.append(f"Accession:   {hit['accession']}")
        lines.append(f"Definition:  {hit['definition']}")
        lines.append(f"Length:      {hit['length']} bp/aa")
        lines.append("")
        
        for j, hsp in enumerate(hit['hsps'], 1):
            identity_pct = (hsp['identity'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0
            positive_pct = (hsp['positive'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0
            
            lines.append(f"  HSP #{j}")
            lines.append(f"  {'-'*60}")
            lines.append(f"  Score:     {hsp['score']} bits({hsp['bit_score']:.1f})")
            lines.append(f"  E-value:   {hsp['evalue']:.2e}")
            lines.append(f"  Identity:  {hsp['identity']}/{hsp['align_len']} ({identity_pct:.1f}%)")
            lines.append(f"  Positives: {hsp['positive']}/{hsp['align_len']} ({positive_pct:.1f}%)")
            lines.append(f"  Gaps:      {hsp['gaps']}/{hsp['align_len']}")
            lines.append("")
            
            # Alignment
            lines.append(f"  Query  {hsp['query_from']:>4}  {hsp['query_seq']}  {hsp['query_to']}")
            lines.append(f"               {hsp['midline']}")
            lines.append(f"  Sbjct  {hsp['hit_from']:>4}  {hsp['hit_seq']}  {hsp['hit_to']}")
            lines.append("")
    
    return '\n'.join(lines)


def format_json_output(results):
    """
    Format BLAST results as JSON
    """
    return json.dumps(results, indent=2)


def format_csv_output(results):
    """
    Format BLAST results as CSV
    """
    output = []
    output.append(['Hit #', 'ID', 'Accession', 'Definition', 'Length', 
                   'HSP #', 'Score', 'Bit Score', 'E-value', 'Identity %', 
                   'Query From', 'Query To', 'Hit From', 'Hit To'])
    
    for i, hit in enumerate(results['hits'], 1):
        for j, hsp in enumerate(hit['hsps'], 1):
            identity_pct = (hsp['identity'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0
            output.append([
                i, hit['id'], hit['accession'], hit['definition'][:100], hit['length'],
                j, hsp['score'], hsp['bit_score'], hsp['evalue'], f"{identity_pct:.1f}%",
                hsp['query_from'], hsp['query_to'], hsp['hit_from'], hsp['hit_to']
            ])
    
    # Convert to CSV string
    import io
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(output)
    return csv_buffer.getvalue()


def run_blast(sequence, program, database, evalue=10, max_hits=10, output_format='text', output_file=None):
    """
    Main function to run BLAST search and return results
    
    Args:
        sequence: Query sequence
        program: BLAST program
        database: Target database
        evalue: E-value threshold
        max_hits: Maximum hits
        output_format: Output format (text, json, csv)
        output_file: Output file path
    
    Returns:
        Formatted results string
    """
    print(f"Submitting BLAST request...", file=sys.stderr)
    print(f"  Program:  {program}", file=sys.stderr)
    print(f"  Database: {database}", file=sys.stderr)
    print(f"  Sequence: {sequence[:50]}{'...' if len(sequence) > 50 else ''}", file=sys.stderr)
    
    # Submit request
    rid, estimated_time = submit_blast_request(sequence, program, database, evalue, max_hits)
    print(f"\nRequest ID: {rid}", file=sys.stderr)
    print(f"Estimated wait: ~{estimated_time} seconds", file=sys.stderr)
    
    # Poll for results
    max_wait = 300  # 5 minutes max
    waited = 0
    check_interval = max(5, min(estimated_time // 3, 30))
    
    while waited < max_wait:
        time.sleep(check_interval)
        waited += check_interval
        
        if check_blast_status(rid):
            print(f"\nResults ready! (waited {waited}s)", file=sys.stderr)
            break
        else:
            print(f"  Still processing... ({waited}s)", file=sys.stderr)
    else:
        raise RuntimeError(f"Search timeout after {max_wait} seconds")
    
    # Retrieve results
    print("\nRetrieving results...", file=sys.stderr)
    xml_content = retrieve_blast_results(rid)
    results = parse_blast_xml(xml_content)
    
    # Format output
    if output_format == 'json':
        formatted = format_json_output(results)
    elif output_format == 'csv':
        formatted = format_csv_output(results)
    else:
        formatted = format_text_output(results)
    
    # Write to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(formatted)
        print(f"\nResults saved to: {output_file}", file=sys.stderr)
    
    return formatted


def main():
    parser = argparse.ArgumentParser(
        description='Sequence Alignment using NCBI BLAST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # DNA sequence search
  python main.py --sequence "ATGGCCCTGTGGATGCGCTTCTTAGTCG" --program blastn --database nt

  # Protein sequence search
  python main.py --sequence "MKTAYIAKQRQISFVK" --program blastp --database swissprot

  # Save to file
  python main.py -s "ATGCGTACG" -p blastn -d nt -o results.txt
        """
    )
    
    parser.add_argument('-s', '--sequence', required=True,
                        help='Query sequence (DNA or protein)')
    parser.add_argument('-p', '--program', required=True, choices=VALID_PROGRAMS,
                        help='BLAST program type')
    parser.add_argument('-d', '--database', required=True, choices=VALID_DATABASES,
                        help='Target database')
    parser.add_argument('-o', '--output',
                        help='Output file path')
    parser.add_argument('-f', '--format', default='text', choices=['text', 'json', 'csv'],
                        help='Output format (default: text)')
    parser.add_argument('-m', '--max_hits', type=int, default=10,
                        help='Maximum number of hits (default: 10)')
    parser.add_argument('-e', '--evalue', type=float, default=10.0,
                        help='E-value threshold (default: 10)')
    
    args = parser.parse_args()
    
    try:
        results = run_blast(
            sequence=args.sequence,
            program=args.program,
            database=args.database,
            evalue=args.evalue,
            max_hits=args.max_hits,
            output_format=args.format,
            output_file=args.output
        )
        print(results)
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

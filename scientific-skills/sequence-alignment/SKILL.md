---
name: sequence-alignment
description: Trigger when user needs to align DNA/protein sequences, compare biological
  sequences, search for similar sequences in databases, or perform BLAST-based similarity
  analysis. Use for bioinformatics sequence comparison tasks.
version: 1.0.0
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Sequence Alignment

A skill for performing sequence alignment using NCBI BLAST API. Supports nucleotide and protein sequence comparison against major biological databases.

## Features

- **BLAST API Integration**: Query NCBI BLAST service for sequence similarity search
- **Multiple BLAST Programs**: blastn, blastp, blastx, tblastn, tblastx
- **Alignment Visualization**: Display results in human-readable format
- **Database Support**: nr, nt, swissprot, refseq, pdb, and more

## Usage

```bash
python scripts/main.py --sequence "ATGCGTACGTAGCTAGCTAG" --program blastn --database nt --output results.txt
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--sequence` | Query sequence (DNA/Protein) | Yes |
| `--program` | BLAST program: blastn, blastp, blastx, tblastn, tblastx | Yes |
| `--database` | Target database: nr, nt, swissprot, pdb, refseq_protein | Yes |
| `--output` | Output file path | No |
| `--format` | Output format: text, json, csv | No (default: text) |
| `--max_hits` | Maximum number of hits to return | No (default: 10) |
| `--evalue` | E-value threshold | No (default: 10) |

## Technical Difficulty

**Medium** - Requires understanding of BLAST algorithm, API handling with retry logic, and biological sequence formats.

## BLAST Programs Reference

| Program | Query Type | Database Type | Use Case |
|---------|-----------|---------------|----------|
| blastn | Nucleotide | Nucleotide | DNA vs DNA |
| blastp | Protein | Protein | Protein vs Protein |
| blastx | Nucleotide (translated) | Protein | DNA vs Protein |
| tblastn | Protein | Nucleotide (translated) | Protein vs DNA |
| tblastx | Nucleotide (translated) | Nucleotide (translated) | Translated DNA vs DNA |

## Example Workflows

### DNA Sequence Similarity Search
```bash
python scripts/main.py --sequence "ATGGCCCTGTGGATGCGCTTCTTAGTCG" --program blastn --database nt --max_hits 5
```

### Protein Sequence Alignment
```bash
python scripts/main.py --sequence "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGT" --program blastp --database swissprot --evalue 0.001
```

## Output Format

Results include:
- Query sequence info
- Hit definitions and accession numbers
- Alignment scores (bit score, e-value)
- Percent identity and similarity
- Alignment visualization with match/mismatch highlighting

## References

- [BLAST Documentation](references/blast_docs.md)
- [NCBI BLAST API Guide](references/ncbi_api_guide.md)

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
## Prerequisites

No additional Python packages required.

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

---
name: citation-formatter
description: Automatically formats academic citations to AMA (American Medical Association) 11th edition style. Converts from APA, MLA, Vancouver, BibTeX, and free-text formats to standardized AMA format for medical and scientific publications.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
  skill-author: AIPOCH
---

# Citation Formatter

Convert academic citations from various formats (APA, MLA, Vancouver, BibTeX) to standardized AMA (American Medical Association) 11th edition format. Essential for preparing reference lists for medical journals, research papers, and academic manuscripts requiring AMA style compliance.

**Key Capabilities:**
- **Multi-Format Input Support**: Parse APA, MLA, Vancouver, BibTeX, and unstructured citations
- **Automatic Format Detection**: Intelligently identify input citation format
- **AMA 11th Edition Compliance**: Output conforms to current AMA style guidelines
- **Batch Processing**: Convert entire reference lists efficiently
- **Journal Abbreviation**: Automatically abbreviate common journal names per AMA standards
- **Interactive Mode**: Real-time citation formatting for quick conversions

---

## When to Use

**✅ Use this skill when:**
- Preparing **reference lists for medical journals** that require AMA style (JAMA, NEJM, etc.)
- Converting citations from **other styles** (APA, MLA) to AMA for submission
- **Standardizing reference formats** across a manuscript with mixed citation styles
- **Reformatting references** when transferring between journals with different requirements
- **Cleaning up citations** copied from databases with inconsistent formatting
- **Preparing thesis or dissertation** references in AMA format
- **Creating bibliographies** for systematic reviews requiring AMA style
- **Converting BibTeX entries** from reference managers to AMA format

**❌ Do NOT use when:**
- Target journal requires **different citation style** (APA, Chicago, Vancouver) → Use appropriate converter
- Needing **full bibliographic management** → Use Zotero, EndNote, or Mendeley
- Converting **in-text citations** (author-date formats) → This tool formats reference lists only
- Working with **legal citations** → Use Bluebook or legal-specific tools
- Needing **citation validation** against PubMed or CrossRef → Use reference validation tools
- Formatting **non-medical humanities citations** → Use appropriate style guide

**Related Skills:**
- **上游 (Upstream)**: `citation-chasing-mapping`, `literature-full-text-fetcher`
- **下游 (Downstream)**: `journal-club-presenter`, `manuscript-format-checker`

---

## Integration with Other Skills

**Upstream Skills:**
- `citation-chasing-mapping`: Find relevant papers before formatting their citations
- `literature-full-text-fetcher`: Retrieve papers that need to be cited
- `abstract-summarizer`: Review papers before adding to reference list

**Downstream Skills:**
- `journal-club-presenter`: Create presentations with properly formatted references
- `manuscript-format-checker`: Verify reference formatting meets journal requirements
- `cover-letter-drafter`: Include properly formatted references in cover letters

**Complete Workflow:**
```
Literature Search → citation-chasing-mapping → citation-formatter → manuscript-format-checker → Submission
```

---

## Core Capabilities

### 1. Automatic Format Detection and Conversion

Automatically detect input citation format and convert to AMA style without manual specification.

```python
from scripts.main import format_citation, detect_format

# Example citations in different formats
apa_citation = "Smith, J. D., & Jones, M. A. (2020). Understanding CRISPR mechanisms. Journal of Molecular Biology, 45(3), 123-145. https://doi.org/10.1000/jmb.2020.001"

mla_citation = 'Smith, John D., and Mary A. Jones. "Understanding CRISPR Mechanisms." Journal of Molecular Biology, vol. 45, no. 3, 2020, pp. 123-145.'

vancouver_citation = "Smith JD, Jones MA. Understanding CRISPR mechanisms. J Mol Biol. 2020;45(3):123-145."

# Auto-detect and format
for name, citation in [("APA", apa_citation), ("MLA", mla_citation), ("Vancouver", vancouver_citation)]:
    detected = detect_format(citation)
    ama_formatted = format_citation(citation)
    
    print(f"\n{name} Format Detected:")
    print(f"  Input: {citation[:60]}...")
    print(f"  AMA Output: {ama_formatted}")
```

**Supported Input Formats:**

| Format | Characteristics | Example Identifier |
|--------|----------------|-------------------|
| **APA** | Year in parentheses, & between authors | `(2020)` |
| **MLA** | "Title." in quotes, vol./no. labels | `"Title."` |
| **Vancouver** | Numbered, year;volume(issue):pages | `2020;45(3):123` |
| **BibTeX** | @article/book format with {} | `@article{` |
| **Free Text** | Unstructured, mixed elements | Various |

**Best Practices:**
- ✅ **Use auto-detect for mixed formats** - handles most cases correctly
- ✅ **Specify format if known** - improves accuracy for edge cases
- ✅ **Check author name handling** - different formats vary in name order
- ✅ **Verify DOI formatting** - ensures consistent DOI presentation

**Common Issues and Solutions:**

**Issue: Format not detected correctly**
- Symptom: Auto-detection identifies wrong format
- Solution: Specify format explicitly using `--format` parameter

**Issue: Incomplete citations fail to parse**
- Symptom: Missing fields in output
- Solution: Ensure all required elements present (authors, title, journal, year)

### 2. Author Name Formatting

Parse and reformat author names according to AMA guidelines (Lastname FM, up to 6 authors, et al. for 7+).

```python
from scripts.main import parse_name, format_author_ama

# Various author name formats
name_examples = [
    "Smith, John D.",           # Last, First Middle
    "John D. Smith",            # First Middle Last
    "Smith, J. D.",             # Initials
    "John Smith",               # First Last
    "Maria Garcia-Rodriguez",   # Compound last name
]

print("Author Name Formatting:")
for name in name_examples:
    parsed = parse_name(name)
    ama_format = format_author_ama(parsed)
    print(f"  {name:30} → {ama_format}")

# Output:
# Smith, John D.                → Smith JD
# John D. Smith                 → Smith JD
# Smith, J. D.                  → Smith JD
# John Smith                    → Smith J
# Maria Garcia-Rodriguez        → Garcia-Rodriguez M
```

**AMA Author Rules:**

| Number of Authors | AMA Format | Example |
|------------------|-----------|---------|
| **1** | Lastname FM | Smith JA |
| **2** | Lastname1 FM1, Lastname2 FM2 | Smith JA, Jones MB |
| **3-6** | List all authors | Smith JA, Jones MB, Lee CD |
| **7+** | First 3 + et al. | Smith JA, Jones MB, Lee CD, et al. |

**Best Practices:**
- ✅ **Verify compound surnames** - ensure correct parsing (e.g., "van der Waals")
- ✅ **Check for missing initials** - full names should include all initials
- ✅ **Handle Jr./Sr. suffixes** - place after initials (Smith JA Jr.)
- ✅ **Watch for non-standard formats** - some databases format names oddly

**Common Issues and Solutions:**

**Issue: Names with particles (van, de, etc.)**
- Symptom: "van der Waals" parsed incorrectly
- Solution: Check output; manually correct if needed (van der Waals JD)

**Issue: Organizations as authors**
- Symptom: Organization names split as personal names
- Solution: Use specific organization formatting; may need manual correction

### 3. Journal Abbreviation and Formatting

Automatically abbreviate journal names according to AMA standard abbreviations and NLM catalog.

```python
from scripts.main import format_citation

# Journal name variations
journal_examples = [
    "New England Journal of Medicine",
    "Journal of the American Medical Association",
    "British Medical Journal",
    "Nature Medicine",
    "Annals of Internal Medicine"
]

# Create minimal citations to show journal abbreviation
print("Journal Name Abbreviations:")
for journal in journal_examples:
    # Create a minimal citation with just journal name
    citation = f"Smith J. Title. {journal}. 2020;1:1-10."
    formatted = format_citation(citation)
    
    # Extract journal from formatted output
    parts = formatted.split('. ')
    if len(parts) >= 3:
        abbreviated = parts[2].rstrip('.')
        print(f"  {journal:45} → {abbreviated}")
```

**Common Journal Abbreviations:**

| Full Journal Name | AMA Abbreviation |
|------------------|------------------|
| New England Journal of Medicine | N Engl J Med |
| Journal of the American Medical Association | JAMA |
| British Medical Journal | BMJ |
| Nature Medicine | Nat Med |
| Lancet | Lancet |
| Annals of Internal Medicine | Ann Intern Med |
| Circulation | Circulation |
| Pediatrics | Pediatrics |
| American Journal of Public Health | Am J Public Health |
| Journal of Clinical Oncology | J Clin Oncol |

**Best Practices:**
- ✅ **Verify journal abbreviation** - use NLM catalog for unfamiliar journals
- ✅ **Check for new journals** - may not be in abbreviation database
- ✅ **Maintain italics** - journal names italicized in final output (if supported)
- ✅ **Follow punctuation rules** - period after abbreviated journal name

**Common Issues and Solutions:**

**Issue: Journal not abbreviated**
- Symptom: Full journal name appears in output
- Solution: Manually abbreviate using NLM guidelines or keep full name if preferred

**Issue: Ambiguous abbreviations**
- Symptom: Multiple journals share same abbreviation
- Solution: Use full journal name to avoid confusion

### 4. Multi-Document Type Support

Format various document types including journal articles, books, book chapters, conference papers, and websites.

```python
from scripts.main import format_citation

# Different document types
doc_types = {
    "Journal Article": "Smith J, Jones M. Article title here. Journal Name. 2020;45(3):123-145.",
    
    "Book": "Smith JA. Book Title: A Comprehensive Guide. 2nd ed. New York, NY: Publisher Name; 2020.",
    
    "Book Chapter": "Smith JA. Chapter title. In: Jones MB, Lee CD, eds. Book Title. New York, NY: Publisher; 2020:45-67.",
    
    "Website": "Centers for Disease Control and Prevention. Title of webpage. CDC website. https://www.cdc.gov/example. Updated January 15, 2020. Accessed March 1, 2020.",
    
    "Conference": "Smith JA, Jones MB. Presentation title. Paper presented at: Conference Name; October 15, 2020; City, State."
}

print("Document Type Formatting:")
for doc_type, citation in doc_types.items():
    formatted = format_citation(citation)
    print(f"\n{doc_type}:")
    print(f"  Input:  {citation[:50]}...")
    print(f"  Output: {formatted}")
```

**AMA Format by Document Type:**

| Type | Format Pattern | Example |
|------|---------------|---------|
| **Journal** | Author. Title. Journal. Year;Vol(Issue):Pages. | Smith J. Title. JAMA. 2020;324(5):456-462. |
| **Book** | Author. Title. City: Publisher; Year. | Smith J. Book Title. New York: Wiley; 2020. |
| **Chapter** | Author. Chapter. In: Editors, eds. Book. City: Publisher; Year:pages. | Smith J. Chapter 1. In: Jones M, ed. Textbook. NY: Wiley; 2020:1-20. |
| **Website** | Author/Org. Title. Website. URL. Date. | CDC. Guidelines. CDC website. https://... Accessed 2020. |
| **Conference** | Author. Title. Paper presented at: Name; Date; Location. | Smith J. Title. Presented at: ASM; Oct 2020; Boston. |

**Best Practices:**
- ✅ **Specify edition for books** - include edition number after title
- ✅ **Include access date for websites** - required for web resources
- ✅ **Format editors correctly** - "ed." or "eds." after editor names
- ✅ **Verify publisher location** - city and state/country

**Common Issues and Solutions:**

**Issue: Document type not recognized**
- Symptom: Formatted as journal article regardless of actual type
- Solution: Check input includes clear type indicators ("In:", "eds.", URL)

**Issue: Missing required fields**
- Symptom: Incomplete output for books/websites
- Solution: Ensure all AMA-required elements present in input

### 5. Batch Processing

Process entire reference lists efficiently from text files.

```python
from scripts.main import batch_format

# Process file with multiple citations
input_file = "references_input.txt"
output_file = "references_output.txt"

# Create sample input file
sample_references = """Smith, J. D. (2020). Understanding CRISPR mechanisms. Journal of Molecular Biology, 45(3), 123-145. https://doi.org/10.1000/jmb.2020.001

Jones, M. A., & Lee, C. D. (2019). Clinical applications of gene therapy. New England Journal of Medicine, 381(12), 1156-1168.

@article{brown2021,
  author = {Brown, A. B. and White, D. E.},
  title = {Novel therapeutic approaches},
  journal = {Nature Medicine},
  year = {2021},
  volume = {27},
  pages = {234-245}
}"""

# Write sample file
with open(input_file, 'w') as f:
    f.write(sample_references)

# Batch format
num_formatted = batch_format(input_file, output_file, format_type='auto')

print(f"Batch Processing Complete:")
print(f"  Input file: {input_file}")
print(f"  Output file: {output_file}")
print(f"  Citations formatted: {num_formatted}")

# Display results
print("\nFormatted References:")
with open(output_file, 'r') as f:
    for i, line in enumerate(f, 1):
        print(f"{i}. {line.strip()}")
```

**Batch Processing Features:**

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Mixed formats** | Handles different formats in same file | Flexibility |
| **Line-by-line** | Each citation on separate line | Organization |
| **Error handling** | Continues on parse errors | Robustness |
| **UTF-8 support** | Handles international characters | Global use |

**Best Practices:**
- ✅ **One citation per line** - ensures proper separation
- ✅ **Remove blank lines** - prevents empty entries
- ✅ **Check output file** - verify formatting accuracy
- ✅ **Maintain backup** - keep original reference list

**Common Issues and Solutions:**

**Issue: Multi-line citations split incorrectly**
- Symptom: Single citation broken into multiple entries
- Solution: Ensure each citation is on single line; use semicolons for multiple works

**Issue: Encoding errors with special characters**
- Symptom: Garbled characters in output
- Solution: Use UTF-8 encoding for input files

### 6. Interactive Mode

Real-time citation formatting for quick conversions without creating files.

```python
from scripts.main import format_citation

def quick_format_examples():
    """Demonstrate quick formatting examples."""
    
    examples = [
        "Smith, J. D., Jones, M. A., & Lee, C. D. (2020). Understanding gene therapy. Nature Medicine, 25(4), 567-580.",
        'Smith, John. "The Future of Medicine." Journal of Medical Research, vol. 45, 2020, pp. 123-145.',
        "Smith JD, Jones MA, Lee CD. Understanding gene therapy. Nat Med. 2020;25(4):567-580."
    ]
    
    print("Interactive Formatting Examples:")
    print("="*70)
    
    for i, citation in enumerate(examples, 1):
        formatted = format_citation(citation)
        print(f"\nExample {i}:")
        print(f"Input:  {citation}")
        print(f"Output: {formatted}")
        print()

# Command line usage:
# python scripts/main.py --interactive
```

**Interactive Mode Features:**

| Feature | Command | Description |
|---------|---------|-------------|
| **Single citation** | Type citation + Enter | Formats immediately |
| **Exit** | `quit` or `q` | Exit interactive mode |
| **Help** | N/A (built-in) | Shows usage instructions |
| **History** | Up arrow | Recall previous inputs |

**Best Practices:**
- ✅ **Use for quick conversions** - single citations or testing
- ✅ **Copy-paste from databases** - PubMed, Google Scholar
- ✅ **Check output before using** - verify accuracy
- ✅ **Exit properly** - use 'quit' to close cleanly

**Common Issues and Solutions:**

**Issue: Long citations wrap poorly**
- Symptom: Multi-line input not handled well
- Solution: Paste as single line or use file input for long citations

---

## Complete Workflow Example

**From mixed-format references to AMA-compliant list:**

```bash
# Step 1: Create input file with mixed formats
cat > references.txt << 'EOF'
Smith, J. D. (2020). CRISPR applications. Nature, 578(7793), 24-26.
Doe JA, Smith MB. Gene editing review. J Med Genet. 2019;56(3):123-135.
@article{johnson2021,
  author = {Johnson, A. B.},
  title = {Future therapies},
  journal = {Science},
  year = {2021},
  volume = {371}
}
EOF

# Step 2: Batch format to AMA
python scripts/main.py --input references.txt --output ama_references.txt

# Step 3: Verify output
cat ama_references.txt
```

**Python API Usage:**

```python
from scripts.main import format_citation, batch_format
from pathlib import Path

def prepare_manuscript_references(
    raw_references_file: str,
    output_file: str = "formatted_references.txt"
) -> dict:
    """
    Complete workflow for preparing manuscript references.
    
    Returns:
        Dictionary with statistics and output file path
    """
    print("="*70)
    print("MANUSCRIPT REFERENCE PREPARATION")
    print("="*70)
    
    # Check input file exists
    if not Path(raw_references_file).exists():
        return {"error": f"Input file not found: {raw_references_file}"}
    
    # Count input references
    with open(raw_references_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        input_count = len(lines)
    
    print(f"\nInput file: {raw_references_file}")
    print(f"References found: {input_count}")
    
    # Format references
    formatted_count = batch_format(raw_references_file, output_file)
    
    print(f"\nFormatting Results:")
    print(f"  Successfully formatted: {formatted_count}/{input_count}")
    
    if formatted_count < input_count:
        print(f"  ⚠️  {input_count - formatted_count} references had formatting issues")
    
    # Display sample outputs
    print(f"\nSample Formatted References:")
    print("-"*70)
    
    with open(output_file, 'r') as f:
        samples = f.readlines()[:3]  # Show first 3
        for i, ref in enumerate(samples, 1):
            print(f"{i}. {ref.strip()}")
    
    if formatted_count > 3:
        print(f"... and {formatted_count - 3} more")
    
    print("-"*70)
    print(f"\nOutput saved to: {output_file}")
    print("="*70)
    
    return {
        "input_file": raw_references_file,
        "output_file": output_file,
        "input_count": input_count,
        "formatted_count": formatted_count,
        "success_rate": f"{formatted_count/input_count*100:.1f}%"
    }

# Execute workflow
results = prepare_manuscript_references(
    raw_references_file="my_references.txt",
    output_file="ama_formatted_refs.txt"
)
```

**Expected Output Files:**

```
manuscript/
├── my_references.txt          # Original mixed-format references
├── ama_formatted_refs.txt     # AMA-formatted output
└── formatting_report.txt      # Summary statistics
```

---

## Common Patterns

### Pattern 1: Journal Submission Preparation

**Scenario**: Preparing references for submission to AMA-style journal.

```json
{
  "task": "journal_submission_prep",
  "target_journal": "JAMA",
  "style": "AMA 11th edition",
  "input_sources": [
    "Zotero export (various formats)",
    "Manually collected references",
    "PubMed citations"
  ],
  "output": "Numbered reference list",
  "verification": "Cross-check with journal guidelines"
}
```

**Workflow:**
1. Export references from reference manager
2. Ensure one citation per line in input file
3. Run batch formatter with auto-detect
4. Review output for accuracy
5. Check against journal-specific requirements
6. Add numbering if required (1., 2., 3.)
7. Insert into manuscript reference section

**Output Example:**
```
Journal Submission Ready:
  Input references: 42
  Successfully formatted: 42 (100%)
  
Quality Checks:
  ✓ All journal names abbreviated
  ✓ Author format: Lastname FM
  ✓ DOIs included where available
  ✓ Punctuation per AMA guidelines
  
Ready for submission to: JAMA
```

### Pattern 2: Reference List Cleanup

**Scenario**: Cleaning up a messy reference list with mixed formatting.

```json
{
  "task": "reference_cleanup",
  "current_state": "Mixed formats, inconsistencies",
  "issues": [
    "Some APA, some MLA",
    "Inconsistent author formatting",
    "Full vs abbreviated journal names",
    "Missing DOIs"
  ],
  "target": "Uniform AMA format"
}
```

**Workflow:**
1. Copy all references to single text file
2. Remove existing numbering
3. Run batch format with auto-detect
4. Review for parsing errors
5. Manually correct any failed conversions
6. Reformat corrected citations
7. Add sequential numbering

**Output Example:**
```
Reference Cleanup Results:
  Original references: 85
  Auto-formatted: 78 (92%)
  Manual correction needed: 7
  
Common issues found:
  - 12 references: missing DOIs
  - 5 references: incomplete author lists
  - 3 references: unclear document types
  
After correction: 85/85 formatted (100%)
```

### Pattern 3: Citation Database Migration

**Scenario**: Converting entire reference library to AMA format.

```json
{
  "task": "library_migration",
  "source": "EndNote library",
  "target_format": "AMA",
  "library_size": "1,247 references",
  "approach": "Export to text, batch format"
}
```

**Workflow:**
1. Export entire library to text format
2. Split into manageable batches (100 refs each)
3. Process each batch separately
4. Log errors for manual review
5. Reformat failed citations individually
6. Merge all batches
7. Import back to reference manager

**Output Example:**
```
Library Migration Progress:
  Batch 1: 100/100 formatted ✓
  Batch 2: 100/100 formatted ✓
  Batch 3: 98/100 formatted (2 errors)
  ...
  Batch 13: 47/47 formatted ✓
  
Total: 1,245/1,247 formatted (99.8%)
Manual review needed: 2 references
Time elapsed: 3 minutes
```

### Pattern 4: Systematic Review Bibliography

**Scenario**: Creating standardized bibliography for systematic review.

```json
{
  "task": "systematic_review_refs",
  "inclusion_criteria": "Peer-reviewed articles only",
  "format": "AMA + PRISMA requirements",
  "sections": [
    "Included studies",
    "Excluded studies",
    "Additional references"
  ],
  "annotation": "Include search source"
}
```

**Workflow:**
1. Compile all identified references
2. Format all to AMA standard
3. Add annotations for search source (e.g., [PubMed])
4. Organize by inclusion status
5. Add PRISMA flow diagram references
6. Cross-check with inclusion/exclusion log
7. Export final bibliography

**Output Example:**
```
Systematic Review Bibliography:
  
Included Studies (n=23):
  1. Smith JA, et al. Primary outcome study. JAMA. 2020;...
     [PubMed, included for efficacy data]
  2. Jones MB, et al. Secondary analysis. Lancet. 2019;...
     [EMBASE, included for safety data]
  ...
  
Additional References (n=8):
  [Methodology papers, guidelines]
  
Total: 31 references, all AMA formatted
```

---

## Quality Checklist

**Pre-Formatting:**
- [ ] **CRITICAL**: Verify target journal requires AMA style (not APA, Vancouver, etc.)
- [ ] Check AMA edition (10th vs 11th) - this tool uses 11th edition
- [ ] Ensure input file is plain text (UTF-8 encoding)
- [ ] Remove existing numbering from reference list
- [ ] Check for one citation per line
- [ ] Verify all citations have complete information
- [ ] Note any special document types (websites, conference papers)

**During Formatting:**
- [ ] **CRITICAL**: Review auto-detected formats for accuracy
- [ ] Check author name formatting (Lastname FM)
- [ ] Verify journal abbreviations (especially for new/rare journals)
- [ ] Confirm year, volume, issue, and page numbers present
- [ ] Check DOI formatting (doi:10.xxxx format)
- [ ] Watch for parsing errors or failed conversions
- [ ] Note any unusual citation formats that may need manual correction

**Post-Formatting:**
- [ ] **CRITICAL**: Manually verify 10-20% of formatted citations
- [ ] Check author count rules (et al. for 7+ authors)
- [ ] Verify punctuation (periods, semicolons, colons)
- [ ] Confirm consistent capitalization in article titles
- [ ] Check that journal names are italicized (if using rich text)
- [ ] Verify website citations include access dates
- [ ] Compare sample citations with AMA manual examples

**Journal-Specific Checks:**
- [ ] **CRITICAL**: Verify against target journal's specific guidelines
- [ ] Check DOI requirements (some journals want URL format)
- [ ] Verify website citation format (varies by journal)
- [ ] Check if PMID numbers required
- [ ] Confirm pagination format (123-45 vs 123-145)
- [ ] Verify book citation format (some journals differ)
- [ ] Check conference proceeding requirements

---

## Common Pitfalls

**Input Issues:**
- ❌ **Inconsistent separators** → Mixed commas, semicolons, periods
  - ✅ Standardize input format before processing
  
- ❌ **Missing required fields** → Incomplete citation information
  - ✅ Verify all AMA-required elements present
  
- ❌ **Non-standard formats** → Database-specific formatting
  - ✅ Clean data from PubMed/Google Scholar before formatting
  
- ❌ **Special characters** → Accented letters, symbols
  - ✅ Use UTF-8 encoding throughout

**Formatting Issues:**
- ❌ **Wrong style applied** → Used APA instead of AMA
  - ✅ Double-check target journal requirements
  
- ❌ **Missing et al.** → Listed all 15 authors
  - ✅ Apply AMA rule: list all up to 6, et al. for 7+
  
- ❌ **Full journal names** → Didn't abbreviate
  - ✅ Verify journal abbreviation database coverage
  
- ❌ **Incorrect punctuation** → Periods vs semicolons
  - ✅ Follow AMA punctuation rules strictly

**Output Issues:**
- ❌ **No numbering** → AMA uses numbered references
  - ✅ Add sequential numbering to final output
  
- ❌ **Wrong DOI format** → Some journals want https://doi.org/
  - ✅ Check journal-specific DOI requirements
  
- ❌ **Missing access dates** → Required for websites
  - ✅ Add access date to web resource citations
  
- ❌ **Inconsistent italics** → Journal names should be italic
  - ✅ Apply formatting in word processor

---

## Troubleshooting

**Problem: Citation won't parse**
- Symptoms: Error message or garbled output
- Causes:
  - Unusual format not recognized
  - Missing critical fields
  - Corrupted text encoding
- Solutions:
  - Try specifying format explicitly (--format)
  - Check all required fields present
  - Re-save file with UTF-8 encoding
  - Manually format problematic citations

**Problem: Author names formatted incorrectly**
- Symptoms: Wrong order or missing initials
- Causes:
  - Unusual name formats
  - Missing punctuation
  - Compound surnames
- Solutions:
  - Check input format matches expected pattern
  - Manually verify output for compound surnames
  - Add missing initials to input

**Problem: Journal name not abbreviated**
- Symptoms: Full journal name in output
- Causes:
  - Journal not in abbreviation database
  - Non-standard journal name format
- Solutions:
  - Manually abbreviate per NLM catalog
  - Add custom abbreviation to code
  - Keep full name if journal prefers

**Problem: Batch processing fails**
- Symptoms: Error or empty output file
- Causes:
  - Empty input file
  - Wrong file path
  - Permission issues
- Solutions:
  - Verify input file exists and contains text
  - Check file path is correct
  - Ensure write permissions to output directory

**Problem: Format detection wrong**
- Symptoms: APA interpreted as MLA, etc.
- Causes:
  - Ambiguous formatting
  - Mixed formats in single citation
- Solutions:
  - Specify format explicitly (--format)
  - Standardize input citations before processing

**Problem: Special characters corrupted**
- Symptoms: Accented letters appear as ? or random characters
- Causes:
  - Wrong file encoding
  - Terminal encoding issues
- Solutions:
  - Save input as UTF-8
  - Set terminal encoding to UTF-8
  - Use Python 3 (better Unicode support)

---

## References

Available in `references/` directory:

- (No reference files currently available for this skill)

**External Resources:**
- AMA Manual of Style, 11th Edition: https://www.amamanualofstyle.com
- NLM Catalog (journal abbreviations): https://www.ncbi.nlm.nih.gov/nlmcatalog/journals
- CrossRef DOI lookup: https://search.crossref.org
- PubMed Citation Guidelines: https://pubmed.ncbi.nlm.nih.gov/help/#citation-format

---

## Scripts

Located in `scripts/` directory:

- `main.py` - Citation formatting engine with multi-format support

---

## AMA Quick Reference

**Basic Journal Article:**
```
Author AA, Author BB. Article title. Journal Abbrev. Year;Vol(Issue):Pages. doi:xxxxx
```

**Book:**
```
Author AA. Book Title. City, State: Publisher; Year.
```

**Website:**
```
Author/Organization. Page Title. Website Name. URL. Published Date. Accessed Date.
```

**Author Count Rules:**
- 1-6 authors: List all
- 7+ authors: First 3 + et al.

---

**Last Updated**: 2026-02-09  
**Skill ID**: 188  
**Version**: 2.0 (K-Dense Standard)

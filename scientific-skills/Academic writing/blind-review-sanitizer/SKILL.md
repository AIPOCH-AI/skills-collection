---
name: blind-review-sanitizer
description: One-click removal of author names, affiliations, acknowledgments, and excessive self-citations from manuscripts to meet double-blind peer review requirements. Preserves document structure while anonymizing sensitive information.
allowed-tools: [Read, Write, Bash, Edit, Grep]
license: MIT
metadata:
  skill-author: AIPOCH
---

# Blind Review Sanitizer

Automatically anonymize academic manuscripts for double-blind peer review by removing author identifiers, institutional affiliations, acknowledgments, and excessive self-citations while preserving document formatting and scholarly content integrity.

**Key Capabilities:**
- **Author Identity Removal**: Automatically detect and redact author names, institutional affiliations, and contact information using pattern matching and customizable rules
- **Acknowledgment Section Sanitization**: Identify and remove or flag acknowledgment sections that may reveal author identity through funding sources or personal thanks
- **Self-Citation Detection and Neutralization**: Identify first-person citations and excessive self-references that could deanonymize the submission
- **Multi-Format Document Support**: Process DOCX, Markdown, and plain text files with format-aware sanitization strategies
- **Audit Trail Generation**: Create detailed logs of all redactions made for verification and transparency

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--input` | str | Yes | - | Path to input manuscript file (DOCX, MD, or TXT) |
| `--output` | str | Yes | - | Path for sanitized output file |
| `--authors` | list[str] | No | - | List of author names to redact |
| `--keep-acknowledgments` | bool | No | false | Whether to preserve acknowledgment sections |
| `--highlight-self-cites` | bool | No | false | Only highlight self-citations without replacement |

---

## When to Use

**✅ Use this skill when:**
- Preparing a manuscript for **double-blind peer review** at journals requiring author anonymity
- Submitting to **conferences with anonymization requirements** (e.g., NeurIPS, ICML, ACL, major medical journals)
- Performing a **final compliance check** before submission to ensure no identifying information remains
- **Re-sanitizing** a previously rejected manuscript for submission to a new venue with different anonymization standards
- Creating **anonymized versions** of papers for public preprints while maintaining citation integrity
- Processing **collaborative manuscripts** where some authors need to remain anonymous for specific submissions

**❌ Do NOT use when:**
- Preparing for **open peer review** or journals with transparent review processes → Use `cover-letter-drafter` instead
- The manuscript contains **patent-pending innovations** requiring author identification → Consult legal counsel first
- You need to **add author information** rather than remove it → Use `citation-formatter` for bibliography management
- Working with **highly sensitive clinical data** requiring HIPAA compliance → Use `hipaa-compliance-auditor` for medical data
- The document uses **complex LaTeX formatting** with embedded author macros → Manual review required

**Related Skills:**
- **上游 (Upstream)**: `cover-letter-drafter`, `citation-formatter`, `conflict-of-interest-checker`
- **下游 (Downstream)**: `journal-club-presenter`, `conference-abstract-adaptor`

---

## Integration with Other Skills

**Upstream Skills:**
- `cover-letter-drafter`: Generate cover letters AFTER manuscript sanitization to avoid including blinded content in correspondence
- `citation-formatter`: Format citations BEFORE sanitization to ensure proper numbering and formatting
- `conflict-of-interest-checker`: Check co-author conflicts BEFORE anonymization to maintain disclosure accuracy

**Downstream Skills:**
- `journal-club-presenter`: Create presentation materials using sanitized versions for external review
- `conference-abstract-adaptor`: Adapt abstracts for conferences that may have different anonymity requirements

**Complete Workflow:**
```
Manuscript Writing → citation-formatter → conflict-of-interest-checker → blind-review-sanitizer → cover-letter-drafter → Submission
```

---

## Core Capabilities

### 1. Author Identity Detection and Removal

Systematically identify and remove author names, institutional affiliations, and contact information from manuscripts using pattern recognition and user-specified rules.

```python
from scripts.main import BlindReviewSanitizer

# Initialize sanitizer with known author names
sanitizer = BlindReviewSanitizer(
    authors=["Zhang San", "Li Si", "Wang Wu"],
    keep_acknowledgments=False,
    highlight_self_cites=False
)

# Process text content
text = """Zhang San¹, Li Si²
¹Tsinghua University Computer Science Department
²Peking University School of Information

Email: zhangsan@tsinghua.edu.cn"""

sanitized = sanitizer.sanitize_text(text)
print(sanitized)
```

**Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `authors` | List[str] | No | List of author names to redact. Improves accuracy when specified. | None |
| `case_sensitive` | bool | No | Whether author name matching is case-sensitive | False |
| `partial_match` | bool | No | Allow partial name matching (e.g., "Zhang" matches "Zhang San") | True |

**Best Practices:**
- ✅ **Always provide explicit author names** when known to improve detection accuracy and reduce false positives
- ✅ **Test with sample documents** before processing important manuscripts to verify redaction patterns
- ✅ **Include all name variants** (full names, initials, anglicized versions) in the authors list
- ✅ **Review output carefully** for author names that may appear in figures, tables, or supplementary materials

**Common Issues and Solutions:**

**Issue: Common words flagged as author names**
- Symptom: Words like "Wang" (meaning "king" in Chinese) or common English names appearing in text are incorrectly redacted
- Solution: Use explicit author list with full names; disable partial matching for documents with many common name words

**Issue: Author names in citations not detected**
- Symptom: "As Smith et al. (2023) showed..." retains author name when Smith is an author
- Solution: Use self-citation detection mode which specifically targets author names in citation contexts

### 2. Institutional Affiliation Masking

Automatically detect and replace institutional identifiers including universities, research institutes, departments, and laboratories with generic placeholders.

```python
from scripts.main import BlindReviewSanitizer

sanitizer = BlindReviewSanitizer()

# Institutional detection uses pattern matching
text_with_institutions = """
Department of Computer Science, Stanford University
Max Planck Institute for Informatics
MIT CSAIL Laboratory
"""

# Process institutional information
result = sanitizer._remove_institutions(text_with_institutions)
print(result)
# Output: [INSTITUTION], [INSTITUTION], [INSTITUTION]
```

**Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `institution_keywords` | List[str] | No | Custom keywords for institution detection | Predefined list |
| `strict_mode` | bool | No | Only match explicit institutional patterns, reduces false positives | False |

**Best Practices:**
- ✅ **Add custom institution keywords** for specialized domains (e.g., "Consortium", "Network") not in default list
- ✅ **Use strict mode for documents** with many false positives (e.g., medical texts mentioning "hospitals" frequently)
- ✅ **Check institutional abbreviations** which may not be caught by full-name patterns (e.g., "JHU" for Johns Hopkins)
- ✅ **Verify geographical references** as some may indirectly reveal institutions (e.g., "Silicon Valley campus")

**Common Issues and Solutions:**

**Issue: Generic words flagged as institutions**
- Symptom: "Research group" or "technical institute" in generic contexts are replaced
- Solution: Enable strict mode or add negative context patterns to exclude generic usage

**Issue: Multi-campus institutions not fully masked**
- Symptom: "University of California, Berkeley" partially masked as "[INSTITUTION], Berkeley"
- Solution: Pre-process to combine multi-part institutional names before sanitization

### 3. Acknowledgment Section Management

Intelligently identify and handle acknowledgment sections, funding disclosures, and personal thanks that may reveal author identity or institutional affiliations.

```python
from scripts.main import BlindReviewSanitizer

# Initialize without keeping acknowledgments
sanitizer = BlindReviewSanitizer(keep_acknowledgments=False)

# Sample acknowledgment section
acknowledgment_text = """Acknowledgments

We thank Professor Johnson for valuable discussions and the NSF Grant #12345 for funding.
This work was conducted at the Advanced Computing Center.

References"""

lines = acknowledgment_text.split('\n')
processed_lines = sanitizer.remove_acknowledgments(lines)

print('\n'.join(processed_lines))
# Output: [ACKNOWLEDGMENTS REMOVED] followed by References section
```

**Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `keep_acknowledgments` | bool | No | Retain acknowledgment section instead of removing | False |
| `acknowledgment_titles` | List[str] | No | Custom section titles to recognize | Predefined list |

**Best Practices:**
- ✅ **Remove acknowledgments by default** for strict double-blind review requirements
- ✅ **Check funding disclosure requirements** - some journals require anonymized funding info in acknowledgments
- ✅ **Use custom titles** for non-English manuscripts or specialized formats
- ✅ **Review anonymized funding numbers** - grant numbers sometimes contain institutional codes

**Common Issues and Solutions:**

**Issue: Acknowledgment section not detected**
- Symptom: Acknowledgments section with non-standard title (e.g., "Gratitude", "Credits") remains in document
- Solution: Add custom acknowledgment titles or manually review document structure

**Issue: Essential content in acknowledgment section**
- Symptom: Data availability statements or ethical approvals mentioned in acknowledgments are removed
- Solution: Move essential content to appropriate sections before sanitization; use `keep_acknowledgments` with manual redaction

### 4. Self-Citation Detection and Neutralization

Identify excessive self-citations and first-person references to previous work that could deanonymize the submission, replacing them with neutral language.

```python
from scripts.main import BlindReviewSanitizer

# Mode 1: Replace self-citations
sanitizer_replace = BlindReviewSanitizer(highlight_self_cites=False)

text_with_self_cites = """
As we showed in our previous work [1], the algorithm achieves 95% accuracy.
Our earlier study demonstrated similar findings [2].
In our prior research, we found that...
"""

result = sanitizer_replace.sanitize_text(text_with_self_cites)
print(result)
# Output: As [PREVIOUS WORK] described in their previous study [1]...

# Mode 2: Highlight only (for manual review)
sanitizer_highlight = BlindReviewSanitizer(highlight_self_cites=True)
result_highlighted = sanitizer_highlight.sanitize_text(text_with_self_cites)
print(result_highlighted)
# Output: As [SELF-CITE: we showed in our previous work] [1]...
```

**Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `highlight_self_cites` | bool | No | Only highlight self-citations without replacing | False |
| `neutral_replacements` | Dict[str, str] | No | Custom replacement phrases | Default mappings |

**Best Practices:**
- ✅ **Use highlight mode first** to review all self-citations before final replacement
- ✅ **Maintain citation integrity** - ensure numbered references remain valid after text changes
- ✅ **Check context carefully** - some self-references may be essential for narrative flow
- ✅ **Balance anonymity with scholarship** - excessive neutralization may make the paper less clear

**Common Issues and Solutions:**

**Issue: Legitimate references flagged as self-citations**
- Symptom: General references to "our approach" or "our method" in methodology sections are flagged
- Solution: Review highlighted instances manually; adjust context to use passive voice before sanitization

**Issue: Citations broken after text replacement**
- Symptom: "As we showed [1]" becomes "As [PREVIOUS WORK] showed [1]" but reference [1] is the author's paper
- Solution: This is expected behavior - reviewers should not see author self-citations; citations will be restored post-review

### 5. Multi-Format Document Processing

Process manuscripts in DOCX, Markdown, and plain text formats with format-aware handling to preserve structure while sanitizing content.

```python
from pathlib import Path
from scripts.main import BlindReviewSanitizer, get_processor

# Initialize sanitizer
sanitizer = BlindReviewSanitizer(authors=["Dr. Smith", "Prof. Jones"])

# Process different file formats
input_files = [
    Path("paper.docx"),
    Path("manuscript.md"),
    Path("article.txt")
]

for input_file in input_files:
    if input_file.exists():
        processor = get_processor(input_file, sanitizer)
        output_file = input_file.parent / f"{input_file.stem}-blinded{input_file.suffix}"
        processor.process(input_file, output_file)
        print(f"Processed: {input_file} → {output_file}")
```

**Supported Formats:**

| Format | Extension | Features Preserved | Special Handling |
|--------|-----------|-------------------|------------------|
| Microsoft Word | .docx | Styles, tables, formatting | python-docx library required |
| Markdown | .md | Headers, lists, links | Line-based processing |
| Plain Text | .txt | Line breaks, spacing | Line-based processing |

**Best Practices:**
- ✅ **Prefer DOCX for complex documents** with tables and formatting; preserves structure best
- ✅ **Use Markdown for version-controlled manuscripts** (e.g., Git-tracked LaTeX alternatives)
- ✅ **Validate output formatting** especially for complex tables and mathematical content
- ✅ **Check figure/table captions** which may contain author information in DOCX files

**Common Issues and Solutions:**

**Issue: DOCX formatting lost after processing**
- Symptom: Complex formatting, styles, or tracked changes are stripped
- Solution: Accept all changes and remove comments before sanitization; save as clean document first

**Issue: Unicode/UTF-8 characters corrupted in text files**
- Symptom: Special characters (accents, mathematical symbols) display incorrectly
- Solution: Ensure files are UTF-8 encoded; specify encoding explicitly if needed

### 6. Audit Trail and Verification Reporting

Generate comprehensive logs of all sanitization actions for transparency, quality assurance, and compliance verification.

```python
from scripts.main import BlindReviewSanitizer

sanitizer = BlindReviewSanitizer(
    authors=["Alice Chen", "Bob Smith"]
)

# Process document
text = """Alice Chen and Bob Smith from MIT present their findings.
Contact: alice@mit.edu"""

sanitized = sanitizer.sanitize_text(text)

# Review audit trail
print("=== Audit Trail ===")
for item in sanitizer.removed_items:
    print(f"- {item}")

# Output shows:
# - Institution: MIT
# - Email: alice@mit.edu
```

**Audit Information Captured:**

| Information Type | Description | Use Case |
|-----------------|-------------|----------|
| `author_names` | List of author names redacted | Verification, re-identification post-review |
| `institutions` | Institutional affiliations masked | Compliance checking |
| `contact_info` | Emails and phone numbers removed | Privacy verification |
| `acknowledgments` | Whether acknowledgment section was removed | Journal requirement verification |
| `self_citations` | Count and type of self-citations neutralized | Review bias prevention |

**Best Practices:**
- ✅ **Save audit logs** for compliance verification and post-review re-identification
- ✅ **Review audit trail** before submission to ensure nothing was missed
- ✅ **Use logs for quality improvement** - identify patterns in missed redactions
- ✅ **Share logs with co-authors** for multi-author verification

**Common Issues and Solutions:**

**Issue: Audit log too verbose**
- Symptom: Every instance of common words (e.g., "University") is logged separately
- Solution: Use summary mode for large documents; filter by category for review

**Issue: Sensitive information in audit logs**
- Symptom: Audit logs themselves contain the sensitive data that was removed
- Solution: Store logs securely; consider encrypting or limiting access to audit data

---

## Complete Workflow Example

**From input to output for double-blind journal submission:**

```bash
# Step 1: Prepare input manuscript
cp my_paper.docx manuscript.docx

# Step 2: Run sanitization with explicit author list
python scripts/main.py \
  --input manuscript.docx \
  --authors "Zhang San,Li Si,Wang Wu" \
  --output manuscript-blinded.docx

# Step 3: Review highlighted self-citations (optional but recommended)
python scripts/main.py \
  --input manuscript-blinded.docx \
  --highlight-self-cites \
  --output manuscript-reviewed.docx

# Step 4: Verify audit trail
cat sanitization_report.txt

# Step 5: Final check for remaining identifiers
grep -i "zhang\|tsinghua\|peking" manuscript-blinded.docx || echo "No matches found - good!"
```

**Python API Usage:**

```python
from pathlib import Path
from scripts.main import BlindReviewSanitizer, get_processor

def sanitize_for_submission(
    input_path: Path,
    authors: list[str],
    output_dir: Path
) -> Path:
    """
    Complete sanitization workflow for journal submission.
    """
    # Initialize sanitizer with strict settings
    sanitizer = BlindReviewSanitizer(
        authors=authors,
        keep_acknowledgments=False,
        highlight_self_cites=False
    )
    
    # Determine output path
    output_path = output_dir / f"{input_path.stem}-blinded{input_file.suffix}"
    
    # Get appropriate processor
    processor = get_processor(input_path, sanitizer)
    
    # Process document
    processor.process(input_path, output_path)
    
    # Log results
    print(f"Sanitization complete:")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Items redacted: {len(sanitizer.removed_items)}")
    
    # Generate summary by category
    categories = {}
    for item in sanitizer.removed_items:
        category = item.split(":")[0]
        categories[category] = categories.get(category, 0) + 1
    
    print("  Breakdown:")
    for cat, count in categories.items():
        print(f"    - {cat}: {count}")
    
    return output_path

# Execute workflow
authors = ["Zhang San", "Li Si", "Wang Wu"]
output = sanitize_for_submission(
    Path("paper.docx"),
    authors,
    Path("./submissions/")
)
```

**Expected Output Files:**

```
submissions/
├── manuscript-blinded.docx    # Anonymized manuscript
├── sanitization_report.txt    # Audit trail of all redactions
└── verification_checklist.md  # Pre-submission verification
```

---

## Common Patterns

### Pattern 1: Standard Double-Blind Journal Submission

**Scenario**: Preparing a research paper for submission to Nature, Science, or IEEE Transactions with strict double-blind review.

```json
{
  "input_file": "neural_network_study.docx",
  "authors": ["Alice Chen", "Bob Smith", "Carol Wang"],
  "keep_acknowledgments": false,
  "highlight_self_cites": false,
  "expected_processing": [
    "Remove all author names from title page",
    "Replace institutional affiliations with [INSTITUTION]",
    "Remove complete acknowledgment section",
    "Neutralize all self-citations",
    "Remove email addresses and ORCID IDs"
  ]
}
```

**Workflow:**
1. Run sanitization with full author list and strict settings
2. Manually verify title page, headers, and footers
3. Check supplementary materials for author metadata
4. Submit blinded version with separate cover letter

**Output Example:**
```
Original: Alice Chen¹, Bob Smith²
          ¹MIT CSAIL, ²Stanford AI Lab
          Email: achen@mit.edu

Sanitized: [AUTHOR NAME]¹, [AUTHOR NAME]²
           ¹[INSTITUTION], ²[INSTITUTION]
           [EMAIL]
```

### Pattern 2: Conference Submission with Anonymization Period

**Scenario**: Submitting to computer science conference (e.g., ICML, NeurIPS) that requires anonymization during review but allows deanonymization after acceptance.

```json
{
  "input_file": "deep_learning_paper.pdf",
  "authors": ["Anonymous"],
  "keep_acknowledgments": true,
  "highlight_self_cites": true,
  "special_requirements": [
    "Preserve citations to arXiv preprints",
    "Keep URLs and repository links",
    "Anonymize GitHub repositories"
  ]
}
```

**Workflow:**
1. Use highlight mode to identify all potential identity leaks
2. Review highlighted sections manually
3. Replace GitHub URLs with anonymous placeholder
4. Keep general acknowledgments but remove personal thanks
5. Create separate deanonymization key for post-acceptance

**Output Example:**
```
Original: Our implementation is available at 
          github.com/alicechen/bert-optimizer

Sanitized: Our implementation is available at
           [ANONYMOUS_REPOSITORY] 
           (link will be provided upon acceptance)
```

### Pattern 3: Medical Journal with Funding Disclosure Requirements

**Scenario**: Submitting to medical journal requiring funding disclosure but author anonymity during review.

```json
{
  "input_file": "clinical_trial_results.docx",
  "authors": ["Dr. Sarah Johnson", "Prof. Michael Lee"],
  "keep_acknowledgments": true,
  "special_handling": [
    "Anonymize investigator names in acknowledgments",
    "Keep funding sources with neutral language",
    "Remove institutional affiliations",
    "Preserve ethics committee information"
  ]
}
```

**Workflow:**
1. Keep acknowledgments section but redact investigator names
2. Retain funding information with anonymized grant numbers
3. Remove all institutional identifiers
4. Maintain IRB/ethics committee references
5. Add note about funding disclosure availability

**Output Example:**
```
Original: We thank Dr. Sarah Johnson and the Clinical Research 
          Team at Mayo Clinic. Funded by NIH R01CA12345.

Sanitized: We thank [INVESTIGATOR] and the Clinical Research
          Team at [INSTITUTION]. Funded by [FUNDING_SOURCE].
```

### Pattern 4: Resubmission After Previous Rejection

**Scenario**: Revising and resubmitting a previously rejected manuscript to a new journal, requiring fresh anonymization.

```json
{
  "input_file": "revised_paper.docx",
  "authors": ["Original Author", "New Collaborator"],
  "updated_metadata": {
    "added_authors": ["New Collaborator"],
    "removed_content": ["previous_institutional_mention"],
    "new_acknowledgments": ["new_funding_source"]
  },
  "verification_steps": [
    "Check for editor response letter remnants",
    "Remove previous submission tracking numbers",
    "Update all institutional references",
    "Verify no reviewer comments remain"
  ]
}
```

**Workflow:**
1. Create clean copy without previous submission metadata
2. Update author list to include new collaborators
3. Remove all references to previous submission or reviews
4. Sanitize with updated author information
5. Verify no "response to reviewers" content remains in main text

**Output Example:**
```
Before: "We have revised the manuscript based on Nature 
          Medicine reviewer comments..."

After: Complete removal of all previous submission references
```

---

## Quality Checklist

**Pre-sanitization Checks:**
- [ ] **CRITICAL**: Verify you have permission to anonymize all authors' contributions
- [ ] Confirm target journal/conference anonymization requirements
- [ ] Compile complete list of all author names and name variants
- [ ] Identify all institutional affiliations including secondary appointments
- [ ] Check for author photos or bios in supplementary materials
- [ ] Review document properties/metadata for author information
- [ ] Verify no tracked changes or comments contain author identity

**During Sanitization:**
- [ ] Run initial scan with highlight mode to preview all changes
- [ ] Verify author list is complete (check initials, surnames, full names)
- [ ] Confirm acknowledgment handling matches journal policy
- [ ] Check self-citation replacement maintains citation flow
- [ ] Review institution masking in complex affiliations
- [ ] Validate contact information removal (emails, phone, addresses)
- [ ] Ensure figure captions and table notes are processed

**Post-sanitization Verification:**
- [ ] **CRITICAL**: Search for author surnames in output document
- [ ] Check headers, footers, and page numbers for institutional branding
- [ ] Verify document properties are cleared (File → Properties → Remove Personal Information)
- [ ] Review all figures for embedded author metadata or watermarks
- [ ] Check PDF metadata if converting to PDF for submission
- [ ] Validate that citations remain properly numbered after text changes
- [ ] Ensure mathematical notation and symbols preserved correctly

**Before Submission:**
- [ ] **CRITICAL**: Have a non-author colleague verify anonymity
- [ ] Confirm acknowledgments handling meets journal ethical guidelines
- [ ] Check that funding disclosure requirements are met
- [ ] Verify supplementary materials are also sanitized
- [ ] Test submission system upload with sanitized file
- [ ] Create deanonymization key mapping for post-acceptance
- [ ] Save audit trail securely for potential post-review verification

---

## Common Pitfalls

**Input Preparation Issues:**
- ❌ **Processing tracked changes without accepting** → Hidden revision marks reveal author identity
  - ✅ Accept all changes and remove comments before sanitization
  
- ❌ **Ignoring document metadata** → File properties contain author name and institution
  - ✅ Clear document properties: File → Info → Check for Issues → Inspect Document
  
- ❌ **Forgetting supplementary materials** → Author info in supplementary PDFs not sanitized
  - ✅ Process all supplementary files through sanitizer with same settings
  
- ❌ **Incomplete author lists** → Co-author names appear in text unrecognized
  - ✅ Include all authors, middle names, and common name variants

**Sanitization Strategy Issues:**
- ❌ **Over-aggressive replacement** → Legitimate citations and references damaged
  - ✅ Use highlight mode first; review each replacement context
  
- ❌ **Under-sanitization** → Subtle identifiers remain (e.g., "our previous work")
  - ✅ Enable all detection modules; manually review after automated processing
  
- ❌ **Inconsistent handling** → Some instances replaced, others missed
  - ✅ Use case-insensitive matching; verify regex patterns cover all variants
  
- ❌ **Context-insensitive replacement** → "University research" becomes "[INSTITUTION] research"
  - ✅ Review outputs carefully; consider strict mode for ambiguous terms

**Output Validation Issues:**
- ❌ **Assuming perfect automation** → Automated tools miss edge cases
  - ✅ Always perform manual verification pass
  
- ❌ **Submitting without verification** → Undetected author info reaches reviewers
  - ✅ Use search function to look for author surnames before submission
  
- ❌ **Losing audit trail** → No record of what was changed for post-review
  - ✅ Save and securely store sanitization reports
  
- ❌ **Forgetting downstream effects** → Citations broken, cross-references lost
  - ✅ Verify document integrity after sanitization

---

## Troubleshooting

**Problem: Author names still appear in output**
- Symptoms: Specific author names visible after sanitization
- Causes:
  - Author name not in provided list
  - Different spelling or name variant used
  - Name embedded in image/figure (not text)
  - Name in document metadata, not body text
- Solutions:
  - Add all name variants to authors list
  - Search for partial matches (surnames only)
  - Check document properties and clear metadata
  - Manually review figures and images

**Problem: Excessive false positives**
- Symptoms: Common words like "University" or "Center" replaced throughout document
- Causes:
  - Overly broad pattern matching
  - Generic terms in specialized vocabulary
  - Institution keywords used in non-institutional contexts
- Solutions:
  - Enable strict mode for more precise matching
  - Add context requirements (e.g., must be capitalized)
  - Use explicit author/institution lists instead of pattern matching
  - Post-process to restore legitimate usage

**Problem: Document formatting corrupted**
- Symptoms: Styles lost, fonts changed, layout broken after DOCX processing
- Causes:
  - Complex formatting not supported by python-docx
  - Tracked changes or comments interfering
  - Corrupted original document
- Solutions:
  - Accept all changes and remove comments before processing
  - Save document in compatibility mode if using advanced features
  - Use plain text or Markdown for highly formatted documents
  - Manually verify and correct formatting post-processing

**Problem: Self-citations not detected**
- Symptoms: First-person references to previous work remain in text
- Causes:
  - Non-standard phrasing not matching patterns
  - Citations in different format (e.g., "our Nature 2020 paper")
  - Citations in footnotes not processed
- Solutions:
  - Add custom patterns for specific phrasing
  - Use highlight mode to identify missed citations
  - Check all document sections including footnotes/endnotes
  - Manually review for unique self-reference formulations

**Problem: Acknowledgment section not removed**
- Symptoms: Acknowledgments section remains in output
- Causes:
  - Non-standard section title
  - Section formatted as body text, not heading
  - Acknowledgments integrated into other sections
- Solutions:
  - Add custom acknowledgment titles for your document style
  - Manually identify and mark acknowledgment boundaries
  - Use section-based processing if document has clear structure
  - Review document outline to identify acknowledgment location

**Problem: References/citations broken**
- Symptoms: Citation numbers wrong, references missing, cross-references broken
- Causes:
  - Text replacement affecting citation indices
  - Reference list entries removed that are still cited
  - Self-citation replacement removing reference context
- Solutions:
  - Use neutral replacement that preserves citation markers
  - Verify reference list integrity after processing
  - Consider citations as protected text
  - Manually correct citation numbering if needed

**Problem: python-docx import error**
- Symptoms: "Error: python-docx not installed" when processing DOCX files
- Causes:
  - Required dependency not installed
  - Virtual environment not activated
- Solutions:
  - Install dependency: `pip install python-docx`
  - Check Python environment and activate if needed
  - Consider using text-based formats if dependencies unavailable
  - Verify pip and Python installation

---

## References

Available in `references/` directory:

- (No reference files currently available for this skill)

**External Resources:**
- COPE Guidelines for Peer Review: https://publicationethics.org/resources/guidelines
- IEEE Anonymization Guidelines: https://www.ieee.org/publications/rights/index.html
- ACM Policy on Authorship: https://www.acm.org/publications/policies/authorship

---

## Scripts

Located in `scripts/` directory:

- `main.py` - Main sanitization engine with document processing logic

---

## Limitations and Considerations

⚠️ **Important Limitations:**

1. **Not Foolproof**: Automated sanitization cannot guarantee complete anonymity. Always perform manual verification.

2. **Context Blindness**: Pattern matching may miss context-dependent identifiers or incorrectly flag legitimate content.

3. **Image Processing**: This tool processes text only. Images, figures, and embedded objects may contain identifying information not detected.

4. **LaTeX Support**: Limited support for LaTeX source files. Consider using LaTeX-specific tools for LaTeX manuscripts.

5. **Language Support**: Optimized for English and Chinese. Other languages may have reduced accuracy.

⚠️ **Ethical and Legal Considerations:**

- **Author Consent**: Ensure all authors consent to anonymization before submission
- **Copyright**: Anonymization does not change copyright ownership
- **Data Availability**: Some journals require non-anonymized versions for data/code availability statements
- **Post-Acceptance**: Plan for deanonymization process after paper acceptance

---

**Last Updated**: 2026-02-09  
**Skill ID**: 162  
**Version**: 2.0 (K-Dense Standard)

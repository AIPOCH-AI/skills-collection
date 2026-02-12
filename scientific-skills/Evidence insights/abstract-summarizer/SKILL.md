---
name: abstract-summarizer
description: Transform lengthy academic papers into concise, structured 250-word abstracts 
  capturing background, methods, results, and conclusions. Optimized for research papers, 
  theses, and technical reports across scientific disciplines.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Abstract Summarizer

## Overview

AI-powered academic summarization tool that condenses complex research papers into publication-ready structured abstracts while preserving scientific accuracy and key findings.

**Key Capabilities:**
- **Multi-Format Input**: Process PDFs, text, URLs, or clipboard content
- **Structured Output**: Background, Objective, Methods, Results, Conclusion format
- **Word Count Enforcement**: Strict 250-word limit with validation
- **Quantitative Preservation**: Retains key numbers, statistics, and effect sizes
- **Discipline Adaptation**: Optimized for STEM, medical, and social sciences
- **Batch Processing**: Summarize multiple papers efficiently

## When to Use

**✅ Use this skill when:**
- Creating conference abstracts from full papers
- Preparing literature review summaries
- Quickly assessing paper relevance for reading decisions
- Generating executive summaries for stakeholders
- Drafting journal submission abstracts
- Teaching students how to write scientific abstracts
- Building annotated bibliographies

**❌ Do NOT use when:**
- Source material is highly nuanced philosophy/literary critique → Use `humanities-text-analyzer`
- Mathematical proofs require detailed explanation → Use `math-theorem-simplifier`
- Legal documents or contracts → Use `legal-document-summarizer`
- Creative writing or fiction → Use `creative-writing-editor`
- Patient medical records (HIPAA concerns) → Use clinical documentation tools only

**Integration:**
- **Upstream**: `pdf-text-extractor` (content extraction), `citation-formatter` (reference handling)
- **Downstream**: `conference-abstract-adaptor` (format adjustment), `journal-matchmaker` (submission prep)

## Core Capabilities

### 1. Structured Abstract Generation

Extract and condense key sections into standard format:

```python
from scripts.summarizer import AbstractSummarizer

summarizer = AbstractSummarizer()

# Generate from PDF
abstract = summarizer.summarize(
    source="paper.pdf",
    format="structured",  # structured, plain, or executive
    word_limit=250,
    discipline="biomedical"  # affects terminology handling
)

print(abstract.text)
# Output: Background → Objective → Methods → Results → Conclusion
```

**Output Structure:**
```
**Background**: [Context and problem statement]
**Objective**: [Research goal and hypotheses]
**Methods**: [Study design, sample, key methods]
**Results**: [Primary findings with statistics]
**Conclusion**: [Implications and significance]

---
Word count: 247/250
```

### 2. Quantitative Data Preservation

Ensure numbers and statistics are accurately retained:

```python
# Extract and verify quantitative results
quant_results = summarizer.extract_quantitative(
    text=paper_content,
    priority="high"  # keep all numbers vs. representative samples
)

# Validate against original
validation = summarizer.verify_accuracy(
    abstract=abstract,
    source=paper_content
)
```

**Preserves:**
- Sample sizes (n=128)
- Effect sizes (Cohen's d = 0.82)
- P-values (p < 0.001)
- Confidence intervals (95% CI: [0.45, 0.78])
- Percentages and absolute numbers

### 3. Multi-Disciplinary Adaptation

Adjust extraction strategy by field:

```bash
# Biomedical paper
python scripts/main.py --input paper.pdf --field biomedical

# Physics paper  
python scripts/main.py --input paper.pdf --field physics

# Social science paper
python scripts/main.py --input paper.pdf --field social-science
```

**Field-Specific Handling:**
| Field | Focus Areas | Special Handling |
|-------|-------------|------------------|
| **Biomedical** | Study design, statistical significance, clinical relevance | Preserve P-values, effect sizes |
| **Physics** | Theoretical framework, experimental setup, precision | Keep measurement uncertainties |
| **CS/Engineering** | Algorithm performance, benchmarks, complexity | Retain accuracy percentages |
| **Social Science** | Methodology, sample demographics, theoretical contribution | Preserve effect descriptions |

### 4. Batch Literature Processing

Summarize multiple papers for systematic reviews:

```python
from scripts.batch import BatchProcessor

batch = BatchProcessor()

# Process directory of papers
summaries = batch.summarize_directory(
    directory="literature_review/",
    output_format="csv",  # or json, markdown
    include_metadata=True  # title, authors, year
)

# Generate review matrix
matrix = batch.create_summary_matrix(summaries)
matrix.save("review_matrix.csv")
```

**Output:**
- Individual abstract files
- Comparative summary table
- Key findings synthesis document

## Common Patterns

### Pattern 1: Clinical Trial Summary

**Template for RCTs and clinical studies:**

```json
{
  "paper_type": "clinical_trial",
  "key_elements": [
    "Study design (RCT, cohort, case-control)",
    "Population (n, inclusion/exclusion)",
    "Intervention details",
    "Primary endpoint",
    "Key results (efficacy, safety)",
    "Clinical significance"
  ],
  "emphasis": "P-values, confidence intervals, adverse events"
}
```

**Example Output:**
```
**Background**: Current treatments for X disease have limited efficacy.
**Objective**: Evaluate Drug Y's safety and efficacy in patients with X.
**Methods**: Double-blind RCT (n=342) comparing Drug Y vs placebo for 12 weeks.
**Results**: Primary endpoint achieved (67% vs 32% response, p<0.001, OR=4.2). 
            Adverse events mild (headache 12%, nausea 8%).
**Conclusion**: Drug Y significantly improves outcomes with acceptable safety profile.
```

### Pattern 2: Basic Science Research

**Template for laboratory/mechanistic studies:**

```json
{
  "paper_type": "basic_science",
  "key_elements": [
    "Research question/hypothesis",
    "Model system (cell line, animal, in vitro)",
    "Key methods (CRISPR, Western blot, etc.)",
    "Mechanistic findings",
    "Biological significance"
  ],
  "emphasis": "Molecular mechanisms, pathway diagrams"
}
```

**Example Output:**
```
**Background**: The role of Protein X in Disease Y progression is unknown.
**Objective**: Determine if Protein X regulates Pathway Z in Disease Y.
**Methods**: CRISPR knockout in cell lines, Western blot analysis, mouse model.
**Results**: Protein X deletion reduced Pathway Z activation by 78% (p<0.01). 
            In vivo, knockout mice showed 45% less disease progression.
**Conclusion**: Protein X is a critical regulator of Pathway Z and potential therapeutic target.
```

### Pattern 3: Meta-Analysis Summary

**Template for systematic reviews and meta-analyses:**

```json
{
  "paper_type": "meta_analysis",
  "key_elements": [
    "Search strategy and databases",
    "Number of studies included",
    "Total sample size",
    "Pooled effect size",
    "Heterogeneity assessment",
    "Quality of evidence"
  ],
  "emphasis": "I² values, funnel plots, GRADE assessment"
}
```

**Example Output:**
```
**Background**: Previous trials of Intervention X show conflicting results.
**Objective**: Systematically evaluate efficacy through meta-analysis.
**Methods**: PRISMA-guided search of PubMed, Embase, Cochrane (through 2024). 
            23 RCTs (n=4,847) met inclusion criteria.
**Results**: Significant benefit observed (SMD=0.42, 95% CI [0.28, 0.56], p<0.001). 
            Moderate heterogeneity (I²=45%). Quality: moderate.
**Conclusion**: Intervention X shows modest efficacy with moderate certainty evidence.
```

### Pattern 4: Methodology/Algorithm Paper

**Template for methods and computational papers:**

```json
{
  "paper_type": "methodology",
  "key_elements": [
    "Problem with existing methods",
    "Novel approach description",
    "Key innovations",
    "Performance benchmarks",
    "Comparison to state-of-the-art"
  ],
  "emphasis": "Accuracy, speed, scalability metrics"
}
```

**Example Output:**
```
**Background**: Current algorithms for Problem X are computationally expensive.
**Objective**: Develop efficient method with improved accuracy.
**Methods**: Novel graph neural network architecture with attention mechanism. 
            Validated on 5 benchmark datasets.
**Results**: 3.2× faster than current methods with 12% accuracy improvement 
            (p<0.001). Scales to datasets with 10M+ nodes.
**Conclusion**: Method achieves superior performance with practical computational requirements.
```

## Complete Workflow Example

**From PDF to submission-ready abstract:**

```bash
# Step 1: Extract text from PDF
python scripts/extract.py --input paper.pdf --output paper.txt

# Step 2: Generate structured abstract
python scripts/main.py \
  --input paper.txt \
  --field biomedical \
  --format structured \
  --word-limit 250 \
  --output abstract.md

# Step 3: Verify accuracy
python scripts/verify.py \
  --abstract abstract.md \
  --source paper.txt \
  --check-quantitative \
  --output verification_report.txt

# Step 4: Adapt for specific journal
python scripts/adapt.py \
  --abstract abstract.md \
  --journal "nature_medicine" \
  --output submission_abstract.txt
```

**Python API:**

```python
from scripts.summarizer import AbstractSummarizer
from scripts.validator import AccuracyValidator

# Initialize
summarizer = AbstractSummarizer()
validator = AccuracyValidator()

# Summarize
with open("paper.pdf", "rb") as f:
    abstract = summarizer.summarize(
        source=f,
        discipline="clinical",
        word_limit=250
    )

# Verify numbers are accurate
is_accurate = validator.check_quantitative(
    abstract=abstract,
    source_pdf="paper.pdf"
)

if is_accurate:
    abstract.save("final_abstract.txt")
else:
    discrepancies = validator.get_discrepancies()
    print(f"Review needed: {discrepancies}")
```

## Quality Checklist

**Pre-Summarization:**
- [ ] Source document is complete (not truncated)
- [ ] PDF/text is machine-readable (not scanned images)
- [ ] Document is research paper (not editorial, review, or news)

**During Summarization:**
- [ ] All key sections identified (don't miss Results)
- [ ] Quantitative data preserved accurately
- [ ] Statistical significance indicators kept
- [ ] No interpretation added beyond source

**Post-Summarization:**
- [ ] Word count ≤ 250
- [ ] All 5 sections present
- [ ] **CRITICAL**: Numbers match source document
- [ ] Standalone comprehensibility (makes sense without paper)
- [ ] No citations or references in abstract
- [ ] Technical terms used correctly

**Before Use:**
- [ ] **CRITICAL**: Fact-check all numbers against original
- [ ] Verify author names and affiliations correct
- [ ] Ensure conclusions don't overstate findings

## Common Pitfalls

**Accuracy Issues:**
- ❌ **Misrepresenting statistics** → "Significant improvement" when p>0.05
  - ✅ Preserve exact P-values and confidence intervals
  
- ❌ **Oversimplifying complex findings** → "Drug works" vs nuanced efficacy data
  - ✅ Include effect sizes and confidence intervals

- ❌ **Missing adverse events** → Only reporting positive results
  - ✅ Include safety data for clinical studies

**Structure Issues:**
- ❌ **Methods too detailed** → Protocol steps in abstract
  - ✅ High-level study design only

- ❌ **Results without context** → Numbers without interpretation
  - ✅ Brief clinical/scientific significance

- ❌ **Conclusion overstates** → "Cure for cancer" from preclinical data
  - ✅ Match conclusion to evidence level

**Word Count Issues:**
- ❌ **Exceeding 250 words** → Journal rejection
  - ✅ Strict enforcement with real-time counter

- ❌ **Too short (<150 words)** → Missing key information
  - ✅ Minimum thresholds by section

## References

Available in `references/` directory:

- `abstract_templates.md` - Discipline-specific abstract formats
- `quantitative_checklist.md` - Number verification guidelines  
- `disciplinary_guidelines.md` - Field-specific conventions
- `journal_requirements.md` - Word limits by publisher
- `example_abstracts.md` - High-quality examples by type

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for summarization
- `summarizer.py` - Core abstract generation engine
- `extractor.py` - PDF and text extraction
- `validator.py` - Accuracy checking and verification
- `batch_processor.py` - Multi-document processing
- `adapter.py` - Journal-specific formatting

## Limitations

- **Language**: Optimized for English-language papers
- **Length**: Papers >50 pages may need section-by-section processing
- **Complexity**: Highly mathematical content may lose nuance
- **Figures**: Cannot interpret images, charts, or graphs (text only)
- **Domain**: Best for empirical research; struggles with pure theory papers
- **Context**: May miss field-specific conventions without discipline flag

---

**📝 Note: This tool generates draft abstracts for efficiency, but all summaries require human review before submission. Always verify that numbers, statistics, and conclusions accurately reflect the original paper.**

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | str | Required |  |
| `--text` | str | Required | Direct text input |
| `--url` | str | Required | URL to fetch paper from |
| `--output` | str | Required | Output file path |
| `--format` | str | 'structured' | Output format |

---
name: authorship-credit-gen
description: Generate standardized author contribution statements following CRediT 
  (Contributor Roles Taxonomy) standards. Creates formal contribution declarations 
  for manuscripts with support for 14 contribution roles, co-first authors, 
  corresponding authors, and multiple output formats for journal submission.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Authorship CRediT Generator

## Overview

Standardized contribution statement generator that creates transparent, machine-readable author attribution following the CRediT taxonomy adopted by major scientific publishers (Nature, Science, Elsevier, PLOS).

**Key Capabilities:**
- **CRediT Taxonomy**: All 14 standardized contribution roles
- **Multiple Formats**: Text, XML, JSON for different journals
- **Special Author Types**: Co-first authors, co-corresponding authors
- **Affiliation Integration**: Institution and ORCID support
- **Validation**: Check for ICMJE authorship criteria compliance
- **Visual Summary**: Contribution matrix and Venn diagrams

## When to Use

**✅ Use this skill when:**
- Preparing manuscript submission to journals requiring CRediT statements
- Documenting author contributions for collaborative projects
- Resolving authorship disputes with transparent role assignment
- Creating institutional authorship policies
- Training students on responsible authorship practices
- Reviewing grant applications requiring contribution transparency
- Post-publication clarification of author roles

**❌ Do NOT use when:**
- Determining who should be an author → Use ICMJE criteria first
- Resolving authorship disputes without discussion → Facilitate conversation first
- Ghostwriting or gift authorship situations → Address ethical concerns
- Single-author papers → Contribution statement not needed
- Preprints without journal requirements → Optional unless mandated

**Integration:**
- **Upstream**: `manuscript-prep-assistant` (author list finalization), `grant-proposal-assistant` (contributor documentation)
- **Downstream**: `blind-review-sanitizer` (anonymization for submission), `conflict-of-interest-checker` (ethics compliance)

## Core Capabilities

### 1. CRediT Role Assignment

Map author contributions to 14 standardized roles:

```python
from scripts.credit_generator import CRediTGenerator

generator = CRediTGenerator()

# Define author contributions
authors = [
    {
        "name": "Dr. Sarah Chen",
        "orcid": "0000-0001-2345-6789",
        "affiliation": "Stanford University",
        "roles": ["Conceptualization", "Methodology", "Writing - Original Draft"]
    },
    {
        "name": "Dr. Michael Rodriguez", 
        "orcid": "0000-0002-3456-7890",
        "affiliation": "MIT",
        "roles": ["Data Curation", "Formal Analysis", "Software"]
    }
]

# Generate statement
statement = generator.generate(
    authors=authors,
    format="text",
    language="en"
)

print(statement)
# Dr. Sarah Chen: Conceptualization, Methodology, Writing - Original Draft
# Dr. Michael Rodriguez: Data Curation, Formal Analysis, Software
```

**14 CRediT Roles:**
| Role | Description | Typical Contributors |
|------|-------------|---------------------|
| **Conceptualization** | Ideas, research goals | PI, senior researchers |
| **Data Curation** | Data management, annotation | Data managers, bioinformaticians |
| **Formal Analysis** | Statistical analysis | Statisticians, data scientists |
| **Funding Acquisition** | Grant writing, financial support | PIs, research administrators |
| **Investigation** | Experiments, data collection | Lab members, research assistants |
| **Methodology** | Protocol development | Methods specialists, PIs |
| **Project Administration** | Coordination, logistics | Lab managers, PIs |
| **Resources** | Materials, reagents, samples | Collaborators, core facilities |
| **Software** | Programming, code development | Bioinformaticians, programmers |
| **Supervision** | Mentoring, oversight | PIs, senior scientists |
| **Validation** | Verification, replication | Independent validators |
| **Visualization** | Figures, charts, graphics | Graphic designers, authors |
| **Writing - Original Draft** | Initial manuscript | Lead author, writing committee |
| **Writing - Review & Editing** | Critical revision | All authors, editor |

### 2. Special Author Designations

Handle co-first and corresponding author situations:

```python
# Complex authorship with special designations
statement = generator.generate(
    authors=authors,
    co_first_authors=["Dr. Sarah Chen", "Dr. Michael Rodriguez"],
    corresponding_authors=["Dr. Sarah Chen"],
    co_corresponding=["Prof. James Wilson"],  # Multiple corresponding
    deceased_authors=["Dr. Robert Brown"],  # Posthumous authorship
    current_affiliation={
        "Dr. Sarah Chen": "Now at Genentech"
    }
)
```

**Special Notations:**
- **Co-first authors**: *Authors contributed equally
- **Corresponding**: †Corresponding author
- **Deceased**: ‡Deceased
- **Current affiliation**: Present address
- **Author deceased**: Special footnote handling

### 3. Multi-Format Output

Generate statements for different journal requirements:

```python
# Text format (most journals)
text_statement = generator.generate(authors=authors, format="text")

# XML format (Elsevier, Springer)
xml_statement = generator.generate(authors=authors, format="xml")

# JSON (machine-readable)
json_statement = generator.generate(authors=authors, format="json")

# YAML (human + machine readable)
yaml_statement = generator.generate(authors=authors, format="yaml")

# LaTeX (direct manuscript insertion)
latex_statement = generator.generate(authors=authors, format="latex")
```

**Format Comparison:**
| Format | Best For | Example Journals |
|--------|----------|------------------|
| **Text** | General use, readability | Nature, Science, PLOS |
| **XML** | Structured data, submission systems | Elsevier, Springer |
| **JSON** | API integration, databases | PubMed, ORCID |
| **YAML** | Human editing + processing | GitHub, preprints |
| **LaTeX** | Direct manuscript insertion | arXiv, Overleaf |

### 4. Authorship Validation

Check compliance with authorship standards:

```python
# Validate against ICMJE criteria
validation = generator.validate(
    authors=authors,
    criteria="icmje"  # ICMJE, CRediT, or institutional
)

if validation.issues:
    print("⚠️  Authorship concerns:")
    for issue in validation.issues:
        print(f"  - {issue.author}: {issue.concern}")
        print(f"    Recommendation: {issue.recommendation}")
```

**Validation Checks:**
- Substantial contributions (ICMJE criteria 1)
- Drafting/revising (ICMJE criteria 2)
- Approval of final version (ICMJE criteria 3)
- Accountability (ICMJE criteria 4)
- No ghost authors detected
- No gift authorship red flags
- Senior author supervision present
- Data creator included

## Common Patterns

### Pattern 1: Standard Research Paper

**Scenario**: 4-author research paper with clear roles.

```bash
# Interactive mode for clarity
python scripts/main.py --interactive

# Or command line
python scripts/main.py \
  --authors "Dr_Chen:C1,C6,C10,C13|Dr_Rodriguez:C2,C3,C9,C14|Dr_Kim:C5,C7,C11|Student_Wang:C5,C12,C14" \
  --corresponding "Dr_Chen" \
  --format text \
  --output contribution.txt
```

**Typical Distribution:**
- PI: Conceptualization, Funding, Supervision, Writing
- Postdoc: Methodology, Analysis, Software, Review
- Technician: Investigation, Validation
- Student: Investigation, Visualization, Review

### Pattern 2: Large Consortium

**Scenario**: 50+ author consortium paper (e.g., GWAS study).

```python
# Batch processing for large groups
contributions = generator.process_consortium(
    members_file="consortium_members.csv",
    working_groups={
        "Analysis": ["Formal Analysis", "Software"],
        "Writing": ["Writing - Original Draft", "Writing - Review & Editing"],
        "Steering": ["Conceptualization", "Supervision", "Project Administration"]
    },
    group_authors=True  # Group by contribution type
)
```

**Consortium Best Practices:**
- Group by contribution category
- Subgroup leaders get additional roles
- Writing committee designated
- Analysis core acknowledged
- Steering committee explicit

### Pattern 3: Industry-Academic Collaboration

**Scenario**: Pharma company + university collaboration.

```python
# Handle sensitive industry contributions
statement = generator.generate(
    authors=authors,
    industry_partners=["Pfizer", "Genentech"],
    funding_disclosure="This work was funded by Pfizer Inc. (grant #12345)",
    employee_authors=["Dr_Smith@Pfizer"],
    conflict_notes="Dr. Smith is an employee of Pfizer Inc."
)
```

**Industry Considerations:**
- Clear funding disclosure
- Employee status noted
- IP considerations
- Data sharing limitations
- Publication rights

### Pattern 4: Preprint to Journal Transition

**Scenario**: Update contribution statement from preprint to final submission.

```bash
# Read preprint version
python scripts/main.py \
  --input preprint_contribution.txt \
  --format json \
  --output contribution_structure.json

# Modify for journal (add new analyses, revision roles)
python scripts/main.py \
  --input contribution_structure.json \
  --add-roles "Dr_Chen:Validation|Reviewer_A:C14" \
  --format xml \
  --output journal_credit.xml
```

## Complete Workflow Example

**From raw contributions to journal submission:**

```bash
# Step 1: Collect author inputs via form/survey
python scripts/main.py \
  --collect-contributions \
  --template survey_template.json \
  --output raw_responses.json

# Step 2: Validate and flag issues
python scripts/main.py \
  --input raw_responses.json \
  --validate \
  --criteria icmje \
  --output validation_report.txt

# Step 3: Generate consensus version
python scripts/main.py \
  --input raw_responses.json \
  --resolve-conflicts \
  --output consensus_contributions.json

# Step 4: Create multiple format outputs
python scripts/main.py \
  --input consensus_contributions.json \
  --format text --output credit_statement.txt

python scripts/main.py \
  --input consensus_contributions.json \
  --format xml --output credit.xml

python scripts/main.py \
  --input consensus_contributions.json \
  --format json --output credit.json

# Step 5: Generate visual summary
python scripts/main.py \
  --input consensus_contributions.json \
  --visualize \
  --type matrix \
  --output contribution_matrix.png
```

**Python API:**

```python
from scripts.credit_generator import CRediTGenerator
from scripts.validator import AuthorshipValidator
from scripts.visualizer import ContributionVisualizer

# Initialize
generator = CRediTGenerator()
validator = AuthorshipValidator()
visualizer = ContributionVisualizer()

# Step 1: Define author contributions
authors = [
    {
        "name": "Dr. Sarah Chen",
        "orcid": "0000-0001-2345-6789",
        "affiliation": "Stanford University",
        "roles": ["Conceptualization", "Methodology", "Supervision"]
    },
    # ... more authors
]

# Step 2: Validate
validation = validator.validate_icmje(authors)
if validation.concerns:
    print("⚠️  Authorship issues detected:")
    for concern in validation.concerns:
        print(f"  {concern}")

# Step 3: Generate statements
text = generator.generate_text(authors)
xml = generator.generate_xml(authors)
json_data = generator.generate_json(authors)

# Step 4: Create visual summary
matrix = visualizer.create_contribution_matrix(authors)
matrix.save("contribution_matrix.png")

# Step 5: Export complete package
generator.export_package(
    authors=authors,
    formats=["text", "xml", "json"],
    visuals=["matrix", "venn"],
    output_dir="contribution_package/"
)

print("✅ Contribution package generated")
print(f"   Text statement: contribution_package/statement.txt")
print(f"   XML for submission: contribution_package/credit.xml")
print(f"   Visual matrix: contribution_package/matrix.png")
```

## Quality Checklist

**Content Accuracy:**
- [ ] All authors agree on role assignments
- [ ] Roles accurately reflect actual contributions
- [ ] No significant contributors omitted
- [ ] No minimal contributors inflated
- [ ] Special designations (co-first, corresponding) agreed upon

**CRediT Compliance:**
- [ ] Uses official 14-role taxonomy
- [ ] Role names spelled correctly
- [ ] No invented/custom roles
- [ ] Multiple roles allowed per author
- [ ] All substantial contributions captured

**ICMJE Compliance:**
- [ ] All authors meet ICMJE criteria
- [ ] Substantial intellectual contribution documented
- [ ] Drafting/revising work acknowledged
- [ ] Final approval documented
- [ ] Accountability accepted

**Before Submission:**
- [ ] **CRITICAL**: All authors reviewed and approved
- [ ] Corresponding author verified contact info
- [ ] ORCID iDs included if available
- [ ] Affiliations current and correct
- [ ] Conflict of interest statements prepared

## Common Pitfalls

**Role Assignment Issues:**
- ❌ **Role inflation** → Everyone has every role
  - ✅ Be specific; not everyone needs every role

- ❌ **Ghost authors** → Significant contributors not listed
  - ✅ Include all who meet ICMJE criteria

- ❌ **Gift authorship** → Minimal contributors included
  - ✅ Be honest about contribution levels

- ❌ **Vague roles** → "Writing" without specifying which type
  - ✅ Distinguish original draft vs. review/editing

**Communication Issues:**
- ❌ **No author discussion** → PI decides unilaterally
  - ✅ Discuss contributions early and openly

- ❌ **Last-minute changes** → Adding authors after submission
  - ✅ Lock author list before submission

- ❌ **Disputes unresolved** → Disagreements left lingering
  - ✅ Address conflicts before manuscript submission

**Technical Issues:**
- ❌ **Inconsistent formatting** → Mixed styles in same paper
  - ✅ Follow journal's specific requirements

- ❌ **Missing ORCIDs** → Incomplete author metadata
  - ✅ Collect ORCIDs from all authors

## References

Available in `references/` directory:

- `credit_taxonomy_official.md` - Official CRediT taxonomy documentation
- `icmje_criteria.md` - ICMJE authorship recommendations
- `journal_requirements.md` - Specific requirements by publisher
- `authorship_ethics.md` - COPE and institutional guidelines
- `consensus_templates.md` - Templates for author discussions
- `dispute_resolution.md` - Handling authorship conflicts

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for contribution generation
- `credit_generator.py` - Core CRediT statement creation
- `validator.py` - ICMJE and ethical compliance checking
- `parser.py` - Parse various input formats
- `exporter.py` - Multi-format output generation
- `visualizer.py` - Contribution matrices and charts
- `consensus.py` - Facilitate author agreement

## Limitations

- **Cannot Determine Authorship**: Tool records contributions, doesn't decide who qualifies
- **No Dispute Resolution**: Cannot resolve conflicting claims about contributions
- **Context-Dependent**: Meaning of roles varies by field
- **Journal-Specific**: Some journals have additional requirements
- **Cultural Differences**: Authorship norms vary by country/institution
- **No Legal Authority**: Cannot override institutional authorship policies

---

**⚖️ Ethical Note: Transparent authorship is fundamental to scientific integrity. This tool facilitates documentation, but cannot replace honest discussion among collaborators about who contributed what. When in doubt, err on the side of inclusion and transparency.**

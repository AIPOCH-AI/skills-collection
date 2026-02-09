---
name: bio-ontology-mapper
description: Map unstructured biomedical text to standardized ontologies (SNOMED CT, 
  MeSH, ICD-10) for terminology normalization and semantic interoperability. Extracts 
  medical entities and maps to standardized codes with confidence scoring.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Bio-Ontology Mapper

## Overview

Biomedical terminology normalization tool that maps free-text clinical and scientific concepts to standardized ontologies for semantic interoperability and data harmonization.

**Key Capabilities:**
- **Multi-Ontology Support**: SNOMED CT, MeSH, ICD-10, LOINC, RxNorm
- **Entity Extraction**: NER for diseases, symptoms, procedures, drugs
- **Fuzzy Matching**: Handle typos, abbreviations, and synonyms
- **Confidence Scoring**: Reliability metrics for each mapping
- **Batch Processing**: Normalize large datasets efficiently
- **Cross-Mapping**: Translate between ontology systems

## When to Use

**✅ Use this skill when:**
- Normalizing clinical notes for EHR integration
- Standardizing terminology for multi-site studies
- Mapping legacy data to modern ontologies
- Preparing data for clinical data warehouses
- Converting free-text to coded data for analysis
- Building semantic search for biomedical literature
- Teaching biomedical informatics principles

**❌ Do NOT use when:**
- Clinical diagnosis or decision support → Use clinical decision tools
- Real-time patient care → Latency too high for acute settings
- Replacing expert coding → Use for pre-coding, final review needed
- Processing PHI without de-identification → Ensure HIPAA compliance

**Integration:**
- **Upstream**: `clinical-data-cleaner` (data preparation), `ehr-semantic-compressor` (text extraction)
- **Downstream**: `clinical-data-cleaner` (SDTM mapping), `unstructured-medical-text-miner` (NLP pipelines)

## Core Capabilities

### 1. Entity Recognition and Mapping

Extract and map biomedical entities to ontologies:

```python
from scripts.mapper import BioOntologyMapper

mapper = BioOntologyMapper()

# Map clinical text
result = mapper.map_text(
    text="Patient has diabetes and hypertension, taking metformin",
    ontologies=["snomed", "mesh", "rxnorm"],
    confidence_threshold=0.7
)

for entity in result.entities:
    print(f"{entity.text} → {entity.concept_id} ({entity.ontology})")
    print(f"  Preferred: {entity.preferred_term}")
    print(f"  Confidence: {entity.confidence:.2f}")
```

**Supported Ontologies:**
| Ontology | Domain | Use Case |
|----------|--------|----------|
| **SNOMED CT** | Clinical | EHR interoperability |
| **MeSH** | Literature | PubMed indexing |
| **ICD-10** | Billing | Diagnosis codes |
| **LOINC** | Labs | Test result standardization |
| **RxNorm** | Drugs | Medication normalization |
| **HGNC** | Genes | Gene name standardization |

### 2. Cross-Ontology Translation

Map concepts between different ontologies:

```python
# Cross-map SNOMED to ICD-10
translation = mapper.cross_map(
    source_id="22298006",  # SNOMED: Myocardial infarction
    source_ontology="snomed",
    target_ontology="icd10"
)

print(f"ICD-10: {translation.target_id} - {translation.target_term}")
# Output: I21.9 - Acute myocardial infarction, unspecified
```

**Cross-Mapping Coverage:**
- SNOMED CT ↔ ICD-10-CM (clinical modifications)
- MeSH ↔ SNOMED CT (literature to clinical)
- RxNorm ↔ ATC (drug classifications)
- LOINC ↔ SNOMED (lab to clinical)

### 3. Batch Normalization

Process large datasets:

```python
# Batch process CSV
results = mapper.batch_map(
    input_file="clinical_terms.csv",
    text_column="diagnosis_description",
    ontologies=["snomed", "icd10"],
    output_format="csv",
    max_workers=4
)

# Results include:
# - Original term
# - Mapped concept ID
# - Confidence score
# - Alternative mappings (if ambiguous)
```

**Performance:**
- ~100 terms/second (with caching)
- ~20 terms/second (API lookup)
- Parallel processing for large datasets

### 4. Confidence Scoring and Validation

Assess mapping reliability:

```python
scoring = mapper.score_mapping(
    term="heart attack",
    candidate="22298006",  # Myocardial infarction
    factors=["string_similarity", "context_match", "frequency"]
)

print(f"Overall confidence: {scoring.confidence:.2f}")
print(f"Breakdown: {scoring.factors}")
```

**Scoring Factors:**
- **String similarity**: Levenshtein distance, n-grams
- **Context match**: Surrounding words alignment
- **Frequency**: Common usage in corpus
- **Semantic similarity**: Vector embeddings

## Common Patterns

### Pattern 1: Clinical Note Normalization

**Scenario**: Convert free-text diagnoses to SNOMED codes.

```bash
# Normalize clinical notes
python scripts/main.py \
  --input notes.csv \
  --column diagnosis_text \
  --ontology snomed \
  --threshold 0.8 \
  --output coded_diagnoses.csv

# Results: "heart attack" → 22298006 (Myocardial infarction)
```

**Post-Processing:**
- Review low-confidence mappings (<0.8)
- Handle ambiguous terms manually
- Validate against clinical context

### Pattern 2: Literature Indexing

**Scenario**: Map research paper keywords to MeSH.

```python
# Map keywords to MeSH
mesh_terms = mapper.map_to_mesh(
    keywords=["cancer immunotherapy", "checkpoint inhibitors", "PD-1"],
    include_tree_numbers=True,
    include_qualifiers=True
)

for term in mesh_terms:
    print(f"{term.input} → {term.descriptor}")
    print(f"  Tree: {term.tree_numbers}")
    print(f"  Entry terms: {term.synonyms}")
```

### Pattern 3: Drug Name Normalization

**Scenario**: Standardize medication names across datasets.

```python
# Normalize drug names
drugs = ["Tylenol", "Advil", "Motrin", "acetaminophen"]

for drug in drugs:
    result = mapper.map_to_rxnorm(drug)
    print(f"{drug} → {result.rxcui}: {result.name}")
    # Tylenol → 161: Acetaminophen
    # Advil → 5640: Ibuprofen
    # Motrin → 5640: Ibuprofen
```

### Pattern 4: EHR Data Harmonization

**Scenario**: Merge data from multiple hospital systems.

```bash
# Harmonize diagnoses from 3 hospitals
python scripts/main.py \
  --batch \
  --inputs "hospital_a.csv,hospital_b.csv,hospital_c.csv" \
  --target-ontology snomed \
  --cross-map-to icd10 \
  --output harmonized_data.csv
```

## Complete Workflow Example

**From free-text to coded database:**

```python
from scripts.mapper import BioOntologyMapper
from scripts.validator import MappingValidator

# Initialize
mapper = BioOntologyMapper()
validator = MappingValidator()

# Step 1: Extract entities from text
clinical_note = "Patient has Type 2 diabetes and hypertension..."
entities = mapper.extract_entities(clinical_note)

# Step 2: Map to SNOMED
mappings = []
for entity in entities:
    mapping = mapper.map_to_snomed(
        entity.text,
        context=clinical_note,
        top_n=3
    )
    mappings.append(mapping)

# Step 3: Validate mappings
for mapping in mappings:
    validation = validator.validate(
        mapping,
        check_clinical_plausibility=True
    )
    if not validation.is_valid:
        print(f"Review needed: {mapping}")

# Step 4: Export to database format
db_records = [m.to_database_record() for m in mappings]
```

## Quality Checklist

**Pre-Mapping:**
- [ ] Text preprocessed (lowercase, punctuation handled)
- [ ] Abbreviations expanded where possible
- [ ] Language identified (multilingual support)

**During Mapping:**
- [ ] Confidence threshold appropriate (>0.7 for clinical)
- [ ] Multiple candidates considered for ambiguous terms
- [ ] Context used for disambiguation

**Post-Mapping:**
- [ ] Low-confidence mappings flagged for review
- [ ] Unmapped terms logged
- [ ] **CRITICAL**: Clinical expert validation for high-stakes use

**Before Production:**
- [ ] Mapping accuracy validated on gold standard
- [ ] False positive rate acceptable (<5%)
- [ ] Recall acceptable for use case (>90%)
- [ ] API rate limits respected

## Common Pitfalls

**Mapping Errors:**
- ❌ **Abbreviation ambiguity** → "MI" = Myocardial infarction OR Michigan
  - ✅ Use context; flag for manual review

- ❌ **Outdated terms** → Old terminology not in current ontology
  - ✅ Use historical mappings; update terminology

- ❌ **False confidence** → High score for wrong concept
  - ✅ Always review top-3 candidates

**Technical Issues:**
- ❌ **API failures** → No local fallback
  - ✅ Implement caching; use local reference files

- ❌ **Version mismatches** → Different ontology versions
  - ✅ Track ontology version used

- ❌ **PHI exposure** → Sending patient data to external APIs
  - ✅ De-identify before API calls; use local processing when possible

## References

Available in `references/` directory:

- `snomed_ct_guide.md` - SNOMED CT hierarchy and relationships
- `mesh_structure.md` - MeSH tree structure and qualifiers
- `ontology_mappings.md` - Crosswalks between systems
- `nlp_best_practices.md` - Biomedical text processing
- `api_documentation.md` - External service integration
- `validation_datasets.md` - Gold standard test sets

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for mapping
- `mapper.py` - Core ontology mapping engine
- `extractor.py` - Named entity recognition
- `cross_mapper.py` - Ontology-to-ontology translation
- `scorer.py` - Confidence calculation
- `batch_processor.py` - Large dataset handling
- `validator.py` - Mapping quality checks
- `caching.py` - Local storage for frequent lookups

## Limitations

- **Ambiguity**: Many-to-many mappings common; context required
- **Coverage**: Rare diseases and new concepts may not be in ontologies
- **Versioning**: Ontology updates can change mappings over time
- **Language**: Best support for English; other languages limited
- **Real-time**: Not suitable for time-critical clinical applications
- **API Dependency**: Requires internet for most lookups (caching helps)

---

**⚠️ Critical: Ontology mapping is for research and data integration, not clinical decision-making. Always validate mappings with domain experts before use in patient care contexts. Never process PHI without appropriate de-identification and compliance measures.**

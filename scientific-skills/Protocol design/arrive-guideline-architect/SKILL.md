---
name: arrive-guideline-architect
description: Generate ARRIVE 2.0 compliant animal research protocols with structured 
  experimental design, sample size calculations, and reporting checklists. Ensures 
  transparency, reproducibility, and ethical compliance in in vivo studies.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# ARRIVE Guideline Architect

## Overview

AI-powered protocol design tool that creates publication-ready animal research protocols compliant with ARRIVE 2.0 guidelines (Animal Research: Reporting of In Vivo Experiments). Generates structured documentation for ethical review, transparent reporting, and reproducible science.

**Key Capabilities:**
- **Protocol Generation**: Complete ARRIVE 2.0 compliant study protocols
- **Sample Size Calculator**: Statistical power analysis with justification
- **Compliance Checker**: Validate existing protocols against ARRIVE standards
- **Randomization Schemes**: Generate and document allocation strategies
- **Ethics Support**: IACUC protocol templates and animal welfare documentation
- **Reporting Templates**: Manuscript preparation with required elements

## When to Use

**✅ Use this skill when:**
- Designing new animal studies requiring ethical approval
- Preparing IACUC (Institutional Animal Care and Use Committee) applications
- Writing manuscripts for journals requiring ARRIVE compliance (PLOS, Nature, etc.)
- Validating existing protocols for transparency and completeness
- Training researchers on animal research best practices
- Planning multi-site studies requiring standardized protocols
- Reviewing protocols for grant applications

**❌ Do NOT use when:**
- Human clinical trials → Use `clinical-protocol-designer`
- In vitro studies (cell culture only) → No ARRIVE requirements apply
- Field studies on wild animals → Use specialized wildlife research guidelines
- Veterinary clinical cases → Use veterinary case report standards
- Systematic reviews/meta-analyses → Use PRISMA guidelines

**Integration:**
- **Upstream**: `sample-size-power-calculator` (statistical design)
- **Downstream**: `iacuc-protocol-drafter` (ethics submission), `manuscript-prep-assistant` (publication)

## Core Capabilities

### 1. ARRIVE 2.0 Protocol Builder

Generate complete protocols covering all Essential 10 items:

```python
from scripts.arrive_builder import ARRIVEBuilder

builder = ARRIVEBuilder()

# Generate full protocol
protocol = builder.generate_protocol(
    title="Efficacy of Compound X in Type 2 Diabetes Mouse Model",
    species="Mus musculus",
    strain="db/db",
    groups=[
        {"name": "Control", "n": 15, "treatment": "Vehicle"},
        {"name": "Low Dose", "n": 15, "treatment": "10 mg/kg"},
        {"name": "High Dose", "n": 15, "treatment": "50 mg/kg"}
    ],
    primary_endpoint="Fasting blood glucose reduction",
    duration_days=28
)

protocol.save("protocol.md")
```

**Generates:**
1. **Study Design**: Experimental groups, timelines, endpoints
2. **Sample Size**: Power calculations with justification
3. **Inclusion/Exclusion**: Animal selection criteria
4. **Randomization**: Allocation method (software/hardware)
5. **Blinding**: Who, when, how blinding implemented
6. **Outcome Measures**: Primary, secondary, exploratory endpoints
7. **Statistical Methods**: Analysis plan, software, significance level
8. **Experimental Animals**: Species, strain, sex, age, weight, source
9. **Experimental Procedures**: Detailed methods with timing
10. **Results Reporting**: Data presentation templates

### 2. Sample Size Calculator

Statistical power analysis with ARRIVE-compliant justification:

```python
from scripts.sample_size import SampleSizeCalculator

calc = SampleSizeCalculator()

# Calculate with effect size
result = calc.calculate(
    test_type="two_sample_t_test",
    effect_size=0.8,  # Cohen's d
    alpha=0.05,
    power=0.80,
    expected_dropout=0.10  # 10% attrition
)

# Output: n=26 per group (total 78, accounting for 10% dropout)
```

**Features:**
- **Effect Size Selection**: Cohen's d, odds ratio, hazard ratio
- **Multiple Comparisons**: Bonferroni, FDR corrections
- **Dropout Adjustment**: Account for expected attrition
- **Justification Text**: Auto-generate sample size rationale
- **Power Curves**: Generate power calculations for various sample sizes

### 3. Compliance Validator

Check existing protocols against ARRIVE 2.0:

```bash
python scripts/validate.py --input my_protocol.md --format markdown
```

**Output:**
```
✅ Essential 10: 10/10 complete
⚠️  Recommended Set: 8/15 complete
   Missing: Data sharing statement, Conflict of interest

Detailed Report:
- Item 1 (Study Design): Complete
- Item 2 (Sample Size): Complete  
- Item 3 (Inclusion Criteria): Missing - add exclusion criteria
- ...
```

**Validation Levels:**
- **Essential 10**: Required for all publications
- **Recommended Set**: Required by top-tier journals
- **Journal-Specific**: Custom checks for specific publishers

### 4. Randomization & Blinding Generator

Create allocation schemes with documentation:

```python
from scripts.randomization import RandomizationGenerator

gen = RandomizationGenerator()

# Generate allocation
allocation = gen.generate(
    n_animals=45,
    n_groups=3,
    method="block_randomization",  # or "simple", "stratified"
    block_size=6,
    seed=42  # For reproducibility
)

# Output allocation table
allocation.save("allocation_table.csv")
allocation.generate_blinding_key("blinding_key.xlsx")
```

**Methods Supported:**
- Simple randomization
- Block randomization (fixed/random block sizes)
- Stratified randomization (by sex, age, baseline)
- Covariate-adaptive minimization

## Common Patterns

### Pattern 1: Drug Efficacy Study

**Template for therapeutic intervention studies:**

```json
{
  "study_type": "efficacy",
  "species": "Mus musculus",
  "model": "Disease model (e.g., db/db diabetic mice)",
  "intervention": "Test compound",
  "groups": [
    "Sham control",
    "Disease control (vehicle)",
    "Positive control (reference drug)",
    "Test compound (low dose)",
    "Test compound (high dose)"
  ],
  "primary_endpoint": "Disease biomarker",
  "secondary_endpoints": ["Safety markers", "Histopathology"],
  "sampling_timepoints": ["Baseline", "Week 2", "Week 4"]
}
```

**Key Considerations:**
- Include positive control for assay validation
- Multiple doses to establish dose-response
- Power calculation based on expected effect size
- Sample size accounts for disease variability

### Pattern 2: Toxicology Study

**Template for safety assessment:**

```json
{
  "study_type": "toxicology",
  "species": "Rat",
  "duration": "28-day repeat dose",
  "dose_levels": ["Vehicle", "Low", "Mid", "High", "Limit"],
  "endpoints": [
    "Clinical observations (daily)",
    "Body weight (twice weekly)",
    "Food consumption",
    "Clinical pathology (hematology, chemistry)",
    "Necropsy and organ weights",
    "Histopathology"
  ],
  "recovery_groups": true  # 14-day recovery period
}
```

**Key Considerations:**
- Dose selection based on MTD (maximum tolerated dose)
- Recovery groups for reversibility assessment
- Comprehensive clinical pathology panels
- Histopathology on all high-dose and control animals

### Pattern 3: Behavioral Study

**Template for neuroscience/behavioral research:**

```json
{
  "study_type": "behavioral",
  "species": "C57BL/6 mice",
  "tests": [
    "Open field (anxiety/locomotion)",
    "Elevated plus maze (anxiety)",
    "Novel object recognition (memory)",
    "Fear conditioning (learning)"
  ],
  "controls": [
    "Positive pharmacological control",
    "Negative control (vehicle)"
  ],
  "blinding": "Video analysis performed blinded",
  "randomization": "Latin square design for test order"
}
```

**Key Considerations:**
- Counterbalance test order (learning effects)
- Blind video analysis to prevent bias
- Standardized testing environment (lighting, noise)
- Experimenter training and reliability testing

### Pattern 4: Surgical Model Study

**Template for procedure-based research:**

```json
{
  "study_type": "surgical",
  "procedure": "Myocardial infarction (LAD ligation)",
  "species": "Sprague-Dawley rats",
  "sham_control": true,
  "perioperative_care": {
    "analgesia": "Buprenorphine SR",
    "antibiotics": "Enrofloxacin",
    "monitoring": "Temperature, respiration, pain scoring"
  },
  "outcome_measures": [
    "Survival rate",
    "Echocardiography",
    "Histological infarct size"
  ],
  "humane_endpoints": ["Severe distress", "Inability to ambulate"]
}
```

**Key Considerations:**
- Detailed surgical protocol with timing
- Comprehensive perioperative care
- Clear humane endpoints (refinement)
- Sham surgery controls for procedure effects
- Pain management per IACUC guidelines

## Complete Workflow Example

**From study concept to IACUC submission:**

```bash
# Step 1: Create study brief
cat > study_brief.json << EOF
{
  "title": "Novel Compound X in Diabetic Nephropathy",
  "species": "Mouse",
  "strain": "db/db",
  "groups": 4,
  "primary_endpoint": "Albuminuria reduction",
  "duration_weeks": 12
}
EOF

# Step 2: Generate protocol
python scripts/main.py \
  --input study_brief.json \
  --output protocol.md \
  --include-checklist

# Step 3: Calculate sample size
python scripts/sample_size.py \
  --test t_test \
  --effect-size 0.8 \
  --alpha 0.05 \
  --power 0.80 \
  --dropout 0.10

# Step 4: Generate randomization
python scripts/randomize.py \
  --n-total 64 \
  --n-groups 4 \
  --method block \
  --output allocation.csv

# Step 5: Validate ARRIVE compliance
python scripts/validate.py \
  --input protocol.md \
  --format pdf \
  --output compliance_report.pdf
```

**Output Files:**
```
output/
├── protocol.md                    # Complete ARRIVE protocol
├── sample_size_justification.txt  # Statistical rationale
├── allocation.csv                 # Randomization table
├── blinding_key.xlsx             # Blinding documentation
├── compliance_report.pdf         # ARRIVE checklist
└├── iacuc_supplemental.pdf       # Ethics committee materials
```

## Quality Checklist

**Pre-Study:**
- [ ] **CRITICAL**: IACUC approval obtained before starting
- [ ] Sample size adequately powered (≥80%)
- [ ] Randomization method documented and reproducible
- [ ] Blinding plan clear for all assessors
- [ ] Humane endpoints defined with clear criteria
- [ ] Inclusion/exclusion criteria prespecified

**During Study:**
- [ ] Randomization followed without deviations
- [ ] Blinding maintained (unblinding only for safety)
- [ ] All animals accounted for (CONSORT-style flow diagram)
- [ ] Adverse events documented and reported to IACUC
- [ ] Sample collection at predetermined timepoints

**Reporting:**
- [ ] All Essential 10 items addressed in manuscript
- [ ] CONSORT-style flow diagram for animal studies
- [ ] Raw data available (or sharing statement)
- [ ] Conflict of interest disclosed
- [ ] Funding sources acknowledged

## Common Pitfalls

**Design Issues:**
- ❌ **Inadequate controls** → Cannot distinguish treatment from confounding effects
  - ✅ Always include appropriate controls (vehicle, positive, sham)
  
- ❌ **Convenience sampling** → Selection bias
  - ✅ Random allocation to treatment groups

- ❌ **Unblinded assessment** → Observer bias
  - ✅ Blinded outcome assessment whenever possible

**Sample Size Issues:**
- ❌ **No power calculation** → Underpowered study, false negatives
  - ✅ Calculate sample size a priori with justification

- ❌ **Ignoring dropout** → Final sample too small
  - ✅ Account for expected attrition (typically 10-20%)

**Reporting Issues:**
- ❌ **Selective outcome reporting** → Publication bias
  - ✅ Pre-register primary and secondary endpoints

- ❌ **Missing animal numbers** → Transparency concerns
  - ✅ Report n for every analysis

## References

Available in `references/` directory:

- `arrive_2.0_guidelines.md` - Official ARRIVE 2.0 checklist and explanations
- `sample_size_guidelines.md` - Statistical methods for animal studies
- `species_specific_requirements.md` - Mouse, rat, zebrafish considerations
- `journal_compliance.md` - Requirements by publisher (Nature, Science, Cell)
- `statistical_methods.md` - Analysis approaches for common designs
- `iacuc_templates.md` - Ethics committee application templates
- `example_protocols.md` - Published compliant protocols as examples

## Scripts

Located in `scripts/` directory:

- `main.py` - Protocol generation CLI
- `arrive_builder.py` - Core protocol builder
- `sample_size.py` - Power analysis calculator
- `randomization.py` - Allocation scheme generator
- `validate.py` - ARRIVE compliance checker
- `checklist_generator.py` - Interactive checklist tool
- `export.py` - Multi-format output (PDF, Word, Markdown)

## Limitations

- **Template-Based**: Generates standard protocols; highly specialized studies may need customization
- **No Statistical Analysis**: Calculates sample size but does not perform analysis
- **No Real-Time Monitoring**: Protocol generation only; does not track actual experiments
- **Species Coverage**: Optimized for mice and rats; other species may need adaptation
- **Regulatory Variation**: IACUC requirements vary by institution; may need local customization

---

**🐾 Remember: The 3Rs (Replacement, Reduction, Refinement) are ethical imperatives. This tool supports Reduction (optimal sample sizes) and Refinement (better experimental design), but consider Replacement alternatives (in vitro, in silico) whenever possible.**

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--interactive` | flag | - | **Interactive mode**: Run wizard with guided prompts (uses `input()` for user interaction). Recommended for first-time users or complex study designs. |
| `--input` | str | Required | Input JSON file path (batch/automation mode) |
| `--output` | str | "protocol.md" | Output file path |
| `--validate` | str | Required | Validate existing protocol file |
| `--checklist` | str | Required | Generate ARRIVE 2.0 checklist |
| `--format` | str | "markdown" | Output format: markdown, pdf, or docx |

**Usage Modes:**
- **Automation Mode (Recommended for CI/CD)**: Use `--input` with JSON configuration file
- **Interactive Mode**: Use `--interactive` for guided setup via prompts

**Example - Automation Mode:**
```bash
# Create JSON config
cat > study_config.json << 'EOF'
{
  "title": "Diabetes Drug Study",
  "species": "Mus musculus",
  "strain": "db/db",
  "groups": 4,
  "animals_per_group": 15
}
EOF

# Generate protocol
python scripts/main.py --input study_config.json --output protocol.md
```

**Example - Interactive Mode:**
```bash
# Launch interactive wizard
python scripts/main.py --interactive
```

---
name: inclusion-criteria-gen
description: 'Generate and optimize clinical trial subject inclusion/exclusion criteria
  to balance

  scientific rigor with recruitment feasibility. Trigger when users need to design

  eligibility criteria for new trials, optimize existing criteria for better enrollment,

  analyze competitor trial eligibility patterns, or assess recruitment barriers.

  Use cases: Protocol design, eligibility optimization, recruitment strategy,

  competitive eligibility analysis, feasibility assessment.

  '
version: 1.0.0
category: General
tags:
- pharma
- clinical-trials
- inclusion-criteria
- exclusion-criteria
- protocol-design
- recruitment
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Inclusion Criteria Generator

Generate and optimize clinical trial subject inclusion/exclusion criteria to balance scientific rigor with recruitment feasibility.

## Use Cases

- **Protocol Design**: Create initial eligibility criteria for new clinical trials
- **Criteria Optimization**: Refine existing criteria to improve enrollment without compromising safety/efficacy
- **Competitive Analysis**: Analyze eligibility patterns across similar trials
- **Recruitment Strategy**: Identify and mitigate barriers to enrollment
- **Feasibility Assessment**: Evaluate if proposed criteria are realistic for target population

## Usage

### CLI Usage

```bash
# Generate criteria from study design
python scripts/main.py generate \
  --indication "Type 2 Diabetes" \
  --phase "Phase 2" \
  --population "adults" \
  --duration "24 weeks" \
  --output criteria.json

# Optimize existing criteria
python scripts/main.py optimize \
  --input current_criteria.json \
  --enrollment-target 200 \
  --current-enrollment 120 \
  --output optimized_criteria.json

# Analyze criteria complexity
python scripts/main.py analyze \
  --input criteria.json \
  --output analysis_report.json

# Compare with competitor trials
python scripts/main.py benchmark \
  --input criteria.json \
  --condition "Type 2 Diabetes" \
  --output benchmark_report.json
```

### Python API

```python
from scripts.main import CriteriaGenerator, CriteriaOptimizer

# Generate new criteria
generator = CriteriaGenerator()
criteria = generator.generate(
    indication="Type 2 Diabetes",
    phase="Phase 2",
    population="adults",
    study_duration="24 weeks",
    endpoints=["HbA1c reduction", "weight change"]
)

# Optimize existing criteria
optimizer = CriteriaOptimizer()
optimized = optimizer.optimize(
    criteria=existing_criteria,
    enrollment_target=200,
    current_enrollment=120,
    retention_rate=0.85
)

# Analyze criteria complexity
analysis = optimizer.analyze_complexity(criteria)
```

## Input Format

### Study Design Parameters

```json
{
  "indication": "Type 2 Diabetes Mellitus",
  "phase": "Phase 2",
  "population": "adults",
  "age_range": {"min": 18, "max": 75},
  "study_duration": "24 weeks",
  "treatment_type": "oral",
  "primary_endpoints": ["HbA1c change from baseline"],
  "safety_considerations": ["cardiovascular risk"],
  "concomitant_meds_allowed": ["metformin"]
}
```

### Existing Criteria Format

```json
{
  "inclusion_criteria": [
    {
      "id": "I1",
      "criterion": "Age 18-75 years",
      "rationale": "Adult population per regulatory guidance",
      "category": "demographics"
    }
  ],
  "exclusion_criteria": [
    {
      "id": "E1",
      "criterion": "HbA1c < 7.0% or > 11.0%",
      "rationale": "Ensure measurable treatment effect",
      "category": "disease_severity"
    }
  ]
}
```

## Output Format

### Generated/Optimized Criteria

```json
{
  "inclusion_criteria": [
    {
      "id": "I1",
      "criterion": "Age 18-75 years, inclusive",
      "category": "demographics",
      "rationale": "Adult population; upper limit for safety",
      "priority": "required",
      "impact": "low"
    }
  ],
  "exclusion_criteria": [
    {
      "id": "E1",
      "criterion": "HbA1c < 7.5% or > 10.5% at screening",
      "category": "disease_severity",
      "rationale": "Optimal range for detecting treatment effect",
      "priority": "required",
      "impact": "medium",
      "flexibility": "widen by 0.5% if enrollment slow"
    }
  ],
  "optimization_notes": [
    "Widened HbA1c range from 7.0-11.0% to 7.5-10.5% based on feasibility data"
  ],
  "recruitment_metrics": {
    "estimated_screen_success_rate": 0.35,
    "estimated_enrollment_rate": 0.65,
    "key_barriers": ["HbA1c upper limit", "concomitant medication restrictions"]
  }
}
```

## Criteria Categories

| Category | Description | Examples |
|----------|-------------|----------|
| demographics | Age, sex, race, ethnicity | Age 18-75, women of childbearing potential |
| disease_severity | Disease stage, severity markers | HbA1c range, tumor stage, NYHA class |
| medical_history | Prior conditions, comorbidities | No cardiovascular events within 6 months |
| concomitant_meds | Allowed/prohibited medications | Stable metformin dose allowed |
| laboratory | Lab value requirements | eGFR > 30 mL/min, normal liver function |
| lifestyle | Diet, exercise, habits | Non-smoker, willing to maintain diet |
| compliance | Ability to participate | Able to provide informed consent |
| safety | Risk minimization criteria | No history of severe hypoglycemia |

## Optimization Strategies

### Common Modifications

| Issue | Strategy | Example |
|-------|----------|---------|
| Narrow age range | Widen limits | 18-70 → 18-75 years |
| Restrictive lab values | Adjust thresholds | eGFR > 60 → eGFR > 30 mL/min |
| Comorbidity exclusions | Add time limits | Exclude "current" vs "history of" |
| Medication washouts | Shorten periods | 4 weeks → 2 weeks |
| Geographic barriers | Add telemedicine | Include remote visits option |

### Retention Considerations

- Minimize visit frequency when possible
- Allow window periods for visit timing
- Provide transportation assistance language
- Consider patient-reported outcome burden

## Technical Details

- **Difficulty**: Medium
- **Standards**: ICH E6(R2) GCP, CDISC Protocol Representation Model
- **Data Sources**: ClinicalTrials.gov eligibility patterns, literature feasibility data
- **Dependencies**: None (pure Python)

## References

- `references/criteria_templates.json` - Templates by therapeutic area
- `references/optimization_guidelines.md` - Best practices for criteria optimization
- `references/common_pitfalls.md` - Frequent eligibility design mistakes
- `references/regulatory_guidance.md` - FDA/EMA guidance on eligibility criteria
- `references/feasibility_data.json` - Screen failure rates by criterion type

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

```bash
# Python dependencies
pip install -r requirements.txt
```

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

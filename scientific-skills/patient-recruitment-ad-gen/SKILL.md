---
name: patient-recruitment-ad-gen
description: Generate IRB-compliant patient recruitment advertisements for clinical
  trials. Trigger when user needs to create patient recruitment materials, clinical
  trial ads, or ethical review board compliant recruitment content for pharmaceutical/medical
  research.
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Patient Recruitment Ad Generator

Generate ethical, compliant, and patient-friendly recruitment advertisements for clinical trials.

## Purpose

This skill helps researchers, CROs, and medical institutions create patient recruitment advertisements that meet Institutional Review Board (IRB) / Ethics Committee (EC) requirements while being accessible and encouraging to potential participants.

## When to Use

- Creating recruitment ads for clinical trials
- Drafting patient information sheets
- Preparing materials for IRB/EC submission
- Translating complex medical protocols into patient-friendly language

## Key Compliance Requirements

### Essential Elements (IRB/EC Standards)

1. **Trial Identity**
   - Study title or identifier
   - Sponsor information (if required)

2. **Purpose Statement**
   - Clear description of the research
   - Why the study is being conducted

3. **Eligibility Criteria**
   - Inclusion criteria (who can participate)
   - Exclusion criteria (who cannot participate)

4. **Study Procedures**
   - What participants will do
   - Time commitment required
   - Number of visits

5. **Risks and Benefits**
   - Potential risks/discomforts
   - Potential benefits (direct and societal)
   - Statement that benefits are not guaranteed

6. **Confidentiality**
   - How personal information is protected
   - Regulatory oversight mention

7. **Voluntary Participation**
   - Right to withdraw at any time
   - No penalty for withdrawal
   - No impact on regular medical care

8. **Contact Information**
   - Principal Investigator
   - Study coordinator
   - IRB/EC contact for questions about rights

### Prohibited Content

- **Promises of cure** or guaranteed benefits
- **Undue influence** (excessive payment, coercion)
- **Misleading language** ("free treatment" when experimental)
- **Stigmatizing terms** ("sufferers," "victims")
- **Pressure tactics** (limited spots, urgency)

## Usage

### Input Parameters

```python
{
    "disease_condition": str,        # Target disease/condition
    "study_phase": str,              # Phase I/II/III/IV
    "intervention_type": str,        # Drug, device, procedure, etc.
    "target_population": str,        # Demographics, age range
    "study_duration": str,           # Expected time commitment
    "site_location": str,            # Study site location
    "compensation": Optional[str],   # Participant payment (if any)
    "pi_name": str,                  # Principal Investigator
    "contact_info": str,             # Phone/email for inquiries
    "irb_reference": str             # IRB/EC approval number
}
```

### Example

```python
python /Users/z04030865/.openclaw/workspace/skills/patient-recruitment-ad-gen/scripts/main.py \
    --disease "Type 2 Diabetes" \
    --phase "Phase II" \
    --intervention "Investigational oral medication" \
    --population "Adults 18-65 with T2DM" \
    --duration "12 weeks, 6 clinic visits" \
    --location "City Medical Center, Building C" \
    --pi "Dr. Sarah Chen" \
    --contact "(555) 123-4567 or diabetes-study@cmc.edu" \
    --irb "IRB-2024-001"
```

### Output

Generates a structured recruitment ad with:
- Headline (attention-grabbing, compliant)
- Study summary (plain language)
- Who can participate (eligibility)
- What's involved (procedures)
- Rights and protections (ethics)
- Contact information

## Technical Notes

- **Difficulty**: Medium
- **Language**: Patient-friendly (6th-8th grade reading level)
- **Tone**: Respectful, informative, empowering
- **Format**: Print, digital, or social media ready
- **Compliance**: Based on FDA, EMA, CIOMS, and ICH-GCP guidelines

## References

See `references/` folder for:
- `fda_guidance.md` - FDA guidance on informed consent
- `ema_guidelines.md` - European ethics requirements
- `ich_gcp.md` - ICH-GCP E6(R2) recruitment provisions
- `plain_language_guide.pdf` - NIH Plain Language guidelines
- `template_examples/` - Sample ads for different therapeutic areas

## Safety & Ethics

- Always include voluntary participation statement
- Never guarantee therapeutic benefit
- Ensure readability for target population
- Review with IRB/EC before use
- Avoid therapeutic misconception

---

**Technical Difficulty**: Medium  
**Category**: Pharma / Clinical Research  
**Last Updated**: 2026-02-05

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
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

# Common Pitfalls in Eligibility Criteria Design

## Overview

This document outlines frequent mistakes in clinical trial eligibility criteria design and provides guidance on how to avoid them.

## 1. Vague or Subjective Language

### Problem
Subjective terms lead to inconsistent application across sites and increase protocol deviation risk.

### Examples
| ❌ Poor | ✅ Better |
|---------|-----------|
| "Significant renal impairment" | "eGFR < 30 mL/min/1.73m²" |
| "Severe hepatic disease" | "Child-Pugh Class C or total bilirubin > 3× ULN" |
| "Unstable medical condition" | "Hospitalization for [specific condition] within 30 days" |
| "In the opinion of the investigator" (overused) | Objective criteria with investigator discretion as exception |

### Impact
- Site-to-site variability in eligibility decisions
- Increased eligibility queries
- Higher screen failure rates due to uncertainty
- Regulatory scrutiny during inspections

### Solution
- Use validated scales and objective measurements
- Provide specific thresholds
- Reserve subjective judgment for truly complex cases
- Provide training with case examples

## 2. Overly Restrictive Criteria

### Problem
Excessive restrictions limit generalizability and slow enrollment without improving safety.

### Common Examples

**Age Restrictions**
- Upper age limits without scientific rationale
- Excluding elderly patients who represent the actual disease population
- Impact: May exclude 30-40% of target population for cardiovascular and cancer trials

**Laboratory Thresholds**
- Using "normal" ranges that don't account for disease state
- eGFR > 60 mL/min in diabetes trials (excludes ~25% of eligible patients)
- Liver function thresholds stricter than drug metabolism data supports

**Comorbidity Exclusions**
- Complete exclusion for "history of" rather than "active" or "recent"
- Excluding common comorbidities that don't affect study endpoints
- Not considering disease stability

### Solution
- Justify each exclusion with specific safety or scientific rationale
- Use time-limited exclusions when appropriate
- Consider allowing stable comorbidities
- Document evidence supporting thresholds

## 3. Inadequate Washout Periods

### Problem
Washout periods that are too short risk carryover effects; too long delay enrollment unnecessarily.

### Guidelines by Drug Class

| Drug Class | Minimum Washout | Rationale |
|------------|-----------------|-----------|
| Cytotoxic chemotherapy | 4-5 half-lives or 3 weeks | Allow immune recovery |
| Immunotherapy | 4-6 weeks | Immune effects persist |
| Corticosteroids | 2 weeks (systemic) | HPA axis recovery |
| Anticoagulants | 5 half-lives | Elimination time |
| Biologics | 4-5 half-lives | Clearance plus safety margin |

### Solution
- Base washout on pharmacokinetic data
- Consider disease-specific factors (e.g., bone marrow recovery for myelosuppressive agents)
- Document rationale in protocol
- Allow shorter washouts with supportive safety data

## 4. Inconsistent Concomitant Medication Rules

### Problem
Unclear or inconsistent rules about permitted/prohibited medications create confusion.

### Common Issues
- Not specifying dose ranges for permitted medications
- Prohibiting medications without clear drug interaction rationale
- Inconsistent rules across drug classes
- Not allowing rescue medications

### Solution
- Create clear concomitant medication table
- Specify permitted dose ranges
- Provide rationale for prohibitions
- Allow dose adjustments during run-in periods

## 5. Ignoring Real-World Population

### Problem
Criteria designed for "ideal" patients don't reflect the actual disease population.

### Examples

**Diabetes Trials**
- Excluding patients on insulin when insulin is standard of care
- Not accounting for variable HbA1c in real-world diabetes
- Overly restrictive BMI criteria

**Oncology Trials**
- ECOG performance status 0-1 when many patients are 2
- Excluding all prior therapy when patients have received multiple lines
- Not allowing stable brain metastases

**Cardiovascular Trials**
- Excluding patients with common comorbidities (CKD, diabetes)
- Upper age limits when elderly have highest event rates
- Not accounting for polypharmacy

### Solution
- Review epidemiology data for target population
- Consider pragmatic trial designs
- Plan for real-world effectiveness studies
- Include diverse populations intentionally

## 6. Complex Eligibility Algorithms

### Problem
Overly complex eligibility rules increase errors and screening time.

### Examples
- Multiple conditional criteria ("If X, then Y; if Z, then...")
- Conflicting criteria that require interpretation
- Calculated values without clear formulas
- Criteria that vary by visit

### Solution
- Simplify to essential criteria
- Use flowcharts for complex decisions
- Provide clear examples in protocol
- Consider eligibility committee for borderline cases

## 7. Inadequate Reproductive Safety Language

### Problem
Outdated or unclear reproductive safety language can exclude appropriate participants or create safety risks.

### Issues
- Binary pregnancy exclusion without considering contraception
- Not accounting for diverse family planning needs
- Unclear contraception requirements
- Outdated definitions of "childbearing potential"

### Solution (Per FDA Guidance)
- Use contraception-based approach rather than blanket exclusions
- Define acceptable contraception methods
- Consider pregnancy testing requirements
- Allow for individual circumstances

## 8. Geographic and Access Barriers

### Problem
Criteria that create unnecessary access barriers limit diversity and enrollment.

### Examples
- Requiring frequent on-site visits when remote monitoring is feasible
- Not providing language-appropriate materials
- Visit windows too narrow for working participants
- Not allowing electronic consent in appropriate settings

### Solution
- Incorporate decentralized trial elements
- Provide flexible visit windows
- Support transportation/logistics
- Use technology for remote assessments

## 9. Lack of Flexibility Provisions

### Problem
Rigid criteria without pathways for reasonable exceptions limit appropriate enrollment.

### Issues
- No provision for minor protocol deviations
- No eligibility waiver process
- No adaptive criteria mechanisms
- No consideration of benefit-risk in individual cases

### Solution
- Define minor deviation categories
- Establish eligibility waiver committee
- Plan for protocol amendments if needed
- Document rationale for individual decisions

## 10. Inadequate Screening Data Collection

### Problem
Not collecting detailed screening failure data limits optimization opportunities.

### Issues
- Generic "did not meet eligibility" documentation
- Not tracking which specific criteria caused exclusion
- Missing data on near-miss participants
- No analysis of cumulative exclusion impact

### Solution
- Implement detailed screening logs
- Track reasons for screen failure by criterion
- Collect data on marginally eligible patients
- Regular analysis of screen failure patterns

## Quick Reference: Criteria Quality Checklist

### Before Finalizing Protocol

- [ ] Each criterion has documented scientific or safety rationale
- [ ] Language is objective and measurable where possible
- [ ] Age limits are scientifically justified
- [ ] Laboratory thresholds match drug pharmacology
- [ ] Washout periods are based on PK data
- [ ] Concomitant medication rules are clear
- [ ] Criteria reflect real-world disease population
- [ ] Complex algorithms are simplified or diagrammed
- [ ] Reproductive safety language is current
- [ ] Access barriers are minimized
- [ ] Flexibility provisions are defined
- [ ] Screening data collection plan is established

### During Enrollment

- [ ] Screen success rate is monitored monthly
- [ ] Top 3 exclusion reasons are tracked
- [ ] Site feedback on criteria is collected
- [ ] Protocol deviations are analyzed
- [ ] Amendment needs are assessed quarterly

## References

1. FDA Guidance for Industry: Considerations for Inclusion of Women in Clinical Trials
2. ICH E6(R2) Good Clinical Practice Guidelines
3. Van Spall HGC et al. Eligibility criteria of randomized controlled trials. JAMA. 2007;297(11):1183-1190
4. Murthy VH et al. Participation in cancer clinical trials. JAMA. 2004;291(22):2720-2726

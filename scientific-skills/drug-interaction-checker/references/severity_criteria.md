# Drug Interaction Severity Classification Criteria

## Overview

This document defines the criteria used to classify drug interaction severity in the drug interaction checker.

## Severity Levels

### 🔴 Critical

**Definition**: Life-threatening interaction requiring immediate intervention

**Criteria**:
- High risk of death or permanent disability
- Absolute contraindication in most clinical scenarios
- Requires immediate discontinuation of one or more agents
- Examples: Severe bleeding with anticoagulant combinations, respiratory depression with opioid + benzodiazepine

**Action Required**:
- Do not combine under any circumstances
- If inadvertently combined, immediate medical attention required
- Document reason thoroughly if combination absolutely necessary

### 🟠 Major

**Definition**: Significant risk that may require medical intervention or hospitalization

**Criteria**:
- May cause significant clinical deterioration
- Requires therapy modification (dose change, additional monitoring)
- May require temporary discontinuation
- Examples: INR elevation with warfarin + amiodarone, myopathy with statin + fibrate

**Action Required**:
- Avoid combination if possible
- If combination necessary, implement monitoring plan
- Consider prophylactic measures
- Patient education on warning signs

### 🟡 Moderate

**Definition**: Moderate risk that may cause significant symptoms but unlikely to be life-threatening

**Criteria**:
- May require dose adjustment
- May cause symptoms requiring symptomatic treatment
- Effects are usually manageable
- Examples: Enhanced sedation, mild QT prolongation, reduced drug efficacy

**Action Required**:
- Monitor for adverse effects
- Consider dose adjustment
- Patient awareness of possible symptoms
- Alternative therapy consideration

### 🟢 Minor

**Definition**: Mild interaction, unlikely to cause significant clinical issues

**Criteria**:
- Minimal clinical significance
- Usually does not require therapy modification
- May cause mild symptoms that don't affect daily function
- Examples: Slight increase in drug levels without clinical consequence

**Action Required**:
- Be aware of interaction
- Usually no action needed
- Monitor if patient has additional risk factors

### ⚪ Unknown

**Definition**: Insufficient data to assess interaction risk

**Criteria**:
- No published interaction data
- Theoretical interaction only
- Case reports exist but causality unclear

**Action Required**:
- Proceed with caution
- Monitor for unexpected effects
- Consider therapeutic drug monitoring if available

## Classification Factors

### 1. Pharmacokinetic Interactions

| Mechanism | Typical Severity | Notes |
|-----------|-----------------|-------|
| CYP450 inhibition (strong) | Moderate to Major | Depends on substrate therapeutic index |
| CYP450 inhibition (weak/moderate) | Minor to Moderate | Usually manageable |
| CYP450 induction | Moderate | May cause therapeutic failure |
| Protein binding displacement | Usually Minor | Rarely clinically significant |
| Renal clearance reduction | Moderate to Major | Depends on drug toxicity |
| Absorption alteration | Minor to Moderate | Usually manageable with timing |

### 2. Pharmacodynamic Interactions

| Mechanism | Typical Severity | Notes |
|-----------|-----------------|-------|
| Additive toxicity (same organ) | Major to Critical | Hepatotoxicity, nephrotoxicity, cardiotoxicity |
| Synergistic effect | Moderate to Major | Enhanced therapeutic or adverse effects |
| Antagonistic effect | Moderate | Therapeutic failure |
| Contradictory effects | Minor to Moderate | May reduce efficacy of both agents |

### 3. Patient Factors Affecting Severity

Factors that may upgrade severity classification:
- Advanced age (>75 years)
- Renal impairment (eGFR <60)
- Hepatic impairment (Child-Pugh B or C)
- Low body weight (<50 kg)
- Pregnancy
- Multiple comorbidities
- Polypharmacy (>10 medications)

## Evidence Levels

Interactions are classified based on available evidence:

1. **Established**: Multiple well-designed studies or extensive clinical experience
2. **Probable**: Good evidence from pharmacokinetic studies or case series
3. **Suspected**: Limited evidence, mainly from case reports or theoretical basis
4. **Possible**: Based on mechanism only, minimal clinical data
5. **Unlikely**: Evidence suggests interaction does not occur

## References

1. Tatro DS. Drug Interaction Facts. Facts & Comparisons.
2. Baxter K, Preston CL. Stockley's Drug Interactions. Pharmaceutical Press.
3. FDA Drug Development and Drug Interactions Website
4. Indiana University School of Medicine - CLINICAL Tables

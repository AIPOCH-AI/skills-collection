# Clinical Coding Scenarios and Examples

## Scenario 1: Diabetes Management Visit

### Clinical Documentation
```
Patient: 62-year-old female
Chief Complaint: Follow-up for diabetes management
History: Type 2 diabetes mellitus with diabetic neuropathy and diabetic nephropathy. 
Hypertension. Last HbA1c was 8.2%. Patient reports tingling in feet.
Exam: Bilateral decreased sensation to monofilament testing in feet.
Plan: Continue metformin, add insulin. Order HbA1c, BMP, urinalysis. 
Follow up in 3 months.
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | Rationale |
|----------|------|-------------|-----------|
| Primary | E11.42 | Type 2 diabetes with diabetic neuropathy | Chief reason for visit |
| Secondary | E11.21 | Type 2 diabetes with diabetic nephropathy | Additional manifestation |
| Secondary | E11.9 | Type 2 diabetes mellitus | Underlying condition |
| Secondary | I10 | Essential hypertension | Comorbidity |
| Secondary | Z79.4 | Long-term insulin use | New medication |

**CPT Procedure Codes:**
| Code | Description | Rationale |
|------|-------------|-----------|
| 99214 | Office visit, established patient, moderate complexity | MDM: Multiple chronic conditions, new medication |
| 83036 | HbA1c | Diabetes monitoring |
| 80048 | Basic metabolic panel | Renal function monitoring |
| 81001 | Urinalysis with microscopy | Nephropathy monitoring |

---

## Scenario 2: Emergency Department - Chest Pain

### Clinical Documentation
```
Patient: 45-year-old male
Chief Complaint: Chest pain
History: Sudden onset chest pain radiating to left arm. Associated with 
diaphoresis and nausea. History of hypertension and hyperlipidemia.
Vitals: BP 160/95, HR 98, RR 18, O2 98%
Exam: No murmurs, clear lungs, chest wall non-tender
EKG: ST depression in V4-V6
Troponin: 0.08 (slightly elevated)
Diagnosis: Unstable angina
Plan: Admit to observation unit. Continue ASA, start heparin drip.
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | Rationale |
|----------|------|-------------|-----------|
| Primary | I20.0 | Unstable angina | Principal diagnosis |
| Secondary | I10 | Essential hypertension | Comorbidity |
| Secondary | E78.5 | Hyperlipidemia | Comorbidity |
| Secondary | R06.02 | Shortness of breath | Symptom |
| Secondary | R11.0 | Nausea | Symptom |

**CPT Procedure Codes:**
| Code | Description | Rationale |
|------|-------------|-----------|
| 99284 | ED visit, moderate complexity | Moderate MDM, high risk |
| 93000 | EKG | Diagnostic test performed |
| 84484 | Troponin | Lab test performed |
| 36415 | Venipuncture | Blood draw |

---

## Scenario 3: Surgical Procedure - Laparoscopic Cholecystectomy

### Clinical Documentation
```
Preoperative Diagnosis: Acute cholecystitis with cholelithiasis
Postoperative Diagnosis: Same
Procedure: Laparoscopic cholecystectomy with intraoperative cholangiography

Indications: 38-year-old female with RUQ pain, fever, positive Murphy sign.
US showed gallstones and gallbladder wall thickening.

Procedure Details: Four-port laparoscopic approach. Cystic duct identified 
and clipped. Cholangiogram showed patent common bile duct without stones. 
Gallbladder removed without complications. Specimen sent to pathology.

Estimated Blood Loss: Minimal
Complications: None
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | Rationale |
|----------|------|-------------|-----------|
| Primary | K80.00 | Calculus of gallbladder with acute cholecystitis | Principal diagnosis |
| Secondary | K80.20 | Calculus of gallbladder without mention of cholecystitis | Additional finding |

**CPT Procedure Codes:**
| Code | Description | Rationale |
|------|-------------|-----------|
| 47563 | Laparoscopic cholecystectomy with cholangiography | Procedure performed |

**Modifiers:** None required

---

## Scenario 4: Physical Therapy Initial Evaluation

### Clinical Documentation
```
Patient: 55-year-old male referred for PT after right TKA 3 weeks ago
Chief Complaint: Knee stiffness and weakness
Assessment: Right knee ROM 5-95 degrees (limited). Quadriceps strength 3/5. 
Gait antalgic with walker. Incision well-healed.
Goals: Improve ROM to 0-125, strength to 4+/5, ambulate independently.
Plan: 2x/week PT for 8 weeks - therapeutic exercise, manual therapy, gait training
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | Rationale |
|----------|------|-------------|-----------|
| Primary | M25.561 | Pain in right knee | Primary complaint |
| Secondary | Z47.1 | Aftercare following joint replacement surgery | Status post TKA |
| Secondary | M93.261 | Stiffness of knee | Finding |
| Secondary | M62.461 | Weakness of muscle, lower leg | Finding |

**CPT Procedure Codes:**
| Code | Description | Units | Rationale |
|------|-------------|-------|-----------|
| 97161 | PT evaluation, low complexity | 1 | Initial evaluation |
| 97110 | Therapeutic exercise | 4 | 4 x 15 min = 60 min |
| 97140 | Manual therapy | 2 | 2 x 15 min = 30 min |
| 97116 | Gait training | 2 | 2 x 15 min = 30 min |

---

## Scenario 5: Preventive Visit with Chronic Conditions

### Clinical Documentation
```
Patient: 50-year-old female
Visit Type: Annual preventive exam

Preventive Services:
- Complete history and physical
- Counseling on diet and exercise
- Screening mammogram ordered
- Colonoscopy referral (age 50)
- Immunizations: Flu vaccine given

Chronic Conditions Addressed:
- Hypothyroidism - stable on levothyroxine 100mcg, TSH ordered
- Depression - stable on sertraline 50mg, PHQ-9 = 3
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | Rationale |
|----------|------|-------------|-----------|
| Primary | Z00.00 | Encounter for general adult medical examination | Preventive visit |
| Secondary | E03.9 | Hypothyroidism | Stable chronic condition |
| Secondary | F32.9 | Major depressive disorder | Stable chronic condition |
| Secondary | Z79.899 | Other long-term drug therapy | Medication management |

**CPT Procedure Codes:**
| Code | Description | Modifier | Rationale |
|------|-------------|----------|-----------|
| 99395 | Preventive visit, age 18-39 |  | Main preventive service |
| 99213 | Office visit, established | -25 | Significant, separately identifiable E/M |
| 77067 | Screening mammography |  | Preventive screening |
| 45378 | Screening colonoscopy | -33 | ACA preventive (modifier 33) |
| 90662 | Flu vaccine |  | Immunization |
| 90471 | Vaccine administration |  | Administration |

**Important:** Use modifier -25 on 99213 because problem-oriented E/M is significant and separately identifiable from the preventive service.

---

## Scenario 6: Hospital Discharge Summary

### Clinical Documentation
```
Admission Date: 01/15/2024
Discharge Date: 01/20/2024

Principal Diagnosis: Community-acquired pneumonia
Secondary Diagnoses:
- COPD with acute exacerbation
- Type 2 diabetes mellitus
- Acute kidney injury (resolved)

Hospital Course:
Patient admitted with fever, cough, hypoxia. CXR showed RLL infiltrate.
Started on ceftriaxone and azithromycin. COPD exacerbation treated with 
steroids and nebulizers. AKI resolved with hydration. Glucose controlled 
with sliding scale insulin.

Discharge Condition: Improved
Discharge Medications: Augmentin, prednisone taper, albuterol, metformin
Follow-up: PCP in 1 week
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description | POA Indicator |
|----------|------|-------------|---------------|
| Primary | J18.9 | Pneumonia, unspecified | Y |
| Secondary | J44.1 | COPD with acute exacerbation | Y |
| Secondary | E11.9 | Type 2 diabetes mellitus | Y |
| Secondary | N17.9 | Acute kidney failure | Y (resolved) |

**CPT Procedure Codes:**
| Code | Description | Rationale |
|------|-------------|-----------|
| 99223 | Initial hospital care, high complexity | Initial admission |
| 99233 | Subsequent hospital care x 3 | Daily visits |
| 99239 | Hospital discharge, >30 minutes | Comprehensive discharge |

---

## Scenario 7: Radiology - Multiple Studies

### Clinical Documentation
```
Indication: Motor vehicle accident, chest and abdominal trauma

Studies Performed:
1. CT Chest with IV contrast - no aortic injury, small L hemothorax
2. CT Abdomen/Pelvis with IV contrast - liver laceration Grade II, 
   no active extravasation
3. CT Head without contrast - negative for acute hemorrhage

Findings:
- Grade II liver laceration
- Small left hemothorax
- No intracranial hemorrhage
```

### Recommended Coding

**ICD-10-CM Diagnosis Codes:**
| Sequence | Code | Description |
|----------|------|-------------|
| Primary | S36.112A | Laceration of liver, initial encounter |
| Secondary | S27.1XXA | Hemothorax, initial encounter |
| Secondary | V89.2XXA | Person injured in unspecified motor vehicle accident |

**CPT Procedure Codes:**
| Code | Description | Modifier | Rationale |
|------|-------------|----------|-----------|
| 71260 | CT chest with contrast |  | Study performed |
| 74160 | CT abdomen with contrast | 59 | Distinct session/study |
| 70450 | CT head without contrast | 59 | Distinct session/study |

**Note:** Modifier 59 on second and third studies because separate anatomical regions.

---

## Common Coding Pitfalls

### Pitfall 1: Unspecified Codes
❌ Using J44.9 (COPD) when J44.1 (COPD with acute exacerbation) is documented

✅ Code to highest level of specificity documented

### Pitfall 2: Missing Manifestations
❌ Only coding E11.9 (DM2) when E11.42 (DM2 with neuropathy) is documented

✅ Code diabetes first, then manifestations

### Pitfall 3: Incorrect E/M Level
❌ Coding 99285 for simple suture removal

✅ Match MDM/time to documented medical necessity

### Pitfall 4: Modifier Omission
❌ Coding 99213 and 99214 on same day without modifier

✅ Use modifier -25 for significant, separately identifiable E/M

### Pitfall 5: Global Package Violations
❌ Coding 99213 for routine post-op visit within global period

✅ Understand global periods for surgical procedures

---

## Quick Reference: E/M Level Selection

### MDM Table for Office/Outpatient

| Problems | Data | Risk | Code (New) | Code (Est) |
|----------|------|------|------------|------------|
| 1 self-limited | Minimal/min | Minimal | 99201 | 99211 |
| 2+ self-limited OR 1 stable chronic | Limited | Low | 99202 | 99212 |
| 1 stable chronic OR 1 acute uncomplicated | Limited | Low | 99203 | 99213 |
| 1+ chronic with exacerbation OR 2+ stable chronic | Moderate | Moderate | 99204 | 99214 |
| 1+ chronic with severe exacerbation OR 1 acute illness with systemic symptoms | Extensive | High | 99205 | 99215 |

---

*Examples are for educational purposes. Always verify with current coding guidelines.*

# Medical Terminology Sources and References

## Standard Medical Ontologies

### SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)
- **Purpose**: Comprehensive clinical healthcare terminology
- **Coverage**: Clinical findings, procedures, body structures, substances, etc.
- **Usage**: Clinical documentation, EHR systems, decision support
- **Access**: https://www.snomed.org/
- **License**: Free for IHTSDO member countries (including USA via NLM)

### ICD-10-CM/PCS
- **ICD-10-CM**: International Classification of Diseases, 10th Revision, Clinical Modification
  - Used for diagnosis coding
  - USA-specific clinical modification
- **ICD-10-PCS**: Procedure Coding System
  - Used for inpatient procedure coding
- **Access**: https://www.cdc.gov/nchs/icd/icd-10-cm.htm

### LOINC (Logical Observation Identifiers Names and Codes)
- **Purpose**: Standard codes for laboratory tests and clinical observations
- **Coverage**: Lab tests, vital signs, imaging, survey instruments
- **Usage**: Interoperability, lab result reporting
- **Access**: https://loinc.org/

### RxNorm
- **Purpose**: Normalized naming system for clinical drugs
- **Coverage**: Medications, ingredients, dose forms, strength
- **Usage**: Medication reconciliation, e-prescribing
- **Access**: https://www.nlm.nih.gov/research/umls/rxnorm/

### CPT (Current Procedural Terminology)
- **Purpose**: Medical procedure codes
- **Coverage**: Medical, surgical, diagnostic procedures
- **Usage**: Billing, reimbursement
- **Publisher**: American Medical Association

## Drug Reference Sources

### Standard Drug Databases
1. **FDA Orange Book** - Approved drug products with therapeutic equivalence
2. **DrugBank** - Open-access drug and drug target database
3. **DailyMed** - FDA drug labels
4. **RxList** - Drug information database

### Common Drug Suffix Patterns
| Suffix | Drug Class | Examples |
|--------|-----------|----------|
| -mycin | Antibiotics | erythromycin, gentamicin |
| -cillin | Penicillins | amoxicillin, ampicillin |
| -sartan | ARBs | losartan, valsartan |
| -pril | ACE inhibitors | lisinopril, enalapril |
| -statin | HMG-CoA reductase | atorvastatin, simvastatin |
| -zolam | Benzodiazepines | alprazolam, midazolam |
| -tidine | H2 antagonists | ranitidine, famotidine |
| -sone | Corticosteroids | prednisone, hydrocortisone |
| -olol | Beta blockers | metoprolol, propranolol |

## Medical Terminology Standards

### Anatomy
- **Terminologia Anatomica**: International standard for human anatomical terminology
- **FMA (Foundational Model of Anatomy)**: Ontology for anatomy

### Laboratory Medicine
- **UCUM (Unified Code for Units of Measure)**: Standard for units
- **CLSI**: Clinical and Laboratory Standards Institute

### Imaging
- **DICOM**: Digital Imaging and Communications in Medicine
- **RadLex**: Radiology lexicon

## SOAP Note Standards

### Documentation Guidelines
1. **CMS Guidelines**: Centers for Medicare & Medicaid Services
2. **Joint Commission Standards**: Accreditation requirements
3. **HIPAA**: Privacy and security requirements

### Required Elements by Section

#### Subjective
- Chief Complaint (CC)
- History of Present Illness (HPI)
  - Location
  - Quality
  - Severity
  - Duration
  - Timing
  - Context
  - Modifying factors
  - Associated signs/symptoms

#### Objective
- Vital Signs
- Physical Examination findings
- Diagnostic test results
- Review of existing data

#### Assessment
- Diagnosis/differential diagnosis
- Clinical reasoning
- Problem list

#### Plan
- Diagnostic tests
- Therapeutic interventions
- Referrals
- Patient education
- Follow-up

## Clinical Validation Sources

### Evidence-Based Medicine
- **PubMed/MEDLINE**: Biomedical literature database
- **Cochrane Library**: Systematic reviews
- **UpToDate**: Clinical decision support
- **ClinicalTrials.gov**: Trial registry

### Quality Measures
- **HEDIS**: Healthcare Effectiveness Data and Information Set
- **PQRS**: Physician Quality Reporting System
- **MACRA**: Quality payment program

## Implementation Notes

### Medical NLP Considerations
1. **Negation Detection**: Identifying negative findings
2. **Temporal Expressions**: Timing of symptoms/procedures
3. **Certainty Modality**: Degree of certainty in statements
4. **Family History**: Distinguishing patient vs. family conditions

### Common Documentation Challenges
- Ambiguous abbreviations (e.g., "MS" = multiple sclerosis vs. mitral stenosis vs. morphine sulfate)
- Unclear antecedents in pronoun references
- Incomplete medication lists
- Missing temporal information
- Uncertainty in assessment

### Quality Assurance Checklist
- [ ] All required sections present
- [ ] Chief complaint clearly stated
- [ ] HPI elements documented
- [ ] Vital signs recorded
- [ ] Relevant physical exam findings
- [ ] Assessment linked to subjective/objective data
- [ ] Plan includes follow-up
- [ ] Medications reconciled
- [ ] Allergies documented
- [ ] Signature/date present

# Medical Referral Letter Template

## Base Template Structure

```markdown
# MEDICAL REFERRAL LETTER

**Date:** {date}
**Urgency:** {urgency}

---

## REFERRING PROVIDER
**Name:** {referring_name}  
**Title:** {referring_title}  
**Organization:** {referring_organization}  
**Contact:** {referring_contact}  
**NPI:** {referring_npi}

## RECEIVING PROVIDER
**Name:** {receiving_name}  
**Specialty:** {receiving_specialty}  
**Organization:** {receiving_organization}  
**Address:** {receiving_address}

---

## PATIENT INFORMATION
**Name:** {patient_name}  
**Date of Birth:** {patient_dob}  
**Gender:** {patient_gender}  
**MRN:** {patient_mrn}  
**Contact:** {patient_contact}  
**Insurance:** {patient_insurance}

---

## REASON FOR REFFERAL
{reason}

---

## CLINICAL SUMMARY

### Chief Complaint
{chief_complaint}

### History of Present Illness
{history_present_illness}

### Relevant Diagnoses
{diagnoses}

### Past Medical History
{relevant_history}

### Current Medications
{medications}

### Allergies
{allergies}

---

## INVESTIGATION RESULTS

### Laboratory Results
{labs}

### Imaging Studies
{imaging}

### Procedures
{procedures}

---

## REQUESTED CONSULTATION
Please evaluate and manage as clinically indicated.

**Requested Timeframe:** {timeframe}

Thank you for your consultation and co-management of this patient.

---

Sincerely,

{referring_name}  
{referring_title}  
{referring_organization}  
{referring_contact}

---
*This referral letter was generated on {date} using automated clinical documentation tools.*
```

---

## Specialty-Specific Templates

### Cardiology Referral Template

Additional fields to include:
- **Cardiovascular Risk Factors**: HTN, DM, smoking, family history
- **Cardiac History**: Previous MI, CABG, stents, valve disease
- **Current Symptoms**: Chest pain characteristics, dyspnea, palpitations
- **Recent Cardiac Workup**: ECG findings, troponin levels, echocardiogram results
- **Blood Pressure Trends**: Recent readings and variability

### Neurology Referral Template

Additional fields to include:
- **Seizure History**: Type, frequency, last seizure date, triggers
- **Neurological Examination**: Key findings from mental status, cranial nerves, motor/sensory
- **Headache Characteristics**: Pattern, severity, associated symptoms
- **Cognitive Assessment**: MMSE or MoCA scores if available
- **Neuroimaging Summary**: CT/MRI key findings

### Oncology Referral Template

Additional fields to include:
- **Pathology Results**: Histology, grade, molecular markers
- **Staging Information**: TNM stage, imaging-based stage
- **Performance Status**: ECOG or Karnofsky score
- **Tumor Board Discussion**: Summary of multidisciplinary recommendations
- **Clinical Trial Eligibility**: Relevant trials considered

### Orthopedic Referral Template

Additional fields to include:
- **Mechanism of Injury**: How and when injury occurred
- **Functional Status**: Impact on daily activities
- **Previous Imaging**: X-ray, MRI, CT findings
- **Physical Examination**: Range of motion, strength testing
- **Conservative Treatment Attempted**: PT, injections, medications

### Mental Health Referral Template

Additional fields to include:
- **Safety Assessment**: Suicide/homicide risk screening
- **Psychiatric History**: Previous diagnoses, hospitalizations
- **Substance Use History**: Current and past use patterns
- **Social Support**: Living situation, support network
- **Current Functioning**: Work/school status, relationships

## Template Variables Reference

| Variable | Description | Format |
|----------|-------------|--------|
| `{date}` | Letter generation date | YYYY-MM-DD |
| `{urgency}` | Referral urgency level | Stat/Urgent/Routine |
| `{referring_name}` | Referring provider full name | Dr. First Last |
| `{referring_title}` | Referring provider title/role | Primary Care Physician |
| `{referring_organization}` | Referring organization name | Medical Center Name |
| `{referring_contact}` | Contact phone/fax | 555-0100 |
| `{referring_npi}` | National Provider Identifier | 10-digit number |
| `{receiving_name}` | Receiving provider name | Dr. First Last |
| `{receiving_specialty}` | Medical specialty | Cardiology |
| `{receiving_organization}` | Receiving organization | Clinic Name |
| `{receiving_address}` | Full mailing address | Street, City, State ZIP |
| `{patient_name}` | Patient full legal name | First Last |
| `{patient_dob}` | Patient date of birth | YYYY-MM-DD |
| `{patient_gender}` | Patient gender | M/F/Other |
| `{patient_mrn}` | Medical Record Number | alphanumeric |
| `{patient_contact}` | Patient phone number | 555-0200 |
| `{patient_insurance}` | Insurance provider name | Insurance Company |
| `{reason}` | Primary reason for referral | Free text |
| `{chief_complaint}` | Patient's primary concern | Free text |
| `{history_present_illness}` | Detailed symptom narrative | Free text |
| `{diagnoses}` | List of relevant diagnoses | Bulleted list |
| `{relevant_history}` | Pertinent past medical history | Free text |
| `{medications}` | Current medications list | Formatted list |
| `{allergies}` | Known allergies | Bulleted list |
| `{labs}` | Laboratory results | Formatted list |
| `{imaging}` | Imaging study results | Formatted list |
| `{procedures}` | Procedure findings | Formatted list |
| `{timeframe}` | Requested consultation timeframe | Based on urgency |

## Usage Notes

1. **Customization**: Copy the base template and modify sections as needed for specialty-specific referrals.

2. **Conditional Sections**: Omit sections that don't apply to the specific case (e.g., no pending labs).

3. **Formatting**: Use Markdown for consistent rendering across platforms.

4. **Validation**: Always review generated letters for clinical accuracy before sending.

5. **Documentation**: Keep a copy of the referral letter in the patient's medical record.

# ICSR Narrative Template

Use this template structure when writing CIOMS-compliant narratives.

---

## Standard Template

```
CASE IDENTIFIER: [Unique case ID]
DATE OF REPORT: [YYYY-MM-DD]

PATIENT DEMOGRAPHICS:
A [age]-old [sex]. [Additional relevant characteristics if applicable: weight, height, special population status].

RELEVANT MEDICAL HISTORY:
- [Condition 1]
- [Condition 2]
- [Condition 3]

CONCOMITANT MEDICATIONS:
- [Drug name] for [indication], [dose] [frequency]
- [Drug name] for [indication]

SUSPECT DRUG(S):
Drug: [Drug name] (indicated for [indication])
  Dosage: [dose] [frequency] via [route]
  Therapy start: [YYYY-MM-DD]
  Therapy stop: [YYYY-MM-DD or "ongoing"]
  Lot/Batch: [number if known]

ADVERSE EVENT(S):
1. [MedDRA PT term]
   Onset date: [YYYY-MM-DD]
   Time to onset: [e.g., "5 days after first dose"]
   Severity: [Mild/Moderate/Severe]
   Seriousness criteria: [Death/Life-threatening/Hospitalization/etc.]
   Description: [Detailed description of signs, symptoms, course]

DIAGNOSTIC TESTS AND RESULTS:
- [Test name]: [value] (reference: [range]) on [date]
- [Test name]: [value] on [date]

TREATMENT OF ADVERSE EVENT:
- [Intervention 1]
- [Intervention 2]

DECHALLENGE AND RECHALLENGE:
Dechallenge: [Positive/Negative/Unknown - describe what happened when drug stopped]
Rechallenge: [Positive/Negative/Not performed - describe if applicable]

OUTCOME: [Recovered/Recovering/Not recovered/Fatal/Unknown]
Date of outcome: [YYYY-MM-DD if known]
Sequelae: [Any lasting effects if applicable]

CAUSALITY ASSESSMENT: [Certain/Probable/Possible/Unlikely/etc.]
Rationale: [Brief explanation of causality reasoning]

REPORTER COMMENTS:
[Any additional relevant information provided by reporter]
```

---

## Minimal Narrative (Required Elements Only)

For cases with limited information:

```
CASE IDENTIFIER: [ID]

PATIENT DEMOGRAPHICS:
A [age]-old [sex].

SUSPECT DRUG(S):
Drug: [Drug name] for [indication]
  Therapy dates: [start] to [stop]

ADVERSE EVENT(S):
[MedDRA PT term] on [date]

OUTCOME: [status]
```

---

## Narrative Checklist

Before finalizing, verify:

- [ ] Patient age and sex included
- [ ] All suspect drugs identified with indication
- [ ] Therapy dates provided (start/stop)
- [ ] Event onset date specified
- [ ] Time to onset calculable
- [ ] Seriousness criteria documented
- [ ] Dechallenge result stated
- [ ] Outcome documented
- [ ] No patient identifiers present
- [ ] MedDRA terms used for events
- [ ] Chronological order followed

# Example Cases - Medical Scribe Dictation

## Example 1: Internal Medicine - Hypertension Follow-up

### Input Dictation
```
Patient is a 58-year-old male here for follow-up of hypertension. He reports taking his lisinopril 10 milligrams daily but admits to missing doses occasionally. He denies chest pain, shortness of breath, or dizziness. He says his home blood pressure readings have been around 140 over 90. His weight is stable. He continues to smoke about half a pack per day. He denies any headaches or vision changes.

On exam, blood pressure is 148 over 92, heart rate 78, temperature 98.6. He appears comfortable. Lungs are clear. Heart is regular rate and rhythm without murmurs. Abdomen is soft, non-tender. Extremities without edema.

Assessment is uncontrolled hypertension, currently on lisinopril. His blood pressure goal is less than 130 over 80 given his cardiovascular risk factors. He has a significant smoking history which increases his risk.

Plan is to increase lisinopril to 20 milligrams daily. Reinforce importance of medication compliance. Discussed smoking cessation and provided resources. Follow up in 4 weeks with home blood pressure log. Check BMP in one week to monitor creatinine and potassium after dose increase.
```

### Expected SOAP Output

```markdown
# Clinical Note

## Subjective
**Chief Complaint:** Follow-up of hypertension

**History of Present Illness:**
58-year-old male presents for follow-up of hypertension. Reports taking lisinopril 10mg daily but admits to occasional missed doses. Denies chest pain, shortness of breath, dizziness, headaches, or vision changes. Reports home BP readings approximately 140/90 mmHg. Weight is stable. Continues to smoke approximately 0.5 packs per day.

**Review of Systems:**
- Cardiovascular: Denies chest pain, dyspnea, orthopnea
- Neurological: Denies headache, vision changes, dizziness

**Social History:**
Smoking: 0.5 packs/day (active)

**Current Medications:**
- Lisinopril 10mg daily

## Objective
**Vital Signs:**
- Blood Pressure: 148/92 mmHg
- Heart Rate: 78 bpm
- Temperature: 98.6°F

**Physical Examination:**
- General: Appears comfortable, well-nourished
- Cardiovascular: Regular rate and rhythm, no murmurs
- Respiratory: Lungs clear to auscultation bilaterally
- Abdomen: Soft, non-tender
- Extremities: No peripheral edema

## Assessment
**Primary Diagnosis:** Uncontrolled essential hypertension

**Clinical Reasoning:**
Blood pressure remains above goal despite ACE inhibitor therapy. Contributing factors include medication non-adherence and continued tobacco use. Target BP <130/80 mmHg based on ACC/AHA guidelines for patients with cardiovascular risk factors.

## Plan
**Therapeutic:**
1. Increase lisinopril to 20mg daily
2. Reinforce medication compliance

**Diagnostic:**
- BMP in 1 week (monitor creatinine, potassium post-dose escalation)

**Patient Education:**
- Discussed importance of medication adherence
- Provided smoking cessation resources

**Follow-up:**
Return in 4 weeks with home blood pressure log
```

---

## Example 2: Emergency Medicine - Chest Pain Evaluation

### Input Dictation
```
Forty-five-year-old female presents to the emergency department with chest pain. Pain started 2 hours ago while at rest. She describes it as pressure-like, 8 out of 10 severity, radiating to her left arm. Associated with nausea and diaphoresis. No shortness of breath. Past medical history includes hypertension and hyperlipidemia. Takes amlodipine and atorvastatin. Allergic to penicillin.

Vital signs: temperature 37.2, heart rate 102, blood pressure 165 over 95, respiratory rate 18, oxygen saturation 97 percent on room air. She appears diaphoretic and uncomfortable. Cardiovascular exam shows regular rhythm, no murmurs. Lungs are clear. Abdomen is benign.

ECG shows ST elevation in leads V2 through V4. Initial troponin is 0.5, trending up. Chest X-ray is unremarkable.

Assessment is acute ST-elevation myocardial infarction, anterior wall. Cardiology has been consulted. Given aspirin 325, ticagrelor loading dose, and heparin bolus. Patient is being taken emergently to the cath lab for primary PCI.
```

### Expected SOAP Output

```markdown
# Clinical Note

## Subjective
**Chief Complaint:** Chest pain

**History of Present Illness:**
45-year-old female with acute onset chest pain x 2 hours. Pain began at rest, described as pressure-like, 8/10 severity, radiating to left arm. Associated symptoms: nausea, diaphoresis. Denies dyspnea.

**Past Medical History:**
- Hypertension
- Hyperlipidemia

**Current Medications:**
- Amlodipine
- Atorvastatin

**Allergies:**
- Penicillin

## Objective
**Vital Signs:**
- Temperature: 37.2°C
- Heart Rate: 102 bpm
- Blood Pressure: 165/95 mmHg
- Respiratory Rate: 18/min
- O₂ Saturation: 97% (room air)

**Physical Examination:**
- General: Diaphoretic, appears uncomfortable
- Cardiovascular: Regular rhythm, no murmurs
- Respiratory: Lungs clear bilaterally
- Abdomen: Benign

**Diagnostic Studies:**
- ECG: ST elevation leads V2-V4 (anterior wall)
- Troponin: 0.5 ng/mL (elevated, trending upward)
- Chest X-ray: Unremarkable

## Assessment
**Primary Diagnosis:** Acute ST-elevation myocardial infarction (STEMI), anterior wall

**ESI Level:** 1 (Immediate life-saving intervention)

## Plan
**Immediate Interventions:**
- Aspirin 325mg given
- Ticagrelor loading dose administered
- Heparin bolus given
- Cardiology consultation obtained

**Disposition:**
Emergent transfer to cardiac catheterization laboratory for primary PCI
```

---

## Example 3: Pediatrics - Well Child Visit

### Input Dictation
```
Six-month-old male here for well child check. Born full term via normal vaginal delivery. Birth weight was 7 pounds 8 ounces. He is up to date on immunizations. Parents report he is eating well, taking 6 ounces of formula every 4 hours. He started solid foods last month and tolerating them well. Sleeping through the night. Meeting developmental milestones - rolling over, sitting with support, smiling and cooing.

Vital signs: weight 17 pounds 4 ounces, 75th percentile. Length 26 inches, 50th percentile. Head circumference 43 centimeters, 50th percentile. Temperature 98.4. Physical exam is normal. Alert and interactive. Fontanelles are flat. Eyes tracking well. Ear canals clear. Heart regular, no murmurs. Lungs clear. Abdomen soft. Hip exam normal. Skin clear.

Assessment is healthy 6-month-old male, growing appropriately. Development on track.

Plan is to give routine immunizations today - DTaP, IPV, Hib, PCV13, and rotavirus. Discussed introduction of new foods one at a time. Counsel about child safety - car seats, water safety. Follow up at 9 months.
```

### Expected SOAP Output

```markdown
# Clinical Note

## Subjective
**Chief Complaint:** Well child check, 6-month visit

**History of Present Illness:**
6-month-old male for routine well child examination. Full-term vaginal delivery, birth weight 7 lbs 8 oz.

**Feeding/Nutrition:**
Formula feeding: 6 oz every 4 hours. Started solid foods last month, tolerating well.

**Sleep:** Sleeping through night

**Developmental Milestones:**
- Rolling over ✓
- Sitting with support ✓
- Social smiling ✓
- Cooing/vocalization ✓

**Immunizations:** Up to date

**Past Medical History:**
- Birth: Full term NVD
- No significant medical history

## Objective
**Vital Signs:**
- Temperature: 98.4°F
- Weight: 17 lbs 4 oz (75th percentile)
- Length: 26 inches (50th percentile)
- Head Circumference: 43 cm (50th percentile)

**Physical Examination:**
- General: Alert, interactive, well-nourished
- HEENT: Fontanelles flat, eyes tracking, ear canals clear
- Cardiovascular: Regular rate and rhythm, no murmurs
- Respiratory: Lungs clear
- Abdomen: Soft, non-tender
- Musculoskeletal: Hip exam normal
- Skin: Clear

## Assessment
**Primary Diagnosis:** Healthy 6-month-old male

- Growth: Appropriate, maintaining growth curves
- Development: On track for age

## Plan
**Immunizations Administered Today:**
- DTaP (Diphtheria, Tetanus, Pertussis)
- IPV (Inactivated Polio Vaccine)
- Hib (Haemophilus influenzae type b)
- PCV13 (Pneumococcal conjugate)
- Rotavirus

** anticipatory Guidance:**
- Solid food introduction: one new food at a time, 3-5 days between new foods
- Car seat safety
- Water safety

**Follow-up:**
Return for 9-month well child visit
```

---

## Example 4: Orthopedics - Ankle Sprain

### Input Dictation
```
Twenty-two-year-old college athlete twisted his right ankle during basketball game about 3 hours ago. He landed on another player's foot and heard a pop. Immediate pain and swelling. Unable to bear weight. No prior ankle injuries.

Exam shows swelling and ecchymosis over lateral ankle. Tenderness over anterior talofibular ligament. Negative anterior drawer test. Able to bear weight with severe pain. Range of motion limited by pain. Neurovascular intact distally.

X-rays show no fracture or dislocation. Ottawa ankle rules negative for radiographic indication but obtained due to severe pain.

Assessment is grade 2 right ankle sprain, lateral.

Plan is RICE protocol - rest, ice, compression, elevation. Provided ankle brace. Weight bearing as tolerated with crutches. Ibuprofen 600mg three times daily with food. Physical therapy referral for rehabilitation. Follow up in 1 week or sooner if worsening. Return precautions given for signs of compartment syndrome or DVT.
```

### Expected SOAP Output

```markdown
# Clinical Note

## Subjective
**Chief Complaint:** Right ankle pain after injury

**History of Present Illness:**
22-year-old male athlete injured right ankle during basketball game 3 hours ago. Mechanism: landed on opponent's foot. Reports hearing a "pop" at time of injury. Immediate pain and swelling developed. Unable to bear weight. No prior ankle injuries.

**Pain Assessment:**
- Location: Right lateral ankle
- Character: Sharp, throbbing
- Severity: Severe (limits weight-bearing)

## Objective
**Physical Examination - Right Ankle:**
- Inspection: Swelling, ecchymosis over lateral ankle
- Palpation: Tenderness over ATFL (anterior talofibular ligament)
- Stability: Negative anterior drawer test
- Weight-bearing: Severe pain, requires assistance
- ROM: Limited by pain
- Neurovascular: Intact distally (pulses palpable, sensation intact)

**Diagnostic Studies:**
- X-ray right ankle: Negative for fracture or dislocation

## Assessment
**Primary Diagnosis:** Grade II lateral right ankle sprain

## Plan
**Conservative Management:**
- RICE protocol (Rest, Ice, Compression, Elevation)
- Ankle brace provided
- Weight-bearing: As tolerated with crutches

**Medications:**
- Ibuprofen 600mg PO TID with food

**Referrals:**
- Physical therapy for ankle rehabilitation

**Follow-up:**
Return in 1 week or sooner if worsening

**Return Precautions:**
- Seek immediate care for: increasing pain, numbness/tingling, pale/cool foot, calf pain/swelling (DVT signs)
```

---

## Example 5: Psychiatry - Depression Follow-up

### Input Dictation
```
Thirty-five-year-old female here for follow-up of major depressive disorder. She started sertraline 50mg four weeks ago. She reports mood has improved somewhat, about 30 percent better. She is sleeping better, getting 6 to 7 hours now versus 4 before. Still having some anhedonia and difficulty concentrating at work. She denies suicidal thoughts. No side effects from medication.

Mental status exam shows appropriately dressed female, cooperative. Mood is "better but not great." Affect is congruent, mildly constricted. Thought process is linear. No suicidal or homicidal ideation. Insight and judgment are intact.

PHQ-9 score today is 12, down from 18 last month.

Assessment is major depressive disorder, moderate, partial response to sertraline.

Plan is to increase sertraline to 100mg daily. Continue weekly therapy. Follow up in 4 weeks. Crisis line number provided. She agrees to seek immediate care if suicidal thoughts develop.
```

### Expected SOAP Output

```markdown
# Clinical Note

## Subjective
**Chief Complaint:** Depression follow-up

**History of Present Illness:**
35-year-old female with MDD, 4 weeks after initiating sertraline 50mg daily. Reports:
- Mood improvement: approximately 30% better
- Sleep: Improved from 4 hours to 6-7 hours nightly
- Persistent symptoms: Anhedonia, difficulty concentrating
- Denies: Suicidal ideation, medication side effects

**Psychiatric History:**
- Major Depressive Disorder

**Current Medications:**
- Sertraline 50mg daily

## Objective
**Mental Status Examination:**
- Appearance: Appropriately dressed, cooperative
- Mood: "Better but not great"
- Affect: Congruent with mood, mildly constricted
- Thought Process: Linear, goal-directed
- Thought Content: No SI/HI, no psychotic symptoms
- Insight/Judgment: Intact

**Objective Scales:**
- PHQ-9: 12 (moderate, improved from 18)

## Assessment
**Primary Diagnosis:** Major Depressive Disorder, moderate, recurrent
- Partial response to pharmacotherapy
- PHQ-9 improved from 18 to 12

## Plan
**Pharmacotherapy:**
- Increase sertraline to 100mg daily

**Psychotherapy:**
- Continue weekly therapy sessions

**Safety Planning:**
- Crisis line number provided
- Patient agrees to seek immediate care if SI develops
- Emergency contact established

**Follow-up:**
Return in 4 weeks for medication monitoring
```

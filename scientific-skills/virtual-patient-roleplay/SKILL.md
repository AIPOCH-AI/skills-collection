---
name: virtual-patient-roleplay
description: AI-powered standardized patient simulator for clinical interview training. Generates realistic patient responses based on medical history and symptoms, enabling medical students to practice history-taking and communication skills in a safe environment.
version: 1.0.0
category: Education
tags: [medical-education, clinical-training, standardized-patient, communication-skills]
author: Medical Science Skills
license: MIT
---

# Virtual Patient Roleplay

AI-powered standardized patient (SP) simulator for medical education. Roleplays various clinical scenarios to help students practice patient interview skills.

## Features

- Multiple patient personas with realistic medical histories
- Dynamic response generation based on student questions
- Physical exam findings and lab results simulation
- Feedback on communication skills and diagnostic approach
- Support for various clinical scenarios (cardiology, neurology, GI, etc.)

## Use Cases

- Medical student OSCE preparation
- Clinical communication skills training
- Differential diagnosis practice
- Breaking bad news simulation

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scenario` | str | Yes | Clinical scenario type (e.g., "chest_pain", "headache", "abdominal_pain") |
| `student_question` | str | Yes | Student's question to the patient |
| `conversation_history` | list | No | Previous Q&A exchanges |
| `difficulty` | str | No | Difficulty level ("beginner", "intermediate", "advanced") |

## Output Format

```json
{
  "patient_response": "string",
  "emotional_state": "string",
  "physical_cues": "string",
  "hidden_information": "string",
  "feedback": {
    "communication_tips": ["string"],
    "missed_questions": ["string"]
  }
}
```

## Example Usage

```python
from virtual_patient_roleplay import PatientSimulator

simulator = PatientSimulator(scenario="chest_pain")
response = simulator.ask("Can you describe your pain?")
print(response.patient_response)
```

## Limitations

- Does not replace real patient interaction
- Limited physical exam simulation
- Responses are generated, not from real patients

## References

- Association of Standardized Patient Educators (ASPE) Standards
- OSCE Best Practices in Medical Education

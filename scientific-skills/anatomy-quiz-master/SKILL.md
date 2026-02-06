---
name: anatomy-quiz-master
description: Interactive anatomy quiz generator covering gross anatomy, neuroanatomy, and clinical anatomy. Supports multiple quiz modes and difficulty levels for medical education.
version: 1.0.0
category: Education
tags: [anatomy, medical-education, quiz, gross-anatomy, neuroanatomy]
author: Medical Science Skills
license: MIT
---

# Anatomy Quiz Master

Interactive anatomy quiz generator for medical students.

## Features

- Regional anatomy quizzes (upper limb, lower limb, thorax, abdomen, head/neck)
- Neuroanatomy pathway tracing
- Clinical correlation questions
- Image-based identification
- Difficulty levels: basic, intermediate, advanced

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region` | str | Yes | Body region to quiz on |
| `difficulty` | str | No | "basic", "intermediate", "advanced" |
| `question_type` | str | No | "identification", "function", "clinical" |

## Output Format

```json
{
  "question": "string",
  "options": ["string"],
  "correct_answer": "string",
  "explanation": "string",
  "clinical_note": "string"
}
```

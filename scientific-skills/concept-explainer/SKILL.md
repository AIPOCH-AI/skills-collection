---
name: concept-explainer
description: Uses analogies to explain complex medical concepts in accessible terms.
version: 1.0.0
category: Info
tags: [education, analogies, medical-concepts, explanation]
author: Medical Science Skills
license: MIT
---

# Concept Explainer

Explains medical concepts using everyday analogies.

## Features

- Analogy generation
- Concept simplification
- Multiple explanation levels
- Visual description support

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `concept` | str | Yes | Medical concept to explain |
| `audience` | str | No | "child", "patient", "student" |

## Output Format

```json
{
  "explanation": "string",
  "analogy": "string",
  "key_points": ["string"]
}
```

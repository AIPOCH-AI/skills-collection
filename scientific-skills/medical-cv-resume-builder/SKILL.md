---
name: medical-cv-resume-builder
description: Generates US medical industry standard CVs and resumes.
version: 1.0.0
category: Career
tags: [cv, resume, career, medical, formatting]
author: Medical Science Skills
license: MIT
---

# Medical CV/Resume Builder

Creates medical CVs following US standards.

## Features

- Medical CV formatting
- Section organization
- Achievement highlighting
- Template selection

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `experiences` | list | Yes | Work experiences |
| `education` | list | Yes | Education history |
| `type` | str | No | "cv" or "resume" |

## Output Format

```json
{
  "cv_markdown": "string",
  "sections": ["string"]
}
```

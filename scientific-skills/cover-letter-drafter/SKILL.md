---
name: cover-letter-drafter
description: Generates professional cover letters for journal submissions and job applications in medical and academic contexts.
version: 1.0.0
category: Career
tags: [cover-letter, job-application, journal-submission, academic-writing]
author: Medical Science Skills
license: MIT
---

# Cover Letter Drafter

Creates tailored cover letters for academic and medical positions.

## Features

- Journal submission cover letters
- Job application cover letters
- Fellowship application letters
- Customizable templates

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `purpose` | str | Yes | "journal", "job", "fellowship" |
| `recipient` | str | Yes | Target journal or institution |
| `key_points` | list | Yes | Main points to highlight |

## Output Format

```json
{
  "cover_letter": "string",
  "subject_line": "string",
  "word_count": "int"
}
```

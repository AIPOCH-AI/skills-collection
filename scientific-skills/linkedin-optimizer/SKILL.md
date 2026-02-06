---
name: linkedin-optimizer
description: Optimizes LinkedIn profiles for medical professionals.
version: 1.0.0
category: Career
tags: [linkedin, profile, career, networking]
author: Medical Science Skills
license: MIT
---

# LinkedIn Optimizer

Optimizes LinkedIn profiles for healthcare professionals.

## Features

- Headline optimization
- About section writing
- Keyword integration
- Professional branding

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | str | Yes | Current role |
| `specialty` | str | Yes | Medical specialty |
| `achievements` | list | Yes | Key achievements |

## Output Format

```json
{
  "headline": "string",
  "about_section": "string",
  "keywords": ["string"]
}
```

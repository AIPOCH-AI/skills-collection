---
name: personal-statement
description: Helps craft compelling personal statements for applications and promotions.
version: 1.0.0
category: Utility
tags: [personal-statement, application, narrative, career]
author: Medical Science Skills
license: MIT
---

# Personal Statement

Crafts personal narratives for applications.

## Features

- Story development
- Experience integration
- Motivation articulation
- Goal alignment

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `purpose` | str | Yes | Application purpose |
| `experiences` | list | Yes | Key experiences |
| `goals` | str | Yes | Career goals |

## Output Format

```json
{
  "personal_statement": "string",
  "themes": ["string"]
}
```

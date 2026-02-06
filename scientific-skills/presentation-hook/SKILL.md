---
name: presentation-hook
description: Creates engaging opening statements and powerful closings for medical presentations.
version: 1.0.0
category: Present
tags: [presentation, hook, opening, closing, speaking]
author: Medical Science Skills
license: MIT
---

# Presentation Hook

Crafts presentation openings and closings.

## Features

- Attention-grabbing openings
- Memorable closings
- Audience-specific hooks
- Storytelling elements

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | str | Yes | Presentation topic |
| `audience` | str | Yes | Target audience |
| `type` | str | Yes | "opening" or "closing" |

## Output Format

```json
{
  "hook": "string",
  "alternative_hooks": ["string"]
}
```

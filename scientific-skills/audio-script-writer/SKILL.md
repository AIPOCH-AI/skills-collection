---
name: audio-script-writer
description: Converts written reports into podcast or video scripts optimized for audio delivery.
version: 1.0.0
category: Info
tags: [script, podcast, audio, medical-education]
author: Medical Science Skills
license: MIT
---

# Audio Script Writer

Transforms written content into audio-friendly scripts.

## Features

- Podcast script conversion
- Spoken word optimization
- Pronunciation guides
- Timing estimates

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | str | Yes | Written content |
| `duration` | int | No | Target duration in minutes |

## Output Format

```json
{
  "script": "string",
  "estimated_duration": "string",
  "pronunciation_notes": ["string"]
}
```

---
name: meeting-minutes
description: Converts unstructured medical meeting transcripts into structured minutes with action items and decisions.
version: 1.0.0
category: Info
tags: [meeting-minutes, transcription, action-items, compliance]
author: Medical Science Skills
license: MIT
---

# Meeting Minutes

Structures medical meeting transcripts into formal minutes.

## Features

- Action item extraction
- Decision logging
- Attendee tracking
- FDA/ICH E6 compliance

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transcript` | str | Yes | Meeting transcript |
| `meeting_type` | str | No | "clinical", "research", "admin" |

## Output Format

```json
{
  "minutes": "string",
  "action_items": ["string"],
  "decisions": ["string"],
  "attendees": ["string"]
}
```

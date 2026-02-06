---
name: key-takeaways
description: Extracts 3-5 core conclusions from lengthy medical documents or PDFs.
version: 1.0.0
category: Info
tags: [summary, key-points, document-analysis]
author: Medical Science Skills
license: MIT
---

# Key Takeaways

Extracts essential conclusions from medical documents.

## Features

- Automatic key point extraction
- Priority ranking
- Concise bullet points
- Multi-document support

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | str | Yes | Document text |
| `num_takeaways` | int | No | Number of points (default: 5) |

## Output Format

```json
{
  "takeaways": ["string"],
  "source_word_count": "int"
}
```

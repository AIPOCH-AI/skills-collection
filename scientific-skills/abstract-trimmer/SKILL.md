---
name: abstract-trimmer
description: Compresses abstracts to meet strict word limits while preserving key information and scientific accuracy.
version: 1.0.0
category: General
tags: [abstract, word-limit, compression, editing]
author: Medical Science Skills
license: MIT
---

# Abstract Trimmer

Trims medical abstracts to fit journal word limits.

## Features

- Smart word reduction
- Key information preservation
- Multiple compression levels
- Readability maintenance

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `abstract` | str | Yes | Original abstract text |
| `target_words` | int | Yes | Target word count |

## Output Format

```json
{
  "trimmed_abstract": "string",
  "original_words": "int",
  "final_words": "int",
  "reduction_percent": "float"
}
```

---
name: comparison-table-gen
description: Auto-generates comparison tables for concepts, drugs, or study results in Markdown format.
version: 1.0.0
category: Info
tags: [comparison, table, markdown, research]
author: Medical Science Skills
license: MIT
---

# Comparison Table Gen

Generates comparison tables for medical content.

## Features

- Side-by-side comparisons
- Markdown table output
- Drug comparison templates
- Study result comparisons

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `items` | list | Yes | Items to compare |
| `attributes` | list | Yes | Comparison attributes |

## Output Format

```json
{
  "markdown_table": "string",
  "html_table": "string"
}
```

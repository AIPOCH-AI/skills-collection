---
name: graph-interpretation
description: Describes statistical graphs in academic language for manuscripts.
version: 1.0.0
category: Present
tags: [graphs, statistics, writing, description]
author: Medical Science Skills
license: MIT
---

# Graph Interpretation

Describes graphs in academic language.

## Features

- Statistical description
- Trend analysis
- Academic phrasing
- Figure caption support

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `graph_type` | str | Yes | "bar", "line", "scatter" |
| `data_description` | str | Yes | Key data features |

## Output Format

```json
{
  "description": "string",
  "caption_suggestion": "string"
}
```

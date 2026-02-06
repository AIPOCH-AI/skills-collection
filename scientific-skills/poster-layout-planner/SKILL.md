---
name: poster-layout-planner
description: Plans layout and content distribution for academic posters.
version: 1.0.0
category: Present
tags: [poster, layout, academic, visualization]
author: Medical Science Skills
license: MIT
---

# Poster Layout Planner

Designs academic poster layouts.

## Features

- Section placement
- Visual hierarchy
- Size recommendations
- Content flow optimization

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `size` | str | Yes | Poster dimensions |
| `sections` | list | Yes | Content sections |

## Output Format

```json
{
  "layout_plan": "string",
  "section_placement": "dict"
}
```

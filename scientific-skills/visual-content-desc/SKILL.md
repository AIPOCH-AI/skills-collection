---
name: visual-content-desc
description: Generates detailed text descriptions of medical images and charts for accessibility and manuscript writing.
version: 1.0.0
category: Info
tags: [accessibility, image-description, alt-text, visualization]
author: Medical Science Skills
license: MIT
---

# Visual Content Desc

Creates accessible descriptions of medical visuals.

## Features

- Image description generation
- Chart interpretation
- Alt text creation
- Figure legend assistance

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_type` | str | Yes | "microscopy", "chart", "scan" |
| `key_features` | list | Yes | Important visual elements |

## Output Format

```json
{
  "description": "string",
  "alt_text": "string",
  "figure_text": "string"
}
```

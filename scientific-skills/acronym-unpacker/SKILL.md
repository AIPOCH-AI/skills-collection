---
name: acronym-unpacker
description: Medical acronym disambiguation tool with context-aware full form lookup
version: 1.0.0
category: Utility
---

# Acronym Unpacker

Expand medical acronyms based on clinical context.

## Use Cases
- Reading clinical notes with abbreviations
- Writing patient-friendly summaries
- Medical education and training

## Parameters
- `acronym`: The abbreviation to expand (e.g., "PID")
- `context`: Clinical context (e.g., "gynecology", "immunology")

## Returns
- List of possible expansions with confidence scores
- Context-appropriate ranking
- Usage frequency data

## Example
Input: "PID", context="gynecology"
Output: "Pelvic Inflammatory Disease" (primary), "Prolapsed Intervertebral Disc" (alternative)

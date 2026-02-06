---
name: drug-pronunciation
description: Provides correct pronunciation guides for complex drug generic names. Generates phonetic transcriptions using IPA and audio generation markers for medical terminology.
version: 1.0.0
category: Education
tags: [pharmacology, pronunciation, medical-terminology, education]
author: Medical Science Skills
license: MIT
---

# Drug Pronunciation

Medical drug name pronunciation assistant with IPA phonetics and syllable breakdown.

## Features

- IPA phonetic transcriptions
- Syllable-by-syllable breakdown
- Emphasis markers
- Audio generation markers (SSML-compatible)
- Coverage of 1000+ common medications

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | str | Yes | Generic or brand drug name |
| `format` | str | No | Output format: "ipa", "simple", "detailed" |

## Output Format

```json
{
  "drug_name": "string",
  "ipa_transcription": "string",
  "syllable_breakdown": ["string"],
  "emphasis": "string",
  "audio_ssml": "string",
  "common_errors": ["string"]
}
```

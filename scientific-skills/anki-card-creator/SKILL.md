---
name: anki-card-creator
description: Convert medical textbook content into Anki flashcards
version: 1.0.0
category: Education
---

# Anki Card Creator

Automated flashcard generation.

## Use Cases
- Medical school exam prep
- Board certification review
- Drug information memorization
- Anatomy retention

## Parameters
- `source_text`: Input content
- `card_type`: Basic/reversible/cloze
- `difficulty`: Step 1/2/3 level

## Returns
- Anki-importable cards
- Cloze deletions
- Image occlusion templates
- Tagged and organized deck

## Example
Input: Pathoma chapter on inflammation
Output: 50 cards with cloze deletions

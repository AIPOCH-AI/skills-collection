---
name: waste-disposal-guide
description: Guide for proper chemical waste disposal by waste container color
trigger: waste, disposal, chemical, safety, guide
tier: C
---

# Waste Disposal Guide

Guide for disposing specific chemical wastes into the correct colored waste containers.

## Usage

```bash
python scripts/main.py --chemical "chloroform"
python scripts/main.py --list-categories
```

## Waste Categories

| Container | Color | Accepts |
|-----------|-------|---------|
| Halogenated | Orange | Chloroform, DCM, halogenated solvents |
| Non-halogenated | Red | Ethanol, acetone, organic solvents |
| Aqueous | Blue | Water-based solutions, buffers |
| Acid | Yellow | Acids (dilute/concentrated) |
| Base | White | Bases, alkali solutions |
| Heavy Metal | Gray | Mercury, lead, cadmium waste |
| Solid | Black | Gloves, paper, solid debris |

## Parameters

- `--chemical`: Chemical name to look up
- `--list-categories`: List all waste categories
- `--safety`: Show safety notes

## Output

- Disposal instructions
- Container color
- Safety precautions

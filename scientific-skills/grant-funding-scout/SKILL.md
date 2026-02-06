---
name: grant-funding-scout
description: NIH funding trend analysis to identify high-priority research areas
version: 1.0.0
category: Research
---

# Grant Funding Scout

Analyze funding patterns to guide research strategy.

## Use Cases
- Identifying "hot" research topics
- Avoiding oversaturated areas
- Strategic grant positioning

## Parameters
- `research_area`: Field of interest
- `years`: Analysis window (default 3 years)

## Returns
- Funding trend visualization
- Top-funded institutions and PIs
- Emerging topic identification

## Example
Input: "cancer immunotherapy", years=3
Output: Funding increased 40% YoY; CAR-T and checkpoint inhibitors dominate

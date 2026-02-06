---
name: citation-chasing-mapping
description: Trace citation networks to discover related research and field evolution
version: 1.0.0
category: Research
---

# Citation Chasing & Mapping

Map knowledge networks through citation analysis.

## Use Cases
- Literature review expansion
- Identifying foundational papers
- Finding recent developments

## Parameters
- `paper_id`: DOI or PubMed ID of seed paper
- `direction`: Ancestors (cited) or Descendants (citing)
- `depth`: Number of citation hops (1-3)

## Returns
- Citation network visualization data
- Key papers at each generation
- Knowledge pathway summary

## Example
Input: Paper on CRISPR-Cas9, direction="descendants", depth=2
Output: Network showing how research evolved from 2012 to present

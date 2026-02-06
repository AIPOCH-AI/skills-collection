---
name: upset-plot-converter
description: Convert complex Venn diagrams with more than 4 sets to clearer Upset
  plots
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Upset Plot Converter

Convert complex Venn diagrams (more than 4 sets) to clearer Upset Plots.

## Usage

```python
from skills.upset_plot_converter.scripts.main import convert_venn_to_upset

# From set data
sets = {
    'A': {1, 2, 3, 4, 5},
    'B': {4, 5, 6, 7, 8},
    'C': {3, 5, 7, 9, 10},
    'D': {2, 4, 6, 8, 10},
    'E': {1, 3, 5, 7, 9}
}
convert_venn_to_upset(sets, output_path="upset_plot.png")

# From list data
from skills.upset_plot_converter.scripts.main import upset_from_lists
set_names = ['Genes A', 'Genes B', 'Genes C', 'Genes D', 'Genes E']
lists = [
    ['gene1', 'gene2', 'gene3'],
    ['gene2', 'gene4', 'gene5'],
    ['gene3', 'gene5', 'gene6'],
    ['gene7', 'gene8', 'gene9'],
    ['gene1', 'gene10', 'gene11']
]
upset_from_lists(set_names, lists, output_path="gene_upset.png", title="Gene Intersections")
```

## Input

- **sets**: Dictionary of set names to sets/lists of elements, OR
- **set_names**: List of set names
- **lists**: List of lists (each containing elements)
- **output_path**: Path to save the output figure
- **title**: Optional title for the plot
- **min_subset_size**: Minimum subset size to display (default: 1)
- **max_intersections**: Maximum number of intersections to show (default: 30)

## Output

PNG file of the Upset Plot visualization.

## Notes

- When Venn diagrams exceed 4 sets, they become difficult to read
- Upset Plots provide a clearer alternative for visualizing set intersections
- The x-axis shows set intersections as dot patterns
- Bar heights represent the size of each intersection
- Automatically sorts intersections by size for better readability

## Requirements

- matplotlib
- numpy
- pandas

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

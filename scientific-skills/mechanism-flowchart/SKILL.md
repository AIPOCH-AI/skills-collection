---
name: mechanism-flowchart
description: Generates Mermaid flowchart code and visual diagrams for pathophysiological mechanisms. Converts medical concepts into clear, publication-quality flowcharts showing disease progression, drug mechanisms, and physiological processes.
version: 1.0.0
category: Education
tags: [medical-education, flowchart, visualization, mermaid, pathophysiology]
author: Medical Science Skills
license: MIT
---

# Mechanism Flowchart

Generates Mermaid flowchart code and visual representations of medical mechanisms, pathophysiology, and drug action pathways.

## Features

- Automatic flowchart generation from text descriptions
- Multiple diagram types (flowchart, sequence, state)
- Customizable styling for publication
- Support for complex branching logic
- Export to multiple formats

## Use Cases

- Creating educational diagrams for presentations
- Visualizing drug mechanism of action
- Illustrating disease pathways
- Thesis and publication figure preparation

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mechanism_description` | str | Yes | Text description of the mechanism |
| `diagram_type` | str | No | Type: "flowchart", "sequence", "state" (default: "flowchart") |
| `direction` | str | No | Flow direction: "TB", "LR", "RL", "BT" |
| `style` | str | No | Visual style: "default", "medical", "minimal" |

## Output Format

```json
{
  "mermaid_code": "string",
  "diagram_type": "string",
  "nodes": ["string"],
  "edges": ["string"],
  "rendered_svg": "string (optional)"
}
```

## Example Usage

```python
from mechanism_flowchart import MechanismDiagram

diagram = MechanismDiagram()
result = diagram.generate(
    "Type 2 Diabetes: Insulin resistance leads to hyperglycemia, "
    "causing beta cell dysfunction and further glucose elevation"
)
print(result['mermaid_code'])
```

## Sample Output

```mermaid
flowchart TB
    A[Insulin Resistance] --> B[Hyperglycemia]
    B --> C[Beta Cell Dysfunction]
    C --> D[Worsening Glucose Control]
    B --> D
```

## Limitations

- Requires Mermaid renderer for visualization
- Complex mechanisms may need manual refinement
- Limited to Mermaid-supported diagram types

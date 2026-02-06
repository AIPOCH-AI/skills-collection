---
id: 158
name: graphical-abstract-wizard
description: Generate graphical abstract layout recommendations based on paper abstracts
version: 1.0.0
author: OpenClaw
language: python
entry_point: scripts/main.py
tags:
  - academic
  - visualization
  - ai-art
  - research
requirements:
  - python>=3.8
  - openai
  - click
---

# Graphical Abstract Wizard

This Skill analyzes academic paper abstracts and generates graphical abstract layout recommendations, including element suggestions, visual arrangements, and AI art prompts for Midjourney and DALL-E.

## Usage

```bash
python scripts/main.py --abstract "Your paper abstract text here"
```

Or from stdin:

```bash
cat abstract.txt | python scripts/main.py
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--abstract` / `-a` | string | Yes* | The paper abstract text to analyze |
| `--style` / `-s` | string | No | Visual style preference (scientific/minimal/colorful/sketch) |
| `--format` / `-f` | string | No | Output format (json/markdown/text), default: markdown |
| `--output` / `-o` | string | No | Output file path (default: stdout) |

*Required if not providing input via stdin

## Examples

### Example 1: Basic Usage

```bash
python scripts/main.py -a "We propose a novel deep learning approach for protein structure prediction that combines transformer architectures with geometric constraints. Our method achieves state-of-the-art accuracy on CASP14 benchmarks."
```

### Example 2: With Style Preference

```bash
python scripts/main.py -a "abstract.txt" -s scientific -o layout.md
```

### Example 3: JSON Output for Integration

```bash
python scripts/main.py -a "$(cat abstract.txt)" -f json > result.json
```

## Output Format

The Skill produces a structured analysis including:

### 1. Key Concepts Extracted
- Core research topic
- Methods/techniques used
- Key findings/results
- Implications

### 2. Visual Element Recommendations
- Recommended icons/symbols
- Color palette suggestions
- Layout structure

### 3. AI Art Prompts
- **Midjourney Prompt**: Optimized for Midjourney v6
- **DALL-E Prompt**: Optimized for DALL-E 3

### 4. Layout Blueprint
- Grid-based layout suggestion
- Element positioning
- Flow direction

## Example Output

```markdown
# Graphical Abstract Recommendation

## Abstract Summary
**Topic**: Deep learning protein structure prediction
**Method**: Transformer + Geometric constraints
**Result**: State-of-the-art CASP14 accuracy

## Key Concepts
- 🧬 Protein structures
- 🤖 Neural networks
- 📊 Accuracy metrics

## Visual Elements
| Element | Symbol | Position | Color |
|---------|--------|----------|-------|
| Core Concept | Brain + DNA | Center | Blue |
| Method | Neural Network | Left | Purple |
| Result | Trophy/Chart | Right | Gold |

## Layout Suggestion
```
┌─────────────────────────────────┐
│        [Title/Concept]          │
│            🧬🤖                 │
├──────────┬──────────┬───────────┤
│  Input   │ Process  │  Output   │
│   📥     │   ⚙️     │    📈     │
└──────────┴──────────┴───────────┘
```

## AI Art Prompts

### Midjourney
```
Scientific graphical abstract, protein structure prediction with neural networks, 3D molecular structures connected by glowing neural network nodes, blue and purple gradient background, clean minimalist style, academic journal style, high quality --ar 16:9 --v 6
```

### DALL-E
```
A clean scientific illustration for a research paper about protein structure prediction using deep learning. Show a 3D protein structure in the center surrounded by abstract neural network connections. Use a professional blue and white color scheme with subtle gradients. Include geometric shapes representing data flow. Modern, minimalist academic style suitable for a Nature or Science journal cover.
```
```

## Technical Details

The Skill uses NLP techniques to:
1. Extract named entities (methods, materials, concepts)
2. Identify research actions and outcomes
3. Map concepts to visual representations
4. Generate style-appropriate prompts

## Dependencies

- Python 3.8+
- OpenAI API (optional, for enhanced analysis)
- Standard library: re, json, argparse, sys

## License

MIT License - Part of OpenClaw Skills Collection

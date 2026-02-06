---
name: q-and-a-prep-partner
description: Predict challenging questions for presentations and prepare responses
trigger: Q&A, presentation, questions, defense, preparation
tier: C
---

# Q&A Prep Partner

Predict challenging questions for presentations and prepare structured responses.

## Usage

```bash
python scripts/main.py --abstract abstract.txt --field oncology
python scripts/main.py --topic "CRISPR therapy" --audience experts
```

## Parameters

- `--abstract`: Abstract text or file
- `--topic`: Research topic
- `--field`: Research field
- `--audience`: Audience type (general/experts/peers)
- `--n-questions`: Number of questions to generate (default: 10)

## Question Types

1. Methodology questions
2. Statistical questions
3. Interpretation questions
4. Limitation questions
5. Future work questions
6. Comparison questions

## Output

- Predicted questions
- Suggested response frameworks
- Key points to address

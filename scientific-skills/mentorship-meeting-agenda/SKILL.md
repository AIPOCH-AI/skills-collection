---
name: mentorship-meeting-agenda
description: Generate structured agendas for mentor-student one-on-one meetings
trigger: mentorship, meeting, agenda, advisor, student, one-on-one
tier: C
---

# Mentorship Meeting Agenda

Generate structured agendas for mentor-student one-on-one meetings to ensure productive discussions.

## Usage

```bash
python scripts/main.py --student "Alice" --phase early --output agenda.md
```

## Parameters

- `--student`: Student name
- `--phase`: Career phase (early/mid/late)
- `--topics`: Specific topics to cover
- `--output`: Output file

## Agenda Sections

1. Progress updates (5 min)
2. Current challenges (10 min)
3. Goal setting (10 min)
4. Resource needs (5 min)
5. Action items (5 min)

## Output

- Structured meeting agenda
- Time allocations
- Discussion prompts
- Follow-up tracker

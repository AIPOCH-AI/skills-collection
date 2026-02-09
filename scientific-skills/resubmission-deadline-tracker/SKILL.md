---
name: resubmission-deadline-tracker
description: Monitor resubmission deadlines for academic papers and automatically
  break down tasks based on remaining time. Trigger when user mentions "resubmission
  deadline", "revision due", "paper deadline", "revise and resubmit deadline", "R&R
  deadline", or needs to track manuscript revision timelines.
version: 1.0.0
category: Writing
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Resubmission Deadline Tracker

A specialized tool for academic researchers to monitor manuscript resubmission deadlines and automatically generate task breakdowns based on remaining time.

## Overview

This skill helps researchers manage the critical period between receiving reviewer feedback and submitting revisions. It calculates remaining time, assesses workload, and creates actionable task schedules.

## When to Use

- After receiving "revise and resubmit" (R&R) decisions
- When planning major revisions with journal deadlines
- For tracking multiple concurrent resubmissions
- When breaking down large revision tasks into manageable chunks
- For prioritizing tasks based on deadline urgency

## Workflow

### Step 1: Input Collection

Gather essential deadline information:
- **Manuscript title**: Paper identifier
- **Journal name**: Target publication
- **Deadline date**: Submission due date (YYYY-MM-DD format)
- **Deadline time**: Optional time (defaults to 23:59)
- **Reviewer comments**: Summary or count of major/minor issues
- **Current status**: Just started / In progress / Final review

### Step 2: Time Analysis

Calculate and display:
- Total remaining days/hours
- Weekday breakdown (excludes weekends for realistic planning)
- Urgency level classification

### Step 3: Task Breakdown

Based on remaining time, automatically generate:

| Time Remaining | Task Structure |
|----------------|----------------|
| >30 days | Relaxed schedule with buffer days |
| 14-30 days | Standard revision workflow |
| 7-14 days | Accelerated schedule |
| 3-7 days | Urgent mode - priority only |
| <3 days | Emergency checklist |

### Step 4: Priority Assignment

Tasks are automatically prioritized:
1. **Critical** (P0): Must complete for resubmission
2. **High** (P1): Strongly recommended improvements
3. **Medium** (P2): Enhancements if time permits
4. **Low** (P3): Optional polish items

## Task Templates

### Standard Revision Tasks (>14 days)

```
Phase 1: Analysis (Days 1-2)
- [ ] Re-read reviewer comments carefully
- [ ] Categorize comments by type (major/minor)
- [ ] Create response strategy document
- [ ] Identify required new analyses

Phase 2: Core Revisions (Days 3-10)
- [ ] Address major concerns
- [ ] Revise methodology if needed
- [ ] Update figures and tables
- [ ] Add new data/analyses

Phase 3: Writing (Days 11-14)
- [ ] Draft response letter
- [ ] Revise manuscript text
- [ ] Update supplementary materials
- [ ] Proofread all changes

Phase 4: Final Review (Days 15-16)
- [ ] Internal review by co-authors
- [ ] Final formatting checks
- [ ] Journal submission system prep
- [ ] Submit before deadline
```

### Urgent Mode (3-7 days)

```
Day 1: Triage
- [ ] Prioritize critical reviewer concerns only
- [ ] Identify "must-fix" vs "nice-to-have"
- [ ] Draft quick response outline

Day 2-5: Execute
- [ ] Address P0 items only
- [ ] Make essential figure updates
- [ ] Draft concise response letter

Day 6-7: Finalize
- [ ] Co-author sign-off (async if possible)
- [ ] Final proofread
- [ ] Submit
```

### Emergency Checklist (<3 days)

```
Immediate Actions:
- [ ] List minimum viable changes for acceptance
- [ ] Contact co-authors for emergency review
- [ ] Focus only on deal-breaker issues
- [ ] Request deadline extension (if possible)
- [ ] Prepare minimal response letter
- [ ] Submit even if imperfect
```

## Usage Examples

### Example 1: Standard Tracking

```
User: Track my resubmission for the Cancer Research paper.
Deadline is 2024-03-15.

Skill Output:
📅 Resubmission Deadline Tracker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manuscript: Cancer Research Paper
Deadline: March 15, 2024 (23:59)
Remaining: 18 days, 6 hours
Status: ⏰ Standard Pace

📋 Recommended Task Schedule:
[Task breakdown based on 18-day timeline]
```

### Example 2: Multiple Papers

```
User: Show all my tracked deadlines.

Skill Output:
📊 Active Resubmissions:
┌─────────────────────┬────────────┬───────────┬──────────┐
│ Paper               │ Deadline   │ Remaining │ Status   │
├─────────────────────┼────────────┼───────────┼──────────┤
│ Nature Medicine     │ 2024-03-10 │ 3 days    │ 🔴 Urgent│
│ Cell Reports        │ 2024-03-25 │ 18 days   │ 🟡 Active│
│ JCI                 │ 2024-04-02 │ 26 days   │ 🟢 On Track│
└─────────────────────┴────────────┴───────────┴──────────┘
```

## Output Format

The skill provides:
1. **Deadline Summary**: Current status and urgency level
2. **Task Breakdown**: Phase-by-phase schedule
3. **Daily Targets**: Recommended tasks per day
4. **Progress Tracking**: Checkbox list for completion
5. **Deadline Alerts**: Warnings as deadline approaches

## Parameters

- `deadline`: Target submission date (YYYY-MM-DD)
- `deadline_time`: Optional time (HH:MM, defaults to 23:59)
- `timezone`: User's timezone (defaults to Asia/Shanghai)
- `reviewer_count`: Number of reviewers (affects workload estimate)
- `major_issues`: Count of major concerns
- `minor_issues`: Count of minor concerns
- `manuscript_title`: Paper title
- `journal`: Target journal name
- `notes`: Additional context

## Command-Line Usage

```bash
# Add new deadline
python scripts/main.py --add --title "Cancer Research Paper" \
  --journal "Nature Medicine" \
  --deadline "2024-03-15" \
  --major-issues 2 \
  --minor-issues 8

# List all tracked deadlines
python scripts/main.py --list

# Show details for specific paper
python scripts/main.py --show "Cancer Research Paper"

# Update progress
python scripts/main.py --update "Cancer Research Paper" --progress 60

# Generate task breakdown
python scripts/main.py --tasks "Cancer Research Paper"

# Interactive mode
python scripts/main.py --interactive
```

## Data Storage

Deadlines are stored locally in:
- `data/deadlines.json` - Active deadlines
- `data/completed.json` - Historical submissions

## Integration

Can export to:
- Calendar events (.ics)
- Task managers (Todoist, Things)
- Project management tools (Trello, Notion)

## Technical Notes

- **Difficulty**: Medium - Requires date calculations, task scheduling logic
- **Dependencies**: Python 3.8+, no external packages required
- **Storage**: Local JSON files (no cloud dependency)
- **Safety**: No external API calls; all data stays local

## Limitations

- Does not automatically sync with journal systems
- Task estimates are based on typical revision patterns
- User must manually update progress
- Does not send actual reminders (displays status on demand)

## References

- `references/task_templates.json` - Standard task breakdowns
- `references/journal_deadlines.md` - Common journal policies
- `references/revision_checklist.md` - Best practices

## Quality Checklist

Before relying on deadline calculations:
- [ ] Verify deadline date and timezone
- [ ] Confirm if deadline is "received by" or "submitted by"
- [ ] Check journal's time zone policy
- [ ] Account for institutional submission approval time
- [ ] Add buffer for technical issues

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

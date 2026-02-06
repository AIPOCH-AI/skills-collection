# Skill Development Completion Report

## Skill: adverse-event-narrative (ID: 44)

### Status Summary

| Field | Value |
|-------|-------|
| **Skill Name** | adverse-event-narrative |
| **Bitable Record ID** | recvakkyWeUkrO |
| **Tier** | Tier B, Pharma |
| **AI Completion Status** | ✔️ 已完成 |
| **AI Self-Review Status** | 需人工检查 |
| **Technical Difficulty** | 高 |
| **File Path** | /Users/z04030865/.openclaw/workspace/skills/adverse-event-narrative/ |

### Files Created

```
skills/adverse-event-narrative/
├── SKILL.md                          # Main skill documentation (English, YAML frontmatter)
├── scripts/
│   └── main.py                       # Python narrative generator (executable)
└── references/
    ├── CIOMS_I_Guidelines.md         # CIOMS I standard guidelines
    ├── ICSR_Template.md              # Standard narrative template
    ├── MedDRA_Reference.md           # Medical terminology reference
    ├── Quick_Reference.md            # User quick start guide
    ├── sample_case_001.json          # Full example case
    └── sample_case_minimal.json      # Minimal example case
```

### Functionality

The skill generates CIOMS-compliant adverse event narratives for Individual Case Safety Report (ICSR) submissions.

**Features:**
- Structured narrative generation following CIOMS I standard
- Input validation for required fields
- Support for complex cases with multiple drugs, events, and test results
- Dechallenge/Rechallenge documentation
- Causality assessment formatting
- MedDRA-aware output structure

**Tested Successfully:**
- Full sample case (Lactic acidosis with Metformin) ✓
- Minimal sample case (Anaphylactic reaction) ✓
- Input validation ✓

### Technical Notes

**Difficulty: High** ⚠️

This skill involves:
- Medical domain knowledge requirements
- Pharmacovigilance regulatory compliance
- Temporal relationship assessments
- MedDRA terminology integration
- Causality evaluation principles

**Required fields:** case_id, patient_age/sex, suspect_drugs, adverse_events

### Bitable Update Note

⚠️ **Cannot update Bitable via API** - Feishu App has `bitable:app:readonly` permission only.

**Manual update required:**
- Record ID: recvakkyWeUkrO
- Fields to update:
  - `AI完成状态` = `✔️ 已完成`
  - `AI自主验收状态` = `需人工检查`
  - `技术难度` = `高`
  - `文件` = `/Users/z04030865/.openclaw/workspace/skills/adverse-event-narrative/`

### Sample Output Verification

The generated narrative includes all CIOMS-required sections:
1. Case identifier and date
2. Patient demographics
3. Medical history
4. Concomitant medications
5. Suspect drug details (name, indication, dose, dates, lot)
6. Adverse events (MedDRA PT, onset, severity, seriousness)
7. Diagnostic test results with reference ranges
8. Treatment interventions
9. Dechallenge and rechallenge results
10. Outcome and sequelae
11. Causality assessment with rationale
12. Reporter comments

### Usage Example

```bash
cd /Users/z04030865/.openclaw/workspace/skills/adverse-event-narrative
python3 scripts/main.py --input references/sample_case_001.json --output narrative.txt
```

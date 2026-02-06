# Data Management Plan (DMP) Creator

This Skill automatically generates NIH 2023-compliant Data Management and Sharing Plans (DMSP) following FAIR principles.

## Quick Start

```bash
# Interactive mode
python scripts/main.py --interactive

# Command line
python scripts/main.py \
    --project-title "Your Project" \
    --pi-name "Dr. Investigator" \
    --institution "Your Institution" \
    --data-types "genomic,clinical" \
    --repository "dbGaP,GEO"
```

## Documentation

- [Full Skill Documentation](SKILL.md)
- [NIH DMSP Template](references/nih_dmp_template.md)

## Files

```
.
├── SKILL.md                          # Main documentation
├── scripts/
│   └── main.py                       # DMSP generator script
├── references/
│   └── nih_dmp_template.md           # NIH template reference
└── README.md                         # This file
```

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT

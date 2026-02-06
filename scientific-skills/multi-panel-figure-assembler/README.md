# Multi-panel Figure Assembler

## File Structure

```
multi-panel-figure-assembler/
├── SKILL.md              # Skill documentation with YAML frontmatter
├── README.md             # This file
└── scripts/
    ├── __init__.py       # Package initialization
    ├── main.py           # Main assembler implementation
    └── example.py        # Example usage script
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install Pillow numpy
   ```

2. **Basic usage:**
   ```bash
   cd scripts
   python main.py -i A.png B.png C.png D.png E.png F.png -o figure.png
   ```

3. **See examples:**
   ```bash
   python scripts/example.py
   ```

## Requirements

- Python 3.8+
- Pillow (PIL)
- NumPy (optional, for advanced features)

## License

MIT

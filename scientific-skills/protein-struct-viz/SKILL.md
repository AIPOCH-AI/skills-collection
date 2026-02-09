---
name: protein-struct-viz
description: Generate PyMOL scripts to highlight specific protein residues in PDB
  structures. Use this skill when the user needs to visualize specific amino acid
  residues, create publication-quality protein images, or highlight functional sites
  in protein structures.
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# protein-struct-viz

Generate PyMOL scripts for highlighting specific protein residues in molecular structures.

## Overview

This skill creates PyMOL command scripts to visualize protein structures with specific residues highlighted using various representation styles (sticks, spheres, surface, etc.).

## Usage

The skill generates `.pml` script files that can be executed directly in PyMOL to:
- Load PDB structures
- Apply custom color schemes
- Highlight specific residues with different representation styles
- Create publication-ready visualization settings

### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdb_file` | string | Path to PDB file or PDB ID (e.g., "1abc") |
| `residues` | list | List of residue specifications (chain:resnum:resname) |
| `style` | string | Visualization style: "sticks", "spheres", "surface", "cartoon" |
| `color_scheme` | string | Color scheme: "rainbow", "chain", "element", custom hex |
| `output_name` | string | Output filename for the generated script |

### Residue Specification Format

- Format: `chain:resnum:resname` or `resnum` (for single chain)
- Examples: `A:145:ASP`, `B:23:LYS`, `156`
- Wildcards: `A:*` (all residues in chain A)

## Example

```bash
python scripts/main.py --pdb 1mbn --residues "A:64:HIS,A:93:VAL,A:97:LEU" --style sticks --color_scheme rainbow --output myoglobin_active_site.pml
```

This will generate a PyMOL script highlighting the specified residues in myoglobin's active site.

## Output

Generated `.pml` script includes:
1. Structure loading commands
2. Background and lighting settings
3. Global representation settings
4. Specific residue highlighting
5. View optimization commands
6. Optional: ray tracing for high-quality images

## References

See `references/` directory for:
- PyMOL command reference
- Color palette templates
- Example scripts for common visualization tasks

## Technical Difficulty

Medium - requires understanding of PyMOL scripting syntax and protein structure concepts.

## Dependencies

- PyMOL (installed separately)
- Python 3.7+
- No Python package dependencies (generates plain text scripts)

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
## Prerequisites

No additional Python packages required.

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

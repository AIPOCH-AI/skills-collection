---
name: protein-struct-viz
description: Generate PyMOL scripts to highlight specific protein residues in PDB structures. Use this skill when the user needs to visualize specific amino acid residues, create publication-quality protein images, or highlight functional sites in protein structures.
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

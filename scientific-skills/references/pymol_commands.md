# PyMOL Command Reference

## Basic Commands

### Structure Loading
```
fetch <pdb_id>          # Download from RCSB PDB
cmd.load <file.pdb>     # Load local file
cmd.read_pdbstr <str>   # Load from PDB string
```

### Selection Syntax
```
selection-name: selection-expression

# Selection operators
and         # intersection
or          # union
not         # difference
around X    # atoms within X Angstroms
expand X    # expand selection by X Angstroms
byres       # extend to complete residues
```

### Selection Examples
```
chain A                 # All atoms in chain A
resi 145                # Residue number 145
resn ASP                # All aspartate residues
name CA                 # All alpha carbons
chain A and resi 145    # Residue 145 in chain A
resi 145-160            # Residue range
center chain A          # Center of chain A
```

## Representation Commands

```
show <representation> [, <selection>]
hide <representation> [, <selection>]

# Representations:
lines       # Lines between bonded atoms
sticks      # Cylinders for bonds
spheres     # Spheres for atoms
surface     # Solvent accessible surface
mesh        # Mesh surface
dots        # Dotted surface
cartoon     # Secondary structure cartoon
ribbon      # Smooth ribbon
cells       # Unit cell
```

## Color Commands

```
color <color> [, <selection>]

# Predefined colors:
red, green, blue, yellow, magenta, cyan
orange, salmon, lime, pink, slate, teal
gray, white, black, wheat, paleyellow

# Color schemes:
util.cbc()              # Color by chain
cmd.spectrum()          # Rainbow gradient
cmd.spectrum('b')       # Color by B-factor
```

## View Settings

```
bg_color <color>        # Background color
zoom <selection>        # Zoom on selection
center <selection>      # Center view
reset                   # Reset view
orient <selection>      # Orient selection
```

## Rendering Settings

```
set ray_trace_mode, 0   # Normal rendering
set ray_trace_mode, 1   # Normal + shadows
set ray_trace_mode, 2   # Normal + black outlines
set ray_trace_mode, 3   # Quicker outline mode

set antialias, 2        # Antialiasing (0-4)
set ray_shadows, 0      # Disable shadows
set ray_shadows, 1      # Enable shadows

ray [width, height]     # Ray trace image
png <filename>          # Save image
```

## Atom Properties

```
resi    # Residue number
resn    # Residue name (3-letter code)
name    # Atom name (CA, CB, N, O, etc.)
elem    # Element symbol
chain   # Chain identifier
seg     # Segment identifier
alt     # Alternate conformation
```

## Common Residue Names

| Code | Name          | Code | Name          |
|------|---------------|------|---------------|
| ALA  | Alanine       | LEU  | Leucine       |
| ARG  | Arginine      | LYS  | Lysine        |
| ASN  | Asparagine    | MET  | Methionine    |
| ASP  | Aspartate     | PHE  | Phenylalanine |
| CYS  | Cysteine      | PRO  | Proline       |
| GLN  | Glutamine     | SER  | Serine        |
| GLU  | Glutamate     | THR  | Threonine     |
| GLY  | Glycine       | TRP  | Tryptophan    |
| HIS  | Histidine     | TYR  | Tyrosine      |
| ILE  | Isoleucine    | VAL  | Valine        |

## Tips

1. Use `cmd.dss()` to assign secondary structure
2. Use `util.cbc()` for chain coloring
3. Use `center` and `zoom` together for focused views
4. Save sessions with `save session.pse`
5. Use `label sele and name CA, '%s %s' % (resn, resi)` for residue labels

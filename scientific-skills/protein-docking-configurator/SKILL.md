---
name: protein-docking-configurator
description: Prepare input files for molecular docking software, automatically determine Grid Box center and size. Supports AutoDock Vina, AutoDock4, and other mainstream docking tools.
---

# Protein Docking Configurator

## Features

- Parse protein PDB files, identify ligand binding pockets
- Automatically calculate Grid Box center coordinates and dimensions
- Generate AutoDock Vina configuration files
- Generate AutoDock4 Grid parameter files
- Support Box positioning based on active site residues or ligands

## Usage

### As Command Line Tool

```bash
# Calculate Grid Box based on active site residues
python scripts/main.py --receptor protein.pdb --active-site-residues "A:120,A:145,A:189" --software vina

# Calculate Grid Box based on reference ligand
python scripts/main.py --receptor protein.pdb --reference-ligand ligand.pdb --software vina

# Manually specify Box parameters
python scripts/main.py --receptor protein.pdb --center-x 10.5 --center-y -5.2 --center-z 20.1 --size-x 20 --size-y 20 --size-z 20 --software vina
```

### As Python Module

```python
from scripts.main import DockingConfigurator

config = DockingConfigurator()

# Calculate box from receptor and active site
config.from_active_site("protein.pdb", ["A:120", "A:145", "A:189"])
config.write_vina_config("config.txt", exhaustiveness=32)

# Calculate box from receptor and reference ligand
config.from_reference_ligand("protein.pdb", "ligand.pdb", padding=5.0)
config.write_autodock4_gpf("protein.gpf", spacing=0.375)
```

## Parameter Description

### Command Line Parameters

| Parameter | Description | Required |
|------|------|------|
| `--receptor` | Receptor protein PDB file path | Yes |
| `--software` | Docking software type (vina/autodock4) | Yes |
| `--active-site-residues` | Active site residue list, format: "chain:residue_number" | No |
| `--reference-ligand` | Reference ligand PDB/MOL file | No |
| `--center-x/y/z` | Grid Box center coordinates | No |
| `--size-x/y/z` | Grid Box dimensions (Å) | No |
| `--spacing` | Grid spacing (AutoDock4 only) | No (default 0.375) |
| `--exhaustiveness` | Search exhaustiveness (Vina only) | No (default 32) |
| `--output` | Output file path | No |

## Output

- **AutoDock Vina**: Generates config.txt configuration file
- **AutoDock4**: Generates .gpf (Grid Parameter File) and corresponding macromolecule files

## Dependencies

- Python 3.8+
- numpy

## Examples

```bash
# Example 1: Using active site residues
python scripts/main.py --receptor 1abc_receptor.pdb --active-site-residues "A:45,A:92,A:156" --software vina --output vina_config.txt

# Example 2: Using reference ligand with custom Box size
python scripts/main.py --receptor kinase.pdb --reference-ligand ATP.pdb --software vina --size-x 25 --size-y 25 --size-z 25

# Example 3: AutoDock4 configuration
python scripts/main.py --receptor protein.pdb --active-site-residues "A:100" --software autodock4 --spacing 0.375 --output protein.gpf
```

## Notes

1. Input PDB files should have water molecules and heteroatoms removed (unless needed)
2. It is recommended to protonate and calculate charges for the receptor (using AutoDock Tools, etc.)
3. Grid Box size should be sufficient to cover ligand conformational space, typically 20-30Å
4. Active site residues should include catalytic residues and key binding residues

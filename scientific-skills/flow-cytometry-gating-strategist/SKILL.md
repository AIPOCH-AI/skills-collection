---
name: flow-cytometry-gating-strategist
description: Recommend optimal flow cytometry gating strategies for specific cell types and fluorophores
---

# Skill: Flow Cytometry Gating Strategist

Recommend optimal flow cytometry gating strategies for given cell types and fluorophores.

## Basic Information

- **ID**: 103
- **Name**: Flow Cytometry Gating Strategist
- **Purpose**: Flow cytometry data analysis and gating strategy recommendations

## Usage

### Command Line

```bash
# Recommended format: comma-separated cell types and fluorophores
python scripts/main.py "CD4+ T cells,CD8+ T cells" "FITC,PE,APC"

# Or specify parameters separately
python scripts/main.py --cell-types "CD4+ T cells,CD8+ T cells" --fluorophores "FITC,PE,APC"

# Support more options
python scripts/main.py \
  --cell-types "B cells" \
  --fluorophores "FITC,PE,PerCP-Cy5.5,APC" \
  --instrument "BD FACSCanto II" \
  --purpose "cell sorting"
```

### Output Format

```json
{
  "recommended_strategy": {
    "name": "Sequential Gating Strategy",
    "description": "Gating based on FSC-A/SSC-A, followed by fluorescence intensity analysis",
    "steps": [
      {
        "step": 1,
        "gate": "FSC-A vs SSC-A",
        "purpose": "Identify target cell population, exclude debris and dead cells",
        "recommendation": "Set oval gate in lymphocyte region"
      }
    ]
  },
  "fluorophore_recommendations": [
    {
      "fluorophore": "FITC",
      "channel": "BL1",
      "detector": "530/30",
      "considerations": ["May spillover with GFP"]
    }
  ],
  "panel_optimization": {
    "suggestions": ["Recommend pairing weakly expressed antigens with bright fluorophores"],
    "avoid_combinations": ["FITC and GFP used simultaneously"]
  },
  "compensation_notes": ["FITC and PE require careful compensation"],
  "quality_control": ["Recommend setting FMO controls", "Use viability dyes to exclude dead cells"]
}
```

## Supported Cell Types

- **T cells**: CD4+ T cells, CD8+ T cells, Treg cells, Th1, Th2, Th17, γδ T cells
- **B cells**: B cells, Plasma cells, Memory B cells, Naive B cells
- **Myeloid cells**: Monocytes, Macrophages, Dendritic cells, Neutrophils, Eosinophils
- **Stem cells**: HSC, MSC, iPSC
- **Tumor cells**: Tumor cells, Cancer stem cells
- **Others**: NK cells, NKT cells, Platelets, Erythrocytes

## Supported Fluorophores

| Fluorophore | Excitation Wavelength | Emission Wavelength | Detection Channel |
|------|---------|---------|---------|
| FITC | 488nm | 525nm | BL1 |
| PE | 488nm | 575nm | YL1/BL2 |
| PerCP | 488nm | 675nm | RL1 |
| PerCP-Cy5.5 | 488nm | 695nm | RL1 |
| PE-Cy7 | 488nm | 785nm | RL2 |
| APC | 640nm | 660nm | RL1 |
| APC-Cy7 | 640nm | 785nm | RL2 |
| BV421 | 405nm | 421nm | VL1 |
| BV510 | 405nm | 510nm | VL2 |
| BV605 | 405nm | 605nm | VL3 |
| BV650 | 405nm | 650nm | VL4 |
| BV785 | 405nm | 785nm | VL6 |
| DAPI | 355nm | 461nm | UV |
| PI | 488nm | 617nm | YL2 |

## Gating Strategy Types

### 1. Sequential Gating
Applicable scenario: Simple immunophenotyping analysis
- FSC-A/SSC-A → Exclude debris/dead cells → Fluorescence intensity analysis

### 2. Boolean Gating
Applicable scenario: Complex cell subset analysis
- Use logical operators (AND, OR, NOT) to define cell populations

### 3. Dimensionality Reduction Gating
Applicable scenario: High-dimensional data (>15 colors)
- t-SNE/UMAP visualization-assisted gating

### 4. Unsupervised Clustering
Applicable scenario: Discovery of unknown cell populations
- FlowSOM, PhenoGraph and other algorithms

## Notes

1. **Spectral Overlap Compensation**: Multi-color panels must undergo compensation calculation
2. **Control Setup**: Must use FMO (fluorescence minus one) and isotype controls
3. **Dead Cell Exclusion**: Strongly recommend using viability dyes
4. **Instrument Calibration**: Perform QC and standard bead detection before experiments

## Dependencies

- Python 3.8+
- No external dependencies (pure Python standard library)

## Version

v1.0.0 - Initial version, supports basic gating strategy recommendations

---
name: 3d-molecule-ray-tracer
description: Generate photorealistic rendering scripts for PyMOL and UCSF ChimeraX.
  Creates publication-quality molecular images with ray-tracing, depth of field (DOF),
  ambient occlusion, and cinematic lighting effects suitable for journal covers and
  high-impact figures.
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

# 3D Molecule Ray-tracer

Generate cinematic-quality molecular visualization scripts with advanced rendering effects.

## Overview

This skill creates professional-grade rendering scripts for:
- **PyMOL**: Ray-traced images with depth of field, ambient occlusion, and shadows
- **UCSF ChimeraX**: Photorealistic rendering with physically-based lighting

Perfect for creating cover-worthy protein structure images with cinematic visual effects.

## Features

### Rendering Effects
| Effect | Description |
|--------|-------------|
| Ray Tracing | Physically accurate light simulation |
| Depth of Field | Focus on specific regions with blurred background |
| Ambient Occlusion | Enhanced depth perception through soft shadows |
| Soft Shadows | Realistic shadow casting |
| Volumetric Fog | Atmospheric depth effects |
| Reflection/Gloss | Surface material properties |

### Supported Software
- **PyMOL** (2.5+): Classic molecular visualization with ray_tracing
- **UCSF ChimeraX** (1.5+): Next-gen rendering with physical lighting

## Usage

### Basic Cover-Quality Render
```bash
python scripts/main.py --software pymol --pdb 1mbn --preset cover --output render.pml
```

### Custom Depth of Field
```bash
python scripts/main.py --software chimerax --pdb 1mbn \
    --dof-focus "A:64" --dof-aperture 2.0 \
    --lighting cinematic --output dof_render.cxc
```

### Advanced Scene Setup
```bash
python scripts/main.py --software pymol --pdb protein.pdb \
    --style surface --ao-on --shadows --fog 0.3 \
    --resolution 3000 --output advanced.pml
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `software` | string | `pymol` | Target software: `pymol` or `chimerax` |
| `pdb` | string | required | PDB file path or 4-letter PDB ID |
| `preset` | string | `standard` | Preset: `standard`, `cover`, `publication`, `cinematic` |
| `style` | string | `cartoon` | Representation: `cartoon`, `surface`, `ribbon`, `spheres` |
| `resolution` | int | `2400` | Output image resolution (width in pixels) |
| `dof-focus` | string | `center` | DOF focus: `center`, `selection`, or residue spec |
| `dof-aperture` | float | `1.0` | Aperture size (higher = more blur) |
| `ao-on` | bool | false | Enable ambient occlusion |
| `shadows` | bool | false | Enable shadow casting |
| `fog` | float | `0.0` | Fog density (0-1) |
| `lighting` | string | `default` | Lighting preset: `default`, `cinematic`, `studio`, `outdoor` |
| `bg-color` | string | `white` | Background color |
| `output` | string | `output.pml` | Output script filename |

## Presets

### `standard`
Basic ray-traced image with default settings.

### `cover`
- 3000px resolution
- Depth of field on center
- Ambient occlusion enabled
- Soft shadows
- Enhanced lighting

### `publication`
- 2400px resolution (journal standard)
- Clean white background
- No depth of field (all in focus)
- Consistent lighting

### `cinematic`
- 4K resolution
- Dramatic depth of field
- Volumetric fog
- Three-point lighting setup
- Reflection effects

## Output

Generated script includes:
1. Structure loading
2. Representation setup
3. Advanced rendering configuration
4. Lighting setup
5. Camera positioning
6. Ray tracing/render commands

## Technical Requirements

| Software | Minimum Version | Recommended |
|----------|----------------|-------------|
| PyMOL | 2.5 | 3.0+ |
| ChimeraX | 1.5 | 1.7+ |

### Hardware Recommendations
- **RAM**: 8GB minimum, 16GB+ recommended for large structures
- **GPU**: Optional but speeds up preview; CPU used for final ray-trace
- **Storage**: 100MB+ free for high-resolution output images

## Tips for Cover-Quality Images

1. **Focus**: Use DOF to draw attention to active sites or key features
2. **Lighting**: Cinematic lighting creates drama; studio lighting for clarity
3. **Angle**: Slight tilt adds dynamism; eye-level is more neutral
4. **Color**: Consider using a color scheme that matches the journal's style
5. **Composition**: Rule of thirds; place the main subject off-center

## References

- PyMOL Ray Tracing: https://pymolwiki.org/index.php/Ray
- ChimeraX Lighting: https://www.cgl.ucsf.edu/chimerax/docs/user/commands/lighting.html
- Depth of Field in Molecular Viz: https://pymolwiki.org/index.php/Depth_cueing

## Technical Difficulty

Advanced - requires understanding of:
- Rendering concepts (ray tracing, depth of field, lighting)
- PyMOL/ChimeraX command syntax
- Molecular representation choices
- Photography/composition basics

## Dependencies

- Python 3.8+
- PyMOL or UCSF ChimeraX (installed separately)
- No additional Python packages required

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

# Example PyMOL Scripts

## Example 1: Active Site Highlighting

```python
# Load structure
fetch 1mbn, async=0

# Settings
bg_color white
set antialias, 2
hide everything
show cartoon

# Color protein
color gray70, all

# Highlight active site residues
select active_site, resi 64+93+97 and chain A
show sticks, active_site
color red, active_site
show spheres, active_site and name FE

# Add water molecules nearby
select waters, resn HOH within 5 of active_site
show spheres, waters
color cyan, waters

# Center view
center active_site
zoom active_site, 10

# Optional labels
label active_site and name CA, "%s%s" % (resn, resi)
```

## Example 2: Protein-Ligand Interaction

```python
fetch 3fgu, async=0

bg_color white
set antialias, 2
hide everything
show cartoon
color gray70, polymer

# Highlight ligand
select ligand, organic
show sticks, ligand
color green, ligand

# Show interacting residues
select interface, byres ligand around 4
show sticks, interface and not ligand
color yellow, interface and not ligand

# Polar contacts
dist polar_contacts, ligand, interface, 3.5, mode=2
hide labels, polar_contacts

zoom ligand, 10
```

## Example 3: Domain Coloring

```python
fetch 1tgn, async=0

hide everything
show cartoon

# Color by domain
select domain1, chain A and resi 1-100
color red, domain1

select domain2, chain A and resi 101-250
color blue, domain2

select domain3, chain A and resi 251-400
color green, domain3

# Show domain boundaries
select boundary1, resi 100-101
color yellow, boundary1

select boundary2, resi 250-251
color orange, boundary2

show sticks, boundary1 or boundary2
```

## Example 4: Surface Representation with Highlighted Interior

```python
fetch 1abc, async=0

hide everything
show surface
color white, all
set transparency, 0.3

# Highlight binding pocket
select pocket, resi 45+78+112+156
show sticks, pocket
color red, pocket
set sphere_scale, 0.3, pocket

# Add light source
set light_count, 2
set specular, 0.5

ray 1200, 1200
png pocket_view.png, dpi=300
```

## Example 5: Multiple Chain Comparison

```python
fetch 1abc, async=0

hide everything
show cartoon

# Color chains differently
color red, chain A
color blue, chain B
color green, chain C
color yellow, chain D

# Show interface residues
select interface_AB, (chain A around 4 of chain B) or (chain B around 4 of chain A)
show sticks, interface_AB
color magenta, interface_AB

# Label chains
pseudoatom label_A, chain A and resi 1 and name CA
label label_A, "Chain A"

set label_size, 20
```

## Example 6: Publication Quality Figure

```python
fetch 1mbn, async=0

# High quality settings
bg_color white
set antialias, 2
set ray_shadows, 0
set orthoscopic, 1

# Representation
hide everything
show cartoon
color gray90, all

# Highlight residues
select key_residues, resi 64+93+97+103
color red, key_residues
show sticks, key_residues

# Smooth appearance
set cartoon_smooth_loops, 1
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1

# Lighting
set ambient, 0.4
set specular, 0.5
set spec_power, 200

# Ray trace for publication quality
set ray_trace_mode, 1
set ray_trace_gain, 0.005
ray 2400, 2400

png figure.png, dpi=300
```

---
name: circos-plot-generator
description: Generate Circos configuration files for circular genomics data visualization. Supports genomic variations (SNPs, CNVs, structural variants), cell-cell communication networks, and custom track configurations for publication-ready circular plots.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
  skill-author: AIPOCH
---

# Circos Plot Generator

Generate configuration files for Circos circular visualization plots, enabling genomics data visualization including genomic variations, chromosome ideograms, cell-cell communication networks, and custom track annotations. Simplifies the complex Circos configuration process for researchers without Perl expertise.

**Key Capabilities:**
- **Genomic Variation Visualization**: Create plots for SNPs, CNVs, structural variants (translocations, inversions)
- **Cell-Cell Communication Networks**: Visualize intercellular interactions and signaling pathways
- **Chromosome Ideograms**: Display chromosome structure with bands and annotations
- **Multiple Track Types**: Support histograms, scatter plots, links, heatmaps, and text tracks
- **Publication-Ready Output**: Generate configurations for high-quality PNG/SVG figures

---

## When to Use

**✅ Use this skill when:**
- Visualizing **genomic variations** across chromosomes (SNPs, CNVs, SVs) for publication
- Creating **circular genome maps** showing multiple data types simultaneously
- Plotting **cell-cell communication networks** from single-cell RNA-seq data
- Displaying **synteny or chromosomal rearrangements** between genomes
- Creating **circos plots** for grant proposals, presentations, or papers
- Generating **custom track visualizations** for genomic features
- Comparing **structural variants** across multiple samples or conditions

**❌ Do NOT use when:**
- Needing **interactive genome browsers** (e.g., IGV, UCSC) → Use genome browser tools
- Creating **linear genome plots** → Use `cnv-caller-plotter` or `gene-structure-mapper`
- Analyzing **time-series or trajectory data** → Use trajectory analysis tools
- Working with **protein structures** → Use PyMOL or ChimeraX
- Requiring **real-time data visualization** → Use web-based dashboards
- Making **simple bar charts or line plots** → Use matplotlib, ggplot2, or Excel

**Related Skills:**
- **上游 (Upstream)**: `cnv-caller-plotter`, `crispr-screen-analyzer`, `bio-ontology-mapper`
- **下游 (Downstream)**: `dpi-upscaler-checker`, `journal-cover-prompter`, `figure-legend-gen`

---

## Integration with Other Skills

**Upstream Skills:**
- `cnv-caller-plotter`: Generate CNV calls for visualization in Circos
- `crispr-screen-analyzer`: Prepare hit data for genomic context visualization
- `bio-ontology-mapper`: Map features to genomic coordinates for track display

**Downstream Skills:**
- `dpi-upscaler-checker`: Verify output resolution meets publication requirements
- `journal-cover-prompter`: Generate AI prompts for journal covers using Circos plots
- `figure-legend-gen`: Create figure legends for complex Circos visualizations

**Complete Workflow:**
```
WGS Data → cnv-caller-plotter → circos-plot-generator → dpi-upscaler-checker → Publication Figure
```

---

## Core Capabilities

### 1. Genomic Variation Track Generation

Create tracks for visualizing genomic variations including SNPs, CNVs, and structural variants.

```python
from scripts.main import CircosConfig

# Configuration for genomic variation plot
config = {
    "type": "variation",
    "title": "Sample Genomic Variations",
    "data": "variations.csv",
    "width": 1200,
    "height": 1200,
    "color_scheme": "nature",
    "output": "./circos_output"
}

# Generate configuration
generator = CircosConfig(config)
config_path = generator.generate()

print(f"Configuration generated: {config_path}")
print(f"Tracks included:")
print("  - Histogram track for SNPs/CNVs")
print("  - Link track for structural variants")
print("  - Chromosome ideogram")
```

**Input Data Format:**

| Column | Description | Example |
|--------|-------------|---------|
| `chrom` | Chromosome name | chr1, chrX |
| `start` | Start position | 1000000 |
| `end` | End position | 2000000 |
| `type` | Variation type | SNP, CNV, TRANSLOCATION |
| `value` | Score or magnitude | 0.5, -0.8 |
| `target_chrom` | For SVs: target chromosome | chr5 |
| `target_start` | For SVs: target start | 5000000 |

**Variation Types Supported:**

| Type | Visualization | Color Coding |
|------|--------------|--------------|
| **SNP** | Histogram points | Blue/Red (gain/loss) |
| **CNV** | Histogram bars | Green/Orange (amplification/deletion) |
| **TRANSLOCATION** | Links between chromosomes | Purple ribbons |
| **INVERSION** | Intra-chromosomal links | Yellow |
| **DELETION** | Histogram bars | Red |
| **DUPLICATION** | Histogram bars | Blue |

**Best Practices:**
- ✅ **Normalize values** to -1 to +1 range for consistent scaling
- ✅ **Use appropriate bin sizes** (1-10 Mb) for genome-wide views
- ✅ **Color code by type** for easy interpretation
- ✅ **Include ideogram** for chromosome context

**Common Issues and Solutions:**

**Issue: Too many data points causing clutter**
- Symptom: Plot looks crowded with overlapping elements
- Solution: Increase bin size; filter for significant variants only; use transparency

**Issue: Chromosome naming mismatch**
- Symptom: Data not appearing on correct chromosomes
- Solution: Use consistent naming (chr1, chr2, ... chrX, chrY); check for "1" vs "chr1"

### 2. Cell-Cell Communication Visualization

Create circular plots showing interactions between cell types in tissues or tumors.

```python
from scripts.main import CircosConfig

# Configuration for cell-cell communication
config = {
    "type": "cell-comm",
    "title": "Tumor Microenvironment Interactions",
    "data": "cell_communication.csv",
    "width": 1000,
    "height": 1000,
    "color_scheme": "cell",
    "output": "./cell_comm_plots"
}

generator = CircosConfig(config)
config_path = generator.generate()

print("Cell-cell communication plot configured:")
print("  - Cell types arranged in circle")
print("  - Connection ribbons showing interactions")
print("  - Labels for each cell type")
```

**Input Format for Cell Communication:**

| Column | Description | Example |
|--------|-------------|---------|
| `source` | Source cell type | T_Cell |
| `target` | Target cell type | Macrophage |
| `weight` | Interaction strength (0-1) | 0.8 |
| `type` | Interaction type | Ligand-Receptor, Secreted |

**Visualization Features:**

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Ribbon links** | Connection width ∝ interaction strength | Show communication intensity |
| **Cell segments** | Each cell type as chromosome segment | Compare cell type abundance |
| **Labels** | Cell type names outside circle | Identify cells easily |
| **Colors** | Distinct colors per cell type | Distinguish cell types |

**Best Practices:**
- ✅ **Normalize weights** to 0-1 scale for consistent ribbon sizing
- ✅ **Group related cell types** together in input file
- ✅ **Use distinct colors** for each cell type (max 8-10 for clarity)
- ✅ **Filter weak interactions** (weight < 0.2) to reduce clutter

**Common Issues and Solutions:**

**Issue: Too many cell types causing confusion**
- Symptom: Plot crowded with >10 cell types
- Solution: Group rare cell types into "Other"; create separate plots for major groups

**Issue: Bidirectional interactions not clear**
- Symptom: Can't distinguish A→B from B→A
- Solution: Use arrow indicators; color-code by direction; split into two plots

### 3. Chromosome Ideogram Configuration

Generate chromosome ideograms showing banding patterns and genomic coordinates.

```python
from scripts.main import CircosConfig, CHROMOSOME_SIZES

# View available chromosomes
print("Available chromosomes (GRCh38/hg38):")
for chrom, size in CHROMOSOME_SIZES.items():
    size_mb = size / 1_000_000
    print(f"  {chrom}: {size_mb:.1f} Mb")

# Custom chromosome selection
config = {
    "type": "variation",
    "title": "Chr1-5 Variations",
    "chromosomes": ["chr1", "chr2", "chr3", "chr4", "chr5"],  # Subset
    "width": 1000,
    "height": 1000,
    "output": "./chr1-5_plots"
}

# Note: Chromosome selection handled in data preprocessing
```

**Chromosome Specifications:**

| Chromosome | Size (bp) | Display Color |
|------------|-----------|---------------|
| chr1 | 248,956,422 | Red |
| chr2 | 242,193,529 | Orange |
| chr3 | 198,295,559 | Yellow |
| ... | ... | ... |
| chrX | 156,040,895 | Purple |
| chrY | 57,227,415 | Grey |

**Ideogram Features:**

| Feature | Description | Configuration |
|---------|-------------|---------------|
| **Spacing** | Gap between chromosomes | 0.005r (0.5% of radius) |
| **Thickness** | Chromosome bar width | 25 pixels |
| **Labels** | Chromosome names | Outside circle |
| **Bands** | Cytogenetic bands | Show/hide option |
| **Ticks** | Scale markers | 5u and 25u spacing |

**Best Practices:**
- ✅ **Include all autosomes** for genome-wide views
- ✅ **Show X and Y** for sex chromosome analysis
- ✅ **Use consistent scaling** across samples
- ✅ **Add cytoband information** for clinical relevance

**Common Issues and Solutions:**

**Issue: Small chromosomes (chr21, chrY) hard to see**
- Symptom: Very small segments for small chromosomes
- Solution: Use non-linear scaling; create zoomed inset plots

**Issue: Mitochondrial DNA not included**
- Symptom: chrM variants not shown
- Solution: Add chrM to CHROMOSOME_SIZES dict; or exclude mitochondrial from plot

### 4. Multiple Track Layering

Overlay multiple data tracks in concentric circles for complex visualizations.

```python
from scripts.main import CircosConfig

# Multi-track configuration
config = {
    "type": "custom",
    "title": "Multi-Track Genome View",
    "width": 1200,
    "height": 1200,
    "tracks": [
        {
            "type": "histogram",
            "file": "data/cnv_track.txt",
            "color": "color0"  # Red
        },
        {
            "type": "histogram", 
            "file": "data/snp_track.txt",
            "color": "color1"  # Blue
        },
        {
            "type": "link",
            "file": "data/sv_links.txt",
            "color": "color2"  # Green
        }
    ],
    "output": "./multi_track"
}

generator = CircosConfig(config)
config_path = generator.generate()
```

**Track Positioning:**

| Track | Radius Range | Typical Use |
|-------|--------------|-------------|
| **Outer 1** | 0.95r - 0.80r | Primary data (CNVs) |
| **Outer 2** | 0.80r - 0.65r | Secondary data (SNPs) |
| **Middle** | 0.65r - 0.50r | Links/connections |
| **Inner** | 0.50r - 0.35r | Annotations/labels |

**Track Types:**

| Type | Data Format | Best For |
|------|-------------|----------|
| **Histogram** | chr start end value | Continuous values (CNVs, expression) |
| **Scatter** | chr start end value x y | Point data with categories |
| **Heatmap** | chr start end value0 value1... | Multi-sample comparisons |
| **Link** | chr1 start1 end1 chr2 start2 end2 | Connections (SVs, interactions) |
| **Text** | chr start end label | Gene names, annotations |

**Best Practices:**
- ✅ **Limit to 3-4 tracks** for readability
- ✅ **Use complementary colors** for different data types
- ✅ **Add track labels** in figure legend
- ✅ **Consider track order** - most important data outermost

**Common Issues and Solutions:**

**Issue: Tracks overlapping**
- Symptom: Data from different tracks hard to distinguish
- Solution: Adjust radius ranges; use different track types; add transparency

**Issue: Scale differences between tracks**
- Symptom: One track dominates visualization
- Solution: Normalize each track to 0-1 range; use separate color scales

### 5. Color Scheme Customization

Select from predefined color schemes or define custom colors for publication consistency.

```python
from scripts.main import CircosConfig, COLOR_SCHEMES

# View available color schemes
print("Available color schemes:")
for name, colors in COLOR_SCHEMES.items():
    print(f"\n{name.upper()}:")
    print(f"  Colors: {', '.join(colors[:4])}...")

# Example outputs for each scheme
scheme_examples = {
    "default": ["red", "blue", "green", "orange"],
    "nature": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488"],
    "lancet": ["#00468B", "#ED0000", "#42B540", "#0099B4"],
    "cell": ["#1B9E77", "#D95F02", "#7570B3", "#E7298A"]
}

# Usage
config = {
    "type": "variation",
    "color_scheme": "nature",  # Publication-quality colors
    # ... other config
}
```

**Color Schemes:**

| Scheme | Style | Best For |
|--------|-------|----------|
| **default** | Basic colors | Quick visualization, drafts |
| **nature** | Nature journal colors | Nature publications |
| **lancet** | Lancet journal colors | Medical/clinical papers |
| **cell** | Cell journal colors | Cell biology papers |

**Custom Colors:**
```python
# Define custom scheme
my_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
COLOR_SCHEMES["custom"] = my_colors

config["color_scheme"] = "custom"
```

**Best Practices:**
- ✅ **Use colorblind-friendly palettes** for accessibility
- ✅ **Match journal requirements** for submissions
- ✅ **Maintain consistency** across all figures in paper
- ✅ **Test printed output** - colors may differ from screen

**Common Issues and Solutions:**

**Issue: Colors not distinct enough**
- Symptom: Hard to distinguish adjacent tracks
- Solution: Increase color contrast; use complementary colors

**Issue: Colors don't match brand/institution**
- Symptom: Need specific institutional colors
- Solution: Define custom color scheme with hex codes

### 6. Configuration Export and Rendering

Generate complete Circos configuration and optionally render the plot.

```python
import subprocess
from pathlib import Path
from scripts.main import CircosConfig

def generate_and_render(config: dict, render: bool = False) -> dict:
    """
    Generate Circos config and optionally render plot.
    
    Returns:
        dict with paths and status
    """
    # Generate configuration
    generator = CircosConfig(config)
    config_path = generator.generate()
    
    result = {
        "config_path": config_path,
        "data_dir": str(generator.data_dir),
        "rendered": False,
        "output_image": None
    }
    
    # Attempt to render
    if render:
        output_dir = Path(config["output"])
        try:
            proc_result = subprocess.run(
                ["circos", "-conf", config_path],
                capture_output=True,
                text=True,
                cwd=output_dir
            )
            
            if proc_result.returncode == 0:
                result["rendered"] = True
                result["output_image"] = str(output_dir / "circos.png")
                print("✅ Plot rendered successfully!")
            else:
                print(f"❌ Rendering failed: {proc_result.stderr}")
        except FileNotFoundError:
            print("⚠️  Circos not installed. Configuration ready for manual rendering.")
            print(f"   Run: cd {output_dir} && circos -conf circos.conf")
    
    return result

# Example usage
config = {
    "type": "variation",
    "title": "Genomic Landscape",
    "data": "variants.csv",
    "output": "./output"
}

result = generate_and_render(config, render=True)
```

**Output Files:**

| File | Description | Format |
|------|-------------|--------|
| `circos.conf` | Main configuration | Text |
| `data/karyotype.txt` | Chromosome definitions | Text |
| `data/*.txt` | Track data files | TSV |
| `circos.png` | Raster image (if rendered) | PNG |
| `circos.svg` | Vector image (if rendered) | SVG |

**Rendering Requirements:**

| Component | Installation | Command |
|-----------|--------------|---------|
| **Circos** | `conda install -c bioconda circos` | `circos -conf circos.conf` |
| **Perl** | Usually pre-installed | Required by Circos |
| **GD library** | System package | Image generation |

**Best Practices:**
- ✅ **Generate SVG for publication** - scalable, editable
- ✅ **Use PNG for drafts** - faster rendering
- ✅ **Check file sizes** - high-res images can be large
- ✅ **Archive configurations** - for reproducibility

**Common Issues and Solutions:**

**Issue: Circos installation fails**
- Symptom: "circos: command not found"
- Solution: Use conda installation; check Perl and GD dependencies

**Issue: Rendering produces warnings**
- Symptom: Many "skip" or "warning" messages
- Solution: Usually harmless; check output image quality; adjust data ranges

---

## Complete Workflow Example

**From variant calls to publication figure:**

```bash
# Step 1: Create sample data for testing
python scripts/main.py --create-sample variation --output ./data

# Step 2: Generate configuration
python scripts/main.py \
  --data ./data/sample_variations.csv \
  --type variation \
  --title "Tumor Genomic Landscape" \
  --color-scheme nature \
  --width 1200 \
  --height 1200 \
  --output ./plots

# Step 3: Render plot (requires Circos)
python scripts/main.py \
  --data ./data/sample_variations.csv \
  --type variation \
  --output ./plots \
  --render
```

**Python API Usage:**

```python
from scripts.main import CircosConfig
import pandas as pd

def create_genomic_landscape_plot(
    variation_data: pd.DataFrame,
    output_dir: str = "./circos_output",
    title: str = "Genomic Variations"
) -> str:
    """
    Create comprehensive genomic landscape Circos plot.
    
    Args:
        variation_data: DataFrame with columns [chrom, start, end, type, value]
        output_dir: Output directory for files
        title: Plot title
        
    Returns:
        Path to generated configuration file
    """
    # Save data to CSV
    data_path = f"{output_dir}/input_data.csv"
    variation_data.to_csv(data_path, index=False)
    
    # Generate configuration
    config = {
        "type": "variation",
        "title": title,
        "data": data_path,
        "width": 1200,
        "height": 1200,
        "color_scheme": "nature",
        "output": output_dir
    }
    
    generator = CircosConfig(config)
    config_path = generator.generate()
    
    # Print summary
    print(f"✅ Circos configuration generated")
    print(f"   Config: {config_path}")
    print(f"   Data directory: {generator.data_dir}")
    print(f"\nTo render:")
    print(f"   circos -conf {config_path}")
    
    return config_path

# Example with sample data
sample_data = pd.DataFrame({
    'chrom': ['chr1', 'chr1', 'chr2', 'chr5', 'chrX'],
    'start': [1000000, 5000000, 1000000, 5000000, 5000000],
    'end': [2000000, 6000000, 1500000, 7000000, 8000000],
    'type': ['SNP', 'CNV', 'SNP', 'TRANSLOCATION', 'DELETION'],
    'value': [0.5, -0.8, 0.3, None, -1.0],
    'target_chrom': [None, None, None, 'chr2', None],
    'target_start': [None, None, None, 8000000, None],
    'target_end': [None, None, None, 10000000, None]
})

config_file = create_genomic_landscape_plot(
    sample_data,
    output_dir="./my_plot",
    title="Sample Genomic Landscape"
)
```

**Expected Output Files:**

```
circos_output/
├── circos.conf              # Main configuration
├── data/
│   ├── karyotype.txt        # Chromosome definitions
│   ├── variations.txt       # Histogram data
│   └── links.txt            # Structural variant links
└── (after rendering)
    ├── circos.png           # Raster output
    └── circos.svg           # Vector output
```

---

## Common Patterns

### Pattern 1: Cancer Genomic Landscape

**Scenario**: Visualize genomic alterations in a tumor sample for publication.

```json
{
  "plot_type": "variation",
  "title": "Tumor Genomic Landscape",
  "data_layers": [
    "CNV (outer track)",
    "SNV density (middle track)",
    "Structural variants (links)"
  ],
  "color_scheme": "nature",
  "resolution": "1200x1200",
  "publication": "Nature Medicine"
}
```

**Workflow:**
1. Collect CNV data from WGS or SNP array
2. Get SNV calls from exome/WGS
3. Identify structural variants (SVs)
4. Generate Circos configuration
5. Render and export high-resolution PNG/SVG
6. Create figure legend and methods description

**Output Example:**
```
Cancer Genomic Landscape Plot:
  - CNV track: 47 copy number alterations
  - SNV track: 2,847 mutations (density)
  - SV links: 12 translocations, 8 inversions
  
Key findings visible:
  - Chr8 MYC amplification
  - Chr17 TP53 deletion
  - Chr7-14 translocation
  
Publication ready: 1200x1200 PNG + SVG
```

### Pattern 2: Tumor Microenvironment

**Scenario**: Visualize cell-cell communication in tumor microenvironment.

```json
{
  "plot_type": "cell-comm",
  "title": "TME Communication Network",
  "cell_types": [
    "T_Cell", "B_Cell", "Macrophage",
    "NK_Cell", "Tumor_Cell", "Fibroblast"
  ],
  "data_source": "CellChat analysis",
  "filter": "weight > 0.3",
  "color_scheme": "cell"
}
```

**Workflow:**
1. Run CellChat or similar on scRNA-seq data
2. Export communication probabilities
3. Filter for significant interactions
4. Generate Circos configuration
5. Adjust colors for each cell type
6. Add annotations for key pathways

**Output Example:**
```
TME Communication Network:
  Cell types: 6
  Interactions: 24 (filtered from 156)
  
Major communication axes:
  - T_Cell → Macrophage (strongest)
  - Dendritic → T_Cell
  - Tumor → Macrophage
  
Insights:
  - Immunosuppressive signaling dominant
  - Limited NK cell activation
```

### Pattern 3: Comparative Genomics

**Scenario**: Compare synteny between two species or strains.

```json
{
  "plot_type": "custom",
  "title": "Human-Mouse Synteny",
  "tracks": [
    {
      "type": "link",
      "data": "synteny_blocks.txt",
      "description": "Conserved regions"
    }
  ],
  "genomes": ["hg38", "mm10"],
  "color_by": "chromosome"
}
```

**Workflow:**
1. Identify syntenic blocks between genomes
2. Map coordinates to common reference
3. Create link track for conserved regions
4. Generate dual-genome Circos plot
5. Color-code by chromosome of origin
6. Highlight breakpoints and rearrangements

**Output Example:**
```
Synteny Comparison:
  Human chromosomes: 22 + X + Y
  Mouse chromosomes: 19 + X + Y
  Syntenic blocks: 342
  
Key observations:
  - Chr12 conservation strong
  - Multiple breakpoints on Chr1
  - X chromosome largely conserved
```

### Pattern 4: Time-Series Evolution

**Scenario**: Track clonal evolution through treatment timepoints.

```json
{
  "plot_type": "custom",
  "title": "Clonal Evolution Over Time",
  "timepoints": ["Baseline", "Post-Treatment", "Relapse"],
  "tracks": [
    "Baseline CNV",
    "Post-Treatment CNV",
    "Relapse CNV",
    "Clonal links"
  ],
  "color_scheme": "lancet"
}
```

**Workflow:**
1. Collect CNV data from multiple timepoints
2. Track clone frequencies
3. Create separate track for each timepoint
4. Add links showing clone relationships
5. Generate evolution Circos plot
6. Annotate treatment events

**Output Example:**
```
Clonal Evolution Plot:
  Timepoints: 3
  Clones tracked: 5
  
Evolutionary trajectory:
  - Baseline: 3 subclones
  - Post-treatment: 1 dominant clone
  - Relapse: New clone emergence
  
Therapeutic implications:
  - Pre-existing resistance clone expanded
  - New mutation acquired at relapse
```

---

## Quality Checklist

**Data Preparation:**
- [ ] **CRITICAL**: Verify chromosome naming consistency (chr1 vs 1)
- [ ] Check coordinate system (0-based vs 1-based)
- [ ] Validate all positions within chromosome bounds
- [ ] Normalize values to appropriate ranges
- [ ] Filter out low-quality or ambiguous data
- [ ] Ensure no duplicate entries
- [ ] Check for missing values and handle appropriately
- [ ] Verify file formats (CSV with proper headers)

**Configuration:**
- [ ] **CRITICAL**: Set appropriate image size for publication (min 1200x1200)
- [ ] Choose color scheme matching journal requirements
- [ ] Set track radii to avoid overlap
- [ ] Configure chromosome spacing for readability
- [ ] Add descriptive title
- [ ] Set up proper scaling for each track
- [ ] Choose appropriate color for each data type
- [ ] Test with subset of data first

**Rendering:**
- [ ] **CRITICAL**: Generate SVG for publication-quality output
- [ ] Check PNG output for visual quality
- [ ] Verify all tracks visible and correctly positioned
- [ ] Test color visibility (colorblind-friendly check)
- [ ] Confirm labels readable at target size
- [ ] Check for rendering warnings or errors
- [ ] Verify file sizes reasonable
- [ ] Archive configuration files

**Publication:**
- [ ] **CRITICAL**: Include scale bars and legends
- [ ] Add chromosome labels clearly
- [ ] Include figure caption with data description
- [ ] Note software version in methods
- [ ] Provide data availability statement
- [ ] Check journal figure requirements (size, format)
- [ ] Create supplementary data files if needed
- [ ] Test figure at print resolution

---

## Common Pitfalls

**Data Issues:**
- ❌ **Inconsistent chromosome names** → Data missing from plot
  - ✅ Use consistent "chr" prefix (chr1, chr2, not 1, 2)
  
- ❌ **Coordinates out of bounds** → Rendering errors
  - ✅ Verify all coordinates ≤ chromosome size
  
- ❌ **Too many data points** → Cluttered, slow rendering
  - ✅ Filter for significance; increase bin size
  
- ❌ **Missing values not handled** → Gaps or errors
  - ✅ Impute or filter missing values before plotting

**Configuration Issues:**
- ❌ **Tracks overlap** → Data unreadable
  - ✅ Adjust radius ranges; use transparency
  
- ❌ **Colors too similar** → Can't distinguish tracks
  - ✅ Use distinct, contrasting colors
  
- ❌ **Font too small** → Labels unreadable
  - ✅ Increase font sizes for publication
  
- ❌ **Image too small** → Poor resolution
  - ✅ Use minimum 1200x1200 for publications

**Interpretation Issues:**
- ❌ **No scale reference** → Values unclear
  - ✅ Add color scale and value ranges
  
- ❌ **Missing legend** → Data types unexplained
  - ✅ Include comprehensive figure legend
  
- ❌ **No chromosome labels** → Location unclear
  - ✅ Label all chromosomes clearly
  
- ❌ **Too much information** → Figure overwhelming
  - ✅ Limit to 3-4 key data types per plot

---

## Troubleshooting

**Problem: Configuration generates but Circos won't render**
- Symptoms: "Can't open file" or "Invalid configuration" errors
- Causes:
  - Missing data files
  - Incorrect file paths
  - Syntax errors in configuration
  - Missing Circos installation
- Solutions:
  - Verify all data files exist in data/ directory
  - Check file paths are absolute or correct relative paths
  - Validate configuration syntax
  - Install Circos: `conda install -c bioconda circos`

**Problem: Plot is blank or missing data**
- Symptoms: Chromosomes shown but no data tracks
- Causes:
  - Data format incorrect
  - Chromosome name mismatch
  - Values out of visible range
- Solutions:
  - Check data format matches expected (TSV, correct columns)
  - Verify chromosome names (chr1 vs 1)
  - Check min/max values in data files

**Problem: Colors not as expected**
- Symptoms: Wrong colors or all same color
- Causes:
  - Color scheme name misspelled
  - Custom colors not defined
  - Color values out of range
- Solutions:
  - Check color_scheme name matches available schemes
  - Define custom colors if needed
  - Verify color values are valid hex codes

**Problem: Links/connections not showing**
- Symptoms: Histograms visible but no SV links
- Causes:
  - Link data format incorrect
  - Target coordinates missing
  - Link radius outside visible area
- Solutions:
  - Check link file format: chr1 start1 end1 chr2 start2 end2
  - Verify target coordinates provided for translocations
  - Adjust link radius parameter

**Problem: Text labels overlapping**
- Symptoms: Gene names or labels unreadable
- Causes:
  - Too many labels in small space
  - Font size too large
  - Insufficient label radius
- Solutions:
  - Filter labels to show only most important
  - Reduce font size
  - Increase label radius (move further from center)
  - Use label collision detection if available

**Problem: Rendering is very slow**
- Symptoms: Takes minutes or hours to generate plot
- Causes:
  - Too many data points
  - High resolution settings
  - Complex link calculations
- Solutions:
  - Reduce data points (filter or bin)
  - Lower image resolution for drafts
  - Simplify link visualization
  - Use PNG instead of SVG for faster rendering

---

## References

Available in `references/` directory:

- (No reference files currently available for this skill)

**External Resources:**
- Circos Official Documentation: http://circos.ca/documentation
- Circos Tutorials: http://circos.ca/documentation/tutorials
- Bioconda Circos: https://bioconda.github.io/recipes/circos/README.html
- Nature Genetics Circos Examples: https://www.nature.com/ng/

---

## Scripts

Located in `scripts/` directory:

- `main.py` - Circos configuration generator with support for variations and cell communication

---

## Color Scheme Reference

**Default:** red, blue, green, orange, purple, cyan

**Nature:** #E64B35, #4DBBD5, #00A087, #3C5488, #F39B7F, #8491B4

**Lancet:** #00468B, #ED0000, #42B540, #0099B4, #925E9F, #FDAF91

**Cell:** #1B9E77, #D95F02, #7570B3, #E7298A, #66A61E, #E6AB02

---

**Last Updated**: 2026-02-09  
**Skill ID**: 186  
**Version**: 2.0 (K-Dense Standard)

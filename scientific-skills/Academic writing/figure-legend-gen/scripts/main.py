#!/usr/bin/env python3
"""
Figure Legend Generator - Generate standardized legends for scientific charts.

Usage:
    python main.py --input <image_path> --type <chart_type> [options]

Supported chart types:
    bar, line, scatter, box, heatmap, microscopy, flow, western
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    BOX = "box"
    HEATMAP = "heatmap"
    MICROSCOPY = "microscopy"
    FLOW = "flow"
    WESTERN = "western"


@dataclass
class LegendTemplate:
    """Template for generating figure legends."""
    title_template: str
    description_template: str
    data_template: str
    stat_template: str
    notes_template: str


TEMPLATES = {
    ChartType.BAR: LegendTemplate(
        title_template="Comparison of {metric} across {groups}",
        description_template="Bar chart showing {metric} in {sample_description}.",
        data_template="Data are presented as mean ± SEM from n={n} independent experiments.",
        stat_template="Statistical significance was determined by {test}; *p<0.05, **p<0.01, ***p<0.001.",
        notes_template="Error bars represent standard error of the mean (SEM)."
    ),
    ChartType.LINE: LegendTemplate(
        title_template="Time course of {metric} in {condition}",
        description_template="Line graph showing {metric} over {time_range} in {sample_description}.",
        data_template="Data points represent mean ± SEM from n={n} replicates per time point.",
        stat_template="Significance compared to control: *p<0.05, **p<0.01.",
        notes_template="Shaded areas indicate standard error of the mean."
    ),
    ChartType.SCATTER: LegendTemplate(
        title_template="Correlation between {x_var} and {y_var}",
        description_template="Scatter plot showing the relationship between {x_var} and {y_var} in {sample_description}.",
        data_template="Each point represents an individual {sample_unit}. n={n}.",
        stat_template="Correlation coefficient (r) = {r_value}, p = {p_value}.",
        notes_template="Solid line indicates linear regression fit."
    ),
    ChartType.BOX: LegendTemplate(
        title_template="Distribution of {metric} across {groups}",
        description_template="Box plot showing {metric} distribution in {sample_description}.",
        data_template="Boxes represent interquartile range (IQR), lines indicate median, whiskers show 1.5×IQR. n={n} per group.",
        stat_template="Mann-Whitney U test; *p<0.05, **p<0.01.",
        notes_template="Outliers are shown as individual points."
    ),
    ChartType.HEATMAP: LegendTemplate(
        title_template="{metric} matrix across {dimensions}",
        description_template="Heatmap displaying {metric} values across {dimensions}.",
        data_template="Color scale indicates {value_range}. Data normalized by {normalization_method}.",
        stat_template="Hierarchical clustering performed using {clustering_method}.",
        notes_template=""
    ),
    ChartType.MICROSCOPY: LegendTemplate(
        title_template="{staining} staining of {sample_type}",
        description_template="Representative confocal microscopy images of {sample_type} stained with {stains}.",
        data_template="Scale bar: {scale_bar}. Images acquired with {microscope_type}.",
        stat_template="",
        notes_template="DAPI (blue) indicates nuclei."
    ),
    ChartType.FLOW: LegendTemplate(
        title_template="Flow cytometry analysis of {marker}",
        description_template="FACS plots showing {marker} expression in {cell_type}.",
        data_template="{percent_positive}% of cells were positive for {marker}. n={n} experiments.",
        stat_template="Gating strategy shown in supplementary figure.",
        notes_template=""
    ),
    ChartType.WESTERN: LegendTemplate(
        title_template="Western blot analysis of {protein}",
        description_template="Immunoblot showing {protein} expression in {sample_description}.",
        data_template="{loading_control} served as loading control. Representative of n={n} experiments.",
        stat_template="Quantification shown in adjacent bar graph.",
        notes_template="Molecular weight markers (kDa) indicated on left."
    ),
}


class LegendGenerator:
    """Generator for scientific figure legends."""
    
    def __init__(self, chart_type: ChartType, language: str = "en"):
        self.chart_type = chart_type
        self.language = language
        self.template = TEMPLATES.get(chart_type, TEMPLATES[ChartType.BAR])
    
    def generate(
        self,
        figure_number: str = "1",
        metric: str = "experimental values",
        groups: str = "experimental groups",
        sample_description: str = "tested samples",
        n: int = 3,
        **kwargs
    ) -> str:
        """Generate a complete figure legend."""
        
        # Build legend sections
        sections = []
        
        # Figure number and title
        title = self.template.title_template.format(
            metric=metric,
            groups=groups,
            **kwargs
        )
        sections.append(f"**Figure {figure_number}.** {title}")
        sections.append("")
        
        # Main description
        description = self.template.description_template.format(
            metric=metric,
            sample_description=sample_description,
            **kwargs
        )
        sections.append(description)
        
        # Data details
        data_detail = self.template.data_template.format(
            n=n,
            **kwargs
        )
        sections.append(data_detail)
        
        # Statistics
        if self.template.stat_template:
            stats = self.template.stat_template.format(**kwargs)
            if stats:
                sections.append(stats)
        
        # Additional notes
        if self.template.notes_template:
            notes = self.template.notes_template.format(**kwargs)
            if notes:
                sections.append(notes)
        
        return "\n".join(sections)
    
    def analyze_image(self, image_path: Path) -> Dict:
        """Analyze image to extract chart metadata."""
        # Placeholder for image analysis
        # In production, this would use PIL + OCR/vision models
        return {
            "detected_type": self.chart_type.value,
            "has_error_bars": True,
            "has_stats": True,
            "dimensions": "detected"
        }


def detect_chart_type(image_path: Path) -> Optional[ChartType]:
    """Attempt to detect chart type from image."""
    # Simplified detection based on file naming or basic analysis
    name_lower = image_path.stem.lower()
    
    type_hints = {
        "bar": ChartType.BAR,
        "line": ChartType.LINE,
        "scatter": ChartType.SCATTER,
        "box": ChartType.BOX,
        "heatmap": ChartType.HEATMAP,
        "microscopy": ChartType.MICROSCOPY,
        "confocal": ChartType.MICROSCOPY,
        "flow": ChartType.FLOW,
        "facs": ChartType.FLOW,
        "western": ChartType.WESTERN,
        "wb": ChartType.WESTERN,
    }
    
    for hint, ctype in type_hints.items():
        if hint in name_lower:
            return ctype
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate standardized figure legends for scientific charts"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to chart image"
    )
    parser.add_argument(
        "--type", "-t",
        type=str,
        required=False,
        choices=[ct.value for ct in ChartType],
        help="Chart type (auto-detected if not specified)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["text", "markdown", "latex"],
        help="Output format"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="en",
        choices=["en", "zh"],
        help="Output language"
    )
    parser.add_argument(
        "--figure-number", "-n",
        type=str,
        default="1",
        help="Figure number"
    )
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Determine chart type
    chart_type = None
    if args.type:
        chart_type = ChartType(args.type)
    else:
        chart_type = detect_chart_type(input_path)
        if not chart_type:
            print("Error: Could not auto-detect chart type. Please specify with --type", file=sys.stderr)
            sys.exit(1)
        print(f"Auto-detected chart type: {chart_type.value}", file=sys.stderr)
    
    # Generate legend
    generator = LegendGenerator(chart_type, args.language)
    
    # Base parameters for all chart types
    base_params = {
        "figure_number": args.figure_number,
        "metric": "measured values",
        "groups": "experimental conditions",
        "sample_description": "the tested samples",
        "n": 3,
        "test": "one-way ANOVA with Tukey's post-hoc test"
    }
    
    # Add type-specific default parameters
    type_specific_params = {
        ChartType.SCATTER: {
            "x_var": "independent variable",
            "y_var": "dependent variable",
            "r_value": "0.75",
            "p_value": "<0.001",
            "sample_unit": "sample"
        },
        ChartType.WESTERN: {
            "protein": "target protein",
            "loading_control": "β-actin"
        },
        ChartType.FLOW: {
            "marker": "CD marker",
            "cell_type": "cell population",
            "percent_positive": "45"
        },
        ChartType.HEATMAP: {
            "dimensions": "samples and features",
            "value_range": "normalized expression values",
            "normalization_method": "z-score",
            "clustering_method": "Ward's method"
        },
        ChartType.LINE: {
            "condition": "experimental condition",
            "time_range": "24 hours"
        },
        ChartType.MICROSCOPY: {
            "staining": "immunofluorescence",
            "sample_type": "cell culture",
            "stains": "DAPI and phalloidin",
            "scale_bar": "50 μm",
            "microscope_type": "confocal microscope"
        }
    }
    
    # Merge parameters
    if chart_type in type_specific_params:
        base_params.update(type_specific_params[chart_type])
    
    legend = generator.generate(**base_params)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(legend, encoding="utf-8")
        print(f"Legend saved to: {args.output}")
    else:
        print(legend)


if __name__ == "__main__":
    main()

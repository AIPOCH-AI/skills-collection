#!/usr/bin/env python3
"""
Example usage of Multi-panel Figure Assembler.

This script demonstrates how to use the FigureAssembler programmatically.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import FigureAssembler


def create_sample_images():
    """Create sample test images for demonstration."""
    from PIL import Image, ImageDraw, ImageFont
    
    colors = [
        (255, 200, 200),  # Light red
        (200, 255, 200),  # Light green
        (200, 200, 255),  # Light blue
        (255, 255, 200),  # Light yellow
        (255, 200, 255),  # Light magenta
        (200, 255, 255),  # Light cyan
    ]
    
    labels = ["A", "B", "C", "D", "E", "F"]
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)
    
    paths = []
    for i, (color, label) in enumerate(zip(colors, labels)):
        img = Image.new('RGB', (400, 300), color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("Arial", 40)
        except:
            font = ImageFont.load_default()
        
        # Draw label in center
        bbox = draw.textbbox((0, 0), f"Sample {label}", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        
        draw.text((x, y), f"Sample {label}", fill=(0, 0, 0), font=font)
        
        path = output_dir / f"{label}.png"
        img.save(path)
        paths.append(str(path))
        print(f"Created: {path}")
    
    return paths


def example_1_basic():
    """Example 1: Basic usage with default settings."""
    print("\n=== Example 1: Basic Usage ===")
    
    # Create sample images
    inputs = create_sample_images()
    
    # Create assembler with default settings
    assembler = FigureAssembler()
    
    # Assemble figure
    assembler.assemble(
        inputs=inputs,
        output="example_output/figure_basic.png"
    )


def example_2_custom_layout():
    """Example 2: 3x2 layout with high DPI."""
    print("\n=== Example 2: 3x2 Layout with 600 DPI ===")
    
    inputs = [f"example_output/{label}.png" for label in ["A", "B", "C", "D", "E", "F"]]
    
    assembler = FigureAssembler(
        layout="3x2",
        dpi=600,
        label_size=36,
        padding=20
    )
    
    assembler.assemble(
        inputs=inputs,
        output="example_output/figure_3x2.png"
    )


def example_3_custom_styling():
    """Example 3: Custom styling options."""
    print("\n=== Example 3: Custom Styling ===")
    
    inputs = [f"example_output/{label}.png" for label in ["A", "B", "C", "D", "E", "F"]]
    
    assembler = FigureAssembler(
        layout="2x3",
        dpi=300,
        label_size=28,
        label_position="topright",
        padding=15,
        border=4,
        bg_color="#f0f0f0",
        label_color="#333333"
    )
    
    assembler.assemble(
        inputs=inputs,
        output="example_output/figure_styled.png"
    )


def example_4_different_labels():
    """Example 4: Custom panel labels."""
    print("\n=== Example 4: Custom Labels ===")
    
    inputs = [f"example_output/{label}.png" for label in ["A", "B", "C", "D", "E", "F"]]
    
    assembler = FigureAssembler(
        layout="2x3",
        dpi=300,
        label_size=20
    )
    
    # Use custom labels
    custom_labels = ["Fig 1", "Fig 2", "Fig 3", "Fig 4", "Fig 5", "Fig 6"]
    
    assembler.assemble(
        inputs=inputs,
        output="example_output/figure_custom_labels.png",
        labels=custom_labels
    )


if __name__ == "__main__":
    print("Multi-panel Figure Assembler - Examples")
    print("=" * 50)
    
    try:
        example_1_basic()
        example_2_custom_layout()
        example_3_custom_styling()
        example_4_different_labels()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the 'example_output' directory for results.")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

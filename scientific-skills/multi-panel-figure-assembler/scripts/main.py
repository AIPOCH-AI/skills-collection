#!/usr/bin/env python3
"""
Multi-panel Figure Assembler
Automatically assemble 6 sub-figures into a high-resolution composite figure.

Usage:
    python main.py -i A.png B.png C.png D.png E.png F.png -o output.png
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np


class FigureAssembler:
    """Assemble multiple images into a composite figure with labels."""
    
    PANEL_LABELS = ["A", "B", "C", "D", "E", "F"]
    
    def __init__(
        self,
        layout: str = "2x3",
        dpi: int = 300,
        label_font: str = "Arial",
        label_size: int = 24,
        label_position: str = "topleft",
        padding: int = 10,
        border: int = 2,
        bg_color: str = "white",
        label_color: str = "black"
    ):
        """
        Initialize the figure assembler.
        
        Args:
            layout: Grid layout ('2x3' or '3x2')
            dpi: Output resolution in DPI
            label_font: Font family for labels
            label_size: Font size for panel labels
            label_position: Position of labels ('topleft', 'topright', 'bottomleft', 'bottomright')
            padding: Padding between panels in pixels
            border: Border width around each panel in pixels
            bg_color: Background color
            label_color: Label text color
        """
        self.layout = layout
        self.dpi = dpi
        self.label_font = label_font
        self.label_size = label_size
        self.label_position = label_position
        self.padding = padding
        self.border = border
        self.bg_color = bg_color
        self.label_color = label_color
        
        self.rows, self.cols = self._parse_layout(layout)
        self.bg_rgb = self._parse_color(bg_color)
        self.label_rgb = self._parse_color(label_color)
    
    def _parse_layout(self, layout: str) -> Tuple[int, int]:
        """Parse layout string into rows and columns."""
        if layout == "2x3":
            return 2, 3
        elif layout == "3x2":
            return 3, 2
        else:
            raise ValueError(f"Unsupported layout: {layout}. Use '2x3' or '3x2'.")
    
    def _parse_color(self, color: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple."""
        color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 128, 0),
            "blue": (0, 0, 255),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
        }
        
        if color.lower() in color_map:
            return color_map[color.lower()]
        
        # Try hex color
        if color.startswith("#"):
            color = color[1:]
        if len(color) == 6:
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        raise ValueError(f"Unsupported color: {color}")
    
    def _get_font(self) -> ImageFont.FreeTypeFont:
        """Get font for labels with fallback."""
        try:
            return ImageFont.truetype(self.label_font, self.label_size)
        except OSError:
            # Try common system fonts
            fallback_fonts = [
                "DejaVuSans.ttf",
                "LiberationSans-Regular.ttf",
                "FreeSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
            ]
            for font_name in fallback_fonts:
                try:
                    return ImageFont.truetype(font_name, self.label_size)
                except OSError:
                    continue
            # Final fallback to default font
            return ImageFont.load_default()
    
    def _load_image(self, path: str) -> Image.Image:
        """Load an image from file."""
        img_path = Path(path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        
        img = Image.open(path)
        
        # Convert to RGB if necessary (handle RGBA, P, etc.)
        if img.mode in ('RGBA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', img.size, self.bg_rgb)
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
    
    def _resize_to_uniform(self, images: List[Image.Image]) -> List[Image.Image]:
        """Resize all images to the same dimensions."""
        # Find target size (max width and height)
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        resized = []
        for img in images:
            if img.width == max_width and img.height == max_height:
                resized.append(img)
            else:
                # Resize with high-quality resampling
                resized_img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
                resized.append(resized_img)
        
        return resized
    
    def _add_border(self, img: Image.Image) -> Image.Image:
        """Add border around an image."""
        if self.border <= 0:
            return img
        return ImageOps.expand(img, border=self.border, fill=self.bg_rgb)
    
    def _add_label(
        self, 
        img: Image.Image, 
        label: str, 
        font: ImageFont.FreeTypeFont
    ) -> Image.Image:
        """Add panel label to image."""
        draw = ImageDraw.Draw(img)
        
        # Get label bounding box
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        margin = max(self.label_size // 2, 5)
        
        if self.label_position == "topleft":
            x, y = margin, margin
        elif self.label_position == "topright":
            x = img.width - text_width - margin
            y = margin
        elif self.label_position == "bottomleft":
            x = margin
            y = img.height - text_height - margin
        elif self.label_position == "bottomright":
            x = img.width - text_width - margin
            y = img.height - text_height - margin
        else:
            x, y = margin, margin
        
        # Draw label with slight shadow for readability
        shadow_offset = 1
        shadow_color = (255, 255, 255) if self.label_rgb == (0, 0, 0) else (0, 0, 0)
        draw.text((x + shadow_offset, y + shadow_offset), label, font=font, fill=shadow_color)
        draw.text((x, y), label, font=font, fill=self.label_rgb)
        
        return img
    
    def _create_panel(
        self,
        img: Image.Image,
        label: str,
        font: ImageFont.FreeTypeFont
    ) -> Image.Image:
        """Create a complete panel with border and label."""
        # Add border
        img = self._add_border(img)
        # Add label
        img = self._add_label(img, label, font)
        return img
    
    def assemble(
        self,
        inputs: List[str],
        output: str,
        labels: Optional[List[str]] = None
    ) -> Path:
        """
        Assemble images into a composite figure.
        
        Args:
            inputs: List of 6 input image paths
            output: Output file path
            labels: Optional custom labels (default: A-F)
        
        Returns:
            Path to the output file
        """
        if len(inputs) != 6:
            raise ValueError(f"Expected 6 input images, got {len(inputs)}")
        
        if labels is None:
            labels = self.PANEL_LABELS[:len(inputs)]
        
        # Load images
        print(f"Loading {len(inputs)} images...")
        images = [self._load_image(path) for path in inputs]
        
        # Resize to uniform dimensions
        print("Resizing images to uniform dimensions...")
        images = self._resize_to_uniform(images)
        
        # Get font
        font = self._get_font()
        
        # Create panels with borders and labels
        print("Creating panels...")
        panels = [self._create_panel(img, label, font) for img, label in zip(images, labels)]
        
        # Calculate composite dimensions
        panel_width = panels[0].width
        panel_height = panels[0].height
        
        composite_width = self.cols * panel_width + (self.cols - 1) * self.padding
        composite_height = self.rows * panel_height + (self.rows - 1) * self.padding
        
        # Create composite image
        print(f"Creating {self.layout} composite ({composite_width}x{composite_height})...")
        composite = Image.new('RGB', (composite_width, composite_height), self.bg_rgb)
        
        # Arrange panels
        for idx, panel in enumerate(panels):
            row = idx // self.cols
            col = idx % self.cols
            
            x = col * (panel_width + self.padding)
            y = row * (panel_height + self.padding)
            
            composite.paste(panel, (x, y))
        
        # Save with DPI info
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as PNG with DPI
        composite.save(output_path, dpi=(self.dpi, self.dpi))
        
        print(f"✓ Saved composite figure to: {output_path}")
        print(f"  Dimensions: {composite_width}x{composite_height} pixels")
        print(f"  DPI: {self.dpi}")
        print(f"  Physical size: ~{composite_width/self.dpi:.1f}x{composite_height/self.dpi:.1f} inches")
        
        return output_path


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Assemble 6 sub-figures (A-F) into a high-resolution composite figure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i A.png B.png C.png D.png E.png F.png -o figure.png
  %(prog)s -i *.png -o figure.png --layout 3x2 --dpi 600
  %(prog)s -i A.png B.png C.png D.png E.png F.png -o figure.png --label-size 32 --padding 20
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        nargs=6,
        required=True,
        help="6 input image paths (A-F)"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path"
    )
    
    parser.add_argument(
        "--layout", "-l",
        choices=["2x3", "3x2"],
        default="2x3",
        help="Layout grid (default: 2x3)"
    )
    
    parser.add_argument(
        "--dpi", "-d",
        type=int,
        default=300,
        help="Output DPI (default: 300)"
    )
    
    parser.add_argument(
        "--label-font",
        default="Arial",
        help="Font family for labels (default: Arial)"
    )
    
    parser.add_argument(
        "--label-size",
        type=int,
        default=24,
        help="Font size for panel labels (default: 24)"
    )
    
    parser.add_argument(
        "--label-position",
        choices=["topleft", "topright", "bottomleft", "bottomright"],
        default="topleft",
        help="Label position (default: topleft)"
    )
    
    parser.add_argument(
        "--padding", "-p",
        type=int,
        default=10,
        help="Padding between panels in pixels (default: 10)"
    )
    
    parser.add_argument(
        "--border", "-b",
        type=int,
        default=2,
        help="Border width around each panel in pixels (default: 2)"
    )
    
    parser.add_argument(
        "--bg-color",
        default="white",
        help="Background color: white/black/hex (default: white)"
    )
    
    parser.add_argument(
        "--label-color",
        default="black",
        help="Label text color: black/white/hex (default: black)"
    )
    
    args = parser.parse_args()
    
    # Create assembler
    assembler = FigureAssembler(
        layout=args.layout,
        dpi=args.dpi,
        label_font=args.label_font,
        label_size=args.label_size,
        label_position=args.label_position,
        padding=args.padding,
        border=args.border,
        bg_color=args.bg_color,
        label_color=args.label_color
    )
    
    # Assemble figure
    try:
        assembler.assemble(
            inputs=args.input,
            output=args.output
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

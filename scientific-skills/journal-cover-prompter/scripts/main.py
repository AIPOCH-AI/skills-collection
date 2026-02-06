#!/usr/bin/env python3
"""
Journal Cover Prompter
Generate AI art prompts for scientific journal cover designs.
"""

import argparse


class JournalCoverPrompter:
    """Generate prompts for journal cover artwork."""
    
    STYLE_OPTIONS = {
        "realistic": "photorealistic, highly detailed, scientific accuracy",
        "artistic": "artistic interpretation, stylized, visually striking",
        "minimalist": "clean, minimal, elegant, focused composition",
        "dramatic": "dramatic lighting, cinematic, high contrast",
        "abstract": "abstract representation, conceptual, modern art"
    }
    
    MOOD_OPTIONS = {
        "innovative": "cutting-edge, futuristic, breakthrough",
        "hopeful": "optimistic, healing, life-saving",
        "mysterious": "intriguing, discovery, unknown",
        "powerful": "strong, impactful, transformative",
        "serene": "calm, peaceful, balanced"
    }
    
    COLOR_PALETTES = {
        "blue": "deep blue, cyan, scientific blue",
        "green": "emerald, teal, life sciences green",
        "red": "crimson, medical red, vibrant",
        "purple": "violet, scientific purple, rich",
        "warm": "gold, orange, sunset tones",
        "cool": "blue, silver, ice tones",
        "rainbow": "vibrant spectrum, diverse colors"
    }
    
    def generate_prompt(self, research_topic, style="artistic", mood="innovative", 
                       colors="blue", include_text=True):
        """Generate AI art prompt."""
        
        # Base prompt components
        prompt_parts = [
            f"Scientific journal cover art depicting {research_topic}",
            self.STYLE_OPTIONS.get(style, self.STYLE_OPTIONS["artistic"]),
            self.MOOD_OPTIONS.get(mood, self.MOOD_OPTIONS["innovative"]),
            f"color palette: {self.COLOR_PALETTES.get(colors, colors)}",
            "high resolution, professional quality",
            "suitable for journal cover"
        ]
        
        # Technical specifications
        technical = [
            "16:9 aspect ratio",
            "300 DPI",
            "print quality"
        ]
        
        # What to avoid
        negative = [
            "text" if not include_text else "",
            "cluttered",
            "low quality",
            "cartoonish"
        ]
        
        prompt = {
            "main_prompt": ", ".join(prompt_parts),
            "technical_specs": ", ".join(technical),
            "negative_prompt": ", ".join([n for n in negative if n]),
            "suggested_tools": ["Midjourney", "DALL-E 3", "Stable Diffusion"],
            "tips": [
                "Emphasize the central scientific concept",
                "Use metaphorical representations for abstract concepts",
                "Ensure visual clarity at small sizes",
                "Consider how it will look with journal title overlay"
            ]
        }
        
        return prompt
    
    def print_prompt(self, prompt):
        """Print formatted prompt."""
        print(f"\n{'='*70}")
        print("JOURNAL COVER AI ART PROMPT")
        print(f"{'='*70}\n")
        
        print("MAIN PROMPT:")
        print(f"  {prompt['main_prompt']}")
        print()
        
        print("TECHNICAL SPECIFICATIONS:")
        print(f"  {prompt['technical_specs']}")
        print()
        
        if prompt['negative_prompt']:
            print("NEGATIVE PROMPT (what to avoid):")
            print(f"  {prompt['negative_prompt']}")
            print()
        
        print("SUGGESTED AI TOOLS:")
        for tool in prompt['suggested_tools']:
            print(f"  • {tool}")
        print()
        
        print("TIPS:")
        for tip in prompt['tips']:
            print(f"  • {tip}")
        
        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Journal Cover Prompter")
    parser.add_argument("--topic", "-t", required=True, help="Research topic")
    parser.add_argument("--style", "-s", default="artistic",
                       choices=["realistic", "artistic", "minimalist", "dramatic", "abstract"],
                       help="Art style")
    parser.add_argument("--mood", "-m", default="innovative",
                       choices=["innovative", "hopeful", "mysterious", "powerful", "serene"],
                       help="Mood/atmosphere")
    parser.add_argument("--colors", "-c", default="blue",
                       help="Color palette (blue/green/red/purple/warm/cool/rainbow)")
    parser.add_argument("--no-text", action="store_true", help="Exclude text from image")
    
    args = parser.parse_args()
    
    prompter = JournalCoverPrompter()
    
    prompt = prompter.generate_prompt(
        args.topic,
        args.style,
        args.mood,
        args.colors,
        not args.no_text
    )
    
    prompter.print_prompt(prompt)


if __name__ == "__main__":
    main()

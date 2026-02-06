#!/usr/bin/env python3
"""
Conference Poster Pitch
Generate elevator pitches for poster sessions.
"""

import argparse


def generate_pitch(title, duration=60):
    """Generate elevator pitch for given duration."""
    pitches = {
        30: f"Hi, I'm working on {title}. The key finding is... [30 seconds]",
        60: f"Hi, I'm presenting {title}. Our approach was... [60 seconds]",
        180: f"Hi, I'm excited to share {title}. We started with... [3 minutes]"
    }
    return pitches.get(duration, pitches[60])


def main():
    parser = argparse.ArgumentParser(description="Conference Poster Pitch")
    parser.add_argument("--poster-title", "-t", required=True, help="Poster title")
    parser.add_argument("--duration", "-d", type=int, default=60, choices=[30, 60, 180])
    args = parser.parse_args()
    
    pitch = generate_pitch(args.poster_title, args.duration)
    print(f"\n{args.duration}s Pitch:")
    print("-" * 50)
    print(pitch)


if __name__ == "__main__":
    main()

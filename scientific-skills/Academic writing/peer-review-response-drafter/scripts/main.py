#!/usr/bin/env python3
"""
Peer Review Response Drafter

Assists researchers in drafting professional, polite, and structured
responses to peer reviewer comments for academic journal submissions.

Usage:
    python main.py --input reviewer_comments.txt --journal "Nature" --output response.md
    python main.py --interactive
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict


class ToneStyle(Enum):
    """Available tone styles for response drafting."""
    DIPLOMATIC = "diplomatic"
    FORMAL = "formal"
    ASSERTIVE = "assertive"


@dataclass
class ReviewerComment:
    """Represents a single reviewer comment."""
    reviewer_id: int
    comment_id: str
    text: str
    is_major: bool = False
    category: Optional[str] = None


@dataclass
class AuthorChange:
    """Represents an author's change in response to a comment."""
    comment_ref: str
    description: str
    location: Optional[str] = None


@dataclass
class ResponseSection:
    """A drafted response to a reviewer comment."""
    comment: ReviewerComment
    change: Optional[AuthorChange]
    response_text: str


class ResponseDrafter:
    """Main class for drafting peer review response letters."""
    
    # Templates for different response scenarios
    TEMPLATES = {
        "accepted": {
            "openers": [
                "We thank the reviewer for this valuable suggestion.",
                "We appreciate the reviewer's insightful comment.",
                "Thank you for bringing this to our attention.",
                "We are grateful for this constructive feedback."
            ],
            "actions": [
                "We have revised the manuscript accordingly.",
                "This has been addressed in the revised version.",
                "We have incorporated this suggestion.",
                "The manuscript has been updated to reflect this."
            ]
        },
        "partial": {
            "openers": [
                "We thank the reviewer for this thoughtful suggestion.",
                "We appreciate the reviewer's perspective on this matter.",
                "Thank you for raising this important point."
            ],
            "actions": [
                "We have carefully considered this suggestion.",
                "After careful evaluation, we have adopted a modified approach.",
                "We have partially implemented this suggestion."
            ]
        },
        "declined": {
            "openers": [
                "We thank the reviewer for this suggestion.",
                "We appreciate the reviewer's perspective.",
                "Thank you for raising this point."
            ],
            "actions": [
                "Upon careful consideration, we have maintained our original approach.",
                "We respectfully maintain our current formulation.",
                "After careful evaluation, we believe our current approach is appropriate."
            ],
            "rationales": [
                "This is because",
                "Our reasoning is that",
                "This choice was made because"
            ]
        }
    }
    
    def __init__(self, tone: ToneStyle = ToneStyle.DIPLOMATIC):
        self.tone = tone
        self.response_counter = 0
    
    def parse_reviewer_comments(self, text: str) -> List[ReviewerComment]:
        """
        Parse reviewer comments from text.
        
        Supports various formats:
        - "Reviewer 1:" or "Referee 1:"
        - "R1:" or "R1."
        - Numbered lists (1., 1), etc.)
        """
        comments = []
        
        # Pattern to detect reviewer sections
        reviewer_pattern = r'(?:Reviewer|Referee)\s*#?\s*(\d+)[:.\s]'
        
        # Split by reviewer headers
        sections = re.split(reviewer_pattern, text, flags=re.IGNORECASE)
        
        current_reviewer = 0
        for i, section in enumerate(sections):
            if section.isdigit():
                current_reviewer = int(section)
                continue
            
            if current_reviewer == 0:
                continue
                
            # Extract individual comments (numbered items)
            comment_pattern = r'(?:^|\n)\s*(\d+)[:.\)\]]\s*([^\n]+(?:\n(?!(?:^|\n)\s*\d+[:.\)\]])[^\n]+)*)'
            comment_matches = re.findall(comment_pattern, section, re.MULTILINE)
            
            if comment_matches:
                for comment_num, comment_text in comment_matches:
                    comments.append(ReviewerComment(
                        reviewer_id=current_reviewer,
                        comment_id=comment_num,
                        text=comment_text.strip(),
                        is_major=self._is_major_comment(comment_text)
                    ))
            else:
                # If no numbered comments, treat entire section as one comment
                comments.append(ReviewerComment(
                    reviewer_id=current_reviewer,
                    comment_id="General",
                    text=section.strip(),
                    is_major=False
                ))
        
        return comments
    
    def _is_major_comment(self, text: str) -> bool:
        """Detect if a comment addresses a major issue."""
        major_indicators = [
            "major", "significant", "fundamental", "critical",
            "essential", "important concern", "serious"
        ]
        return any(indicator in text.lower() for indicator in major_indicators)
    
    def draft_response(
        self, 
        comment: ReviewerComment, 
        change: Optional[AuthorChange] = None,
        rationale: Optional[str] = None
    ) -> ResponseSection:
        """Draft a response to a single reviewer comment."""
        
        self.response_counter += 1
        
        # Determine response type
        if change is None:
            response_type = "declined"
        elif rationale:
            response_type = "partial"
        else:
            response_type = "accepted"
        
        templates = self.TEMPLATES[response_type]
        
        # Build response
        opener = templates["openers"][(self.response_counter - 1) % len(templates["openers"])]
        action = templates["actions"][(self.response_counter - 1) % len(templates["actions"])]
        
        response_parts = [opener]
        
        if response_type == "accepted":
            if change and change.description:
                response_parts.append(f"{action} {change.description}")
            else:
                response_parts.append(action)
            
            if change and change.location:
                response_parts.append(f"({change.location})")
        
        elif response_type == "partial":
            response_parts.append(action)
            if change and change.description:
                response_parts.append(change.description)
            if rationale:
                response_parts.append(rationale)
            if change and change.location:
                response_parts.append(f"({change.location})")
        
        elif response_type == "declined":
            response_parts.append(action)
            if rationale:
                rationale_opener = templates["rationales"][0]
                response_parts.append(f"{rationale_opener} {rationale}")
        
        response_text = " ".join(response_parts)
        
        return ResponseSection(
            comment=comment,
            change=change,
            response_text=response_text
        )
    
    def generate_full_letter(
        self,
        responses: List[ResponseSection],
        manuscript_title: str,
        journal_name: str,
        authors: Optional[str] = None
    ) -> str:
        """Generate a complete response letter."""
        
        # Group responses by reviewer
        by_reviewer: Dict[int, List[ResponseSection]] = {}
        for resp in responses:
            reviewer_id = resp.comment.reviewer_id
            if reviewer_id not in by_reviewer:
                by_reviewer[reviewer_id] = []
            by_reviewer[reviewer_id].append(resp)
        
        # Build letter
        lines = [
            "Dear Editor and Reviewers,",
            "",
            f'Thank you for your constructive feedback on our manuscript titled '
            f'"{manuscript_title}" submitted to {journal_name}. We have carefully '
            'addressed all comments and revised the manuscript accordingly. Below is '
            "our point-by-point response to each reviewer's comments.",
            ""
        ]
        
        # Add responses by reviewer
        for reviewer_id in sorted(by_reviewer.keys()):
            lines.append(f"## Reviewer #{reviewer_id}")
            lines.append("")
            
            for resp in by_reviewer[reviewer_id]:
                lines.append(f"**Comment {resp.comment.comment_id}:** {resp.comment.text}")
                lines.append("")
                lines.append(f"**Response:** {resp.response_text}")
                lines.append("")
        
        # Closing
        lines.extend([
            "---",
            "",
            "We hope that our revisions satisfactorily address all the reviewers' concerns. "
            "We are grateful for the opportunity to improve our manuscript.",
            "",
            "Sincerely,",
            "",
            authors or "[Author Names]"
        ])
        
        return "\n".join(lines)
    
    def adjust_tone(self, text: str, target_tone: ToneStyle) -> str:
        """Adjust the tone of a drafted response."""
        
        tone_adjustments = {
            ToneStyle.FORMAL: {
                "We thank": "The authors wish to thank",
                "have revised": "have revised and updated",
                "added": "incorporated"
            },
            ToneStyle.ASSERTIVE: {
                "We respectfully": "We",
                "Upon careful consideration": "After evaluation",
                "we believe": "we maintain that"
            }
        }
        
        adjusted = text
        if target_tone in tone_adjustments:
            for original, replacement in tone_adjustments[target_tone].items():
                adjusted = adjusted.replace(original, replacement)
        
        return adjusted


def interactive_mode():
    """Run in interactive mode to collect input from user."""
    print("=" * 60)
    print("Peer Review Response Drafter - Interactive Mode")
    print("=" * 60)
    print()
    
    # Collect manuscript info
    title = input("Manuscript title: ").strip()
    journal = input("Journal name: ").strip()
    authors = input("Author names (comma-separated): ").strip()
    
    print("\nTone preference:")
    print("1. Diplomatic (recommended)")
    print("2. Formal")
    print("3. Assertive")
    tone_choice = input("Select (1-3): ").strip()
    
    tone_map = {"1": ToneStyle.DIPLOMATIC, "2": ToneStyle.FORMAL, "3": ToneStyle.ASSERTIVE}
    tone = tone_map.get(tone_choice, ToneStyle.DIPLOMATIC)
    
    # Collect reviewer comments
    print("\n" + "=" * 60)
    print("Paste reviewer comments below.")
    print("Format: Reviewer 1: then numbered comments")
    print("Type 'END' on a new line when finished:")
    print("=" * 60)
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    comments_text = "\n".join(lines)
    
    # Process
    drafter = ResponseDrafter(tone=tone)
    comments = drafter.parse_reviewer_comments(comments_text)
    
    print(f"\nFound {len(comments)} comments from {len(set(c.reviewer_id for c in comments))} reviewer(s).")
    
    # Collect changes
    changes = {}
    print("\n" + "=" * 60)
    print("For each comment, describe what you changed (or leave blank if no change):")
    print("=" * 60)
    
    for comment in comments:
        print(f"\nReviewer {comment.reviewer_id}, Comment {comment.comment_id}:")
        print(f"  {comment.text[:100]}{'...' if len(comment.text) > 100 else ''}")
        change_desc = input("  Your change: ").strip()
        
        if change_desc:
            location = input("  Location (e.g., 'Page 5, Lines 120-135'): ").strip()
            changes[f"{comment.reviewer_id}.{comment.comment_id}"] = AuthorChange(
                comment_ref=f"{comment.reviewer_id}.{comment.comment_id}",
                description=change_desc,
                location=location if location else None
            )
    
    # Generate responses
    responses = []
    for comment in comments:
        change = changes.get(f"{comment.reviewer_id}.{comment.comment_id}")
        response = drafter.draft_response(comment, change)
        responses.append(response)
    
    # Generate full letter
    letter = drafter.generate_full_letter(responses, title, journal, authors)
    
    print("\n" + "=" * 60)
    print("GENERATED RESPONSE LETTER:")
    print("=" * 60)
    print(letter)
    
    # Save option
    save = input("\nSave to file? (filename or 'n'): ").strip()
    if save and save.lower() != 'n':
        with open(save, 'w') as f:
            f.write(letter)
        print(f"Saved to {save}")


def main():
    parser = argparse.ArgumentParser(
        description="Draft professional peer review response letters"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input file containing reviewer comments"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the response letter"
    )
    parser.add_argument(
        "--title", "-t",
        required=True,
        help="Manuscript title"
    )
    parser.add_argument(
        "--journal", "-j",
        required=True,
        help="Journal name"
    )
    parser.add_argument(
        "--authors", "-a",
        help="Author names"
    )
    parser.add_argument(
        "--tone",
        choices=["diplomatic", "formal", "assertive"],
        default="diplomatic",
        help="Response tone (default: diplomatic)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive or (not args.input and sys.stdin.isatty()):
        interactive_mode()
        return
    
    # Read input
    if args.input:
        with open(args.input, 'r') as f:
            comments_text = f.read()
    else:
        comments_text = sys.stdin.read()
    
    # Process
    tone_map = {
        "diplomatic": ToneStyle.DIPLOMATIC,
        "formal": ToneStyle.FORMAL,
        "assertive": ToneStyle.ASSERTIVE
    }
    
    drafter = ResponseDrafter(tone=tone_map[args.tone])
    comments = drafter.parse_reviewer_comments(comments_text)
    
    # For command-line mode, generate placeholder responses
    responses = []
    for comment in comments:
        response = drafter.draft_response(comment, None)
        responses.append(response)
    
    letter = drafter.generate_full_letter(
        responses, args.title, args.journal, args.authors
    )
    
    # Apply tone adjustment
    letter = drafter.adjust_tone(letter, tone_map[args.tone])
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(letter)
        print(f"Response letter saved to {args.output}")
    else:
        print(letter)


if __name__ == "__main__":
    main()

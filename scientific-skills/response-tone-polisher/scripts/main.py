#!/usr/bin/env python3
"""
Response Tone Polisher

Polishes response letters to peer reviewers by transforming defensive or harsh 
language into professional, courteous academic prose.

Usage:
    python main.py --interactive
    python main.py --reviewer-comment "comment.txt" --draft-response "draft.txt"
    python main.py --reviewer "The data is insufficient" --draft "We disagree"

Author: AI Assistant
Version: 1.0.0
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Tuple
import os


class ResponseType(Enum):
    """Types of response to reviewer comments."""
    ACCEPT = "accept"
    PARTIAL = "partial"
    DECLINE = "decline"


class PolishLevel(Enum):
    """Levels of tone polishing."""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"


@dataclass
class ToneIssue:
    """Represents a tone issue found in text."""
    original_phrase: str
    issue_type: str
    severity: float  # 0-1, higher = more problematic
    position: Tuple[int, int]  # start, end positions


@dataclass
class PolishResult:
    """Result of tone polishing."""
    polished_response: str
    original_tone_score: float
    politeness_score: float
    improvements: List[Dict]
    suggestions: List[str]


class TonePolisher:
    """
    Main class for polishing response letter tone.
    
    Transforms defensive or harsh language into professional, 
    courteous academic prose while preserving scientific positions.
    """
    
    # Defensive/harsh patterns and their polished alternatives
    TONE_PATTERNS = {
        # Direct refusals
        r"\b[Ii] will not (?:change|modify|correct|revise|update)\b": {
            "replacement": "We have carefully considered this suggestion and respectfully maintain our original {noun}",
            "issue_type": "direct_refusal",
            "severity": 0.9
        },
        r"\b[Ww]e will not (?:change|modify|correct|revise|update)\b": {
            "replacement": "We have carefully considered this suggestion and respectfully maintain our original {noun}",
            "issue_type": "direct_refusal",
            "severity": 0.9
        },
        r"\b[Nn]o,? (?:we )?(?:will not|won't|cannot|can't)\b": {
            "replacement": "We respectfully decline to {verb} because",
            "issue_type": "direct_refusal",
            "severity": 0.85
        },
        r"\b[Ii] (?:disagree|don't agree)\b": {
            "replacement": "We respectfully offer a different interpretation",
            "issue_type": "confrontational",
            "severity": 0.7
        },
        r"\b[Ww]e (?:disagree|don't agree)\b": {
            "replacement": "We respectfully offer a different interpretation",
            "issue_type": "confrontational",
            "severity": 0.7
        },
        
        # Defensive statements
        r"\b[Tt]he reviewer is (?:wrong|incorrect|mistaken)\b": {
            "replacement": "We respectfully note that",
            "issue_type": "defensive",
            "severity": 0.95
        },
        r"\b[Tt]his is (?:wrong|incorrect|not correct)\b": {
            "replacement": "We respectfully suggest an alternative view",
            "issue_type": "defensive",
            "severity": 0.8
        },
        r"\b[Ww]e (?:already|previously) (?:stated|mentioned|explained|noted)\b": {
            "replacement": "We have now expanded our explanation to enhance clarity",
            "issue_type": "defensive",
            "severity": 0.75
        },
        r"\b[Bb]ut we (?:already|did)\b": {
            "replacement": "We have now clarified",
            "issue_type": "defensive",
            "severity": 0.7
        },
        
        # Blame shifting
        r"\b[Tt]he reviewer (?:misunderstood|misinterpreted|did not understand)\b": {
            "replacement": "We apologize for the lack of clarity; we have revised",
            "issue_type": "blame_shifting",
            "severity": 0.9
        },
        r"\b[Tt]his was not our (?:fault|responsibility|error)\b": {
            "replacement": "We acknowledge this limitation and have added appropriate caveats",
            "issue_type": "blame_shifting",
            "severity": 0.85
        },
        
        # Dismissive language
        r"\b[Tt]his is (?:unnecessary|not needed|redundant)\b": {
            "replacement": "While we appreciate this suggestion, we believe the current presentation adequately addresses this point",
            "issue_type": "dismissive",
            "severity": 0.75
        },
        r"\b[Tt]his is (?:obvious|clear|evident)\b": {
            "replacement": "This point is addressed",
            "issue_type": "dismissive",
            "severity": 0.6
        },
        r"\b[Ii]t is (?:obvious|clear|evident) that\b": {
            "replacement": "We note that",
            "issue_type": "dismissive",
            "severity": 0.65
        },
        
        # Overly casual/direct
        r"\b[Ii]t's not our (?:fault|problem)\b": {
            "replacement": "This reflects an inherent limitation that we have now addressed",
            "issue_type": "unprofessional",
            "severity": 0.9
        },
        r"\b[Nn]ot our (?:fault|responsibility)\b": {
            "replacement": "We acknowledge this constraint",
            "issue_type": "unprofessional",
            "severity": 0.85
        },
        
        # Emotional/overly apologetic
        r"\b[Uu]nfortunately,? we (?:cannot|can't|are unable to)\b": {
            "replacement": "We are unable to",
            "issue_type": "emotional",
            "severity": 0.4
        },
        r"\b[Ww]e (?:cannot|can't) (?:possibly|really)\b": {
            "replacement": "We are unable to",
            "issue_type": "emotional",
            "severity": 0.5
        },
    }
    
    # Polite academic expression library
    POLITE_EXPRESSIONS = {
        "acknowledgments": [
            "We thank the reviewer for this insightful observation.",
            "We appreciate the reviewer's careful attention to this detail.",
            "We are grateful for this constructive feedback.",
            "This is an excellent point.",
            "We value this thoughtful comment.",
        ],
        "partial_agreement": [
            "We thank the reviewer for this suggestion. While we appreciate this perspective, we note that",
            "We appreciate this recommendation. Upon careful consideration, we believe",
            "We have carefully evaluated this suggestion. However,",
        ],
        "respectful_disagreement": [
            "We respectfully offer an alternative interpretation",
            "Upon careful reconsideration, we maintain that",
            "While we appreciate this perspective, we respectfully note that",
            "We respectfully maintain our position that",
            "We believe an alternative approach may be warranted",
        ],
        "limitations": [
            "We acknowledge this limitation and have addressed it by",
            "This constraint reflects the trade-off between",
            "We have added appropriate caveats regarding this limitation",
            "We recognize this constraint and have noted it in",
        ],
        "changes_made": [
            "We have revised the manuscript to clarify",
            "We have expanded the relevant section to include",
            "We have incorporated this suggestion by",
            "We have updated the text to reflect",
            "We have added the following clarification",
        ],
        "clarification": [
            "To enhance clarity, we have",
            "We have revised this section to more clearly state",
            "The text now explicitly states",
            "We have clarified this point by",
        ]
    }
    
    def __init__(self, polish_level: PolishLevel = PolishLevel.MODERATE):
        self.polish_level = polish_level
        self.context_noun = "approach"  # Default noun for replacements
        
    def analyze_tone(self, text: str) -> Tuple[float, List[ToneIssue]]:
        """
        Analyze the tone of a draft response.
        
        Returns:
            Tuple of (defensiveness_score, list_of_issues)
        """
        issues = []
        total_severity = 0
        
        for pattern, info in self.TONE_PATTERNS.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                issue = ToneIssue(
                    original_phrase=match.group(),
                    issue_type=info["issue_type"],
                    severity=info["severity"],
                    position=(match.start(), match.end())
                )
                issues.append(issue)
                total_severity += info["severity"]
        
        # Calculate overall defensiveness score (0-1)
        word_count = len(text.split())
        if word_count > 0:
            defensiveness_score = min(1.0, total_severity / (word_count / 20 + 1))
        else:
            defensiveness_score = 0.0
            
        return defensiveness_score, issues
    
    def polish(
        self,
        reviewer_comment: str,
        draft_response: str,
        response_type: Optional[ResponseType] = None,
        polish_level: Optional[PolishLevel] = None
    ) -> PolishResult:
        """
        Polish a draft response to make it more professional and courteous.
        
        Args:
            reviewer_comment: The original reviewer comment
            draft_response: The author's draft response
            response_type: Type of response (accept/partial/decline)
            polish_level: Level of polishing to apply
            
        Returns:
            PolishResult containing polished response and metadata
        """
        if polish_level:
            self.polish_level = polish_level
            
        # Auto-detect response type if not provided
        if not response_type:
            response_type = self._detect_response_type(draft_response)
        
        # Analyze original tone
        original_tone_score, issues = self.analyze_tone(draft_response)
        
        # Generate polished response
        polished = self._generate_polished_response(
            reviewer_comment, draft_response, response_type, issues
        )
        
        # Calculate politeness score
        politeness_score = self._calculate_politeness(polished)
        
        # Generate improvements list
        improvements = self._generate_improvements_list(issues, polished)
        
        # Generate additional suggestions
        suggestions = self._generate_suggestions(reviewer_comment, polished)
        
        return PolishResult(
            polished_response=polished,
            original_tone_score=original_tone_score,
            politeness_score=politeness_score,
            improvements=improvements,
            suggestions=suggestions
        )
    
    def _detect_response_type(self, draft_response: str) -> ResponseType:
        """Auto-detect the type of response based on content."""
        decline_indicators = [
            r"\bnot change\b", r"\bnot modify\b", r"\bnot revise\b",
            r"\bdisagree\b", r"\bwon't\b", r"\bcannot\b",
            r"\bmaintain\b", r"\boriginal\b"
        ]
        accept_indicators = [
            r"\bhave revised\b", r"\bhave changed\b", r"\bhave updated\b",
            r"\bthank you\b", r"\bagree\b", r"\bmodified\b"
        ]
        
        decline_count = sum(1 for p in decline_indicators if re.search(p, draft_response, re.I))
        accept_count = sum(1 for p in accept_indicators if re.search(p, draft_response, re.I))
        
        if decline_count > accept_count:
            return ResponseType.DECLINE
        elif accept_count > 0:
            return ResponseType.ACCEPT
        else:
            return ResponseType.PARTIAL
    
    def _generate_polished_response(
        self,
        reviewer_comment: str,
        draft_response: str,
        response_type: ResponseType,
        issues: List[ToneIssue]
    ) -> str:
        """Generate the polished response text."""
        
        # Start with acknowledgment
        result_parts = []
        
        # Add appropriate opening based on response type
        if response_type == ResponseType.ACCEPT:
            opener = self._select_expression("acknowledgments")
            result_parts.append(opener)
            result_parts.append(self._transform_to_acceptance(draft_response))
        elif response_type == ResponseType.PARTIAL:
            opener = self._select_expression("partial_agreement")
            result_parts.append(opener)
            result_parts.append(self._transform_to_partial(draft_response))
        else:  # DECLINE
            opener = self._select_expression("acknowledgments")
            result_parts.append(opener)
            result_parts.append(self._transform_to_decline(draft_response))
        
        # Apply pattern-based replacements
        polished = " ".join(result_parts)
        
        # Apply specific pattern replacements
        for pattern, info in self.TONE_PATTERNS.items():
            replacement = info["replacement"]
            if "{noun}" in replacement:
                replacement = replacement.format(noun=self.context_noun)
            if "{verb}" in replacement:
                # Extract verb from context - simplified
                replacement = replacement.format(verb="make this change")
            
            polished = re.sub(pattern, replacement, polished, flags=re.IGNORECASE)
        
        # Clean up and format
        polished = self._clean_text(polished)
        
        return polished
    
    def _select_expression(self, category: str) -> str:
        """Select a polite expression from the library."""
        import random
        expressions = self.POLITE_EXPRESSIONS.get(category, ["Thank you for this comment."])
        return random.choice(expressions)
    
    def _transform_to_acceptance(self, draft: str) -> str:
        """Transform draft into acceptance language."""
        # Remove defensive prefixes
        cleaned = re.sub(r"^\s*(?:[Bb]ut|[Hh]owever)\s*,?\s*", "", draft)
        
        # Add change language if not present
        if not re.search(r"\b(?:have revised|have changed|have updated|have modified)\b", cleaned, re.I):
            return f"We have revised the manuscript as suggested. {cleaned}"
        return cleaned
    
    def _transform_to_partial(self, draft: str) -> str:
        """Transform draft into partial acceptance language."""
        # Start with partial acceptance framing
        return draft
    
    def _transform_to_decline(self, draft: str) -> str:
        """Transform draft into respectful decline language."""
        # Replace harsh refusals with polite alternatives
        return draft
    
    def _clean_text(self, text: str) -> str:
        """Clean up and format the text."""
        # Fix spacing
        text = re.sub(r"\s+", " ", text)
        # Fix punctuation spacing
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        # Ensure period at end
        if text and not text.endswith((".", "!", "?")):
            text += "."
        return text
    
    def _calculate_politeness(self, text: str) -> float:
        """Calculate a politeness score for the text."""
        polite_indicators = [
            r"\bthank\b", r"\bappreciate\b", r"\bgrateful\b",
            r"\brespectfully\b", r"\bcarefully considered\b",
            r"\bvaluable\b", r"\binsightful\b", r"\bconstructive\b"
        ]
        
        rude_indicators = [
            r"\bwrong\b", r"\bincorrect\b", r"\bdisagree\b(?!\s+with)",
            r"\bnot\s+(?:correct|true|accurate)\b", r"\byou\s+(?:are|have)\s+(?:wrong|mistaken)"
        ]
        
        polite_count = sum(1 for p in polite_indicators if re.search(p, text, re.I))
        rude_count = sum(1 for p in rude_indicators if re.search(p, text, re.I))
        
        score = 0.5 + (polite_count * 0.1) - (rude_count * 0.2)
        return max(0.0, min(1.0, score))
    
    def _generate_improvements_list(
        self,
        issues: List[ToneIssue],
        polished: str
    ) -> List[Dict]:
        """Generate a list of improvements made."""
        improvements = []
        for issue in issues:
            # Find what this issue was transformed to (simplified)
            improvements.append({
                "original_phrase": issue.original_phrase,
                "polished_phrase": f"[Transformed {issue.issue_type}]",
                "issue_type": issue.issue_type,
                "severity": issue.severity
            })
        return improvements
    
    def _generate_suggestions(self, reviewer_comment: str, polished: str) -> List[str]:
        """Generate additional suggestions for improvement."""
        suggestions = []
        
        # Check for missing location references
        if not re.search(r"\b(?:[Pp]age|[Ll]ine|[Ff]igure|[Tt]able)\b", polished):
            suggestions.append("Consider adding page/line references to help reviewers locate changes.")
        
        # Check for rationale in decline situations
        if "respectfully" in polished.lower() and "because" not in polished.lower():
            suggestions.append("When declining suggestions, provide a brief rationale.")
        
        # Check length
        word_count = len(polished.split())
        if word_count < 20:
            suggestions.append("The response is quite brief; consider adding more detail about the changes made.")
        
        return suggestions


def interactive_mode():
    """Run in interactive mode to collect input from user."""
    print("=" * 70)
    print("Response Tone Polisher - Interactive Mode")
    print("=" * 70)
    print()
    print("This tool helps polish your responses to peer reviewers.")
    print("It transforms defensive or harsh language into professional, courteous prose.")
    print()
    
    # Get polish level
    print("Select polish level:")
    print("  1. Light (minimal changes)")
    print("  2. Moderate (recommended)")
    print("  3. Heavy (aggressive polishing)")
    level_choice = input("Choice (1-3): ").strip() or "2"
    
    level_map = {
        "1": PolishLevel.LIGHT,
        "2": PolishLevel.MODERATE,
        "3": PolishLevel.HEAVY
    }
    polish_level = level_map.get(level_choice, PolishLevel.MODERATE)
    
    # Get reviewer comment
    print("\n" + "-" * 70)
    print("Paste the REVIEWER COMMENT below (type 'END' on new line when done):")
    print("-" * 70)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    reviewer_comment = "\n".join(lines)
    
    # Get draft response
    print("\n" + "-" * 70)
    print("Paste your DRAFT RESPONSE below (type 'END' on new line when done):")
    print("-" * 70)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    draft_response = "\n".join(lines)
    
    # Process
    print("\n" + "=" * 70)
    print("Polishing your response...")
    print("=" * 70)
    
    polisher = TonePolisher(polish_level=polish_level)
    result = polisher.polish(reviewer_comment, draft_response)
    
    # Display results
    print("\n📊 TONE ANALYSIS:")
    print(f"   Original defensiveness score: {result.original_tone_score:.2f}/1.0")
    print(f"   Politeness score: {result.politeness_score:.2f}/1.0")
    
    if result.improvements:
        print(f"\n🔧 IMPROVEMENTS MADE ({len(result.improvements)}):")
        for i, imp in enumerate(result.improvements[:5], 1):
            print(f"   {i}. [{imp['issue_type'].replace('_', ' ').title()}]")
            print(f"      Original: \"{imp['original_phrase'][:50]}...\" " if len(imp['original_phrase']) > 50 else f"      Original: \"{imp['original_phrase']}\"")
    
    if result.suggestions:
        print(f"\n💡 SUGGESTIONS:")
        for i, sug in enumerate(result.suggestions, 1):
            print(f"   {i}. {sug}")
    
    print("\n" + "=" * 70)
    print("✨ POLISHED RESPONSE:")
    print("=" * 70)
    print(result.polished_response)
    
    # Save option
    save = input("\n\nSave to file? (filename or 'n'): ").strip()
    if save and save.lower() != 'n':
        output = {
            "polished_response": result.polished_response,
            "original_tone_score": result.original_tone_score,
            "politeness_score": result.politeness_score,
            "improvements": result.improvements,
            "suggestions": result.suggestions
        }
        with open(save, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✅ Saved to {save}")


def main():
    parser = argparse.ArgumentParser(
        description="Polish response letters by transforming defensive language into professional prose"
    )
    parser.add_argument(
        "--reviewer-comment", "-r",
        help="File containing reviewer comment, or the comment text directly"
    )
    parser.add_argument(
        "--draft-response", "-d",
        help="File containing draft response, or the text directly"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the polished response"
    )
    parser.add_argument(
        "--response-type", "-t",
        choices=["accept", "partial", "decline"],
        help="Type of response (default: auto-detect)"
    )
    parser.add_argument(
        "--polish-level", "-p",
        choices=["light", "moderate", "heavy"],
        default="moderate",
        help="Level of polishing (default: moderate)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    if args.interactive or (not args.reviewer_comment and not args.draft_response):
        interactive_mode()
        return
    
    # Read inputs
    reviewer_comment = args.reviewer_comment
    draft_response = args.draft_response
    
    # Check if inputs are files
    if reviewer_comment and os.path.isfile(reviewer_comment):
        with open(reviewer_comment, 'r') as f:
            reviewer_comment = f.read()
    
    if draft_response and os.path.isfile(draft_response):
        with open(draft_response, 'r') as f:
            draft_response = f.read()
    
    if not reviewer_comment or not draft_response:
        print("Error: Both --reviewer-comment and --draft-response are required.")
        sys.exit(1)
    
    # Map response type
    response_type = None
    if args.response_type:
        response_type = ResponseType(args.response_type)
    
    # Map polish level
    polish_level = PolishLevel(args.polish_level)
    
    # Process
    polisher = TonePolisher(polish_level=polish_level)
    result = polisher.polish(reviewer_comment, draft_response, response_type, polish_level)
    
    # Output
    if args.json:
        output = {
            "polished_response": result.polished_response,
            "original_tone_score": result.original_tone_score,
            "politeness_score": result.politeness_score,
            "improvements": result.improvements,
            "suggestions": result.suggestions
        }
        output_text = json.dumps(output, indent=2)
    else:
        output_text = result.polished_response
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Polished response saved to {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()

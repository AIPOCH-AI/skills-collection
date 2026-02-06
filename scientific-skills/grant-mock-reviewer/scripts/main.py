#!/usr/bin/env python3
"""
Grant Mock Reviewer - NIH Study Section Simulator

Simulates NIH peer review by applying official scoring criteria,
generating structured critiques, and producing Summary Statement-style output.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class GrantType(Enum):
    R01 = "R01"
    R21 = "R21"
    R03 = "R03"
    K99 = "K99"
    F32 = "F32"


class Criterion(Enum):
    SIGNIFICANCE = "significance"
    INVESTIGATOR = "investigator"
    INNOVATION = "innovation"
    APPROACH = "approach"
    ENVIRONMENT = "environment"


SCORE_DESCRIPTORS = {
    1: "Exceptional",
    2: "Outstanding",
    3: "Excellent",
    4: "Very Good",
    5: "Good",
    6: "Satisfactory",
    7: "Fair",
    8: "Marginal",
    9: "Poor"
}


@dataclass
class CriterionScore:
    """Score and critique for a single NIH review criterion."""
    criterion: str
    score: int
    strengths: List[str]
    weaknesses: List[str]
    narrative: str


@dataclass
class ReviewResult:
    """Complete review results including all criteria and overall impact."""
    overall_impact: int
    criterion_scores: Dict[str, CriterionScore]
    summary_statement: str
    revision_recommendations: List[str]
    priority_score: float  # Percentile estimate


class NIHScoringRubric:
    """Official NIH scoring rubric implementation."""
    
    # Score descriptors and typical characteristics
    RUBRIC = {
        "significance": {
            1: ["Transformative impact", "Addresses critical barrier", "High clinical/public health importance"],
            3: ["Important problem", "Advances scientific knowledge", "Clear health relevance"],
            5: ["Moderately important", "Some knowledge advancement", "Indirect health relevance"],
            7: ["Limited importance", "Minimal knowledge gain", "Unclear health relevance"],
            9: ["Trivial problem", "No meaningful advancement", "No health relevance"]
        },
        "investigator": {
            1: ["Exceptionally qualified", "Outstanding track record", "Perfect expertise match"],
            3: ["Well-qualified", "Strong track record", "Appropriate expertise"],
            5: ["Adequately qualified", "Satisfactory record", "Some expertise gaps"],
            7: ["Marginally qualified", "Limited experience", "Significant expertise gaps"],
            9: ["Unqualified", "No relevant experience", "Wrong expertise area"]
        },
        "innovation": {
            1: ["Paradigm-shifting", "Truly novel concepts", "Breakthrough potential"],
            3: ["Challenges paradigms", "Novel approaches", "Significant advancement"],
            5: ["Some innovation", "Incremental advances", "Minor improvements"],
            7: ["Little innovation", "Standard approaches", "No advancement"],
            9: ["No innovation", "Purely derivative", "Obsolete methods"]
        },
        "approach": {
            1: ["Rigorous design", "Excellent feasibility", "Comprehensive alternatives"],
            3: ["Sound design", "Good feasibility", "Adequate alternatives"],
            5: ["Adequate design", "Questionable feasibility", "Limited alternatives"],
            7: ["Weak design", "Poor feasibility", "No alternatives"],
            9: ["Fatally flawed", "Not feasible", "No consideration of pitfalls"]
        },
        "environment": {
            1: ["Outstanding resources", "Exceptional support", "Ideal collaborative environment"],
            3: ["Adequate resources", "Good support", "Appropriate environment"],
            5: ["Sufficient resources", "Adequate support", "Satisfactory environment"],
            7: ["Inadequate resources", "Limited support", "Challenging environment"],
            9: ["Missing critical resources", "No support", "Hostile environment"]
        }
    }
    
    @classmethod
    def get_score_characteristics(cls, criterion: str, score: int) -> List[str]:
        """Get typical characteristics for a given score."""
        criterion = criterion.lower()
        # Map to nearest defined score (1, 3, 5, 7, 9)
        mapped_score = min([1, 3, 5, 7, 9], key=lambda x: abs(x - score))
        return cls.RUBRIC.get(criterion, {}).get(mapped_score, [])


class WeaknessAnalyzer:
    """Analyzes grant proposals for common weaknesses."""
    
    WEAKNESS_PATTERNS = {
        "significance": {
            "rationale": [
                (r"\bgap\b.*\bknowledge\b|\bknowledge\b.*\bgap\b", "Knowledge gap not clearly articulated"),
                (r"\bunclear\b.*\bproblem\b|\bproblem\b.*\bunclear\b", "Research problem poorly defined"),
            ],
            "impact": [
                (r"\bincremental\b|\bminor\b.*\badvance\b", "Research appears incremental"),
                (r"\bunclear\b.*\bsignificance\b", "Significance not well-established"),
            ]
        },
        "investigator": {
            "expertise": [
                (r"\bnew\b.*\bfield\b|\bunfamiliar\b.*\bmethod\b", "Investigator may lack specific expertise"),
            ],
            "commitment": [
                (r"\b\d+%\b.*\beffort\b|\beffort\b.*\b\d+%\b", "Check effort allocation reasonableness"),
            ]
        },
        "innovation": {
            "novelty": [
                (r"\bstandard\b.*\bmethod\b|\bconventional\b", "Methods appear standard rather than innovative"),
                (r"\bpreviously\b.*\bpublished\b|\bwell-known\b", "Approach may lack novelty"),
            ]
        },
        "approach": {
            "design": [
                (r"\bno\b.*\bcontrol\b|\blacking\b.*\bcontrol\b", "Inadequate experimental controls"),
                (r"\bsample\b.*\bsize\b|\bn\s*=\s*\d+", "Verify sample size justification"),
                (r"\bstatistical\b.*\banalysis\b|\bpower\b.*\bcalculation", "Check statistical rigor"),
            ],
            "feasibility": [
                (r"\bpreliminary\b.*\bdata\b", "Evaluate adequacy of preliminary data"),
                (r"\baim\b.*\btoo\b.*\bambitious\b|\bambitious\b.*\baim\b", "Aims may be overly ambitious"),
                (r"\bthree\b.*\baim\b|\bfour\b.*\baim\b|\bfive\b.*\baim\b", "Multiple aims may be difficult to complete"),
            ],
            "pitfalls": [
                (r"\bpitfall\b|\balternative\b.*\bapproach\b|\bplan\s+B\b", "Check adequacy of alternative plans"),
            ]
        },
        "environment": {
            "resources": [
                (r"\bcore\b.*\bfacility\b|\bfacility\b", "Verify core facility access"),
                (r"\bequipment\b", "Confirm equipment availability"),
            ]
        }
    }
    
    def analyze(self, proposal_text: str, criterion: Optional[str] = None) -> Dict[str, List[str]]:
        """Analyze text for weaknesses."""
        text_lower = proposal_text.lower()
        results = {}
        
        criteria_to_check = [criterion] if criterion else self.WEAKNESS_PATTERNS.keys()
        
        for crit in criteria_to_check:
            if crit not in self.WEAKNESS_PATTERNS:
                continue
                
            weaknesses = []
            for category, patterns in self.WEAKNESS_PATTERNS[crit].items():
                for pattern, description in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        weaknesses.append(description)
            
            if weaknesses:
                results[crit] = weaknesses
                
        return results


class GrantMockReviewer:
    """Main class for grant proposal review."""
    
    def __init__(self):
        self.scoring_rubric = NIHScoringRubric()
        self.weakness_analyzer = WeaknessAnalyzer()
    
    def review(
        self,
        proposal_text: str,
        grant_type: str = "R01",
        section: str = "full",
        focus_criterion: Optional[str] = None
    ) -> ReviewResult:
        """
        Perform a complete mock review of a grant proposal.
        
        Args:
            proposal_text: The text content of the proposal
            grant_type: Type of grant (R01, R21, etc.)
            section: Section being reviewed
            focus_criterion: Optional single criterion to focus on
            
        Returns:
            ReviewResult containing all scores and critiques
        """
        # Analyze weaknesses
        weaknesses = self.weakness_analyzer.analyze(proposal_text, focus_criterion)
        
        # Score each criterion
        criterion_scores = {}
        for criterion in Criterion:
            crit_name = criterion.value
            if focus_criterion and crit_name != focus_criterion.lower():
                continue
                
            score = self._score_criterion(proposal_text, crit_name, weaknesses.get(crit_name, []))
            strengths = self._identify_strengths(proposal_text, crit_name)
            
            criterion_scores[crit_name] = CriterionScore(
                criterion=crit_name.capitalize(),
                score=score,
                strengths=strengths,
                weaknesses=weaknesses.get(crit_name, []),
                narrative=self._generate_narrative(crit_name, score, strengths, weaknesses.get(crit_name, []))
            )
        
        # Calculate overall impact score
        overall = self._calculate_overall_impact(criterion_scores)
        
        # Generate summary statement
        summary = self._generate_summary_statement(criterion_scores, overall)
        
        # Generate revision recommendations
        recommendations = self._generate_recommendations(criterion_scores)
        
        # Estimate priority/percentile
        priority = self._estimate_priority(overall)
        
        return ReviewResult(
            overall_impact=overall,
            criterion_scores=criterion_scores,
            summary_statement=summary,
            revision_recommendations=recommendations,
            priority_score=priority
        )
    
    def _score_criterion(self, text: str, criterion: str, identified_weaknesses: List[str]) -> int:
        """Score a single criterion based on content analysis."""
        # Base scoring logic - in production, this would use more sophisticated NLP
        base_score = 5  # Start at "Good"
        
        # Adjust based on identified weaknesses
        weakness_penalty = len(identified_weaknesses) * 0.5
        
        # Check for positive indicators
        positive_indicators = self._count_positive_indicators(text, criterion)
        strength_bonus = positive_indicators * 0.3
        
        # Calculate final score (1-9 scale)
        score = int(round(base_score + weakness_penalty - strength_bonus))
        score = max(1, min(9, score))  # Clamp to 1-9
        
        return score
    
    def _count_positive_indicators(self, text: str, criterion: str) -> int:
        """Count positive indicators for a criterion."""
        text_lower = text.lower()
        indicators = {
            "significance": ["critical", "important", "transformative", "substantial impact"],
            "investigator": ["expertise", "experience", "published", "track record"],
            "innovation": ["novel", "innovative", "breakthrough", "paradigm"],
            "approach": ["rigorous", "feasible", "sound design", "adequate controls"],
            "environment": ["excellent", "outstanding resources", "core facility"]
        }
        
        count = 0
        for indicator in indicators.get(criterion, []):
            if indicator in text_lower:
                count += 1
        return count
    
    def _identify_strengths(self, text: str, criterion: str) -> List[str]:
        """Identify strengths for a criterion."""
        # Placeholder - in production, would use NLP to extract actual strengths
        strengths = []
        
        text_lower = text.lower()
        
        if criterion == "significance":
            if "important" in text_lower or "critical" in text_lower:
                strengths.append("Addresses an important research question")
            if "gap" in text_lower:
                strengths.append("Identifies clear knowledge gap")
                
        elif criterion == "investigator":
            if "experience" in text_lower or "expertise" in text_lower:
                strengths.append("PI has relevant expertise")
                
        elif criterion == "innovation":
            if "novel" in text_lower or "innovative" in text_lower:
                strengths.append("Proposes innovative approach")
                
        elif criterion == "approach":
            if "preliminary" in text_lower and "data" in text_lower:
                strengths.append("Supported by preliminary data")
            if "control" in text_lower:
                strengths.append("Includes appropriate controls")
                
        elif criterion == "environment":
            if "facility" in text_lower or "resource" in text_lower:
                strengths.append("Access to appropriate resources")
        
        return strengths if strengths else ["Unable to identify specific strengths"]
    
    def _generate_narrative(self, criterion: str, score: int, strengths: List[str], weaknesses: List[str]) -> str:
        """Generate narrative critique for a criterion."""
        descriptor = SCORE_DESCRIPTORS.get(score, "Unknown")
        
        narrative_parts = [f"Criterion: {criterion.capitalize()} - Score: {score} ({descriptor})"]
        
        if strengths:
            narrative_parts.append("\nStrengths:")
            for s in strengths:
                narrative_parts.append(f"  • {s}")
        
        if weaknesses:
            narrative_parts.append("\nWeaknesses:")
            for w in weaknesses:
                narrative_parts.append(f"  • {w}")
        
        return "\n".join(narrative_parts)
    
    def _calculate_overall_impact(self, criterion_scores: Dict[str, CriterionScore]) -> int:
        """Calculate overall impact score from criterion scores."""
        if not criterion_scores:
            return 5
        
        # Approach is typically weighted most heavily
        weights = {
            "significance": 1.0,
            "investigator": 0.8,
            "innovation": 0.9,
            "approach": 1.2,
            "environment": 0.6
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for crit, score_obj in criterion_scores.items():
            weight = weights.get(crit.lower(), 1.0)
            weighted_sum += score_obj.score * weight
            total_weight += weight
        
        overall = int(round(weighted_sum / total_weight)) if total_weight > 0 else 5
        return max(1, min(9, overall))
    
    def _generate_summary_statement(
        self,
        criterion_scores: Dict[str, CriterionScore],
        overall: int
    ) -> str:
        """Generate NIH-style Summary Statement."""
        descriptor = SCORE_DESCRIPTORS.get(overall, "Unknown")
        
        lines = [
            "=" * 70,
            "MOCK NIH SUMMARY STATEMENT",
            "=" * 70,
            f"\nOVERALL IMPACT: {overall} ({descriptor})",
            f"\nThis application proposes research that has been evaluated by a simulated",
            f"NIH study section review. The following critiques reflect the major",
            f"strengths and weaknesses identified during review.\n"
        ]
        
        lines.append("-" * 70)
        lines.append("CRITERION SCORES:")
        lines.append("-" * 70)
        
        for crit, score_obj in criterion_scores.items():
            desc = SCORE_DESCRIPTORS.get(score_obj.score, "Unknown")
            lines.append(f"  {crit.capitalize():20s}: {score_obj.score} ({desc})")
        
        lines.append("\n" + "-" * 70)
        lines.append("CRITIQUE:")
        lines.append("-" * 70)
        
        for crit, score_obj in criterion_scores.items():
            lines.append(f"\n{score_obj.narrative}")
        
        lines.append("\n" + "=" * 70)
        lines.append("END OF SUMMARY STATEMENT")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, criterion_scores: Dict[str, CriterionScore]) -> List[str]:
        """Generate prioritized revision recommendations."""
        recommendations = []
        
        # Sort criteria by score (highest score = biggest weakness in NIH system)
        sorted_criteria = sorted(
            criterion_scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        
        for criterion, score_obj in sorted_criteria:
            if score_obj.score >= 5:  # Needs improvement
                for weakness in score_obj.weaknesses:
                    recommendations.append(f"[{criterion.capitalize()}] Address: {weakness}")
        
        return recommendations if recommendations else ["No major revisions identified"]
    
    def _estimate_priority(self, overall_score: int) -> float:
        """Estimate priority score/percentile based on overall impact."""
        # Rough mapping of scores to percentiles
        # In reality, this depends heavily on study section and payline
        percentile_map = {
            1: 2.0, 2: 5.0, 3: 10.0, 4: 20.0, 5: 35.0,
            6: 50.0, 7: 70.0, 8: 85.0, 9: 95.0
        }
        return percentile_map.get(overall_score, 50.0)
    
    def compare_versions(
        self,
        original_result: ReviewResult,
        revised_result: ReviewResult
    ) -> str:
        """Compare two versions of a proposal and report improvements."""
        lines = [
            "=" * 70,
            "PROPOSAL COMPARISON REPORT",
            "=" * 70,
            f"\nOriginal Overall Impact: {original_result.overall_impact}",
            f"Revised Overall Impact: {revised_result.overall_impact}",
        ]
        
        score_change = original_result.overall_impact - revised_result.overall_impact
        if score_change > 0:
            lines.append(f"\n✓ Score improved by {score_change} points!")
        elif score_change < 0:
            lines.append(f"\n⚠ Score declined by {abs(score_change)} points")
        else:
            lines.append("\n→ No change in overall score")
        
        lines.append("\n" + "-" * 70)
        lines.append("CRITERION-LEVEL CHANGES:")
        lines.append("-" * 70)
        
        for crit in original_result.criterion_scores:
            if crit in revised_result.criterion_scores:
                orig = original_result.criterion_scores[crit].score
                rev = revised_result.criterion_scores[crit].score
                change = orig - rev
                if change != 0:
                    direction = "↑" if change > 0 else "↓"
                    lines.append(f"  {crit.capitalize():20s}: {orig} → {rev} ({direction}{abs(change)})")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Grant Mock Reviewer - NIH Study Section Simulator"
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Path to proposal file (PDF, DOCX, TXT, MD)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["pdf", "docx", "txt", "md"],
        help="Input file format"
    )
    parser.add_argument(
        "--section", "-s",
        choices=["full", "aims", "significance", "innovation", "approach"],
        default="full",
        help="Section to review"
    )
    parser.add_argument(
        "--grant-type", "-g",
        choices=["R01", "R21", "R03", "K99", "F32"],
        default="R01",
        help="Grant mechanism"
    )
    parser.add_argument(
        "--focus",
        choices=["significance", "investigator", "innovation", "approach", "environment"],
        help="Focus on specific criterion"
    )
    parser.add_argument(
        "--scores-only",
        action="store_true",
        help="Output scores only (JSON format)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    parser.add_argument(
        "--original",
        help="Original proposal for comparison mode"
    )
    parser.add_argument(
        "--revised",
        help="Revised proposal for comparison mode"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Enable comparison mode"
    )
    
    return parser.parse_args()


def read_file(filepath: str, fmt: Optional[str] = None) -> str:
    """Read content from various file formats."""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Detect format from extension if not specified
    if fmt is None:
        fmt = path.suffix.lower().lstrip('.')
    
    if fmt == 'txt' or fmt == 'md':
        return path.read_text(encoding='utf-8')
    elif fmt == 'pdf':
        # Would require PyPDF2 or similar in production
        return f"[PDF extraction not implemented - would extract text from {filepath}]"
    elif fmt == 'docx':
        # Would require python-docx in production
        return f"[DOCX extraction not implemented - would extract text from {filepath}]"
    else:
        return path.read_text(encoding='utf-8')


def main():
    """Main entry point."""
    args = parse_args()
    
    reviewer = GrantMockReviewer()
    
    # Comparison mode
    if args.compare or (args.original and args.revised):
        if not args.original or not args.revised:
            print("Error: --compare mode requires both --original and --revised files")
            sys.exit(1)
        
        orig_text = read_file(args.original, args.format)
        rev_text = read_file(args.revised, args.format)
        
        orig_result = reviewer.review(orig_text, args.grant_type, args.section, args.focus)
        rev_result = reviewer.review(rev_text, args.grant_type, args.section, args.focus)
        
        output = reviewer.compare_versions(orig_result, rev_result)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"Comparison report written to: {args.output}")
        else:
            print(output)
        return
    
    # Standard review mode
    if not args.input:
        print("Error: --input required (or use --compare mode)")
        sys.exit(1)
    
    proposal_text = read_file(args.input, args.format)
    
    result = reviewer.review(
        proposal_text,
        args.grant_type,
        args.section,
        args.focus
    )
    
    if args.scores_only:
        output = json.dumps({
            "overall_impact": result.overall_impact,
            "priority_score": result.priority_score,
            "criteria": {
                k: {"score": v.score, "strengths": v.strengths, "weaknesses": v.weaknesses}
                for k, v in result.criterion_scores.items()
            }
        }, indent=2)
    else:
        output = result.summary_statement
        output += "\n\n" + "=" * 70 + "\n"
        output += "REVISION RECOMMENDATIONS:\n"
        output += "=" * 70 + "\n"
        for i, rec in enumerate(result.revision_recommendations, 1):
            output += f"{i}. {rec}\n"
    
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Review written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()

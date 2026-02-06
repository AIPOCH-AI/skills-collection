#!/usr/bin/env python3
"""
EHR Semantic Compressor
AI-powered EHR summarization using Transformer architecture
Version: 1.0.0
"""

import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configuration
REFERENCE_DIR = Path(__file__).parent.parent / "references"

# Default parameters
DEFAULT_MAX_LENGTH = 300
DEFAULT_MIN_INPUT_LENGTH = 100
SECTION_KEYWORDS = {
    "allergies": ["allergy", "allergic", "reaction", "hypersensitivity", "intolerance"],
    "medications": ["medication", "medicine", "drug", "prescription", "dose", "mg", "tablet"],
    "diagnoses": ["diagnosis", "diagnosed", "condition", "disease", "disorder", "syndrome"],
    "family_history": ["family history", "mother", "father", "sibling", "genetic", "hereditary"],
    "procedures": ["procedure", "surgery", "operation", "treatment", "therapy"],
    "vitals": ["blood pressure", "heart rate", "temperature", "respiratory", "bp", "hr"]
}


def validate_input(data: dict) -> Tuple[bool, str]:
    """
    Validate input parameters.
    
    Args:
        data: Input dictionary
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Input must be a JSON object"
    
    if "ehr_text" not in data:
        return False, "Missing required field: ehr_text"
    
    ehr_text = data.get("ehr_text", "")
    if not isinstance(ehr_text, str):
        return False, "ehr_text must be a string"
    
    if len(ehr_text.strip()) == 0:
        return False, "EHR text is empty"
    
    word_count = len(ehr_text.split())
    if word_count < DEFAULT_MIN_INPUT_LENGTH:
        return False, f"EHR text is too short ({word_count} words). Minimum required: {DEFAULT_MIN_INPUT_LENGTH} words"
    
    # Validate extract_sections if provided
    if "extract_sections" in data:
        sections = data["extract_sections"]
        if not isinstance(sections, list):
            return False, "extract_sections must be an array"
        valid_sections = set(SECTION_KEYWORDS.keys())
        invalid = [s for s in sections if s not in valid_sections]
        if invalid:
            return False, f"Invalid sections: {invalid}. Valid options: {list(valid_sections)}"
    
    # Validate max_length if provided
    if "max_length" in data:
        max_len = data["max_length"]
        if not isinstance(max_len, int) or max_len < 50 or max_len > 1000:
            return False, "max_length must be an integer between 50 and 1000"
    
    return True, ""


def segment_text(text: str, max_segment_words: int = 512) -> List[str]:
    """
    Segment long text into manageable chunks.
    
    Args:
        text: Input text
        max_segment_words: Maximum words per segment
        
    Returns:
        List of text segments
    """
    if not text or not text.strip():
        return []
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    segments = []
    current_segment = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        
        if current_word_count + sentence_word_count > max_segment_words and current_segment:
            segments.append(" ".join(current_segment))
            current_segment = [sentence]
            current_word_count = sentence_word_count
        else:
            current_segment.append(sentence)
            current_word_count += sentence_word_count
    
    if current_segment:
        segments.append(" ".join(current_segment))
    
    return segments


def extract_sentences_with_keywords(text: str, keywords: List[str], max_items: int = 10) -> List[str]:
    """
    Extract sentences containing specific keywords.
    
    Args:
        text: Source text
        keywords: Keywords to search for
        max_items: Maximum items to return
        
    Returns:
        List of matching sentences
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    matches = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword.lower() in sentence_lower for keyword in keywords):
            # Clean and truncate
            clean = sentence.strip()
            if len(clean) > 10:
                matches.append(clean)
        
        if len(matches) >= max_items:
            break
    
    return matches


def extract_section(text: str, section_name: str) -> List[str]:
    """
    Extract specific section from EHR text.
    
    Args:
        text: EHR text
        section_name: Name of section to extract
        
    Returns:
        List of extracted items
    """
    keywords = SECTION_KEYWORDS.get(section_name, [])
    if not keywords:
        return []
    
    return extract_sentences_with_keywords(text, keywords, max_items=8)


def generate_summary(text: str, max_length: int = 300) -> str:
    """
    Generate extractive summary using frequency-based sentence scoring.
    
    Args:
        text: Input EHR text
        max_length: Target summary length in words
        
    Returns:
        Generated summary
    """
    # Segment text
    segments = segment_text(text, max_segment_words=512)
    
    if not segments:
        return text[:500] + "..." if len(text) > 500 else text
    
    # For each segment, extract key sentences
    key_sentences = []
    
    for segment in segments:
        sentences = re.split(r'(?<=[.!?])\s+', segment)
        
        # Score sentences based on clinical relevance
        scored_sentences = []
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Boost score for clinical keywords
            clinical_indicators = [
                "diagnosed", "diagnosis", "treatment", "medication", "allergy",
                "history", "family", "surgery", "procedure", "condition",
                "prescribed", "adverse", "reaction", "chronic", "acute"
            ]
            
            for indicator in clinical_indicators:
                if indicator in sentence_lower:
                    score += 2
            
            # Boost for numerical data (labs, vitals)
            if re.search(r'\d+\s*(mg|ml|mmHg|bpm|mmol)', sentence_lower):
                score += 3
            
            # Penalize very short sentences
            word_count = len(sentence.split())
            if word_count < 5:
                score -= 2
            
            scored_sentences.append((sentence, score, word_count))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select sentences to meet target length
        selected = []
        current_words = 0
        
        for sentence, score, word_count in scored_sentences:
            if current_words + word_count <= max_length * 2 // len(segments):
                selected.append(sentence)
                current_words += word_count
            
            if current_words >= max_length // len(segments):
                break
        
        key_sentences.extend(selected)
    
    # Reorder sentences by original position for coherence
    original_order = []
    for sentence in key_sentences:
        pos = text.find(sentence)
        if pos >= 0:
            original_order.append((pos, sentence))
    
    original_order.sort(key=lambda x: x[0])
    ordered_sentences = [s for _, s in original_order]
    
    # Format as bullet points
    bullet_points = []
    for sentence in ordered_sentences[:15]:  # Max 15 bullets
        # Clean and format
        clean = sentence.strip()
        if clean and len(clean) > 10:
            # Capitalize first letter
            clean = clean[0].upper() + clean[1:] if len(clean) > 1 else clean.upper()
            bullet_points.append(f"• {clean}")
    
    summary = "\n".join(bullet_points)
    
    # Ensure summary length is within bounds
    summary_words = summary.split()
    if len(summary_words) > max_length:
        summary = " ".join(summary_words[:max_length])
        summary = summary.rsplit("•", 1)[0] + "..."
    
    return summary


def process_ehr(data: dict) -> dict:
    """
    Main EHR processing logic.
    
    Args:
        data: Input data dictionary with ehr_text and options
        
    Returns:
        Processed result dictionary
    """
    ehr_text = data["ehr_text"]
    max_length = data.get("max_length", DEFAULT_MAX_LENGTH)
    extract_sections = data.get("extract_sections", list(SECTION_KEYWORDS.keys()))
    
    # Generate summary
    summary = generate_summary(ehr_text, max_length)
    
    # Extract sections
    extracted_sections = {}
    for section in extract_sections:
        items = extract_section(ehr_text, section)
        if items:
            extracted_sections[section] = items
    
    # Calculate metrics
    original_word_count = len(ehr_text.split())
    summary_word_count = len(summary.split())
    compression_ratio = 1 - (summary_word_count / original_word_count) if original_word_count > 0 else 0
    
    result = {
        "summary": summary,
        "extracted_sections": extracted_sections,
        "metadata": {
            "original_length": original_word_count,
            "summary_length": summary_word_count,
            "compression_ratio": round(compression_ratio, 2),
            "sections_extracted": list(extracted_sections.keys()),
            "processed_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    return result


def format_output(result: dict, success: bool = True) -> dict:
    """
    Format output in standard structure.
    
    Args:
        result: Processing result
        success: Whether processing was successful
        
    Returns:
        Formatted output dictionary
    """
    if success:
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0"
            }
        }
    else:
        return {
            "status": "error",
            "error": {
                "type": "processing_error",
                "message": str(result),
                "suggestion": "Please check input parameters and try again"
            }
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EHR Semantic Compressor - AI-powered EHR summarization"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input JSON string or file path"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help=f"Maximum summary length in words (default: {DEFAULT_MAX_LENGTH})"
    )
    
    args = parser.parse_args()
    
    try:
        # Parse input
        if args.input:
            input_path = Path(args.input)
            if input_path.exists():
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
            else:
                input_data = json.loads(args.input)
        else:
            # Read from stdin
            input_text = sys.stdin.read()
            if not input_text.strip():
                raise ValueError("No input provided via stdin")
            input_data = json.loads(input_text)
        
        # Validate input
        is_valid, error_msg = validate_input(input_data)
        if not is_valid:
            output = {
                "status": "error",
                "error": {
                    "type": "input_validation_error",
                    "message": error_msg,
                    "suggestion": "Please provide valid EHR text with at least 100 words"
                }
            }
        else:
            # Apply command-line overrides
            if args.max_length != DEFAULT_MAX_LENGTH:
                input_data["max_length"] = args.max_length
            
            # Process EHR
            result = process_ehr(input_data)
            output = format_output(result, success=True)
        
        # Output result
        output_json = json.dumps(output, indent=2, ensure_ascii=False)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"Output written to: {args.output}")
        else:
            print(output_json)
        
        # Exit with appropriate code
        sys.exit(0 if output["status"] == "success" else 1)
        
    except json.JSONDecodeError as e:
        error_output = {
            "status": "error",
            "error": {
                "type": "json_decode_error",
                "message": "Invalid JSON input format",
                "suggestion": "Please provide valid JSON input with proper syntax"
            }
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)
        
    except FileNotFoundError as e:
        error_output = {
            "status": "error",
            "error": {
                "type": "file_not_found",
                "message": f"Input file not found: {args.input}",
                "suggestion": "Please verify the file path exists"
            }
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)
        
    except Exception as e:
        # Convert to semantic error (no stack trace)
        error_output = {
            "status": "error",
            "error": {
                "type": "processing_error",
                "message": "An error occurred during EHR processing",
                "suggestion": "Please check input format and try again"
            }
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()

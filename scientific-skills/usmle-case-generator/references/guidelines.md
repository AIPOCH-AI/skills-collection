# USMLE Case Generator Guidelines

## Purpose
This skill generates realistic USMLE Step 1 and Step 2 style clinical case scenarios for medical education and exam preparation.

## Supported Medical Specialties

### Core Specialties
1. **Cardiology** - Heart failure, MI, arrhythmias
2. **Neurology** - Stroke, seizure, headache
3. **Gastroenterology** - Pancreatitis, liver disease, IBD
4. **Pulmonology** - COPD, asthma, pneumonia
5. **Nephrology** - AKI, CKD, electrolyte disorders
6. **Endocrinology** - DKA, thyroid disorders, adrenal disease
7. **Hematology** - Anemia, coagulopathies
8. **Infectious Disease** - Pneumonia, sepsis, endocarditis
9. **Rheumatology** - RA, SLE, vasculitis
10. **Emergency Medicine** - Anaphylaxis, trauma, toxicology

## Case Structure

### 1. Patient Vignette
- Chief complaint
- History of present illness
- Past medical history
- Medications
- Physical examination findings
- Vital signs
- Diagnostic studies

### 2. Multiple-Choice Question
- Single best answer format
- 5 options (A-E)
- Clinical scenario-based
- Tests high-yield concepts

### 3. Explanation
- Detailed rationale for correct answer
- Why distractors are incorrect
- Key learning objectives
- High-yield takeaways

## Difficulty Levels

### Step 1 (Basic Science)
- Focus on pathophysiology
- Mechanism-based questions
- Laboratory interpretation
- Basic pharmacology

### Step 2 (Clinical Knowledge)
- Focus on diagnosis and management
- Next best step questions
- Treatment algorithms
- Prognosis and complications

## Usage Guidelines

### Generating Cases
```python
from scripts.main import generate_case

# Random case
case = generate_case()

# Specific specialty
case = generate_case(specialty="Cardiology")

# Specific difficulty
case = generate_case(difficulty="Step 2")

# Combined
case = generate_case(specialty="Neurology", difficulty="Step 2")
```

### Command Line
```bash
# Random case
python scripts/main.py

# Specific specialty
python scripts/main.py --specialty Cardiology

# Specific difficulty
python scripts/main.py --difficulty "Step 2"

# Save to file
python scripts/main.py --specialty Neurology --output case.json
```

## Case Template Format

Each case template includes:
- Template identifier
- Chief complaint
- History template with placeholders
- Physical examination findings
- Vital signs template
- Diagnostic studies template
- Question stem
- Options array (5 items)
- Correct answer letter
- Detailed explanation
- Learning objectives array

## Educational Use Only
Cases are generated for educational purposes and should not replace clinical judgment or actual medical advice.

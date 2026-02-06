# Medical Referral Letter Generator - Quick Reference

## Installation

```bash
pip install reportlab python-docx
```

## Usage Examples

### Generate from JSON file
```bash
python scripts/main.py --input patient_data.json --output referral.pdf
```

### Generate sample letter
```bash
python scripts/main.py --sample --output sample_referral.pdf --format pdf
```

### Generate HTML version
```bash
python scripts/main.py --input data.json --format html --output letter.html
```

## Output Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| PDF | .pdf | Professional distribution, printing |
| DOCX | .docx | Editing, EHR integration |
| HTML | .html | Email, web viewing |
| TXT | .txt | Quick preview, plain text systems |

## Input JSON Structure

See `input_template.json` for complete field reference.

### Required Fields
- `patient.name`
- `patient.date_of_birth`
- `patient.patient_id`
- `reason_for_referral`
- `primary_diagnosis`
- `referring_provider.name`
- `receiving_provider.name`

### Optional Fields
- `relevant_history`
- `current_medications`
- `allergies`
- `vital_signs`
- `lab_results`
- `urgency` (Routine/Urgent/Emergent)
- `additional_notes`

## Python API Usage

```python
from scripts.main import ReferralLetterGenerator, ReferralData, PatientData, ProviderInfo

generator = ReferralLetterGenerator()

# Create data objects
patient = PatientData(
    name="John Doe",
    date_of_birth="1970-01-01",
    patient_id="MRN12345"
)

referring = ProviderInfo(name="Dr. Smith", title="Internal Medicine")
receiving = ProviderInfo(name="Dr. Jones", title="Cardiology")

data = ReferralData(
    patient=patient,
    referring_provider=referring,
    receiving_provider=receiving,
    reason_for_referral="Chest pain evaluation",
    primary_diagnosis="Suspected CAD"
)

# Generate PDF
generator.generate(data, OutputFormat.PDF, "referral.pdf")
```

---
name: bmi-bsa-calculator
description: Calculate Body Mass Index (BMI) and Body Surface Area (BSA) for clinical 
  assessment and drug dosing. Supports multiple BSA formulas (DuBois, Mosteller, Haycock) 
  and provides weight category classification with pediatric and adult norms.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# BMI & BSA Calculator

## Overview

Clinical calculator for anthropometric measurements used in health assessment, obesity screening, and chemotherapy dosing calculations.

**Key Capabilities:**
- **BMI Calculation**: Standard and adjusted BMI formulas
- **BSA Estimation**: Multiple validated formulas (DuBois, Mosteller, Haycock)
- **Weight Classification**: WHO and CDC category assignment
- **Dosing Support**: Chemotherapy and medication dose calculations
- **Pediatric Support**: Age-appropriate norms and calculations
- **Unit Flexibility**: Metric and imperial input support

## When to Use

**✅ Use this skill when:**
- Calculating chemotherapy doses requiring BSA (mg/m²)
- Screening for obesity or underweight in clinical practice
- Adjusting drug doses based on body composition
- Documenting baseline anthropometrics in patient charts
- Teaching medical students clinical calculations
- Quick assessment in resource-limited settings

**❌ Do NOT use when:**
- BMI alone for clinical diagnosis → Use comprehensive metabolic assessment
- Pregnancy weight assessment → Use gestational weight gain charts
- Pediatric growth evaluation → Use WHO/CDC growth charts with percentiles
- Body composition analysis → Use DEXA or bioimpedance
- Athletic/muscular patients → Consider body fat % instead of BMI

**Integration:**
- **Upstream**: `ehr-semantic-compressor` (patient data extraction), `automated-soap-note-generator` (vital signs)
- **Downstream**: `drug-interaction-checker` (dose calculation), `medication-reconciliation` (dosing verification)

## Core Capabilities

### 1. BMI Calculation

Calculate Body Mass Index with classification:

```python
from scripts.calculator import BMIBSACalculator

calc = BMIBSACalculator()

# Calculate BMI
result = calc.calculate_bmi(
    weight_kg=70,
    height_cm=175,
    age=45,
    sex="male"
)

print(f"BMI: {result.bmi:.1f} kg/m²")
print(f"Category: {result.category}")  # Normal weight
print(f"Ideal weight range: {result.ideal_weight_range}")
```

**BMI Categories (WHO):**
| Category | BMI Range | Clinical Significance |
|----------|-----------|---------------------|
| **Underweight** | < 18.5 | Malnutrition risk |
| **Normal** | 18.5 - 24.9 | Healthy range |
| **Overweight** | 25.0 - 29.9 | Increased risk |
| **Obese I** | 30.0 - 34.9 | High risk |
| **Obese II** | 35.0 - 39.9 | Very high risk |
| **Obese III** | ≥ 40.0 | Extremely high risk |

**Adjusted BMI:**
- **BMI Prime**: BMI / 25 (obesity severity index)
- **Ponderal Index**: BMI for tall/short individuals
- **Age-adjusted**: For elderly patients (>65)

### 2. BSA Calculation

Multiple formulas for different clinical scenarios:

```python
# Calculate BSA using different formulas
bsa_results = calc.calculate_bsa(
    weight_kg=70,
    height_cm=175,
    formulas=["dubois", "mosteller", "haycock", "gehan_george"]
)

for formula, bsa in bsa_results.items():
    print(f"{formula}: {bsa:.2f} m²")
```

**BSA Formulas:**
| Formula | Equation | Best For |
|---------|----------|----------|
| **DuBois** | 0.007184 × W^0.425 × H^0.725 | Adults (most common) |
| **Mosteller** | √(W × H / 3600) | Adults (simplified) |
| **Haycock** | 0.024265 × W^0.5378 × H^0.3964 | Pediatrics |
| **Gehan-George** | 0.0235 × W^0.51456 × H^0.42246 | Oncology |
| **Yu** | 0.015925 × W^0.5 × H^0.5 | Asian populations |

### 3. Drug Dosing Calculations

Apply BSA to medication dosing:

```python
# Calculate chemotherapy dose
dose = calc.calculate_dose(
    bsa=bsa_results["dubois"],
    drug="carboplatin",
    dose_per_m2=400,  # mg/m²
    max_dose=800  # mg cap
)

print(f"Calculated dose: {dose:.0f} mg")
print(f"BSA used: {bsa_results['dubois']:.2f} m²")
```

**Common BSA-Based Doses:**
- Carboplatin: AUC-based (Calvert formula)
- 5-FU: 400-600 mg/m²
- Doxorubicin: 60-75 mg/m² (lifetime max 450-550 mg/m²)
- Paclitaxel: 135-175 mg/m²

### 4. Pediatric Calculations

Age-appropriate calculations for children:

```python
pediatric = calc.pediatric_mode(
    weight_kg=25,
    height_cm=120,
    age_years=8,
    sex="female"
)

print(f"BMI-for-age percentile: {pediatric.bmi_percentile}%")
print(f"Weight status: {pediatric.weight_status}")
print(f"BSA (Haycock): {pediatric.bsa:.2f} m²")
```

**Pediatric Considerations:**
- BMI percentiles (not absolute values)
- Growth chart integration
- Age-specific BSA formulas
- Body composition changes with development

## Common Patterns

### Pattern 1: Chemotherapy Dosing

**Scenario**: Calculate carboplatin dose for cancer patient.

```bash
# Calculate BSA and dose
python scripts/main.py \
  --weight 70 \
  --height 175 \
  --drug carboplatin \
  --target-auc 5 \
  --creatinine-clearance 80 \
  --output dose_calculation.txt
```

**Output:**
```
BSA (DuBois): 1.79 m²
Calvert Formula: Dose = Target AUC × (GFR + 25)
                 = 5 × (80 + 25)
                 = 525 mg
Maximum dose check: 525 mg ≤ 800 mg ✓
Recommended dose: 525 mg
```

### Pattern 2: Obesity Screening

**Scenario**: BMI assessment for weight management clinic.

```python
# BMI with full assessment
assessment = calc.assess_bmi(
    weight_kg=95,
    height_cm=165,
    age=52,
    sex="female",
    waist_cm=98
)

print(f"BMI: {assessment.bmi:.1f} (Obese Class II)")
print(f"Waist-to-height ratio: {assessment.whtr:.2f} (High risk)")
print(f"Comorbidity risk: {assessment.health_risk}")
print(f"Recommended: {assessment.recommendations}")
```

### Pattern 3: Pediatric Growth Assessment

**Scenario**: Calculate child's BSA for medication dosing.

```python
# Pediatric dosing
child = calc.pediatric_assessment(
    weight_kg=20,
    height_cm=110,
    age_years=6,
    sex="male"
)

print(f"BSA: {child.bsa:.2f} m² (Haycock formula)")
print(f"BMI percentile: {child.bmi_percentile}th")
print(f"Doxorubicin dose: {child.bsa * 60:.0f} mg")
```

### Pattern 4: Rapid Clinical Assessment

**Scenario**: Quick BMI/BSA for admission vital signs.

```bash
# Quick calculation
python scripts/main.py --weight 80 --height 180 --quick

# Output:
# BMI: 24.7 kg/m² (Normal)
# BSA: 2.00 m² (DuBois)
# Ideal weight: 65-80 kg
```

## Complete Workflow Example

**Comprehensive patient assessment:**

```python
from scripts.calculator import BMIBSACalculator
from scripts.reports import ClinicalReport

# Initialize
calc = BMIBSACalculator()
report = ClinicalReport()

# Patient data
patient = {
    "weight_kg": 75,
    "height_cm": 170,
    "age": 55,
    "sex": "female",
    "waist_cm": 88
}

# Calculate all metrics
bmi = calc.calculate_bmi(**patient)
bsa = calc.calculate_bsa(**patient, formula="dubois")
assessment = calc.comprehensive_assessment(**patient)

# Generate report
report_data = {
    "bmi": bmi,
    "bsa": bsa,
    "assessment": assessment,
    "recommendations": assessment.recommendations
}

report.generate(report_data, output="patient_assessment.pdf")
```

## Quality Checklist

**Input Validation:**
- [ ] Weight realistic (2-300 kg range)
- [ ] Height realistic (50-250 cm range)
- [ ] Units clearly specified (kg/lbs, cm/in)
- [ ] Age appropriate for formulas used

**Calculation Accuracy:**
- [ ] Formula selection appropriate for patient
- [ ] BSA formula matches clinical context
- [ ] Pediatric vs. adult norms correctly applied
- [ ] Rounding appropriate (1-2 decimal places)

**Clinical Interpretation:**
- [ ] **CRITICAL**: BMI is screening tool, not diagnostic
- [ ] Ethnicity-specific cutoffs considered
- [ ] Muscle mass considered (athletes)
- [ ] Age adjustments applied (elderly/children)

**Documentation:**
- [ ] Formula used documented (DuBois vs. Mosteller)
- [ ] Units clearly stated
- [ ] Date of calculation recorded
- [ ] Dose limits verified for chemotherapy

## Common Pitfalls

**Calculation Errors:**
- ❌ **Unit confusion** → Pounds vs. kg, inches vs. cm
  - ✅ Always verify units; convert if necessary

- ❌ **Wrong formula** → Using adult BSA for infants
  - ✅ Use Haycock for children < 12 years

- ❌ **BMI over-interpretation** → Diagnosing based on BMI alone
  - ✅ BMI is screening tool; clinical correlation required

**Clinical Misuse:**
- ❌ **Athletes misclassified** → Muscular patients marked obese
  - ✅ Consider waist circumference or body fat %

- ❌ **Elderly inappropriate norms** → Same cutoffs for all ages
  - ✅ Use age-adjusted BMI for >65 years

- ❌ **Ignoring ethnicity** → Universal cutoffs applied
  - ✅ Asian populations: lower obesity thresholds

**Dosing Errors:**
- ❌ **BSA rounding** → 1.79 m² rounded to 1.8 m²
  - ✅ Use precise values for chemotherapy

- ❌ **Max dose ignored** → Exceeding lifetime limits
  - ✅ Always check cumulative doses (doxorubicin)

## References

Available in `references/` directory:

- `bsa_formulas_comparison.md` - Formula accuracy by population
- `pediatric_norms.md` - Growth charts and percentiles
- `chemotherapy_dosing.md` - BSA-based drug calculations
- `ethnic_adjustments.md` - Population-specific cutoffs
- `calculator_validation.md` - Comparison with reference standards

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI calculator interface
- `calculator.py` - Core BMI/BSA calculations
- `formulas.py` - Multiple BSA formula implementations
- `pediatric.py` - Child-specific calculations
- `dosing.py` - Medication dose calculations
- `reports.py` - Clinical report generation

## Limitations

- **BMI Limitations**: Doesn't distinguish fat from muscle; varies by ethnicity
- **BSA Estimation**: All formulas are approximations; 10-15% variation normal
- **Extreme Values**: Very short/tall patients may have inaccurate estimates
- **Not for Diagnosis**: BMI/BSA are tools, not clinical diagnoses
- **Amputees**: Standard formulas inaccurate; adjustment needed
- **Pregnancy**: Special considerations not included

---

**⚕️ Clinical Note: BMI and BSA are screening and calculation tools, not substitutes for clinical judgment. Always correlate with physical examination, patient history, and other assessments. Double-check all chemotherapy calculations independently.**

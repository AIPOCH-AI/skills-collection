#!/usr/bin/env python3
"""
USMLE Case Generator
Generates Step 1/2 style clinical cases for medical education.
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path


class USMLECaseGenerator:
    """Generator for USMLE-style clinical cases."""
    
    def __init__(self):
        self.case_templates = self._load_case_templates()
        self.vital_signs = self._load_vital_signs()
        self.lab_ranges = self._load_lab_ranges()
        self.demographics = self._load_demographics()
        
    def _load_case_templates(self):
        """Load case structure templates."""
        return {
            "step1": {
                "focus": "pathophysiology, mechanism, basic science",
                "question_type": "What is the most likely mechanism/pathogen/findings?",
                "style": "basic_science_focused"
            },
            "step2": {
                "focus": "diagnosis, management, next best step",
                "question_type": "What is the most likely diagnosis/next step/best initial test?",
                "style": "clinical_focused"
            }
        }
    
    def _load_vital_signs(self):
        """Load vital sign abnormalities by condition."""
        return {
            "normal": {"temp": "98.6°F", "hr": "72 bpm", "bp": "120/80 mmHg", "rr": "16/min", "o2": "98%"},
            "fever": {"temp": "101.5°F", "hr": "95 bpm", "bp": "118/75 mmHg", "rr": "18/min", "o2": "97%"},
            "shock": {"temp": "97.2°F", "hr": "120 bpm", "bp": "85/50 mmHg", "rr": "24/min", "o2": "92%"},
            "hypertensive": {"temp": "98.8°F", "hr": "78 bpm", "bp": "175/105 mmHg", "rr": "16/min", "o2": "98%"},
            "tachycardic": {"temp": "99.1°F", "hr": "115 bpm", "bp": "125/82 mmHg", "rr": "20/min", "o2": "96%"},
        }
    
    def _load_lab_ranges(self):
        """Load normal and abnormal lab values."""
        return {
            "normal": {
                "wbc": "7,500/μL",
                "hgb": "14.0 g/dL",
                "plt": "250,000/μL",
                "na": "140 mEq/L",
                "k": "4.0 mEq/L",
                "cl": "100 mEq/L",
                "co2": "24 mEq/L",
                "bun": "15 mg/dL",
                "cr": "1.0 mg/dL",
                "glucose": "90 mg/dL",
                "ph": "7.40"
            },
            "leukocytosis": {"wbc": "15,000/μL"},
            "anemia": {"hgb": "8.5 g/dL"},
            "thrombocytopenia": {"plt": "80,000/μL"},
            "hyponatremia": {"na": "128 mEq/L"},
            "hyperkalemia": {"k": "5.8 mEq/L"},
            "hypokalemia": {"k": "2.8 mEq/L"},
            "azotemia": {"bun": "45 mg/dL", "cr": "2.5 mg/dL"},
            "hyperglycemia": {"glucose": "320 mg/dL"},
            "metabolic_acidosis": {"ph": "7.28", "co2": "18 mEq/L"},
        }
    
    def _load_demographics(self):
        """Load patient demographic options."""
        return {
            "adult_male": {"age_range": (25, 75), "gender": "male"},
            "adult_female": {"age_range": (25, 75), "gender": "female"},
            "elderly_male": {"age_range": (65, 85), "gender": "male"},
            "elderly_female": {"age_range": (65, 85), "gender": "female"},
            "young_adult_male": {"age_range": (18, 35), "gender": "male"},
            "young_adult_female": {"age_range": (18, 35), "gender": "female"},
            "child": {"age_range": (5, 12), "gender": "any"},
            "adolescent": {"age_range": (13, 17), "gender": "any"},
        }
    
    def get_condition_database(self):
        """Get database of medical conditions for case generation."""
        return {
            "cardiology": [
                {
                    "name": "Acute Myocardial Infarction",
                    "step": 2,
                    "demographics": "elderly_male",
                    "chief_complaint": "Chest pain",
                    "hpi": "A {age}-year-old {gender} presents with crushing substernal chest pain radiating to the left arm and jaw, onset 2 hours ago at rest. Associated with diaphoresis, nausea, and shortness of breath.",
                    "vitals": "tachycardic",
                    "pe_findings": "Diaphoretic, anxious. Heart: tachycardic, regular rhythm. Lungs: clear bilaterally.",
                    "ecg": "ST-segment elevation in leads II, III, and aVF",
                    "troponin": "Elevated",
                    "labs": "normal",
                    "question": "What is the most appropriate next step in management?",
                    "options": [
                        "A. Administer aspirin and obtain cardiac enzymes in 6 hours",
                        "B. Give nitroglycerin and discharge home if pain resolves",
                        "C. Start heparin and arrange for emergent cardiac catheterization",
                        "D. Perform CT pulmonary angiography to rule out PE",
                        "E. Order stress echocardiography as outpatient"
                    ],
                    "correct": "C",
                    "explanation": "This patient presents with STEMI (ST-elevation MI) based on ST elevations in inferior leads (II, III, aVF). The standard of care is emergent reperfusion therapy - primary PCI (percutaneous coronary intervention) is preferred if available within 90 minutes. Heparin anticoagulation is initiated while awaiting catheterization.",
                    "learning_objectives": ["STEMI diagnosis", "Emergent reperfusion therapy", "Primary PCI indications"]
                },
                {
                    "name": "Atrial Fibrillation",
                    "step": 2,
                    "demographics": "elderly_male",
                    "chief_complaint": "Palpitations",
                    "hpi": "A {age}-year-old {gender} with history of hypertension presents with sudden onset irregular heartbeat and palpitations for 3 days. Denies chest pain but reports mild dyspnea on exertion.",
                    "vitals": "tachycardic",
                    "pe_findings": "Irregularly irregular pulse. Heart rate approximately 110 bpm. No murmurs.",
                    "ecg": "Irregularly irregular rhythm, no discernible P waves, narrow QRS complexes",
                    "labs": "normal",
                    "question": "What is the most appropriate next step in management?",
                    "options": [
                        "A. Immediate synchronized cardioversion",
                        "B. Rate control with beta-blocker and anticoagulation assessment",
                        "C. Start aspirin daily",
                        "D. Schedule outpatient Holter monitor",
                        "E. Initiate amiodarone for rhythm control"
                    ],
                    "correct": "B",
                    "explanation": "For hemodynamically stable atrial fibrillation (>48 hours duration), the first step is rate control (beta-blocker or calcium channel blocker) and assessment for anticoagulation using CHA2DS2-VASc score. Cardioversion without anticoagulation or TEE increases stroke risk.",
                    "learning_objectives": ["AFib management", "Rate vs rhythm control", "CHA2DS2-VASc score"]
                },
                {
                    "name": "Heart Failure Exacerbation",
                    "step": 2,
                    "demographics": "elderly_female",
                    "chief_complaint": "Shortness of breath",
                    "hpi": "A {age}-year-old {gender} with known heart failure presents with worsening dyspnea over 3 days, orthopnea, and bilateral leg swelling. Non-compliant with sodium restriction and medications.",
                    "vitals": "tachycardic",
                    "pe_findings": "Jugular venous distention to jaw at 45 degrees. Bilateral crackles in lung bases. 2+ pitting edema in bilateral lower extremities.",
                    "cxr": "Cardiomegaly, pulmonary edema, pleural effusions",
                    "bnp": "Elevated",
                    "labs": "normal",
                    "question": "What is the most appropriate initial therapy?",
                    "options": [
                        "A. Start ACE inhibitor and beta-blocker immediately",
                        "B. IV loop diuretics and supplemental oxygen",
                        "C. Emergent hemodialysis",
                        "D. High-dose aspirin therapy",
                        "E. Immediate cardiac catheterization"
                    ],
                    "correct": "B",
                    "explanation": "This patient presents with acute decompensated heart failure with volume overload. The initial management focuses on diuresis (IV loop diuretics) to relieve congestion and supplemental oxygen for hypoxemia. ACE inhibitors and beta-blockers are important chronic therapies but not for acute decompensation.",
                    "learning_objectives": ["Acute heart failure management", "Volume overload treatment", "Diuretic therapy"]
                }
            ],
            "pulmonology": [
                {
                    "name": "Community Acquired Pneumonia",
                    "step": 2,
                    "demographics": "adult_male",
                    "chief_complaint": "Fever and cough",
                    "hpi": "A {age}-year-old {gender} presents with 4 days of productive cough with rust-colored sputum, fever to 102°F, and pleuritic chest pain. Recently had URI symptoms.",
                    "vitals": "fever",
                    "pe_findings": "Decreased breath sounds and dullness to percussion in right lower lobe. Bronchial breath sounds present. Tachycardic.",
                    "cxr": "Right lower lobe consolidation with air bronchograms",
                    "labs": "leukocytosis",
                    "question": "What is the most likely causative organism?",
                    "options": [
                        "A. Pseudomonas aeruginosa",
                        "B. Staphylococcus aureus",
                        "C. Streptococcus pneumoniae",
                        "D. Mycoplasma pneumoniae",
                        "E. Haemophilus influenzae"
                    ],
                    "correct": "C",
                    "explanation": "Streptococcus pneumoniae is the most common cause of community-acquired pneumonia in adults, especially with classic presentation of sudden onset, high fever, productive cough with rust-colored sputum, and lobar consolidation on CXR. CURB-65 score helps determine need for hospitalization.",
                    "learning_objectives": ["CAP microbiology", "S. pneumoniae presentation", "CURB-65 criteria"]
                },
                {
                    "name": "Pulmonary Embolism",
                    "step": 2,
                    "demographics": "adult_female",
                    "chief_complaint": "Sudden dyspnea",
                    "hpi": "A {age}-year-old {gender} presents with sudden onset shortness of breath and pleuritic chest pain. Recently returned from 8-hour flight 2 days ago. History of oral contraceptive use.",
                    "vitals": "tachycardic",
                    "pe_findings": "Tachypneic, using accessory muscles. Clear lung sounds. Right calf swollen and tender.",
                    "ecg": "Sinus tachycardia, S1Q3T3 pattern",
                    "d_dimer": "Elevated",
                    "ctpa": "Filling defect in right pulmonary artery",
                    "question": "What is the most appropriate next diagnostic step?",
                    "options": [
                        "A. Start empiric heparin and obtain CT pulmonary angiography",
                        "B. Order ventilation-perfusion scan",
                        "C. Perform lower extremity Doppler ultrasound",
                        "D. Start warfarin and discharge home",
                        "E. Obtain cardiac catheterization"
                    ],
                    "correct": "A",
                    "explanation": "This patient has high pretest probability for PE (Wells criteria: tachycardia, clinical signs of DVT, immobilization, hemoptysis). The diagnostic test of choice is CT pulmonary angiography (CTPA). Empiric anticoagulation should be started if high suspicion while awaiting imaging.",
                    "learning_objectives": ["PE diagnosis", "Wells criteria", "CTPA as gold standard"]
                },
                {
                    "name": "Asthma Exacerbation",
                    "step": 1,
                    "demographics": "young_adult_female",
                    "chief_complaint": "Wheezing",
                    "hpi": "A {age}-year-old {gender} with asthma presents with worsening wheezing and dyspnea for 2 days after exposure to cat dander. Has required rescue inhaler every 2 hours.",
                    "vitals": "normal",
                    "pe_findings": "Audible wheezing bilaterally. Prolonged expiratory phase. Using accessory muscles.",
                    "pfts": "FEV1/FVC ratio 0.65, increased by 15% after bronchodilator",
                    "question": "What is the mechanism of bronchial hyperresponsiveness in asthma?",
                    "options": [
                        "A. IgE-mediated mast cell degranulation and inflammation",
                        "B. Direct bacterial infection of bronchial epithelium",
                        "C. Autoimmune destruction of alveolar walls",
                        "D. Excessive parasympathetic innervation only",
                        "E. Genetic defect in surfactant production"
                    ],
                    "correct": "A",
                    "explanation": "Asthma is characterized by chronic airway inflammation mediated by type I hypersensitivity (IgE-mediated). Exposure to allergens triggers mast cell degranulation, releasing histamine, leukotrienes, and prostaglandins causing bronchoconstriction, mucus production, and airway edema.",
                    "learning_objectives": ["Asthma pathophysiology", "Type I hypersensitivity", "Mast cell mediators"]
                }
            ],
            "gastroenterology": [
                {
                    "name": "Acute Appendicitis",
                    "step": 2,
                    "demographics": "young_adult_male",
                    "chief_complaint": "Abdominal pain",
                    "hpi": "A {age}-year-old {gender} presents with periumbilical pain that migrated to RLQ over 12 hours. Nausea, vomiting, and anorexia. Low-grade fever.",
                    "vitals": "fever",
                    "pe_findings": "Tenderness at McBurney's point. Positive rebound tenderness and guarding. Rovsing's sign positive.",
                    "wbc": "13,500 with left shift",
                    "ct": "Dilated appendix with wall enhancement and periappendiceal fat stranding",
                    "question": "What is the most appropriate next step?",
                    "options": [
                        "A. Abdominal ultrasound",
                        "B. Emergent laparoscopic appendectomy",
                        "C. IV antibiotics and observation for 24 hours",
                        "D. Colonoscopy",
                        "E. CT chest/abdomen/pelvis with contrast"
                    ],
                    "correct": "B",
                    "explanation": "Acute appendicitis is a surgical emergency. Once diagnosed clinically or confirmed with imaging, the definitive treatment is appendectomy. Delay increases risk of perforation. CT imaging (if obtained) shows the characteristic findings described.",
                    "learning_objectives": ["Appendicitis diagnosis", "Migration of pain", "Surgical management"]
                },
                {
                    "name": "Acute Pancreatitis",
                    "step": 2,
                    "demographics": "adult_male",
                    "chief_complaint": "Epigastric pain",
                    "hpi": "A {age}-year-old {gender} presents with severe epigastric pain radiating to the back after heavy alcohol use and large meal. Nausea and vomiting. History of gallstones.",
                    "vitals": "fever",
                    "pe_findings": "Severe epigastric tenderness with guarding. Decreased bowel sounds. Grey Turner's sign negative.",
                    "amylase": "850 U/L",
                    "lipase": "1,200 U/L",
                    "ct": "Enlarged pancreas with peripancreatic fat stranding",
                    "question": "What is the most common cause of acute pancreatitis in the United States?",
                    "options": [
                        "A. Hypertriglyceridemia",
                        "B. Gallstones",
                        "C. Alcohol abuse",
                        "D. Abdominal trauma",
                        "E. Medications"
                    ],
                    "correct": "B",
                    "explanation": "In the United States, gallstones are the most common cause of acute pancreatitis (40-70%), followed by alcohol abuse (25-35%). The classic presentation is epigastric pain radiating to the back with elevated amylase and lipase (>3x upper limit of normal).",
                    "learning_objectives": ["Pancreatitis etiology", "Gallstone pancreatitis", "Diagnostic criteria"]
                },
                {
                    "name": "GERD Pathophysiology",
                    "step": 1,
                    "demographics": "adult_female",
                    "chief_complaint": "Heartburn",
                    "hpi": "A {age}-year-old {gender} presents with burning retrosternal discomfort after meals and when lying down, occurring 3-4 times per week for 2 months. Worse after spicy foods.",
                    "vitals": "normal",
                    "pe_findings": "Normal physical examination",
                    "question": "What is the primary mechanism of gastroesophageal reflux disease?",
                    "options": [
                        "A. Excessive gastric acid production only",
                        "B. Incompetent lower esophageal sphincter and transient relaxations",
                        "C. H. pylori infection of the esophageal mucosa",
                        "D. Autoimmune destruction of esophageal smooth muscle",
                        "E. Excessive histamine release from gastric G cells"
                    ],
                    "correct": "B",
                    "explanation": "GERD is primarily caused by dysfunction of the lower esophageal sphincter (LES), including transient LES relaxations and decreased basal LES tone. This allows gastric contents to reflux into the esophagus. Contributing factors include hiatal hernia, obesity, and certain foods.",
                    "learning_objectives": ["GERD pathophysiology", "LES dysfunction", "Transient LES relaxations"]
                }
            ],
            "nephrology": [
                {
                    "name": "Acute Kidney Injury",
                    "step": 2,
                    "demographics": "elderly_male",
                    "chief_complaint": "Decreased urine output",
                    "hpi": "A {age}-year-old {gender} underwent elective hip surgery 2 days ago. Now with decreased urine output (300 mL in 24h) and elevated creatinine from 1.0 to 2.8 mg/dL.",
                    "vitals": "normal",
                    "pe_findings": "Dry mucous membranes. Flat neck veins. No peripheral edema.",
                    "labs": "azotemia",
                    "bun_cr_ratio": ">20:1",
                    "fena": "<1%",
                    "question": "What is the most likely cause of this patient's acute kidney injury?",
                    "options": [
                        "A. Acute tubular necrosis",
                        "B. Prerenal azotemia from hypovolemia",
                        "C. Postrenal obstruction",
                        "D. Rhabdomyolysis",
                        "E. Acute interstitial nephritis"
                    ],
                    "correct": "B",
                    "explanation": "This patient has prerenal azotemia secondary to hypovolemia from surgery and poor intake. The BUN/Cr ratio >20:1 and FENa <1% are classic findings of prerenal azotemia. Physical exam findings of volume depletion (dry mucous membranes, flat JVP) support this diagnosis.",
                    "learning_objectives": ["AKI classification", "Prerenal vs intrinsic", "FENa interpretation"]
                },
                {
                    "name": "Nephrotic Syndrome",
                    "step": 2,
                    "demographics": "child",
                    "chief_complaint": "Swelling",
                    "hpi": "A {age}-year-old child presents with periorbital edema in the morning and leg swelling. Parents report foamy urine. No recent illness.",
                    "vitals": "normal",
                    "pe_findings": "Periorbital edema, 2+ pitting edema in lower extremities. Ascites present.",
                    "urinalysis": "4+ protein, no RBCs",
                    "protein_creatinine_ratio": ">3.5",
                    "albumin": "2.1 g/dL",
                    "lipids": "Elevated cholesterol and triglycerides",
                    "question": "What is the most likely diagnosis?",
                    "options": [
                        "A. Acute post-streptococcal glomerulonephritis",
                        "B. Minimal change disease",
                        "C. IgA nephropathy",
                        "D. Rapidly progressive glomerulonephritis",
                        "E. Lupus nephritis"
                    ],
                    "correct": "B",
                    "explanation": "Minimal change disease is the most common cause of nephrotic syndrome in children (80-90% of cases <10 years). The classic tetrad of nephrotic syndrome is heavy proteinuria (>3.5 g/day), hypoalbuminemia, edema, and hyperlipidemia. Minimal change disease typically has normal appearing glomeruli on light microscopy.",
                    "learning_objectives": ["Nephrotic syndrome", "Minimal change disease", "Nephrotic vs nephritic"]
                }
            ],
            "endocrinology": [
                {
                    "name": "Diabetic Ketoacidosis",
                    "step": 2,
                    "demographics": "young_adult_female",
                    "chief_complaint": "Nausea and confusion",
                    "hpi": "A {age}-year-old {gender} with type 1 diabetes presents with nausea, vomiting, and confusion for 24 hours. Ran out of insulin 3 days ago. Also reports polyuria and polydipsia.",
                    "vitals": "tachycardic",
                    "pe_findings": "Kussmaul respirations (deep, rapid breathing). Dry mucous membranes. Fruity breath odor. Altered mental status.",
                    "labs": "hyperglycemia",
                    "ph": "7.15",
                    "bicarb": "12 mEq/L",
                    "anion_gap": "22",
                    "ketones": "Positive serum and urine",
                    "question": "What is the most appropriate initial management?",
                    "options": [
                        "A. Subcutaneous regular insulin only",
                        "B. IV fluid resuscitation followed by IV insulin drip",
                        "C. Oral hypoglycemic agents",
                        "D. Sodium bicarbonate infusion",
                        "E. Glucagon injection"
                    ],
                    "correct": "B",
                    "explanation": "DKA management priorities: 1) Fluid resuscitation with isotonic saline (often 1-2L in first hour), 2) IV regular insulin (0.1 U/kg bolus then 0.1 U/kg/hr drip), 3) Potassium replacement when K+ <5.3, 4) Bicarbonate only if pH <6.9. Glucose monitoring with dextrose added when glucose <250.",
                    "learning_objectives": ["DKA management", "Fluid resuscitation priority", "Insulin therapy protocol"]
                },
                {
                    "name": "Hyperthyroidism",
                    "step": 2,
                    "demographics": "young_adult_female",
                    "chief_complaint": "Weight loss and tremor",
                    "hpi": "A {age}-year-old {gender} presents with 15-pound weight loss over 2 months despite increased appetite, heat intolerance, palpitations, and anxiety. Also notes tremor in hands.",
                    "vitals": "tachycardic",
                    "pe_findings": "Tremor in outstretched hands. Warm, moist skin. Lid lag present. Diffuse thyroid enlargement without nodules.",
                    "tsh": "0.01 mIU/L",
                    "free_t4": "Elevated",
                    "tsi": "Elevated",
                    "question": "What is the most likely diagnosis?",
                    "options": [
                        "A. Hashimoto's thyroiditis",
                        "B. Graves' disease",
                        "C. Toxic multinodular goiter",
                        "D. Subacute thyroiditis",
                        "E. Iatrogenic hyperthyroidism"
                    ],
                    "correct": "B",
                    "explanation": "Graves' disease is the most common cause of hyperthyroidism. The combination of hyperthyroid symptoms (weight loss, heat intolerance, palpitations) with diffuse goiter and elevated TSI (thyroid-stimulating immunoglobulins) is diagnostic. Eye findings (lid lag, exophthalmos) may also be present.",
                    "learning_objectives": ["Graves' disease diagnosis", "TSI antibodies", "Hyperthyroidism workup"]
                }
            ],
            "infectious_disease": [
                {
                    "name": "Meningitis",
                    "step": 2,
                    "demographics": "young_adult_male",
                    "chief_complaint": "Headache and fever",
                    "hpi": "A {age}-year-old {gender} presents with sudden onset severe headache, fever to 103°F, and neck stiffness. Photophobia and confusion noted by roommate.",
                    "vitals": "fever",
                    "pe_findings": "Nuchal rigidity. Positive Kernig's sign. Positive Brudzinski's sign. Altered mental status.",
                    "wbc": "15,000 with left shift",
                    "lp": "CSF: Elevated WBC, low glucose, high protein, gram-positive diplococci",
                    "question": "What is the most appropriate empiric treatment?",
                    "options": [
                        "A. Vancomycin + Ceftriaxone + Ampicillin",
                        "B. Azithromycin monotherapy",
                        "C. Metronidazole alone",
                        "D. Amoxicillin only",
                        "E. Ciprofloxacin"
                    ],
                    "correct": "A",
                    "explanation": "Empiric therapy for suspected bacterial meningitis in adults (18-50): Vancomycin (for possible resistant pneumococcus) + Ceftriaxone (or cefotaxime) + Ampicillin (for Listeria coverage in adults >50 or immunocompromised). Dexamethasone should be given before or with first antibiotic dose.",
                    "learning_objectives": ["Meningitis empiric therapy", "CSF analysis", "Kernig/Brudzinski signs"]
                },
                {
                    "name": "HIV/AIDS Opportunistic Infection",
                    "step": 2,
                    "demographics": "adult_male",
                    "chief_complaint": "Dyspnea",
                    "hpi": "A {age}-year-old {gender} with HIV (last CD4 unknown, not on HAART) presents with 2 weeks of progressive dyspnea, nonproductive cough, and low-grade fever.",
                    "vitals": "fever",
                    "pe_findings": "Tachypneic. Decreased oxygen saturation to 88% on room air. Clear lung sounds bilaterally.",
                    "cd4": "45 cells/μL",
                    "cxr": "Bilateral diffuse interstitial infiltrates",
                    "abg": "PaO2 58 mmHg, increased A-a gradient",
                    "question": "What is the most likely diagnosis?",
                    "options": [
                        "A. Tuberculosis",
                        "B. Pneumocystis jirovecii pneumonia (PCP)",
                        "C. Bacterial community-acquired pneumonia",
                        "D. Kaposi's sarcoma",
                        "E. CMV pneumonitis"
                    ],
                    "correct": "B",
                    "explanation": "PCP is the most common opportunistic infection in AIDS with CD4 <200. The classic presentation is subacute dyspnea, nonproductive cough, fever, hypoxemia with normal or minimal auscultatory findings, and diffuse interstitial infiltrates on CXR. Diagnosis confirmed by silver stain of induced sputum or BAL.",
                    "learning_objectives": ["PCP presentation", "AIDS opportunistic infections", "CD4 thresholds"]
                }
            ],
            "neurology": [
                {
                    "name": "Acute Ischemic Stroke",
                    "step": 2,
                    "demographics": "elderly_male",
                    "chief_complaint": "Weakness",
                    "hpi": "A {age}-year-old {gender} with atrial fibrillation presents with sudden onset right-sided weakness and difficulty speaking. Last known well 2 hours ago.",
                    "vitals": "hypertensive",
                    "pe_findings": "Right facial droop, right arm and leg weakness (3/5), expressive aphasia present. Left gaze preference.",
                    "nihss": "12",
                    "ct_head": "No hemorrhage, early ischemic changes in left MCA territory",
                    "question": "What is the most appropriate next step?",
                    "options": [
                        "A. Start aspirin immediately",
                        "B. Administer IV tPA (thrombolytics)",
                        "C. Anticoagulate with heparin",
                        "D. Perform CT angiography only and observe",
                        "E. Aspirin and clopidogrel dual therapy"
                    ],
                    "correct": "B",
                    "explanation": "For acute ischemic stroke presenting within 4.5 hours of symptom onset, IV tPA (alteplase) is indicated if no contraindications (normal CT ruling out hemorrhage, BP <185/110, no recent surgery/ bleeding). Mechanical thrombectomy may be considered for large vessel occlusion.",
                    "learning_objectives": ["Acute stroke management", "tPA indications", "Time window for thrombolysis"]
                },
                {
                    "name": "Multiple Sclerosis",
                    "step": 1,
                    "demographics": "young_adult_female",
                    "chief_complaint": "Vision loss",
                    "hpi": "A {age}-year-old {gender} presents with painful vision loss in right eye over 3 days. Had episode of leg weakness 6 months ago that resolved spontaneously. Lives in northern climate.",
                    "vitals": "normal",
                    "pe_findings": "Decreased visual acuity OD. Afferent pupillary defect (Marcus Gunn pupil) on right. Internuclear ophthalmoplegia noted on left gaze.",
                    "mri_brain": "Multiple periventricular white matter lesions, ovoid, perpendicular to ventricles (Dawson's fingers)",
                    "csf": "Oligoclonal bands present",
                    "question": "What is the pathophysiology of this disease?",
                    "options": [
                        "A. Autoimmune demyelination of CNS white matter",
                        "B. Direct viral infection of oligodendrocytes",
                        "C. Vasculitic occlusion of cerebral vessels",
                        "D. Autoantibody attack on neuromuscular junction",
                        "E. Progressive neuronal apoptosis"
                    ],
                    "correct": "A",
                    "explanation": "MS is an autoimmune demyelinating disease of the CNS characterized by T-cell mediated attack on myelin basic protein. Features include dissemination in time and space (multiple episodes, multiple locations), periventricular white matter lesions (Dawson's fingers), oligoclonal bands in CSF, and association with HLA-DR2 and vitamin D deficiency.",
                    "learning_objectives": ["MS pathophysiology", "Demyelination", "McDonald criteria"]
                }
            ]
        }
    
    def generate_case(self, step=2, topic=None, condition=None, difficulty="medium", include_answer=True):
        """Generate a USMLE-style clinical case."""
        conditions_db = self.get_condition_database()
        
        # Filter by topic if specified
        if topic and topic.lower() in conditions_db:
            available_conditions = conditions_db[topic.lower()]
        else:
            # Use all conditions
            available_conditions = []
            for topic_conditions in conditions_db.values():
                available_conditions.extend(topic_conditions)
        
        # Filter by step
        available_conditions = [c for c in available_conditions if c.get("step", 2) == step]
        
        if not available_conditions:
            return self._generate_generic_case(step, topic)
        
        # Select condition
        if condition:
            selected = next((c for c in available_conditions if condition.lower() in c["name"].lower()), None)
            if not selected:
                selected = random.choice(available_conditions)
        else:
            selected = random.choice(available_conditions)
        
        return self._format_case(selected, include_answer)
    
    def _format_case(self, condition, include_answer=True):
        """Format a case with demographics filled in."""
        # Get demographics
        demo_key = condition.get("demographics", "adult_male")
        demo = self.demographics.get(demo_key, self.demographics["adult_male"])
        
        age = random.randint(demo["age_range"][0], demo["age_range"][1])
        gender = demo["gender"] if demo["gender"] != "any" else random.choice(["male", "female"])
        
        # Fill in HPI
        hpi = condition.get("hpi", "").format(age=age, gender=gender)
        
        # Build case
        case = {
            "title": f"Case: {condition['name']}",
            "metadata": {
                "condition": condition['name'],
                "step": condition.get('step', 2),
                "topic": self._get_topic_for_condition(condition['name']),
                "difficulty": condition.get('difficulty', 'medium'),
                "generated_at": datetime.now().isoformat()
            },
            "case_content": {
                "chief_complaint": condition.get('chief_complaint', 'Unknown'),
                "history_of_present_illness": hpi,
                "vital_signs": self._get_vitals(condition.get('vitals', 'normal')),
                "physical_examination": condition.get('pe_findings', 'Normal'),
                "diagnostic_studies": self._get_diagnostics(condition),
                "laboratory_results": self._get_labs(condition.get('labs', 'normal'))
            },
            "question": {
                "text": condition.get('question', 'What is the diagnosis?'),
                "options": condition.get('options', ['A', 'B', 'C', 'D', 'E'])
            }
        }
        
        if include_answer:
            case["answer"] = {
                "correct": condition.get('correct', 'A'),
                "explanation": condition.get('explanation', ''),
                "learning_objectives": condition.get('learning_objectives', [])
            }
        
        return case
    
    def _get_vitals(self, vitals_key):
        """Get vital signs for a case."""
        return self.vital_signs.get(vitals_key, self.vital_signs["normal"])
    
    def _get_labs(self, labs_key):
        """Get lab values for a case."""
        base_labs = self.lab_ranges["normal"].copy()
        if labs_key in self.lab_ranges:
            base_labs.update(self.lab_ranges[labs_key])
        return base_labs
    
    def _get_diagnostics(self, condition):
        """Get diagnostic study results."""
        diagnostics = {}
        if 'ecg' in condition:
            diagnostics['ECG'] = condition['ecg']
        if 'cxr' in condition:
            diagnostics['Chest X-ray'] = condition['cxr']
        if 'ct' in condition:
            diagnostics['CT'] = condition['ct']
        if 'mri' in condition:
            diagnostics['MRI'] = condition['mri']
        if 'lp' in condition:
            diagnostics['Lumbar Puncture'] = condition['lp']
        if 'pfts' in condition:
            diagnostics['Pulmonary Function Tests'] = condition['pfts']
        return diagnostics
    
    def _get_topic_for_condition(self, condition_name):
        """Get topic category for a condition."""
        db = self.get_condition_database()
        for topic, conditions in db.items():
            if any(c['name'] == condition_name for c in conditions):
                return topic
        return "general"
    
    def _generate_generic_case(self, step, topic):
        """Generate a generic case when specific one not available."""
        return {
            "title": "Generic Clinical Case",
            "metadata": {
                "step": step,
                "topic": topic or "general",
                "generated_at": datetime.now().isoformat()
            },
            "case_content": {
                "chief_complaint": "Patient presents with symptoms",
                "history_of_present_illness": "Please specify a condition or topic for a detailed case.",
                "vital_signs": self.vital_signs["normal"],
                "physical_examination": "Normal",
                "diagnostic_studies": {},
                "laboratory_results": self.lab_ranges["normal"]
            },
            "question": {
                "text": "What would you like to assess?",
                "options": ["A", "B", "C", "D", "E"]
            }
        }
    
    def format_output(self, case, format_type="text"):
        """Format case for output."""
        if format_type == "json":
            return json.dumps(case, indent=2)
        elif format_type == "markdown":
            return self._format_markdown(case)
        else:
            return self._format_text(case)
    
    def _format_text(self, case):
        """Format case as plain text."""
        content = case["case_content"]
        lines = [
            "=" * 60,
            case["title"],
            "=" * 60,
            "",
            f"CHIEF COMPLAINT: {content['chief_complaint']}",
            "",
            "HISTORY OF PRESENT ILLNESS:",
            content['history_of_present_illness'],
            "",
            "VITAL SIGNS:",
            f"  Temperature: {content['vital_signs']['temp']}",
            f"  Heart Rate: {content['vital_signs']['hr']}",
            f"  Blood Pressure: {content['vital_signs']['bp']}",
            f"  Respiratory Rate: {content['vital_signs']['rr']}",
            f"  O2 Saturation: {content['vital_signs']['o2']}",
            "",
            "PHYSICAL EXAMINATION:",
            content['physical_examination'],
            "",
            "DIAGNOSTIC STUDIES:"
        ]
        
        if content['diagnostic_studies']:
            for study, result in content['diagnostic_studies'].items():
                lines.append(f"  {study}: {result}")
        else:
            lines.append("  None")
        
        lines.extend([
            "",
            "LABORATORY RESULTS:",
        ])
        
        for lab, value in content['laboratory_results'].items():
            lines.append(f"  {lab.upper()}: {value}")
        
        lines.extend([
            "",
            "-" * 60,
            "QUESTION:",
            case["question"]["text"],
            "",
        ])
        
        for option in case["question"]["options"]:
            lines.append(option)
        
        if "answer" in case:
            lines.extend([
                "",
                "-" * 60,
                f"CORRECT ANSWER: {case['answer']['correct']}",
                "",
                "EXPLANATION:",
                case['answer']['explanation'],
                "",
                "LEARNING OBJECTIVES:",
            ])
            for obj in case['answer']['learning_objectives']:
                lines.append(f"  - {obj}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _format_markdown(self, case):
        """Format case as markdown."""
        content = case["case_content"]
        lines = [
            f"# {case['title']}",
            "",
            "## Case Information",
            f"- **Condition**: {case['metadata']['condition']}",
            f"- **USMLE Step**: {case['metadata']['step']}",
            f"- **Topic**: {case['metadata']['topic']}",
            "",
            "## Chief Complaint",
            content['chief_complaint'],
            "",
            "## History of Present Illness",
            content['history_of_present_illness'],
            "",
            "## Vital Signs",
            f"| Parameter | Value |",
            f"|-----------|-------|",
            f"| Temperature | {content['vital_signs']['temp']} |",
            f"| Heart Rate | {content['vital_signs']['hr']} |",
            f"| Blood Pressure | {content['vital_signs']['bp']} |",
            f"| Respiratory Rate | {content['vital_signs']['rr']} |",
            f"| O2 Saturation | {content['vital_signs']['o2']} |",
            "",
            "## Physical Examination",
            content['physical_examination'],
            "",
            "## Diagnostic Studies",
        ]
        
        if content['diagnostic_studies']:
            for study, result in content['diagnostic_studies'].items():
                lines.append(f"- **{study}**: {result}")
        else:
            lines.append("None")
        
        lines.extend([
            "",
            "## Laboratory Results",
        ])
        
        for lab, value in content['laboratory_results'].items():
            lines.append(f"- **{lab.upper()}**: {value}")
        
        lines.extend([
            "",
            "## Question",
            case["question"]["text"],
            "",
        ])
        
        for option in case["question"]["options"]:
            lines.append(f"{option}")
        
        if "answer" in case:
            lines.extend([
                "",
                "---",
                "",
                f"## Answer: **{case['answer']['correct']}**",
                "",
                "### Explanation",
                case['answer']['explanation'],
                "",
                "### Learning Objectives",
            ])
            for obj in case['answer']['learning_objectives']:
                lines.append(f"- {obj}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate USMLE-style clinical cases")
    parser.add_argument("--step", type=int, choices=[1, 2], default=2, help="USMLE Step level")
    parser.add_argument("--topic", type=str, help="Medical topic (cardiology, pulmonology, etc.)")
    parser.add_argument("--condition", type=str, help="Specific medical condition")
    parser.add_argument("--difficulty", type=str, choices=["easy", "medium", "hard"], default="medium")
    parser.add_argument("--format", type=str, choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--include-diagnosis", action="store_true", help="Include answer key")
    parser.add_argument("--count", type=int, default=1, help="Number of cases to generate")
    
    args = parser.parse_args()
    
    generator = USMLECaseGenerator()
    
    for i in range(args.count):
        case = generator.generate_case(
            step=args.step,
            topic=args.topic,
            condition=args.condition,
            difficulty=args.difficulty,
            include_answer=args.include_diagnosis
        )
        
        output = generator.format_output(case, args.format)
        print(output)
        
        if i < args.count - 1:
            print("\n" + "=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

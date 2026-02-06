"""
Example usage of Unstructured Medical Text Miner

演示如何使用医疗文本挖掘器处理MIMIC-IV数据
"""

from scripts.main import MedicalTextMiner

# 示例1: 处理单个文本片段
sample_discharge_summary = """
DISCHARGE SUMMARY

Patient: [**Name**] (M, 67 y/o)
Admission Date: [**Date**]
Discharge Date: [**Date**]

CHIEF COMPLAINT:
Chest pain for 3 hours

HISTORY OF PRESENT ILLNESS:
Patient presented with acute onset chest pain radiating to left arm. 
No prior history of coronary artery disease. Denies dyspnea, nausea, or diaphoresis.
Vital signs on admission: BP 140/90, HR 98, RR 18, SpO2 97% on room air.

HOSPITAL COURSE:
ECG showed ST elevation in V1-V4 consistent with anterior STEMI.
Troponin I peaked at 15.6 ng/mL.
Patient underwent emergent cardiac catheterization with PCI to LAD.
Started on aspirin 81mg daily, clopidogrel 75mg daily, atorvastatin 40mg daily.
No complications post-procedure. Chest pain resolved.

DISCHARGE DIAGNOSIS:
1. Acute anterior ST-elevation myocardial infarction (STEMI), successfully treated with PCI
2. Hypertension

DISCHARGE MEDICATIONS:
1. Aspirin 81mg PO daily
2. Clopidogrel 75mg PO daily  
3. Atorvastatin 40mg PO daily
4. Lisinopril 10mg PO daily

FOLLOW UP:
Cardiology clinic in 1 week
"""


def demo_single_text():
    """演示单个文本的实体和关系抽取"""
    print("=" * 60)
    print("DEMO 1: Single Text Extraction")
    print("=" * 60)
    
    miner = MedicalTextMiner()
    
    # 提取完整洞察
    insights = miner.extract_insights(
        sample_discharge_summary,
        extract_entities=True,
        extract_relations=True,
        extract_timeline=True,
        extract_logic=True
    )
    
    print(f"\nExtracted {insights['entity_count']} entities:")
    for entity_type, entities in insights.get('entities_by_type', {}).items():
        print(f"\n  {entity_type}:")
        for e in entities[:3]:  # 只显示前3个
            neg_mark = " [NEGATED]" if e.get('negated') else ""
            print(f"    - {e['text']}{neg_mark}")
    
    print(f"\nExtracted {insights.get('relation_count', 0)} relations:")
    for r in insights.get('relations', [])[:3]:
        print(f"  - {r['subject']} --{r['predicate']}--> {r['object']}")
    
    print("\nClinical Logic:")
    logic = insights.get('clinical_logic', {})
    if logic.get('presenting_complaint'):
        print(f"  Chief Complaint: {logic['presenting_complaint']}")
    if logic.get('workup'):
        print(f"  Workup: {', '.join(logic['workup'])}")
    
    return insights


def demo_patient_processing():
    """演示患者级别的处理（需要MIMIC-IV数据文件）"""
    print("\n" + "=" * 60)
    print("DEMO 2: Patient Processing (requires MIMIC-IV data)")
    print("=" * 60)
    
    miner = MedicalTextMiner()
    
    # 注意：这需要实际的MIMIC-IV数据文件
    # 取消下面注释并提供正确的文件路径以运行
    
    # miner.load_notes("path/to/noteevents.csv", note_types=["DS", "RR"])
    # patient_insights = miner.process_patient(subject_id=10000032)
    # 
    # print(miner.generate_summary_report(patient_insights))
    # miner.export_to_json(patient_insights, "patient_10000032_insights.json")
    
    print("""
    To run patient processing:
    
    1. Download MIMIC-IV NOTEEVENTS data from PhysioNet
    2. Run:
       
       miner = MedicalTextMiner()
       miner.load_notes("noteevents.csv", note_types=["DS"])
       insights = miner.process_patient(subject_id=10000032)
       miner.export_to_json(insights, "output.json")
    """)


def demo_regex_patterns():
    """演示正则表达式模式匹配"""
    print("\n" + "=" * 60)
    print("DEMO 3: Regex Pattern Matching")
    print("=" * 60)
    
    test_text = """
    The patient was diagnosed with acute myocardial infarction.
    Started on heparin drip and metformin 500mg twice daily.
    No evidence of pneumonia. Troponin elevated at 5.2 ng/mL.
    """
    
    miner = MedicalTextMiner()
    entities = miner.extract_entities_regex(test_text)
    
    print(f"\nFound {len(entities)} entities:")
    for e in entities:
        neg_mark = " [NEGATED]" if e.get('negated') else ""
        print(f"  - [{e['type']}] {e['text']}{neg_mark}")


if __name__ == "__main__":
    # 运行演示
    demo_single_text()
    demo_regex_patterns()
    demo_patient_processing()

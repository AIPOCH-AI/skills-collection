#!/usr/bin/env python3
"""
医学术语翻译脚本
支持中英、中西等医学术语互译
"""

import sys

def translate_medical_term(term, source_lang, target_lang, context=None):
    """
    翻译医学术语
    
    Args:
        term: 待翻译的术语
        source_lang: 源语言
        target_lang: 目标语言
        context: 上下文（可选）
    
    Returns:
        dict: 包含翻译结果和元数据
    """
    # 常见医学术语词典
    cn_to_en = {
        "急性髓系白血病": "Acute Myeloid Leukemia (AML)",
        "高血压": "Hypertension",
        "糖尿病": "Diabetes Mellitus",
        "心肌梗死": "Myocardial Infarction (MI)",
        "脑梗死": "Cerebral Infarction",
        "肿瘤": "Tumor / Neoplasm",
        "化疗": "Chemotherapy",
        "放疗": "Radiotherapy",
        "免疫治疗": "Immunotherapy",
        "靶向治疗": "Targeted Therapy",
    }
    
    en_to_cn = {v.split(" (")[0] if "(" in v else v: k for k, v in cn_to_en.items()}
    
    result = {
        "original": term,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "translated": None,
        "notes": []
    }
    
    if source_lang == "中文" and target_lang == "English":
        result["translated"] = cn_to_en.get(term, f"[需人工确认] {term}")
        if term not in cn_to_en:
            result["notes"].append("术语不在标准词典中，建议复核")
    elif source_lang == "English" and target_lang == "中文":
        result["translated"] = en_to_cn.get(term, f"[需人工确认] {term}")
        if term not in en_to_cn:
            result["notes"].append("术语不在标准词典中，建议复核")
    else:
        result["translated"] = f"[暂不支持] {source_lang} -> {target_lang}"
        result["notes"].append("当前仅支持中英互译")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <term> <source_lang> <target_lang>")
        sys.exit(1)
    
    term = sys.argv[1]
    source_lang = sys.argv[2]
    target_lang = sys.argv[3]
    
    result = translate_medical_term(term, source_lang, target_lang)
    print(f"原文: {result['original']}")
    print(f"译文: {result['translated']}")
    if result['notes']:
        print(f"备注: {'; '.join(result['notes'])}")

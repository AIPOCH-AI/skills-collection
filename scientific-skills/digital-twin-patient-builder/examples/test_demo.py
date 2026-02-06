#!/usr/bin/env python3
"""测试脚本 - 验证 Digital Twin Patient Builder 功能"""

import json
import sys
sys.path.insert(0, '..')

from scripts.main import DigitalTwinBuilder, PatientProfile

def test_basic_functionality():
    """测试基础功能"""
    print("=" * 60)
    print("Digital Twin Patient Builder - 功能测试")
    print("=" * 60)
    
    # 1. 加载示例患者数据
    print("\n[1] 加载患者数据...")
    with open('patient_example.json', 'r') as f:
        patient_data = json.load(f)
    print(f"   患者ID: {patient_data['patient_id']}")
    print(f"   年龄: {patient_data['clinical']['age']}岁")
    print(f"   CYP2D6基因型: {patient_data['genotype']['CYP2D6']}")
    
    # 2. 加载药物配置
    print("\n[2] 加载药物配置...")
    with open('drug_docetaxel.json', 'r') as f:
        drug_profile = json.load(f)
    print(f"   药物名称: {drug_profile['drug_name']}")
    print(f"   标准剂量: {drug_profile['standard_dose_mg_m2']} mg/m²")
    
    # 3. 构建数字孪生
    print("\n[3] 构建数字孪生模型...")
    builder = DigitalTwinBuilder()
    twin = builder.build_twin(patient_data)
    twin.initialize(drug_profile)
    
    # 4. 计算患者生理参数
    patient = twin.patient
    print(f"   体表面积(BSA): {patient.clinical.calculate_bsa():.2f} m²")
    print(f"   肌酐清除率: {patient.clinical.calculate_renal_function():.1f} mL/min")
    print(f"   代谢酶表型: {patient.genotype.get_metabolizer_status().value}")
    print(f"   药物响应概率: {patient.imaging.calculate_drug_response_probability():.2f}")
    
    # 5. 模拟不同剂量
    print("\n[4] 模拟药物剂量方案...")
    doses = [50, 75, 100, 125, 150]
    results = twin.simulate_dose_range(doses)
    
    print("\n   剂量 (mg) | Cmax (mg/L) | AUC | 肿瘤缩小 | 毒性风险")
    print("   " + "-" * 55)
    for r in results:
        print(f"   {r['dose']:9.0f} | {r['cmax']:11.2f} | {r['auc']:.1f} | "
              f"{r['tumor_reduction_percent']:7.1f}% | {r['overall_toxicity_risk']:.3f}")
    
    # 6. 剂量优化
    print("\n[5] 执行剂量优化...")
    optimal = twin.find_optimal_dose((50, 150), n_points=15)
    print(f"   最优剂量: {optimal['optimal_dose']:.1f} mg")
    print(f"   综合评分: {optimal['score']:.3f}")
    
    # 7. 测试高风险患者
    print("\n[6] 测试高风险患者对比...")
    with open('patient_high_risk.json', 'r') as f:
        high_risk_data = json.load(f)
    
    high_risk_twin = builder.build_twin(high_risk_data)
    high_risk_twin.initialize(drug_profile)
    
    print(f"   患者 P002 (高龄+肾功能不全+慢代谢):")
    print(f"   - 代谢表型: {high_risk_twin.patient.genotype.get_metabolizer_status().value}")
    print(f"   - 肌酐清除率: {high_risk_twin.patient.clinical.calculate_renal_function():.1f} mL/min")
    
    hr_result = high_risk_twin.simulate_dose(75)
    normal_result = twin.simulate_dose(75)
    
    print(f"\n   相同剂量(75mg)对比:")
    print(f"   正常患者 - Cmax: {normal_result['cmax']:.2f}, 毒性风险: {normal_result['overall_toxicity_risk']:.3f}")
    print(f"   高风险患者 - Cmax: {hr_result['cmax']:.2f}, 毒性风险: {hr_result['overall_toxicity_risk']:.3f}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    # 保存结果
    with open('test_results.json', 'w') as f:
        json.dump({
            "dose_range_results": results,
            "optimal_dose": optimal['optimal_dose'],
            "optimal_score": optimal['score']
        }, f, indent=2)
    print(f"\n测试结果已保存至: test_results.json")

if __name__ == "__main__":
    test_basic_functionality()

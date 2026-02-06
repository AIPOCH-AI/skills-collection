#!/usr/bin/env python3
"""
Digital Twin Patient Builder (ID: 208)

构建患者的"数字孪生"模型，整合基因型、临床病史和影像数据，
在虚拟环境中测试不同药物剂量的疗效和毒性反应。

Author: AI Assistant
Version: 1.0.0
"""

import json
import argparse
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import warnings

warnings.filterwarnings('ignore')


class MetabolizerStatus(Enum):
    """药物代谢酶表型分类"""
    ULTRA_RAPID = "ultra_rapid"
    EXTENSIVE = "extensive"
    INTERMEDIATE = "intermediate"
    POOR = "poor"


@dataclass
class GenotypeProfile:
    """基因型档案"""
    cyp2d6: str = "*1/*1"
    tpmt: str = "*1/*1"
    snps: Dict[str, str] = field(default_factory=dict)
    
    def get_metabolizer_status(self, enzyme: str = "CYP2D6") -> MetabolizerStatus:
        """根据基因型判断代谢酶表型"""
        poor_alleles = ["*3", "*4", "*5", "*6"]
        ultra_alleles = ["*1xN", "*2xN"]
        
        if enzyme == "CYP2D6":
            alleles = self.cyp2d6.split("/")
            poor_count = sum(1 for a in alleles if any(pa in a for pa in poor_alleles))
            ultra_count = sum(1 for a in alleles if any(ua in a for ua in ultra_alleles))
            
            if ultra_count > 0:
                return MetabolizerStatus.ULTRA_RAPID
            elif poor_count == 2:
                return MetabolizerStatus.POOR
            elif poor_count == 1:
                return MetabolizerStatus.INTERMEDIATE
            else:
                return MetabolizerStatus.EXTENSIVE
        return MetabolizerStatus.EXTENSIVE
    
    def calculate_metabolism_factor(self) -> float:
        """计算代谢因子 (影响药物清除率)"""
        status = self.get_metabolizer_status("CYP2D6")
        factors = {
            MetabolizerStatus.ULTRA_RAPID: 2.0,
            MetabolizerStatus.EXTENSIVE: 1.0,
            MetabolizerStatus.INTERMEDIATE: 0.7,
            MetabolizerStatus.POOR: 0.3
        }
        return factors.get(status, 1.0)


@dataclass
class ClinicalProfile:
    """临床档案"""
    age: int = 50
    weight: float = 70.0
    height: float = 170.0
    lab_values: Dict[str, float] = field(default_factory=dict)
    comorbidities: List[str] = field(default_factory=list)
    
    def calculate_bsa(self) -> float:
        """计算体表面积 (Mosteller公式)"""
        return np.sqrt(self.height * self.weight / 3600)
    
    def calculate_bmi(self) -> float:
        """计算BMI"""
        height_m = self.height / 100
        return self.weight / (height_m ** 2)
    
    def calculate_renal_function(self) -> float:
        """估算肾功能 (Cockcroft-Gault公式)"""
        creatinine = self.lab_values.get("creatinine", 1.0)
        if creatinine <= 0:
            creatinine = 1.0
        
        crcl = ((140 - self.age) * self.weight) / (72 * creatinine)
        return max(crcl, 10.0)  # 最小值限制
    
    def calculate_hepatic_function(self) -> float:
        """评估肝功能 (基于ALT/AST)"""
        alt = self.lab_values.get("alt", 40)
        ast = self.lab_values.get("ast", 40)
        # 标准化评分 (0-1, 1为正常)
        score = 1 - min((alt + ast) / 200, 0.8)
        return max(score, 0.2)


@dataclass
class ImagingProfile:
    """影像档案"""
    tumor_volume: float = 0.0
    perfusion_rate: float = 0.5
    texture_features: Dict[str, float] = field(default_factory=dict)
    
    def calculate_vascular_permeability(self) -> float:
        """计算血管通透性 (影响药物分布)"""
        base = 0.5
        perfusion_factor = self.perfusion_rate
        texture_factor = self.texture_features.get("entropy", 5.0) / 10.0
        return min(base * perfusion_factor * (1 + texture_factor), 1.0)
    
    def calculate_drug_response_probability(self) -> float:
        """基于影像特征计算药物响应概率"""
        # 较小的肿瘤体积通常响应更好
        volume_factor = np.exp(-self.tumor_volume / 100)
        # 高灌注通常意味着更好的药物递送
        perfusion_factor = self.perfusion_rate
        return min(volume_factor * perfusion_factor, 0.95)


class PatientProfile:
    """患者档案管理器"""
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.genotype = GenotypeProfile()
        self.clinical = ClinicalProfile()
        self.imaging = ImagingProfile()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientProfile':
        """从字典创建患者档案"""
        profile = cls(data.get("patient_id", "unknown"))
        
        # 加载基因型数据
        if "genotype" in data:
            g = data["genotype"]
            profile.genotype = GenotypeProfile(
                cyp2d6=g.get("CYP2D6", "*1/*1"),
                tpmt=g.get("TPMT", "*1/*1"),
                snps=g.get("SNPs", {})
            )
        
        # 加载临床数据
        if "clinical" in data:
            c = data["clinical"]
            profile.clinical = ClinicalProfile(
                age=c.get("age", 50),
                weight=c.get("weight", 70.0),
                height=c.get("height", 170.0),
                lab_values=c.get("lab_values", {}),
                comorbidities=c.get("comorbidities", [])
            )
        
        # 加载影像数据
        if "imaging" in data:
            i = data["imaging"]
            profile.imaging = ImagingProfile(
                tumor_volume=i.get("tumor_volume", 0.0),
                perfusion_rate=i.get("perfusion_rate", 0.5),
                texture_features=i.get("texture_features", {})
            )
        
        return profile
    
    def get_risk_factors(self) -> Dict[str, float]:
        """获取患者风险因子"""
        return {
            "age_risk": min(self.clinical.age / 100, 1.0),
            "renal_impairment": max(1 - self.clinical.calculate_renal_function() / 100, 0),
            "hepatic_impairment": 1 - self.clinical.calculate_hepatic_function(),
            "metabolism_factor": self.genotype.calculate_metabolism_factor(),
            "vascular_permeability": self.imaging.calculate_vascular_permeability()
        }


class PharmacokineticModel:
    """药代动力学模型 (PBPK)"""
    
    def __init__(self, patient: PatientProfile):
        self.patient = patient
        self.risk_factors = patient.get_risk_factors()
        
        # 计算患者特异性PK参数
        self.cl = self._calculate_clearance()
        self.vd = self._calculate_volume_distribution()
        self.ka = 1.5  # 吸收速率常数 (1/h)
    
    def _calculate_clearance(self) -> float:
        """计算清除率"""
        base_cl = 15.0  # L/h 基础值
        
        # 肾功能影响
        renal_factor = self.patient.clinical.calculate_renal_function() / 100
        
        # 肝功能影响  
        hepatic_factor = self.patient.clinical.calculate_hepatic_function()
        
        # 基因型代谢影响
        metabolism_factor = self.risk_factors["metabolism_factor"]
        
        # 综合计算
        adjusted_cl = base_cl * renal_factor * hepatic_factor * metabolism_factor
        return max(adjusted_cl, 1.0)
    
    def _calculate_volume_distribution(self) -> float:
        """计算分布容积"""
        bsa = self.patient.clinical.calculate_bsa()
        base_vd = 30.0 * bsa  # 基于体表面积
        
        # 血管通透性影响
        permeability_factor = 1 + self.risk_factors["vascular_permeability"]
        
        return base_vd * permeability_factor
    
    def simulate_concentration(self, dose: float, time_points: np.ndarray) -> np.ndarray:
        """模拟血药浓度-时间曲线"""
        # 一室模型口服给药
        ke = self.cl / self.vd  # 消除速率常数
        
        # C(t) = (F * D * ka / (V * (ka - ke))) * (exp(-ke*t) - exp(-ka*t))
        f = 0.8  # 生物利用度
        numerator = f * dose * self.ka
        denominator = self.vd * (self.ka - ke)
        
        if abs(self.ka - ke) < 0.01:  # 避免除零
            ke = self.ka - 0.1
            denominator = self.vd * (self.ka - ke)
        
        concentration = (numerator / denominator) * (
            np.exp(-ke * time_points) - np.exp(-self.ka * time_points)
        )
        
        return np.maximum(concentration, 0)
    
    def calculate_auc(self, dose: float) -> float:
        """计算AUC (药时曲线下面积)"""
        # AUC = F * D / CL
        f = 0.8
        return f * dose / self.cl
    
    def calculate_cmax(self, dose: float) -> float:
        """计算Cmax (峰浓度)"""
        ke = self.cl / self.vd
        tmax = np.log(self.ka / ke) / (self.ka - ke)
        time_points = np.array([tmax])
        return self.simulate_concentration(dose, time_points)[0]


class PharmacodynamicModel:
    """药效学模型"""
    
    def __init__(self, patient: PatientProfile, drug_profile: Dict):
        self.patient = patient
        self.drug_profile = drug_profile
        self.response_prob = patient.imaging.calculate_drug_response_probability()
    
    def calculate_efficacy(self, concentration: float, time_days: int = 30) -> float:
        """计算疗效 (肿瘤缩小百分比)"""
        # Emax模型
        emax = 60.0  # 最大肿瘤缩小百分比
        ec50 = 10.0  # 半数有效浓度
        hill_coeff = 2.0
        
        # 浓度-效应关系
        effect = emax * (concentration ** hill_coeff) / (
            ec50 ** hill_coeff + concentration ** hill_coeff
        )
        
        # 考虑患者特异性响应概率
        effect *= self.response_prob
        
        # 时间因子 (随时间累积)
        time_factor = min(time_days / 30, 1.0)
        
        return effect * time_factor
    
    def calculate_toxicity_risk(self, concentration: float, auc: float) -> Dict[str, float]:
        """计算毒性风险"""
        risks = {}
        
        # 骨髓抑制风险 (基于AUC)
        base_myelosuppression = auc / 100
        age_factor = 1 + (self.patient.clinical.age - 50) / 100
        risks["neutropenia"] = min(base_myelosuppression * age_factor * 0.5, 0.9)
        
        # 肝毒性风险
        hepatic_factor = 1 - self.patient.clinical.calculate_hepatic_function()
        risks["hepatotoxicity"] = min(concentration / 50 * hepatic_factor, 0.8)
        
        # 肾毒性风险
        renal_factor = 1 - min(self.patient.clinical.calculate_renal_function() / 120, 1.0)
        risks["nephrotoxicity"] = min(auc / 200 * renal_factor, 0.6)
        
        # 胃肠道毒性
        risks["nausea_vomiting"] = min(concentration / 30, 0.7)
        
        # 心脏毒性
        risks["cardiotoxicity"] = min(auc / 300 * age_factor, 0.4)
        
        return risks


class DigitalTwin:
    """数字孪生主类"""
    
    def __init__(self, patient: PatientProfile):
        self.patient = patient
        self.pk_model = None
        self.pd_model = None
    
    def initialize(self, drug_profile: Dict):
        """初始化数字孪生模型"""
        self.pk_model = PharmacokineticModel(self.patient)
        self.pd_model = PharmacodynamicModel(self.patient, drug_profile)
        return self
    
    def simulate_dose(self, dose: float, simulation_days: int = 30) -> Dict[str, Any]:
        """模拟单次给药方案"""
        if self.pk_model is None or self.pd_model is None:
            raise ValueError("Digital twin not initialized. Call initialize() first.")
        
        # 时间轴 (小时)
        time_points = np.linspace(0, 24, 100)
        
        # 模拟血药浓度
        concentration_profile = self.pk_model.simulate_concentration(dose, time_points)
        
        # 计算PK参数
        cmax = self.pk_model.calculate_cmax(dose)
        auc = self.pk_model.calculate_auc(dose)
        
        # 计算疗效
        efficacy = self.pd_model.calculate_efficacy(cmax, simulation_days)
        
        # 计算毒性风险
        toxicity_risks = self.pd_model.calculate_toxicity_risk(cmax, auc)
        
        # 综合评分
        therapeutic_index = self._calculate_therapeutic_index(efficacy, toxicity_risks)
        
        return {
            "dose": dose,
            "cmax": round(cmax, 2),
            "auc": round(auc, 2),
            "efficacy": round(efficacy, 2),
            "tumor_reduction_percent": round(efficacy, 1),
            "toxicity_risks": {k: round(v, 3) for k, v in toxicity_risks.items()},
            "overall_toxicity_risk": round(max(toxicity_risks.values()), 3),
            "therapeutic_index": round(therapeutic_index, 3),
            "concentration_profile": {
                "time_hours": time_points.tolist(),
                "concentration": concentration_profile.tolist()
            }
        }
    
    def simulate_dose_range(
        self, 
        doses: List[float], 
        simulation_days: int = 30
    ) -> List[Dict[str, Any]]:
        """模拟多剂量方案"""
        results = []
        for dose in doses:
            result = self.simulate_dose(dose, simulation_days)
            results.append(result)
        return results
    
    def find_optimal_dose(
        self, 
        dose_range: Tuple[float, float], 
        n_points: int = 20,
        efficacy_weight: float = 0.6,
        safety_weight: float = 0.4
    ) -> Dict[str, Any]:
        """寻找最优剂量"""
        doses = np.linspace(dose_range[0], dose_range[1], n_points)
        results = self.simulate_dose_range(doses.tolist())
        
        # 计算每个剂量的综合评分
        scores = []
        for r in results:
            efficacy_score = r["efficacy"] / 100  # 归一化到0-1
            safety_score = 1 - r["overall_toxicity_risk"]
            combined_score = efficacy_weight * efficacy_score + safety_weight * safety_score
            scores.append(combined_score)
        
        # 找到最优剂量
        best_idx = np.argmax(scores)
        optimal_result = results[best_idx]
        optimal_result["optimization_score"] = round(scores[best_idx], 3)
        
        return {
            "optimal_dose": round(doses[best_idx], 1),
            "score": round(scores[best_idx], 3),
            "all_results": results,
            "dose_response_curve": {
                "doses": doses.tolist(),
                "efficacy": [r["efficacy"] for r in results],
                "toxicity": [r["overall_toxicity_risk"] for r in results],
                "scores": scores
            }
        }
    
    def _calculate_therapeutic_index(
        self, 
        efficacy: float, 
        toxicity_risks: Dict[str, float]
    ) -> float:
        """计算治疗指数"""
        max_toxicity = max(toxicity_risks.values()) if toxicity_risks else 0.5
        if max_toxicity < 0.01:
            max_toxicity = 0.01
        return efficacy / (max_toxicity * 100)


class DigitalTwinBuilder:
    """数字孪生构建器"""
    
    def build_twin(self, patient_data: Dict[str, Any]) -> DigitalTwin:
        """从患者数据构建数字孪生"""
        patient = PatientProfile.from_dict(patient_data)
        return DigitalTwin(patient)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Digital Twin Patient Builder")
    parser.add_argument("--patient", required=True, help="患者数据JSON文件路径")
    parser.add_argument("--drug", required=True, help="药物配置JSON文件路径")
    parser.add_argument("--doses", default="[50, 100, 150]", help="剂量列表 (JSON格式)")
    parser.add_argument("--output", default="simulation_results.json", help="输出文件路径")
    parser.add_argument("--optimize", action="store_true", help="执行剂量优化")
    parser.add_argument("--dose-min", type=float, default=50, help="优化时最小剂量")
    parser.add_argument("--dose-max", type=float, default=200, help="优化时最大剂量")
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.patient, 'r') as f:
        patient_data = json.load(f)
    
    with open(args.drug, 'r') as f:
        drug_profile = json.load(f)
    
    # 构建数字孪生
    builder = DigitalTwinBuilder()
    twin = builder.build_twin(patient_data)
    twin.initialize(drug_profile)
    
    # 执行模拟
    if args.optimize:
        print("正在执行剂量优化...")
        results = twin.find_optimal_dose((args.dose_min, args.dose_max))
        print(f"\n最优剂量: {results['optimal_dose']} mg")
        print(f"综合评分: {results['score']}")
    else:
        doses = json.loads(args.doses)
        print(f"正在模拟剂量方案: {doses}...")
        results = twin.simulate_dose_range(doses)
        
        for r in results:
            print(f"\n剂量: {r['dose']} mg")
            print(f"  Cmax: {r['cmax']:.2f} mg/L")
            print(f"  AUC: {r['auc']:.2f} mg·h/L")
            print(f"  肿瘤缩小: {r['tumor_reduction_percent']:.1f}%")
            print(f"  总体毒性风险: {r['overall_toxicity_risk']:.3f}")
    
    # 保存结果
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n结果已保存至: {args.output}")


if __name__ == "__main__":
    main()

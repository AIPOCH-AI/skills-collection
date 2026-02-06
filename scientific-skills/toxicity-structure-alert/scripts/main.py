#!/usr/bin/env python3
"""
Toxicity Structure Alert (Skill ID: 141)
扫描药物分子结构，识别潜在的毒性警示结构。

Usage:
    python main.py --input <smiles> [--format json|text] [--detail level]
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class ToxicAlert:
    """毒性警示结构数据类"""
    name: str
    name_en: str
    type: str
    smarts: str
    risk_level: RiskLevel
    description: str
    weight: float = 1.0


@dataclass
class AlertMatch:
    """匹配到的警示"""
    name: str
    type: str
    smarts: str
    risk_level: str
    description: str
    match_count: int = 1


@dataclass
class ScanResult:
    """扫描结果"""
    input_smiles: str
    mol_weight: Optional[float]
    alert_count: int
    risk_score: float
    risk_level: str
    alerts: List[AlertMatch]
    recommendations: List[str]


class ToxicityAlertScanner:
    """毒性警示结构扫描器"""
    
    # 预定义的毒性警示结构
    TOXIC_ALERTS = [
        # 高毒性警示
        ToxicAlert(
            name="芳香硝基",
            name_en="Aromatic Nitro",
            type="mutagenic",
            smarts="[N+](=O)[O-]c",
            risk_level=RiskLevel.HIGH,
            description="硝基芳香化合物可能导致DNA损伤，具有致突变性和潜在致癌性",
            weight=1.0
        ),
        ToxicAlert(
            name="芳香伯胺",
            name_en="Aromatic Primary Amine",
            type="carcinogenic",
            smarts="Nc1ccccc1",
            risk_level=RiskLevel.HIGH,
            description="芳香胺类可经代谢活化产生亲电性物质，与DNA形成加合物",
            weight=0.9
        ),
        ToxicAlert(
            name="环氧化物",
            name_en="Epoxide",
            type="alkylating",
            smarts="C1OC1",
            risk_level=RiskLevel.HIGH,
            description="环氧化物是高反应性的三元环醚，可作为烷基化剂损伤DNA",
            weight=1.0
        ),
        ToxicAlert(
            name="氮丙啶",
            name_en="Aziridine",
            type="alkylating",
            smarts="C1NC1",
            risk_level=RiskLevel.HIGH,
            description="氮丙啶环具有高反应性，可作为烷基化剂",
            weight=1.0
        ),
        ToxicAlert(
            name="肼/联氨",
            name_en="Hydrazine",
            type="hepatotoxic",
            smarts="[NX3][NX3]",
            risk_level=RiskLevel.HIGH,
            description="肼类化合物具有肝毒性，可能导致肝损伤",
            weight=0.9
        ),
        ToxicAlert(
            name="卤代烷基",
            name_en="Haloalkyl",
            type="alkylating",
            smarts="[C][F,Cl,Br,I]",
            risk_level=RiskLevel.HIGH,
            description="卤代烷基可作为离去基团，形成亲电中心导致烷基化",
            weight=0.85
        ),
        ToxicAlert(
            name="多环芳烃",
            name_en="Polycyclic Aromatic Hydrocarbon",
            type="carcinogenic",
            smarts="c1ccc2c(c1)ccc1c3ccccc3ccc21",
            risk_level=RiskLevel.HIGH,
            description="多环芳烃可经代谢活化形成致癌性环氧化物",
            weight=0.95
        ),
        
        # 中等毒性警示
        ToxicAlert(
            name="醛基",
            name_en="Aldehyde",
            type="reactive",
            smarts="[CX3H1](=O)",
            risk_level=RiskLevel.MEDIUM,
            description="醛基具有亲电性，可与蛋白质形成Schiff碱",
            weight=0.6
        ),
        ToxicAlert(
            name="酰氯",
            name_en="Acyl Chloride",
            type="reactive",
            smarts="C(=O)Cl",
            risk_level=RiskLevel.MEDIUM,
            description="酰氯具有高反应性，可与亲核基团发生酰化反应",
            weight=0.7
        ),
        ToxicAlert(
            name="Michael受体",
            name_en="Michael Acceptor",
            type="electrophilic",
            smarts="C=CC(=O)",
            risk_level=RiskLevel.MEDIUM,
            description="α,β-不饱和羰基可作为Michael受体与巯基发生共价结合",
            weight=0.65
        ),
        ToxicAlert(
            name="醌类",
            name_en="Quinone",
            type="oxidative",
            smarts="O=C1C=CC(=O)C=C1",
            risk_level=RiskLevel.MEDIUM,
            description="醌类可通过氧化还原循环产生活性氧，导致氧化应激",
            weight=0.7
        ),
        ToxicAlert(
            name="亚硝基",
            name_en="Nitroso",
            type="carcinogenic",
            smarts="N=O",
            risk_level=RiskLevel.MEDIUM,
            description="N-亚硝基化合物具有潜在致癌性",
            weight=0.75
        ),
        ToxicAlert(
            name="硫酯",
            name_en="Thioester",
            type="reactive",
            smarts="C(=O)S",
            risk_level=RiskLevel.MEDIUM,
            description="硫酯可与巯基发生交换反应",
            weight=0.55
        ),
        
        # 低毒性警示
        ToxicAlert(
            name="硫醇",
            name_en="Thiol",
            type="reactive",
            smarts="[SX2H]",
            risk_level=RiskLevel.LOW,
            description="硫醇具有反应性，可参与氧化还原和金属螯合",
            weight=0.3
        ),
        ToxicAlert(
            name="磺酰氯",
            name_en="Sulfonyl Chloride",
            type="reactive",
            smarts="S(=O)(=O)Cl",
            risk_level=RiskLevel.LOW,
            description="磺酰氯可与亲核试剂反应",
            weight=0.4
        ),
    ]
    
    def __init__(self):
        self.alerts = self.TOXIC_ALERTS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译SMARTS模式"""
        try:
            from rdkit import Chem
            self.has_rdkit = True
            self._compiled_patterns = {}
            for alert in self.alerts:
                try:
                    pattern = Chem.MolFromSmarts(alert.smarts)
                    if pattern:
                        self._compiled_patterns[alert.name] = pattern
                except Exception:
                    pass
        except ImportError:
            self.has_rdkit = False
            print("Warning: RDKit not available. Falling back to basic pattern matching.", file=sys.stderr)
    
    def _parse_smiles(self, smiles: str) -> Tuple[Optional['Chem.Mol'], Optional[float]]:
        """解析SMILES字符串"""
        if not self.has_rdkit:
            return None, None
        
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, None
        
        mol_weight = Descriptors.MolWt(mol)
        return mol, mol_weight
    
    def _match_alerts(self, mol) -> List[AlertMatch]:
        """匹配毒性警示结构"""
        matches = []
        
        if self.has_rdkit and mol is not None:
            # 使用RDKit进行精确的子结构匹配
            from rdkit import Chem
            for alert in self.alerts:
                pattern = self._compiled_patterns.get(alert.name)
                if pattern:
                    try:
                        match_list = mol.GetSubstructMatches(pattern)
                        if match_list:
                            matches.append(AlertMatch(
                                name=alert.name,
                                type=alert.type,
                                smarts=alert.smarts,
                                risk_level=alert.risk_level.value,
                                description=alert.description,
                                match_count=len(match_list)
                            ))
                    except Exception:
                        pass
        else:
            # 降级模式：使用简单字符串匹配
            smiles_upper = self._current_smiles.upper()
            matches = self._fallback_string_match(smiles_upper)
        
        return matches
    
    def _fallback_string_match(self, smiles: str) -> List[AlertMatch]:
        """降级模式：基于简单字符串模式匹配"""
        matches = []
        
        # 定义简化的模式字符串
        fallback_patterns = {
            "芳香硝基": ("O=[N+]([O-])", "NO2"),
            "芳香伯胺": ("NC", "NH2"),
            "环氧化物": ("C1OC1",),
            "氮丙啶": ("C1NC1",),
            "肼/联氨": ("NN",),
            "卤代烷基": ("CL", "BR", "F", "I"),
            "多环芳烃": ("C=CC=CC=CC=CC",),
            "醛基": ("C=O", "CHO"),
            "酰氯": ("C(=O)CL", "COCL"),
            "Michael受体": ("C=CC=O",),
            "醌类": ("O=C1C=CC(=O)",),
            "亚硝基": ("N=O", "N-O"),
            "硫醇": ("SH",),
        }
        
        alert_map = {a.name: a for a in self.alerts}
        matched_names = set()
        
        for alert_name, patterns in fallback_patterns.items():
            if alert_name in matched_names:
                continue
            for pattern in patterns:
                if pattern in smiles:
                    alert = alert_map.get(alert_name)
                    if alert:
                        matches.append(AlertMatch(
                            name=alert.name,
                            type=alert.type,
                            smarts=alert.smarts,
                            risk_level=alert.risk_level.value,
                            description=alert.description,
                            match_count=smiles.count(pattern)
                        ))
                        matched_names.add(alert_name)
                        break
        
        return matches
    
    def _calculate_risk_score(self, matches: List[AlertMatch]) -> Tuple[float, str]:
        """计算风险评分和等级"""
        if not matches:
            return 0.0, "NONE"
        
        # 获取匹配警示的权重
        alert_weights = {a.name: (a.weight, a.risk_level) for a in self.alerts}
        
        total_weight = 0.0
        max_risk = RiskLevel.LOW
        
        for match in matches:
            weight, risk = alert_weights.get(match.name, (0.3, RiskLevel.LOW))
            total_weight += weight * match.match_count
            
            if risk == RiskLevel.HIGH:
                max_risk = RiskLevel.HIGH
            elif risk == RiskLevel.MEDIUM and max_risk != RiskLevel.HIGH:
                max_risk = RiskLevel.MEDIUM
        
        # 计算风险评分 (0-1)
        risk_score = min(total_weight / 2.0, 1.0)
        
        return round(risk_score, 2), max_risk.value
    
    def _generate_recommendations(self, matches: List[AlertMatch], risk_level: str) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("⚠️ 检测到高风险毒性结构，强烈建议进行Ames试验验证")
            recommendations.append("⚠️ 考虑结构优化以降低潜在毒性风险")
        elif risk_level == "MEDIUM":
            recommendations.append("⚡ 检测到中等风险结构，建议进行体外毒性筛选")
            recommendations.append("⚡ 评估结构修饰对活性和毒性的影响")
        
        # 基于具体警示类型给出建议
        alert_types = set(m.type for m in matches)
        
        if "mutagenic" in alert_types or "carcinogenic" in alert_types:
            recommendations.append("🧬 建议进行致突变性评估（如Ames、染色体畸变试验）")
        if "hepatotoxic" in alert_types:
            recommendations.append("🫀 建议评估肝毒性风险")
        if "alkylating" in alert_types:
            recommendations.append("⚗️ 烷基化剂具有高反应性，需特别关注脱靶效应")
        if "reactive" in alert_types:
            recommendations.append("🔄 反应性基团可能影响代谢稳定性，建议评估血浆稳定性")
        
        if not recommendations:
            recommendations.append("✅ 未检测到显著毒性警示结构，但仍建议进行标准安全性评估")
        
        return recommendations
    
    def scan(self, smiles: str) -> ScanResult:
        """
        扫描SMILES字符串，识别毒性警示结构
        
        Args:
            smiles: 输入的SMILES字符串
            
        Returns:
            ScanResult: 扫描结果
        """
        self._current_smiles = smiles  # 保存供降级模式使用
        mol, mol_weight = self._parse_smiles(smiles)
        matches = self._match_alerts(mol)
        risk_score, risk_level = self._calculate_risk_score(matches)
        recommendations = self._generate_recommendations(matches, risk_level)
        
        return ScanResult(
            input_smiles=smiles,
            mol_weight=round(mol_weight, 2) if mol_weight else None,
            alert_count=len(matches),
            risk_score=risk_score,
            risk_level=risk_level,
            alerts=matches,
            recommendations=recommendations
        )
    
    def format_text_output(self, result: ScanResult, detail: str = "standard") -> str:
        """格式化文本输出"""
        lines = []
        lines.append("=" * 60)
        lines.append("          毒性结构警示扫描报告")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"输入SMILES: {result.input_smiles}")
        if result.mol_weight:
            lines.append(f"分子量: {result.mol_weight} Da")
        lines.append("")
        
        # 风险等级显示
        risk_emojis = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "NONE": "✅"}
        risk_emoji = risk_emojis.get(result.risk_level, "⚪")
        lines.append(f"风险等级: {risk_emoji} {result.risk_level}")
        lines.append(f"风险评分: {result.risk_score:.2f} / 1.0")
        lines.append(f"警示数量: {result.alert_count}")
        lines.append("")
        
        if result.alerts:
            lines.append("-" * 60)
            lines.append("检测到的警示结构:")
            lines.append("-" * 60)
            for i, alert in enumerate(result.alerts, 1):
                lines.append(f"\n{i}. {alert.name}")
                lines.append(f"   类型: {alert.type}")
                lines.append(f"   风险: {alert.risk_level}")
                if detail in ("standard", "full"):
                    lines.append(f"   SMARTS: {alert.smarts}")
                if detail == "full":
                    lines.append(f"   描述: {alert.description}")
                if alert.match_count > 1:
                    lines.append(f"   匹配次数: {alert.match_count}")
        
        lines.append("")
        lines.append("-" * 60)
        lines.append("建议:")
        lines.append("-" * 60)
        for rec in result.recommendations:
            lines.append(f"  {rec}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("注意: 本工具基于已知警示结构，不能替代全面的毒理学评估")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_json_output(self, result: ScanResult) -> str:
        """格式化JSON输出"""
        data = {
            "input": result.input_smiles,
            "mol_weight": result.mol_weight,
            "alert_count": result.alert_count,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "alerts": [
                {
                    "name": a.name,
                    "type": a.type,
                    "smarts": a.smarts,
                    "risk_level": a.risk_level,
                    "description": a.description,
                    "match_count": a.match_count
                }
                for a in result.alerts
            ],
            "recommendations": result.recommendations
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Toxicity Structure Alert - 扫描药物分子结构的毒性警示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py -i "O=[N+]([O-])c1ccccc1"
  python main.py -i "C1CCCCC1" -f json
  python main.py -i "c1ccc2c(c1)ccc1c3ccccc3ccc21" -d full
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入的SMILES字符串"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="text",
        help="输出格式 (默认: text)"
    )
    
    parser.add_argument(
        "--detail", "-d",
        choices=["basic", "standard", "full"],
        default="standard",
        help="详细程度 (默认: standard)"
    )
    
    args = parser.parse_args()
    
    # 创建扫描器并执行扫描
    scanner = ToxicityAlertScanner()
    result = scanner.scan(args.input)
    
    # 输出结果
    if args.format == "json":
        print(scanner.format_json_output(result))
    else:
        print(scanner.format_text_output(result, args.detail))
    
    # 返回非零退出码如果检测到高风险
    if result.risk_level == "HIGH":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

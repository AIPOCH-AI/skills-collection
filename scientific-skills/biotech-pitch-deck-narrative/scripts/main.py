#!/usr/bin/env python3
"""
Biotech Pitch Deck Narrative Engine

将复杂的生物技术科学数据转化为投资人能理解的商业故事。
用于优化融资路演PPT的叙事逻辑。

Usage:
    python main.py analyze --input pitch.pptx --stage series-a
    python main.py generate --science "技术描述" --stage seed --focus market
    python main.py rewrite --section technology --content "..." --audience generalist-vc
"""

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class PitchStage(str, Enum):
    """融资阶段"""
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B = "series-b"
    SERIES_C = "series-c"
    IPO = "ipo"


class AudienceType(str, Enum):
    """目标受众类型"""
    GENERALIST_VC = "generalist-vc"      # 综合VC，非医疗专业
    HEALTHCARE_VC = "healthcare-vc"      # 医疗专业VC
    PHARMA_CORP = "pharma-corp"          # 药企BD/投资部
    ANGEL = "angel"                       # 天使投资人
    CORPORATE = "corporate"              # 企业投资者


class SectionType(str, Enum):
    """PPT章节类型"""
    HOOK = "hook"
    PROBLEM = "problem"
    SOLUTION = "solution"
    TECHNOLOGY = "technology"
    MARKET = "market"
    TRACTION = "traction"
    TEAM = "team"
    FINANCIALS = "financials"
    VISION = "vision"
    ASK = "ask"


class FocusArea(str, Enum):
    """优化重点领域"""
    MARKET = "market"
    TECHNOLOGY = "technology"
    TRACTION = "traction"
    TEAM = "team"
    FINANCIALS = "financials"


@dataclass
class SlideRecommendation:
    """单页PPT建议"""
    slide_number: int
    title: str
    key_message: str
    content_guidance: str
    visual_suggestion: str
    investor_question: str
    speaking_notes: str = ""


@dataclass
class RiskItem:
    """风险项及应对"""
    risk: str
    mitigation: str
    talking_points: List[str] = field(default_factory=list)


@dataclass
class QAItem:
    """问答准备"""
    question: str
    suggested_answer: str
    key_points: List[str] = field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard


@dataclass
class NarrativeOutput:
    """完整叙事输出"""
    narrative_arc: Dict[str, str]
    slide_recommendations: List[SlideRecommendation]
    terminology_mapping: Dict[str, str]
    scientific_risks: List[RiskItem]
    market_risks: List[RiskItem]
    regulatory_risks: List[RiskItem]
    q_a_preparation: List[QAItem]
    stage_specific_tips: List[str]


class BiotechNarrativeEngine:
    """
    生物技术叙事引擎
    
    核心功能：
    1. 科学术语 → 商业语言转换
    2. 叙事弧线生成
    3. PPT结构优化建议
    4. 投资人Q&A准备
    """
    
    # 科学术语到商业表达的映射
    TERMINOLOGY_MAP = {
        # 基础生物学术语
        "in vitro": "实验室环境",
        "in vivo": "活体实验",
        "in silico": "计算机模拟",
        "proof of concept": "概念验证",
        "mechanism of action": "作用机制",
        "pharmacokinetics": "药物代谢动力学 (PK)",
        "pharmacodynamics": "药效学 (PD)",
        "efficacy": "疗效",
        "safety profile": "安全性特征",
        "tolerability": "耐受性",
        
        # 基因/细胞治疗
        "viral vector": "病毒载体",
        "AAV": "腺相关病毒 (AAV)",
        "Lentivirus": "慢病毒",
        "CAR-T": "CAR-T细胞疗法",
        "ex vivo": "体外基因编辑",
        "in vivo gene editing": "体内基因编辑",
        "knockout": "基因敲除",
        "knockin": "基因插入",
        "off-target": "脱靶效应",
        "on-target": "靶向准确性",
        
        # 核酸药物
        "mRNA": "信使RNA (mRNA)",
        "siRNA": "小干扰RNA",
        "antisense oligonucleotide": "反义寡核苷酸",
        "lipid nanoparticle": "脂质纳米颗粒 (LNP)",
        "codon optimization": "密码子优化",
        "5' cap": "5'端帽结构",
        "poly-A tail": "多聚腺苷酸尾",
        
        # 小分子/抗体
        "small molecule": "小分子药物",
        "monoclonal antibody": "单克隆抗体",
        "bispecific antibody": "双特异性抗体",
        "ADC": "抗体偶联药物 (ADC)",
        "binding affinity": "结合亲和力",
        "Ki": "抑制常数",
        "IC50": "半数抑制浓度",
        "EC50": "半数有效浓度",
        
        # 临床阶段
        "IND-enabling": "IND申报准备",
        "IND": "新药临床试验申请",
        "Phase I": "I期临床（安全性）",
        "Phase II": "II期临床（有效性探索）",
        "Phase III": "III期临床（确证性试验）",
        "NDA/BLA": "新药上市申请",
        "pivotal trial": "关键性临床试验",
        "orphan drug": "孤儿药",
        "fast track": "快速通道认定",
        "breakthrough therapy": "突破性疗法认定",
    }
    
    # 各阶段投资人关注重点
    STAGE_PRIORITIES = {
        PitchStage.PRE_SEED: {
            "focus": ["team", "technology", "vision"],
            "metrics": ["科学突破潜力", "创始人资质", "技术独特性"],
            "risk_tolerance": "high",
            "typical_check": "$250K-$1M"
        },
        PitchStage.SEED: {
            "focus": ["technology", "problem", "market"],
            "metrics": ["概念验证数据", "市场规模", "初步IP布局"],
            "risk_tolerance": "medium-high",
            "typical_check": "$1M-$5M"
        },
        PitchStage.SERIES_A: {
            "focus": ["traction", "market", "solution"],
            "metrics": ["临床前/早期临床数据", "竞争格局", "监管路径清晰度"],
            "risk_tolerance": "medium",
            "typical_check": "$10M-$50M"
        },
        PitchStage.SERIES_B: {
            "focus": ["traction", "financials", "team_expansion"],
            "metrics": ["临床里程碑", "合作伙伴关系", "商业化准备"],
            "risk_tolerance": "medium-low",
            "typical_check": "$50M-$150M"
        },
        PitchStage.SERIES_C: {
            "focus": ["financials", "market_position", "exit"],
            "metrics": ["关键试验数据", "收入/管线价值", "退出路径"],
            "risk_tolerance": "low",
            "typical_check": "$100M+"
        },
    }
    
    # 受众特定的叙事调整
    AUDIENCE_ADJUSTMENTS = {
        AudienceType.GENERALIST_VC: {
            "explain_jargon": True,
            "use_analogies": True,
            "focus": "market_size_and_timing",
            "avoid": "deep_mechanism_details",
            "questions_to_address": [
                "这是什么意思（用最简单的话）？",
                "为什么是现在？",
                "市场规模真的有那么大吗？",
                "这和已上市公司有什么不同？"
            ]
        },
        AudienceType.HEALTHCARE_VC: {
            "explain_jargon": False,
            "use_analogies": False,
            "focus": "differentiation_and_clinical_design",
            "avoid": "oversimplification",
            "questions_to_address": [
                "KOL反馈如何？",
                "临床前模型是否可转化？",
                "IP freedom to operate?",
                "监管路径的潜在挑战？"
            ]
        },
        AudienceType.PHARMA_CORP: {
            "explain_jargon": False,
            "use_analogies": False,
            "focus": "partnership_potential",
            "avoid": "overpromising",
            "questions_to_address": [
                "与我们管线的协同性？",
                "所需投资和时间到POC？",
                "全球权利还是区域权利？",
                "生产可扩展性？"
            ]
        },
    }
    
    def __init__(self):
        self.terminology_map = self.TERMINOLOGY_MAP.copy()
    
    def translate_scientific_to_business(
        self, 
        text: str, 
        audience: AudienceType = AudienceType.GENERALIST_VC
    ) -> str:
        """
        将科学文本转换为商业语言
        
        Args:
            text: 原始科学文本
            audience: 目标受众
            
        Returns:
            转换后的商业文本
        """
        result = text
        
        # 基础术语替换
        for term, business_term in self.terminology_map.items():
            # 大小写不敏感替换，保持原大小写模式
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            result = pattern.sub(business_term, result)
        
        # 根据受众添加解释
        if audience == AudienceType.GENERALIST_VC:
            result = self._add_analogies_for_layman(result)
        
        return result
    
    def _add_analogies_for_layman(self, text: str) -> str:
        """为外行添加类比解释"""
        # 常见技术类比映射
        analogies = {
            "CRISPR": "（类似'分子剪刀'，可以精准修改DNA）",
            "mRNA疫苗": "（类似'体内工厂'，让身体自己产生治疗性蛋白）",
            "CAR-T": "（类似'活体药物'，改造患者自身免疫细胞来攻击癌症）",
            "抗体偶联药物": "（类似'智能导弹'，精准递送毒素到癌细胞）",
            "基因编辑": "（类似'基因的手术刀'，修复错误的DNA序列）",
        }
        
        result = text
        for concept, analogy in analogies.items():
            if concept in result and analogy not in result:
                result = result.replace(concept, f"{concept}{analogy}")
        
        return result
    
    def generate_narrative_arc(
        self,
        science_data: Dict[str, Any],
        target_stage: PitchStage,
        audience: AudienceType = AudienceType.GENERALIST_VC
    ) -> Dict[str, str]:
        """
        生成完整的叙事弧线
        
        Args:
            science_data: 科学数据字典
            target_stage: 目标融资阶段
            audience: 目标受众
            
        Returns:
            叙事弧线各部分
        """
        narrative = {}
        
        # Hook - 开场钩子
        narrative["hook"] = self._generate_hook(science_data, target_stage)
        
        # Problem - 问题陈述
        narrative["problem"] = self._generate_problem_statement(science_data, audience)
        
        # Solution - 解决方案
        narrative["solution"] = self._generate_solution_statement(science_data)
        
        # Why Now - 时机论证
        narrative["why_now"] = self._generate_why_now(science_data)
        
        # Market - 市场机会
        narrative["market"] = self._generate_market_narrative(science_data, target_stage)
        
        # Traction - 里程碑
        narrative["traction"] = self._generate_traction_narrative(science_data, target_stage)
        
        # Team - 团队资质
        narrative["team"] = self._generate_team_narrative(science_data, target_stage)
        
        # Ask - 融资需求
        narrative["ask"] = self._generate_ask_narrative(science_data, target_stage)
        
        # Vision - 愿景
        narrative["vision"] = self._generate_vision_statement(science_data)
        
        return narrative
    
    def _generate_hook(self, data: Dict[str, Any], stage: PitchStage) -> str:
        """生成开场钩子"""
        technology = data.get("technology", "")
        
        # 根据技术类型选择钩子
        if "cancer" in technology.lower() or "肿瘤" in technology:
            return "每年[X]万癌症患者等待更有效的治疗方案，我们的[技术]正在改写这一现实。"
        elif "rare disease" in technology.lower() or "罕见病" in technology:
            return "全球[X]万罕见病患者无药可治，我们的平台将为这一被忽视的群体带来希望。"
        elif "vaccine" in technology.lower() or "疫苗" in technology:
            return "后疫情时代，疫苗技术正在经历[X]年来最大的范式转移。"
        elif "AI" in technology.upper() or "artificial intelligence" in technology.lower():
            return "AI正在重塑药物发现的每一个环节，而我们已经跑通了从算法到临床的完整闭环。"
        else:
            return "我们开发了一项突破性的[技术]，有望改变[疾病领域]的治疗格局。"
    
    def _generate_problem_statement(self, data: Dict[str, Any], audience: AudienceType) -> str:
        """生成问题陈述"""
        current_standard = data.get("current_standard", "现有治疗方案")
        unmet_need = data.get("unmet_need", "存在重大未满足需求")
        
        if audience == AudienceType.GENERALIST_VC:
            return f"当前{current_standard}面临三大痛点：疗效有限、副作用严重、可及性差。{unmet_need}"
        else:
            return f"现有治疗存在明显局限性：{unmet_need}。临床急需更安全有效的替代方案。"
    
    def _generate_solution_statement(self, data: Dict[str, Any]) -> str:
        """生成解决方案陈述"""
        technology = data.get("technology", "我们的技术平台")
        moa = data.get("mechanism", "")
        
        if moa:
            return f"{technology}通过{moa}，直击疾病根源，而非仅仅缓解症状。"
        return f"{technology}代表了该领域的下一代标准，有潜力成为新的治疗范式。"
    
    def _generate_why_now(self, data: Dict[str, Any]) -> str:
        """生成时机论证"""
        reasons = [
            "监管环境成熟：FDA/NMPA对[技术类型]的监管路径逐渐清晰",
            "技术就绪：关键科学障碍已被突破，进入工程优化阶段",
            "市场教育完成：大药企的[相关交易]验证了该方向的商业价值",
            "人才储备：核心团队在该领域平均[X]年经验，时机窗口正在收窄"
        ]
        return " ".join(reasons[:3])
    
    def _generate_market_narrative(self, data: Dict[str, Any], stage: PitchStage) -> str:
        """生成市场叙事"""
        indication = data.get("indication", "目标适应症")
        tam = data.get("tam", "数十亿美元")
        
        if stage in [PitchStage.PRE_SEED, PitchStage.SEED]:
            return f"{indication}全球市场规模超过{tam}，且以[X]%年增长率扩张。我们的平台技术可延伸至多个适应症，潜在市场可达[Platform TAM]。"
        else:
            return f"{indication}的顶峰销售潜力预计超过$tam。基于目前的临床数据，我们有信心抢占[X]%市场份额。"
    
    def _generate_traction_narrative(self, data: Dict[str, Any], stage: PitchStage) -> str:
        """生成功能点里程碑叙事"""
        milestones = data.get("milestones", [])
        
        if stage == PitchStage.PRE_SEED:
            return "已完成概念验证，获得[机构]的种子数据支持，专利布局覆盖核心 markets。"
        elif stage == PitchStage.SEED:
            return f"关键里程碑：{', '.join(milestones[:3]) if milestones else '临床前数据积极，即将提交IND'}"
        elif stage == PitchStage.SERIES_A:
            return f"临床进展：{', '.join(milestones[:3]) if milestones else 'I期临床进行中，初步数据积极'}"
        else:
            return f"临床里程碑：{', '.join(milestones[:3]) if milestones else 'II期临床达到主要终点'}"
    
    def _generate_team_narrative(self, data: Dict[str, Any], stage: PitchStage) -> str:
        """生成团队叙事"""
        team_highlights = data.get("team_highlights", [])
        
        if stage in [PitchStage.PRE_SEED, PitchStage.SEED]:
            return "创始团队来自[顶级机构]，在[领域]拥有[X]年经验，发表过[Nature/Cell/Science]论文[XX]篇。"
        else:
            return f"核心团队具备从0到1再到上市的完整经验：{', '.join(team_highlights[:3]) if team_highlights else '包括前[大药企]VP、成功退出经验的CEO'}"
    
    def _generate_ask_narrative(self, data: Dict[str, Any], stage: PitchStage) -> str:
        """生成融资需求叙事"""
        raise_amount = data.get("raise_amount", "本轮融资")
        use_of_funds = data.get("use_of_funds", [])
        
        uses = "、".join(use_of_funds[:3]) if use_of_funds else "推进临床开发、扩展团队、加强专利布局"
        return f"本轮寻求{raise_amount}，用于{uses}，预期[XX个月]达到[关键里程碑]。"
    
    def _generate_vision_statement(self, data: Dict[str, Any]) -> str:
        """生成愿景陈述"""
        return "成为[疾病领域]的领导者，通过[技术平台]为全球患者提供变革性治疗方案，最终成为一家完全整合的生物技术公司。"
    
    def generate_slide_recommendations(
        self,
        science_data: Dict[str, Any],
        target_stage: PitchStage,
        audience: AudienceType
    ) -> List[SlideRecommendation]:
        """
        生成PPT页面建议
        
        Returns:
            每页PPT的详细建议列表
        """
        slides = []
        
        # 根据阶段确定页面结构
        if target_stage in [PitchStage.PRE_SEED, PitchStage.SEED]:
            slide_structure = [
                (1, "封面", "一句话定位"),
                (2, "问题", "未满足的医疗需求"),
                (3, "解决方案", "技术如何解决问题"),
                (4, "技术", "平台技术和差异化"),
                (5, "市场", "TAM/SAM/SOM分析"),
                (6, "竞争格局", "竞争定位和护城河"),
                (7, "里程碑", "已达成和未来计划"),
                (8, "团队", "核心创始人介绍"),
                (9, "融资需求", "资金用途和里程碑"),
                (10, "愿景", "长期价值和退出路径")
            ]
        else:
            slide_structure = [
                (1, "封面", "公司定位+阶段"),
                (2, "投资亮点", "5-6个bullet总结"),
                (3, "问题与机会", "临床痛点+市场机会"),
                (4, "解决方案", "产品和技术概述"),
                (5, "临床数据", "关键数据和解读"),
                (6, "开发计划", "监管路径和时间线"),
                (7, "市场与竞争", "商业化策略"),
                (8, "团队", "管理层+顾问+董事会"),
                (9, "财务与融资", "资金用途和里程碑"),
                (10, "附录", "详细数据")
            ]
        
        for num, section, focus in slide_structure:
            rec = self._create_slide_recommendation(
                num, section, focus, science_data, target_stage, audience
            )
            slides.append(rec)
        
        return slides
    
    def _create_slide_recommendation(
        self,
        num: int,
        section: str,
        focus: str,
        data: Dict[str, Any],
        stage: PitchStage,
        audience: AudienceType
    ) -> SlideRecommendation:
        """创建单页PPT建议"""
        
        recommendations = {
            "封面": {
                "title": f"{data.get('company_name', '公司名')} - {data.get('tagline', '一句话定位')}",
                "key_message": "清晰传达'你是谁'和'你做什么'",
                "content": "Logo + 一句话定位（15字以内）+ 融资阶段",
                "visual": "简洁专业，避免过多装饰",
                "question": "你们的核心差异化是什么？"
            },
            "问题": {
                "title": "巨大的未满足医疗需求",
                "key_message": "问题真实存在且值得解决",
                "content": "患者痛点 + 现有治疗局限 + 经济负担数据",
                "visual": "患者旅程图或痛点对比图",
                "question": "这个问题真的那么严重吗？"
            },
            "解决方案": {
                "title": "我们的突破性解决方案",
                "key_message": "我们有独特的方法解决这个问题",
                "content": "产品概述 + 作用机制（简化版）+ 预期获益",
                "visual": "作用机制示意图或前后对比",
                "question": "为什么现有公司没做这个？"
            },
            "技术": {
                "title": "独特的技术平台" if stage in [PitchStage.PRE_SEED, PitchStage.SEED] else "差异化技术平台",
                "key_message": "技术可行且有护城河",
                "content": "平台技术 + 关键数据 + 专利布局 + 技术壁垒",
                "visual": "平台示意图或技术对比表",
                "question": "技术的可扩展性和可生产性如何？"
            },
            "临床数据": {
                "title": "积极的早期临床数据" if stage == PitchStage.SERIES_A else "验证性的临床数据",
                "key_message": "数据支持我们的科学假设",
                "content": "研究设计 + 关键终点 + 安全性数据 + 患者案例",
                "visual": "瀑布图 + 蜘蛛图 + 泳道图",
                "question": "这些数据足够支持下一步开发吗？"
            },
            "市场": {
                "title": "数十亿美元的市场机会",
                "key_message": "市场足够大，值得投资",
                "content": "TAM/SAM/SOM + 增长驱动因素 + 定价策略",
                "visual": "市场分层图或增长曲线",
                "question": "你如何计算的市场规模？"
            },
            "里程碑": {
                "title": "显著的进展和清晰的路线图",
                "key_message": "我们有执行力，且未来18个月有明确里程碑",
                "content": "过去成就 + 未来18个月计划 + 关键决策点",
                "visual": "时间线图（泳道图样式）",
                "question": "下一个价值拐点是什么时候？"
            },
            "团队": {
                "title": "世界级的团队",
                "key_message": "团队有能力执行这个计划",
                "content": "创始人 + 核心团队 + 顾问/KOL + 董事会",
                "visual": "团队照片 + 核心成就",
                "question": "团队是否有足够的行业经验？"
            },
            "融资需求": {
                "title": "本轮融资",
                "key_message": "资金用途清晰，里程碑可衡量",
                "content": "融资额 + 资金用途饼图 + 关键里程碑 + 退出前景",
                "visual": "资金用途饼图 + 里程碑时间线",
                "question": "这轮之后还需要融多少？"
            },
        }
        
        rec = recommendations.get(section, {
            "title": section,
            "key_message": focus,
            "content": "根据需要填充",
            "visual": "简洁清晰",
            "question": "请详细说明"
        })
        
        return SlideRecommendation(
            slide_number=num,
            title=rec["title"],
            key_message=rec["key_message"],
            content_guidance=rec["content"],
            visual_suggestion=rec["visual"],
            investor_question=rec["question"],
            speaking_notes=f"[{section}] 演讲要点：准备2-3个支撑故事，用时约2-3分钟"
        )
    
    def prepare_qa(
        self,
        science_data: Dict[str, Any],
        target_stage: PitchStage,
        audience: AudienceType
    ) -> List[QAItem]:
        """
        准备投资人Q&A
        
        Returns:
            预期问题和建议回答
        """
        common_questions = [
            QAItem(
                question="你们的竞争护城河是什么？",
                suggested_answer="我们的护城河来自三个方面：(1)专利组合覆盖核心技术和适应症；(2)难以复制的专有数据集/ know-how；(3)率先进入关键临床试验带来的时间优势。",
                key_points=["IP保护", "数据资产", "时间窗口"],
                difficulty="medium"
            ),
            QAItem(
                question="如果临床试验失败，你们还有plan B吗？",
                suggested_answer="我们的平台技术具有多个适应症应用。即使首个适应症遇到挑战，我们可以快速将资源转向其他高价值适应症。此外，技术平台本身具有合作价值。",
                key_points=["平台韧性", "适应症多元化", "合作机会"],
                difficulty="hard"
            ),
            QAItem(
                question="你们需要多少资金才能达到关键里程碑？",
                suggested_answer="本轮融资[X]百万美元，将支持我们完成[具体里程碑]，预计在[时间]实现。达到下一个价值拐点（[事件]）后，公司估值预期大幅提升。",
                key_points=["明确的资金需求", "可衡量的里程碑", "估值增长逻辑"],
                difficulty="easy"
            ),
            QAItem(
                question="你们的退出策略是什么？",
                suggested_answer="我们有多种退出路径：(1)被大药企收购（参考最近的[交易案例]）；(2)IPO（参照[可比公司]的路径）；(3)战略合作。我们倾向于[首选路径]，因为它能为投资者带来最佳回报。",
                key_points=["可比交易", "战略价值", "投资者回报"],
                difficulty="medium"
            ),
            QAItem(
                question="监管路径有什么风险？",
                suggested_answer="我们已经与FDA/[其他监管机构]进行了pre-IND/科学建议会议，获得积极反馈。主要监管策略是[简述]。潜在风险包括[简述]，我们的缓解措施是[简述]。",
                key_points=["监管沟通", "清晰策略", "风险识别"],
                difficulty="medium"
            ),
        ]
        
        # 根据受众添加特定问题
        if audience == AudienceType.HEALTHCARE_VC:
            common_questions.extend([
                QAItem(
                    question="你们的临床前模型向人体转化的可信度有多高？",
                    suggested_answer="我们使用了多种互补的临床前模型：[列举模型]。更重要的是，我们的[关键机制]已在[人体样本/早期临床]中得到验证，增强了转化信心。",
                    key_points=["多模型验证", "人体数据支持", "转化医学证据"],
                    difficulty="hard"
                ),
            ])
        
        return common_questions
    
    def analyze_risks(
        self,
        science_data: Dict[str, Any],
        target_stage: PitchStage
    ) -> Dict[str, List[RiskItem]]:
        """
        分析风险并提供应对话术
        
        Returns:
            科学风险、市场风险、监管风险的分类列表
        """
        scientific_risks = [
            RiskItem(
                risk="临床转化风险：动物模型结果可能无法在人体中复现",
                mitigation="使用多种互补模型，已在人体组织中验证关键机制",
                talking_points=["多模型策略", "转化医学证据", "适应性试验设计"]
            ),
            RiskItem(
                risk="安全性风险：可能出现意外的毒副作用",
                mitigation="严谨的安全性监测计划，同类产品已有安全性数据支持",
                talking_points=["同类验证", "保守的起始剂量", "独立安全委员会"]
            ),
        ]
        
        market_risks = [
            RiskItem(
                risk="竞争风险：大药企可能推出竞争性产品",
                mitigation="快速推进临床，建立先发优势；差异化定位",
                talking_points=["速度优势", "差异化定位", "合作可能性"]
            ),
            RiskItem(
                risk="定价/支付风险：可能面临支付方压力",
                mitigation="开发具有显著临床获益的产品，为高价提供依据",
                talking_points=["未满足需求", "卫生经济学数据", "患者倡导支持"]
            ),
        ]
        
        regulatory_risks = [
            RiskItem(
                risk="监管延迟风险：审批时间可能超出预期",
                mitigation="与监管机构保持密切沟通，充分准备申报材料",
                talking_points=["监管关系", "CMC准备", "全球同步申报策略"]
            ),
        ]
        
        return {
            "scientific": scientific_risks,
            "market": market_risks,
            "regulatory": regulatory_risks
        }
    
    def generate_full_report(
        self,
        science_data: Dict[str, Any],
        target_stage: PitchStage,
        audience: AudienceType = AudienceType.GENERALIST_VC
    ) -> NarrativeOutput:
        """
        生成完整的叙事优化报告
        
        This is the main entry point for comprehensive narrative generation.
        """
        narrative_arc = self.generate_narrative_arc(science_data, target_stage, audience)
        
        slide_recommendations = self.generate_slide_recommendations(
            science_data, target_stage, audience
        )
        
        # 创建术语映射（基于输入数据）
        terminology_mapping = {}
        input_text = json.dumps(science_data)
        for term, business in self.terminology_map.items():
            if term.lower() in input_text.lower():
                terminology_mapping[term] = business
        
        risks = self.analyze_risks(science_data, target_stage)
        
        qa_items = self.prepare_qa(science_data, target_stage, audience)
        
        # 阶段特定建议
        stage_tips = self._get_stage_specific_tips(target_stage)
        
        return NarrativeOutput(
            narrative_arc=narrative_arc,
            slide_recommendations=slide_recommendations,
            terminology_mapping=terminology_mapping,
            scientific_risks=risks["scientific"],
            market_risks=risks["market"],
            regulatory_risks=risks["regulatory"],
            q_a_preparation=qa_items,
            stage_specific_tips=stage_tips
        )
    
    def _get_stage_specific_tips(self, stage: PitchStage) -> List[str]:
        """获取阶段特定的建议"""
        tips = {
            PitchStage.PRE_SEED: [
                "强调科学突破的潜力和团队资质",
                "避免过度承诺临床时间表",
                "展示对监管路径的基本理解",
                "准备解释为什么这个时机是对的"
            ],
            PitchStage.SEED: [
                "突出概念验证数据",
                "清晰阐述技术差异化",
                "展示初步的市场理解",
                "说明资金用途和里程碑"
            ],
            PitchStage.SERIES_A: [
                "临床数据是核心，准备详细解读",
                "竞争格局分析要深入",
                "监管路径要清晰",
                "展示团队执行力"
            ],
            PitchStage.SERIES_B: [
                "强调临床里程碑的达成",
                "展示商业化准备",
                "建立与大药企的合作关系",
                "清晰的退出路径"
            ],
        }
        return tips.get(stage, ["根据具体阶段调整叙事重点"])


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description="生物技术路演叙事优化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py generate --science "CRISPR基因编辑治疗镰刀型贫血" --stage series-a --audience healthcare-vc
  python main.py rewrite --section technology --content "我们使用AAV载体递送CRISPR..." --audience generalist-vc
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="基于科学数据生成商业叙事")
    gen_parser.add_argument("--science", "-s", required=True, help="科学/技术描述")
    gen_parser.add_argument("--stage", required=True, choices=[s.value for s in PitchStage],
                          help="融资阶段")
    gen_parser.add_argument("--audience", default="generalist-vc",
                          choices=[a.value for a in AudienceType],
                          help="目标受众")
    gen_parser.add_argument("--focus", default="market",
                          choices=[f.value for f in FocusArea],
                          help="优化重点")
    gen_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # rewrite 命令
    rewrite_parser = subparsers.add_parser("rewrite", help="优化特定章节")
    rewrite_parser.add_argument("--section", "-s", required=True,
                               choices=[s.value for s in SectionType],
                               help="PPT章节")
    rewrite_parser.add_argument("--content", "-c", required=True,
                               help="当前内容（文件路径或直接文本）")
    rewrite_parser.add_argument("--audience", default="generalist-vc",
                               choices=[a.value for a in AudienceType],
                               help="目标受众")
    rewrite_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # analyze 命令（占位符，可扩展支持PPT解析）
    analyze_parser = subparsers.add_parser("analyze", help="分析现有PPT")
    analyze_parser.add_argument("--input", "-i", required=True, help="PPT文件路径")
    analyze_parser.add_argument("--stage", required=True, choices=[s.value for s in PitchStage])
    analyze_parser.add_argument("--output", "-o", help="输出文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    engine = BiotechNarrativeEngine()
    
    if args.command == "generate":
        # 构建科学数据字典
        science_data = {
            "technology": args.science,
            "company_name": "[公司名称]",
            "tagline": "[一句话定位]"
        }
        
        target_stage = PitchStage(args.stage)
        audience = AudienceType(args.audience)
        
        # 生成完整报告
        output = engine.generate_full_report(science_data, target_stage, audience)
        
        # 转换为可序列化的字典
        result = {
            "narrative_arc": output.narrative_arc,
            "slide_recommendations": [
                {
                    "slide_number": s.slide_number,
                    "title": s.title,
                    "key_message": s.key_message,
                    "content_guidance": s.content_guidance,
                    "visual_suggestion": s.visual_suggestion,
                    "investor_question": s.investor_question,
                    "speaking_notes": s.speaking_notes
                }
                for s in output.slide_recommendations
            ],
            "terminology_mapping": output.terminology_mapping,
            "risk_mitigation": {
                "scientific_risks": [
                    {"risk": r.risk, "mitigation": r.mitigation, "talking_points": r.talking_points}
                    for r in output.scientific_risks
                ],
                "market_risks": [
                    {"risk": r.risk, "mitigation": r.mitigation, "talking_points": r.talking_points}
                    for r in output.market_risks
                ],
                "regulatory_risks": [
                    {"risk": r.risk, "mitigation": r.mitigation, "talking_points": r.talking_points}
                    for r in output.regulatory_risks
                ]
            },
            "q_a_preparation": [
                {
                    "question": q.question,
                    "suggested_answer": q.suggested_answer,
                    "key_points": q.key_points,
                    "difficulty": q.difficulty
                }
                for q in output.q_a_preparation
            ],
            "stage_specific_tips": output.stage_specific_tips
        }
        
        # 输出
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            Path(args.output).write_text(json_output, encoding="utf-8")
            print(f"报告已保存到: {args.output}")
        else:
            print(json_output)
    
    elif args.command == "rewrite":
        # 读取内容
        content = args.content
        if Path(content).exists():
            content = Path(content).read_text(encoding="utf-8")
        
        audience = AudienceType(args.audience)
        
        # 翻译为商业语言
        translated = engine.translate_scientific_to_business(content, audience)
        
        # 添加章节特定的建议
        section_tips = {
            SectionType.TECHNOLOGY: "技术章节建议：用类比帮助理解，强调可扩展性和差异化",
            SectionType.PROBLEM: "问题章节建议：用患者故事或数据让问题具象化",
            SectionType.SOLUTION: "解决方案建议：聚焦价值主张，而非技术细节",
            SectionType.MARKET: "市场章节建议：展示对竞争格局的深入理解",
            SectionType.TRACTION: "里程碑建议：强调数据质量和执行能力",
        }
        
        result = {
            "original": content,
            "rewritten": translated,
            "section": args.section,
            "audience": args.audience,
            "tips": section_tips.get(SectionType(args.section), "根据章节调整叙事")
        }
        
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            Path(args.output).write_text(json_output, encoding="utf-8")
            print(f"重写结果已保存到: {args.output}")
        else:
            print(json_output)
    
    elif args.command == "analyze":
        # 占位符：未来可集成python-pptx解析PPT
        print("PPT分析功能正在开发中...")
        print(f"将分析文件: {args.input}")
        print(f"针对阶段: {args.stage}")
        print("建议：使用 'generate' 命令基于您的内容描述生成叙事建议")


if __name__ == "__main__":
    main()

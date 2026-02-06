#!/usr/bin/env python3
"""
Blockbuster Therapy Predictor
预测早期技术路线成为重磅炸弹疗法的潜力

数据维度：临床试验 + 专利布局 + VC融资
"""

import json
import argparse
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import random


class InvestmentRecommendation(Enum):
    """投资建议等级"""
    STRONG_BUY = "强烈推荐"
    BUY = "推荐"
    HOLD = "观望"
    CAUTION = "谨慎"


@dataclass
class TechnologyRoute:
    """技术路线数据模型"""
    name: str
    category: str
    description: str
    
    # 临床试验数据
    clinical_trials_phase1: int = 0
    clinical_trials_phase2: int = 0
    clinical_trials_phase3: int = 0
    clinical_success_rate: float = 0.0
    avg_time_to_market: float = 0.0  # 年
    indications_count: int = 0
    
    # 专利数据
    patent_count: int = 0
    patent_growth_rate: float = 0.0  # 年增长率
    core_patents: int = 0
    geographic_coverage: int = 0  # 覆盖国家数
    
    # 融资数据
    total_funding_usd: float = 0.0  # 百万美元
    funding_rounds: int = 0
    top_vc_backed: bool = False
    last_valuation_usd: float = 0.0  # 百万美元
    companies_count: int = 0


@dataclass
class PredictionResult:
    """预测结果模型"""
    tech_name: str
    maturity_score: float
    market_potential_score: float
    momentum_score: float
    blockbuster_index: float
    recommendation: str
    key_drivers: List[str]
    risk_factors: List[str]
    timeline_prediction: str


class ClinicalDataAnalyzer:
    """临床试验数据分析器"""
    
    @staticmethod
    def calculate_clinical_score(tech: TechnologyRoute) -> float:
        """计算临床阶段评分 (0-100)"""
        # 试验阶段权重
        phase_weights = {1: 0.2, 2: 0.5, 3: 0.8}
        total_trials = (tech.clinical_trials_phase1 + 
                       tech.clinical_trials_phase2 + 
                       tech.clinical_trials_phase3)
        
        if total_trials == 0:
            return 10.0  # 基础分
        
        weighted_score = (
            tech.clinical_trials_phase1 * phase_weights[1] +
            tech.clinical_trials_phase2 * phase_weights[2] +
            tech.clinical_trials_phase3 * phase_weights[3]
        ) / total_trials * 100
        
        # 成功率调整
        weighted_score *= (0.5 + tech.clinical_success_rate)
        
        # 适应证多样性加成
        indication_bonus = min(tech.indications_count * 2, 15)
        
        return min(weighted_score + indication_bonus, 100)


class PatentAnalyzer:
    """专利布局分析器"""
    
    @staticmethod
    def calculate_patent_depth_score(tech: TechnologyRoute) -> float:
        """计算专利深度评分 (0-100)"""
        if tech.patent_count == 0:
            return 5.0
        
        # 基础专利数量分
        patent_base = min(tech.patent_count / 10, 40)
        
        # 核心专利质量分
        core_quality = min(tech.core_patents * 3, 30)
        
        # 增长率分
        growth_score = min(tech.patent_growth_rate * 2, 20)
        
        # 地理覆盖分
        geo_score = min(tech.geographic_coverage * 2, 10)
        
        return min(patent_base + core_quality + growth_score + geo_score, 100)


class FundingAnalyzer:
    """融资数据分析器"""
    
    @staticmethod
    def calculate_funding_score(tech: TechnologyRoute) -> float:
        """计算融资阶段评分 (0-100)"""
        if tech.total_funding_usd == 0:
            return 5.0
        
        # 资金规模分
        funding_score = min(tech.total_funding_usd / 50, 40)
        
        # 轮次成熟度分
        round_score = min(tech.funding_rounds * 8, 25)
        
        # 顶级VC背书分
        vc_bonus = 20 if tech.top_vc_backed else 0
        
        # 公司数量分（生态活跃度）
        ecosystem_score = min(tech.companies_count * 3, 15)
        
        return min(funding_score + round_score + vc_bonus + ecosystem_score, 100)


class MarketPotentialEvaluator:
    """市场潜力评估器"""
    
    MARKET_SIZE_ESTIMATES = {
        "PROTAC": 35.0,  # 2030年预估，十亿美元
        "mRNA": 45.0,
        "CRISPR": 25.0,
        "CAR-T": 20.0,
        "Bispecific": 30.0,
        "ADC": 28.0,
        "Cell Therapy": 22.0,
        "Gene Therapy": 18.0,
        "RNAi": 15.0,
        "Allogeneic": 12.0,
    }
    
    UNMET_NEED_SCORES = {
        "PROTAC": 85,  # 难成药靶点突破
        "mRNA": 90,    # 疫苗+肿瘤免疫
        "CRISPR": 88,  # 遗传病治愈
        "CAR-T": 75,   # 血液瘤已验证，实体瘤待突破
        "Bispecific": 80,
        "ADC": 78,
        "Cell Therapy": 72,
        "Gene Therapy": 85,
        "RNAi": 70,
        "Allogeneic": 82,
    }
    
    COMPETITIVE_LANDSCORE = {
        "PROTAC": 75,   # 中等竞争，差异化空间大
        "mRNA": 65,     # 竞争激烈但市场大
        "CRISPR": 70,   # 技术门槛高
        "CAR-T": 60,    # 竞争激烈
        "Bispecific": 65,
        "ADC": 70,
        "Cell Therapy": 68,
        "Gene Therapy": 72,
        "RNAi": 75,
        "Allogeneic": 70,
    }
    
    @classmethod
    def calculate_market_potential(cls, tech_name: str) -> float:
        """计算市场潜力评分 (0-100)"""
        market_size = cls.MARKET_SIZE_ESTIMATES.get(tech_name, 10.0)
        unmet_need = cls.UNMET_NEED_SCORES.get(tech_name, 60)
        competitive = cls.COMPETITIVE_LANDSCORE.get(tech_name, 60)
        
        # 市场规模标准化 (最大50分)
        size_score = min(market_size / 50 * 50, 50)
        
        # 未满足需求 (35分)
        need_score = unmet_need * 0.35
        
        # 竞争格局 (15分)
        comp_score = competitive * 0.15
        
        return min(size_score + need_score + comp_score, 100)


class BlockbusterPredictor:
    """重磅炸弹疗法预测引擎"""
    
    def __init__(self):
        self.clinical_analyzer = ClinicalDataAnalyzer()
        self.patent_analyzer = PatentAnalyzer()
        self.funding_analyzer = FundingAnalyzer()
        self.market_evaluator = MarketPotentialEvaluator()
    
    def calculate_maturity_score(self, tech: TechnologyRoute) -> float:
        """计算技术成熟度评分"""
        clinical = self.clinical_analyzer.calculate_clinical_score(tech)
        patent = self.patent_analyzer.calculate_patent_depth_score(tech)
        funding = self.funding_analyzer.calculate_funding_score(tech)
        
        return clinical * 0.4 + patent * 0.3 + funding * 0.3
    
    def calculate_momentum_score(self, tech: TechnologyRoute) -> float:
        """计算发展势头评分"""
        factors = []
        
        # 专利增长势头
        if tech.patent_growth_rate > 30:
            factors.append(25)
        elif tech.patent_growth_rate > 15:
            factors.append(15)
        else:
            factors.append(5)
        
        # 融资活跃度
        if tech.funding_rounds >= 3:
            factors.append(25)
        elif tech.funding_rounds >= 2:
            factors.append(15)
        else:
            factors.append(5)
        
        # 临床进展
        if tech.clinical_trials_phase3 > 0:
            factors.append(30)
        elif tech.clinical_trials_phase2 > 2:
            factors.append(20)
        elif tech.clinical_trials_phase2 > 0:
            factors.append(10)
        else:
            factors.append(5)
        
        # 生态活跃度
        eco_score = min(tech.companies_count * 5, 20)
        factors.append(eco_score)
        
        return sum(factors)
    
    def get_recommendation(self, index: float) -> str:
        """根据指数给出投资建议"""
        if index >= 80:
            return InvestmentRecommendation.STRONG_BUY.value
        elif index >= 60:
            return InvestmentRecommendation.BUY.value
        elif index >= 40:
            return InvestmentRecommendation.HOLD.value
        else:
            return InvestmentRecommendation.CAUTION.value
    
    def identify_key_drivers(self, tech: TechnologyRoute, scores: Dict) -> List[str]:
        """识别关键驱动因素"""
        drivers = []
        
        if tech.clinical_trials_phase3 > 0:
            drivers.append("已有Phase III临床，接近商业化")
        elif tech.clinical_trials_phase2 > 3:
            drivers.append("多个Phase II临床推进中")
        
        if tech.patent_growth_rate > 25:
            drivers.append("专利布局快速增长，技术护城河加深")
        
        if tech.top_vc_backed:
            drivers.append("获得顶级VC背书，资金支持充足")
        
        if tech.indications_count > 3:
            drivers.append("多适应证布局，市场空间广阔")
        
        if tech.core_patents > 5:
            drivers.append("核心专利数量领先")
        
        return drivers if drivers else ["新兴技术路线，值得持续关注"]
    
    def identify_risks(self, tech: TechnologyRoute) -> List[str]:
        """识别风险因素"""
        risks = []
        
        if tech.clinical_trials_phase3 == 0 and tech.clinical_trials_phase2 == 0:
            risks.append("尚处早期阶段，临床验证不足")
        
        if tech.clinical_success_rate < 0.3:
            risks.append("历史成功率较低")
        
        if tech.patent_count < 10:
            risks.append("专利布局相对薄弱")
        
        if tech.total_funding_usd < 100:
            risks.append("资金规模有限，可能影响研发进度")
        
        if tech.avg_time_to_market > 8:
            risks.append("研发周期较长，不确定性高")
        
        return risks if risks else ["常规研发风险"]
    
    def predict_timeline(self, tech: TechnologyRoute) -> str:
        """预测商业化时间线"""
        if tech.clinical_trials_phase3 > 0:
            return "预计2-4年内首个产品上市"
        elif tech.clinical_trials_phase2 > 2:
            return "预计4-6年内有产品进入III期"
        elif tech.clinical_trials_phase2 > 0:
            return "预计5-7年内关键临床数据读出"
        else:
            return "预计7-10年内进入商业化阶段"
    
    def predict(self, tech: TechnologyRoute) -> PredictionResult:
        """执行完整预测"""
        maturity = self.calculate_maturity_score(tech)
        market_potential = self.market_evaluator.calculate_market_potential(tech.name)
        momentum = self.calculate_momentum_score(tech)
        
        # 重磅炸弹指数计算
        blockbuster_index = (
            market_potential * 0.5 +
            maturity * 0.3 +
            momentum * 0.2
        )
        
        return PredictionResult(
            tech_name=tech.name,
            maturity_score=round(maturity, 1),
            market_potential_score=round(market_potential, 1),
            momentum_score=round(momentum, 1),
            blockbuster_index=round(blockbuster_index, 1),
            recommendation=self.get_recommendation(blockbuster_index),
            key_drivers=self.identify_key_drivers(tech, {}),
            risk_factors=self.identify_risks(tech),
            timeline_prediction=self.predict_timeline(tech)
        )


class DataLoader:
    """数据加载器 - 模拟/真实数据源"""
    
    @staticmethod
    def load_mock_data() -> List[TechnologyRoute]:
        """加载模拟数据用于演示"""
        technologies = [
            TechnologyRoute(
                name="PROTAC",
                category="蛋白降解",
                description="蛋白降解靶向嵌合体技术",
                clinical_trials_phase1=15,
                clinical_trials_phase2=8,
                clinical_trials_phase3=2,
                clinical_success_rate=0.35,
                avg_time_to_market=6.5,
                indications_count=5,
                patent_count=180,
                patent_growth_rate=35,
                core_patents=25,
                geographic_coverage=12,
                total_funding_usd=2800,
                funding_rounds=4,
                top_vc_backed=True,
                last_valuation_usd=450,
                companies_count=18
            ),
            TechnologyRoute(
                name="mRNA",
                category="核酸药物",
                description="信使RNA疗法平台",
                clinical_trials_phase1=25,
                clinical_trials_phase2=12,
                clinical_trials_phase3=5,
                clinical_success_rate=0.45,
                avg_time_to_market=5.0,
                indications_count=8,
                patent_count=450,
                patent_growth_rate=28,
                core_patents=40,
                geographic_coverage=15,
                total_funding_usd=5200,
                funding_rounds=5,
                top_vc_backed=True,
                last_valuation_usd=800,
                companies_count=25
            ),
            TechnologyRoute(
                name="CRISPR",
                category="基因编辑",
                description="CRISPR-Cas基因编辑技术",
                clinical_trials_phase1=12,
                clinical_trials_phase2=6,
                clinical_trials_phase3=2,
                clinical_success_rate=0.40,
                avg_time_to_market=7.0,
                indications_count=6,
                patent_count=320,
                patent_growth_rate=22,
                core_patents=35,
                geographic_coverage=14,
                total_funding_usd=3800,
                funding_rounds=4,
                top_vc_backed=True,
                last_valuation_usd=600,
                companies_count=15
            ),
            TechnologyRoute(
                name="CAR-T",
                category="细胞治疗",
                description="嵌合抗原受体T细胞疗法",
                clinical_trials_phase1=30,
                clinical_trials_phase2=15,
                clinical_trials_phase3=8,
                clinical_success_rate=0.50,
                avg_time_to_market=4.5,
                indications_count=4,
                patent_count=520,
                patent_growth_rate=18,
                core_patents=45,
                geographic_coverage=16,
                total_funding_usd=6500,
                funding_rounds=6,
                top_vc_backed=True,
                last_valuation_usd=1200,
                companies_count=32
            ),
            TechnologyRoute(
                name="Bispecific",
                category="抗体药物",
                description="双特异性抗体技术",
                clinical_trials_phase1=20,
                clinical_trials_phase2=10,
                clinical_trials_phase3=4,
                clinical_success_rate=0.42,
                avg_time_to_market=5.5,
                indications_count=6,
                patent_count=380,
                patent_growth_rate=20,
                core_patents=30,
                geographic_coverage=14,
                total_funding_usd=3200,
                funding_rounds=5,
                top_vc_backed=True,
                last_valuation_usd=550,
                companies_count=22
            ),
            TechnologyRoute(
                name="ADC",
                category="抗体药物",
                description="抗体药物偶联物",
                clinical_trials_phase1=22,
                clinical_trials_phase2=12,
                clinical_trials_phase3=6,
                clinical_success_rate=0.48,
                avg_time_to_market=5.0,
                indications_count=5,
                patent_count=420,
                patent_growth_rate=25,
                core_patents=38,
                geographic_coverage=15,
                total_funding_usd=4100,
                funding_rounds=5,
                top_vc_backed=True,
                last_valuation_usd=700,
                companies_count=28
            ),
            TechnologyRoute(
                name="RNAi",
                category="核酸药物",
                description="RNA干扰疗法",
                clinical_trials_phase1=10,
                clinical_trials_phase2=5,
                clinical_trials_phase3=2,
                clinical_success_rate=0.38,
                avg_time_to_market=6.0,
                indications_count=4,
                patent_count=280,
                patent_growth_rate=15,
                core_patents=22,
                geographic_coverage=12,
                total_funding_usd=2100,
                funding_rounds=4,
                top_vc_backed=False,
                last_valuation_usd=350,
                companies_count=12
            ),
            TechnologyRoute(
                name="Gene Therapy",
                category="基因治疗",
                description="AAV载体基因治疗",
                clinical_trials_phase1=14,
                clinical_trials_phase2=7,
                clinical_trials_phase3=3,
                clinical_success_rate=0.35,
                avg_time_to_market=6.5,
                indications_count=5,
                patent_count=350,
                patent_growth_rate=18,
                core_patents=28,
                geographic_coverage=13,
                total_funding_usd=2900,
                funding_rounds=4,
                top_vc_backed=True,
                last_valuation_usd=480,
                companies_count=16
            ),
            TechnologyRoute(
                name="Allogeneic",
                category="细胞治疗",
                description="通用型/异体细胞治疗",
                clinical_trials_phase1=8,
                clinical_trials_phase2=4,
                clinical_trials_phase3=1,
                clinical_success_rate=0.30,
                avg_time_to_market=7.5,
                indications_count=3,
                patent_count=150,
                patent_growth_rate=40,
                core_patents=15,
                geographic_coverage=10,
                total_funding_usd=1200,
                funding_rounds=3,
                top_vc_backed=False,
                last_valuation_usd=220,
                companies_count=10
            ),
            TechnologyRoute(
                name="Cell Therapy",
                category="细胞治疗",
                description="通用细胞治疗平台",
                clinical_trials_phase1=12,
                clinical_trials_phase2=6,
                clinical_trials_phase3=2,
                clinical_success_rate=0.33,
                avg_time_to_market=6.8,
                indications_count=4,
                patent_count=220,
                patent_growth_rate=24,
                core_patents=20,
                geographic_coverage=11,
                total_funding_usd=2400,
                funding_rounds=4,
                top_vc_backed=True,
                last_valuation_usd=380,
                companies_count=14
            ),
        ]
        return technologies


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_console_report(results: List[PredictionResult], threshold: float = 0):
        """生成控制台报告"""
        # 过滤并排序
        filtered = [r for r in results if r.blockbuster_index >= threshold]
        sorted_results = sorted(filtered, key=lambda x: x.blockbuster_index, reverse=True)
        
        print("\n" + "=" * 100)
        print("🏆 BLOCKBUSTER THERAPY PREDICTOR 报告".center(100))
        print("=" * 100)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"分析技术路线数: {len(sorted_results)}")
        print("-" * 100)
        
        # 排名表
        print("\n📊 技术路线排名")
        print("-" * 100)
        print(f"{'排名':<6}{'技术路线':<15}{'重磅指数':<12}{'成熟度':<10}{'市场潜力':<10}{'发展势头':<10}{'投资建议':<10}")
        print("-" * 100)
        
        for i, r in enumerate(sorted_results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{emoji} {i:<4}{r.tech_name:<15}{r.blockbuster_index:<12.1f}"
                  f"{r.maturity_score:<10.1f}{r.market_potential_score:<10.1f}"
                  f"{r.momentum_score:<10.1f}{r.recommendation:<10}")
        
        print("-" * 100)
        
        # 详细分析
        print("\n📋 详细评估报告")
        print("=" * 100)
        
        for i, r in enumerate(sorted_results[:5], 1):  # 前5名详细报告
            print(f"\n【{i}】{r.tech_name} - 重磅指数: {r.blockbuster_index:.1f}")
            print("-" * 80)
            print(f"  📈 评分详情: 成熟度({r.maturity_score:.1f}) | 市场潜力({r.market_potential_score:.1f}) | 势头({r.momentum_score:.1f})")
            print(f"  💡 关键驱动: {', '.join(r.key_drivers[:3])}")
            print(f"  ⚠️  风险因素: {', '.join(r.risk_factors[:2])}")
            print(f"  ⏰ 时间预测: {r.timeline_prediction}")
            print(f"  🎯 投资建议: {r.recommendation}")
        
        print("\n" + "=" * 100)
        print("💡 投资建议分级: 强烈推荐(≥80) | 推荐(60-79) | 观望(40-59) | 谨慎(<40)")
        print("=" * 100)
    
    @staticmethod
    def generate_json_report(results: List[PredictionResult], threshold: float = 0) -> str:
        """生成JSON报告"""
        filtered = [r for r in results if r.blockbuster_index >= threshold]
        sorted_results = sorted(filtered, key=lambda x: x.blockbuster_index, reverse=True)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_routes": len(sorted_results),
            "rankings": [
                {
                    "rank": i + 1,
                    "tech_name": r.tech_name,
                    "blockbuster_index": r.blockbuster_index,
                    "maturity_score": r.maturity_score,
                    "market_potential_score": r.market_potential_score,
                    "momentum_score": r.momentum_score,
                    "recommendation": r.recommendation,
                    "key_drivers": r.key_drivers,
                    "risk_factors": r.risk_factors,
                    "timeline_prediction": r.timeline_prediction
                }
                for i, r in enumerate(sorted_results)
            ]
        }
        
        return json.dumps(report, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Blockbuster Therapy Predictor - 重磅炸弹疗法预测器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                          # 运行完整分析
  python main.py --tech PROTAC,mRNA       # 仅分析指定技术
  python main.py --output json            # 输出JSON格式
  python main.py --threshold 70           # 只显示指数≥70的技术
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["full", "quick"],
        default="full",
        help="分析模式: full=完整分析, quick=快速分析"
    )
    parser.add_argument(
        "--tech",
        type=str,
        help="指定分析的技术路线，逗号分隔，如: PROTAC,mRNA,CRISPR"
    )
    parser.add_argument(
        "--output",
        choices=["console", "json"],
        default="console",
        help="输出格式"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0,
        help="最小重磅炸弹指数阈值 (0-100)"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="保存报告到文件路径"
    )
    
    args = parser.parse_args()
    
    # 加载数据
    print("📥 正在加载数据...")
    all_techs = DataLoader.load_mock_data()
    
    # 过滤指定技术
    if args.tech:
        target_techs = [t.strip() for t in args.tech.split(",")]
        all_techs = [t for t in all_techs if t.name in target_techs]
        if not all_techs:
            print(f"❌ 未找到指定的技术路线: {args.tech}")
            return
    
    # 执行预测
    print(f"🔬 正在分析 {len(all_techs)} 个技术路线...")
    predictor = BlockbusterPredictor()
    results = [predictor.predict(tech) for tech in all_techs]
    
    # 生成报告
    if args.output == "json":
        report = ReportGenerator.generate_json_report(results, args.threshold)
        print(report)
        if args.save:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n✅ 报告已保存至: {args.save}")
    else:
        ReportGenerator.generate_console_report(results, args.threshold)
        if args.save:
            json_report = ReportGenerator.generate_json_report(results, args.threshold)
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(json_report)
            print(f"\n✅ JSON报告已保存至: {args.save}")


if __name__ == "__main__":
    main()

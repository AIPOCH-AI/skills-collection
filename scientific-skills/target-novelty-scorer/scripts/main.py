#!/usr/bin/env python3
"""
Target Novelty Scorer
基于文献挖掘的靶点新颖度评分工具

Usage:
    python main.py --target "PD-L1"
    python main.py --target "BRCA1" --years 10 --format json
"""

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


@dataclass
class NoveltyScore:
    """新颖度评分数据结构"""
    target: str
    novelty_score: float
    confidence: float
    breakdown: Dict[str, float]
    metadata: Dict
    interpretation: str


class PubMedSearcher:
    """PubMed文献检索器 (模拟实现)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search(self, query: str, years: int = 5) -> Dict:
        """
        搜索PubMed文献
        
        实际实现应该调用NCBI E-utilities API
        这里使用模拟数据用于演示
        """
        # 模拟搜索结果
        current_year = datetime.now().year
        
        # 基于靶点名称生成模拟数据 (实际实现中应该调用真实API)
        np.random.seed(hash(query) % 2**32)
        
        total_papers = np.random.randint(100, 50000)
        recent_papers = int(total_papers * np.random.uniform(0.1, 0.5))
        clinical_trials = np.random.randint(0, min(200, total_papers // 100))
        
        # 生成年份分布
        year_distribution = {
            str(year): np.random.randint(recent_papers // years // 2, recent_papers // years * 2)
            for year in range(current_year - years, current_year + 1)
        }
        
        return {
            "query": query,
            "total_count": total_papers,
            "recent_count": recent_papers,
            "clinical_trials": clinical_trials,
            "year_distribution": year_distribution,
            "search_year": current_year,
            "years_analyzed": years
        }


class NoveltyScorer:
    """靶点新颖度评分器"""
    
    def __init__(self):
        self.searcher = PubMedSearcher()
        
        # 评分权重配置
        self.weights = {
            "research_heat": 0.25,      # 研究热度 25%
            "uniqueness": 0.25,         # 独特性 25%
            "research_depth": 0.20,     # 研究深度 20%
            "collaboration": 0.15,      # 合作网络 15%
            "trend": 0.15               # 时间趋势 15%
        }
    
    def _score_research_heat(self, data: Dict) -> float:
        """
        评分: 研究热度 (0-25分)
        基于近年文献数量和引用量
        """
        total = data.get("total_count", 0)
        recent = data.get("recent_count", 0)
        
        # 文献数量评分 (0-15分)
        if total < 500:
            quantity_score = 12 + (total / 500) * 3  # 稀缺: 高分
        elif total < 5000:
            quantity_score = 8 + (5000 - total) / 4500 * 4
        elif total < 20000:
            quantity_score = 4 + (20000 - total) / 15000 * 4
        else:
            quantity_score = max(0, 4 - (total - 20000) / 50000)
        
        # 近期活跃度评分 (0-10分)
        recent_ratio = recent / total if total > 0 else 0
        recency_score = min(10, recent_ratio * 20)
        
        return min(25, quantity_score + recency_score)
    
    def _score_uniqueness(self, data: Dict, target: str) -> float:
        """
        评分: 独特性 (0-25分)
        与已知热门靶点的区分度
        """
        total = data.get("total_count", 0)
        
        # 热门靶点列表 (示例)
        hot_targets = ["p53", "KRAS", "EGFR", "HER2", "PD-L1", "PD-1", "VEGF"]
        
        # 如果本身就是热门靶点，独特性较低
        if target.upper() in [t.upper() for t in hot_targets]:
            base_score = 5
        else:
            # 基于文献数量的独特性
            if total < 1000:
                base_score = 20 + min(5, (1000 - total) / 200)
            elif total < 5000:
                base_score = 15 + (5000 - total) / 4000 * 5
            elif total < 15000:
                base_score = 8 + (15000 - total) / 10000 * 7
            else:
                base_score = max(0, 8 - (total - 15000) / 20000 * 8)
        
        return min(25, base_score)
    
    def _score_research_depth(self, data: Dict) -> float:
        """
        评分: 研究深度 (0-20分)
        临床前/临床研究的进展程度
        """
        clinical_trials = data.get("clinical_trials", 0)
        total = data.get("total_count", 0)
        
        # 临床试验数量评分
        if clinical_trials == 0:
            clinical_score = 8  # 早期靶点，潜力未知
        elif clinical_trials < 10:
            clinical_score = 12 + clinical_trials * 0.5
        elif clinical_trials < 50:
            clinical_score = 16 + (clinical_trials - 10) * 0.1
        else:
            clinical_score = max(10, 20 - (clinical_trials - 50) * 0.05)
        
        # 基础研究深度 (基于总文献数)
        if total < 1000:
            basic_score = 2
        elif total < 5000:
            basic_score = 3
        else:
            basic_score = 4
        
        return min(20, clinical_score + basic_score)
    
    def _score_collaboration(self, data: Dict) -> float:
        """
        评分: 合作网络 (0-15分)
        研究机构/团队的分布多样性
        """
        total = data.get("total_count", 0)
        
        # 基于文献数量的合作多样性估计
        if total < 100:
            diversity_score = 5
        elif total < 1000:
            diversity_score = 8 + (total - 100) / 900 * 4
        elif total < 5000:
            diversity_score = 12 + (total - 1000) / 4000 * 3
        else:
            diversity_score = 15
        
        return min(15, diversity_score)
    
    def _score_trend(self, data: Dict) -> float:
        """
        评分: 时间趋势 (0-15分)
        近年研究增长趋势
        """
        year_dist = data.get("year_distribution", {})
        
        if not year_dist or len(year_dist) < 2:
            return 7.5  # 中性评分
        
        # 计算增长趋势
        years = sorted(year_dist.keys())
        values = [year_dist[y] for y in years]
        
        if len(values) >= 2:
            # 简单线性趋势
            early_avg = np.mean(values[:len(values)//2])
            recent_avg = np.mean(values[len(values)//2:])
            
            if early_avg > 0:
                growth_rate = (recent_avg - early_avg) / early_avg
            else:
                growth_rate = 0
            
            # 转换为0-15分
            if growth_rate > 1.0:  # 增长超过100%
                trend_score = 15
            elif growth_rate > 0.5:
                trend_score = 12 + (growth_rate - 0.5) * 6
            elif growth_rate > 0.2:
                trend_score = 9 + (growth_rate - 0.2) * 10
            elif growth_rate > 0:
                trend_score = 6 + growth_rate * 15
            elif growth_rate > -0.2:
                trend_score = max(0, 6 + growth_rate * 30)
            else:
                trend_score = max(0, 3 + (growth_rate + 0.2) * 15)
        else:
            trend_score = 7.5
        
        return min(15, max(0, trend_score))
    
    def calculate_confidence(self, data: Dict) -> float:
        """计算置信度 (0-1)"""
        total = data.get("total_count", 0)
        
        # 文献越多，置信度越高
        if total < 50:
            return 0.4
        elif total < 200:
            return 0.6
        elif total < 1000:
            return 0.75
        elif total < 5000:
            return 0.85
        else:
            return 0.90
    
    def generate_interpretation(self, score: float, data: Dict) -> str:
        """生成评分解读"""
        total = data.get("total_count", 0)
        clinical = data.get("clinical_trials", 0)
        
        if score >= 80:
            level = "极高新颖度"
            desc = "该靶点研究较少但具有独特价值，是极具潜力的创新方向。"
        elif score >= 65:
            level = "高新颖度"
            desc = "该靶点具有一定研究基础但仍有较大探索空间，建议重点关注。"
        elif score >= 50:
            level = "中等新颖度"
            desc = "该靶点研究热度适中，需要进一步评估其差异化优势。"
        elif score >= 35:
            level = "较低新颖度"
            desc = "该靶点已有较多研究，竞争激烈，需要寻找细分领域突破口。"
        else:
            level = "低新颖度"
            desc = "该靶点是成熟研究方向，创新空间有限，需谨慎评估投入产出比。"
        
        details = f"文献总量: {total}, 临床试验: {clinical}项。"
        
        return f"【{level}】{desc} {details}"
    
    def score(self, target: str, years: int = 5) -> NoveltyScore:
        """
        计算靶点新颖度评分
        
        Args:
            target: 靶点名称或基因符号
            years: 分析年份范围
            
        Returns:
            NoveltyScore对象
        """
        # 检索文献数据
        search_result = self.searcher.search(target, years)
        
        # 计算各维度得分
        breakdown = {
            "research_heat": self._score_research_heat(search_result),
            "uniqueness": self._score_uniqueness(search_result, target),
            "research_depth": self._score_research_depth(search_result),
            "collaboration": self._score_collaboration(search_result),
            "trend": self._score_trend(search_result)
        }
        
        # 计算总分 (加权平均)
        total_score = sum(
            breakdown[key] * self.weights[key] 
            for key in breakdown
        )
        
        # 归一化到0-100
        novelty_score = round(total_score * 100 / 25, 1)
        
        # 计算置信度
        confidence = self.calculate_confidence(search_result)
        
        # 构建元数据
        metadata = {
            "total_papers": search_result["total_count"],
            "recent_papers": search_result["recent_count"],
            "clinical_trials": search_result["clinical_trials"],
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "years_analyzed": years
        }
        
        # 生成解读
        interpretation = self.generate_interpretation(novelty_score, search_result)
        
        return NoveltyScore(
            target=target,
            novelty_score=novelty_score,
            confidence=round(confidence, 2),
            breakdown={k: round(v * 100 / 25, 1) for k, v in breakdown.items()},
            metadata=metadata,
            interpretation=interpretation
        )


def format_text_output(result: NoveltyScore) -> str:
    """格式化文本输出"""
    lines = [
        "=" * 60,
        f"🎯 靶点新颖度评分报告: {result.target}",
        "=" * 60,
        "",
        f"📊 综合评分: {result.novelty_score}/100",
        f"🔒 置信度: {result.confidence * 100:.0f}%",
        "",
        "📈 维度得分:",
        f"  • 研究热度:   {result.breakdown['research_heat']:.1f}/100",
        f"  • 独特性:     {result.breakdown['uniqueness']:.1f}/100",
        f"  • 研究深度:   {result.breakdown['research_depth']:.1f}/100",
        f"  • 合作网络:   {result.breakdown['collaboration']:.1f}/100",
        f"  • 时间趋势:   {result.breakdown['trend']:.1f}/100",
        "",
        "📋 统计信息:",
        f"  • 文献总量: {result.metadata['total_papers']:,}",
        f"  • 近年文献: {result.metadata['recent_papers']:,}",
        f"  • 临床试验: {result.metadata['clinical_trials']}项",
        f"  • 分析日期: {result.metadata['analysis_date']}",
        "",
        f"💡 解读: {result.interpretation}",
        "",
        "=" * 60
    ]
    return "\n".join(lines)


def format_csv_output(result: NoveltyScore) -> str:
    """格式化CSV输出"""
    headers = [
        "target", "novelty_score", "confidence",
        "research_heat", "uniqueness", "research_depth",
        "collaboration", "trend", "total_papers",
        "recent_papers", "clinical_trials", "interpretation"
    ]
    
    values = [
        result.target,
        result.novelty_score,
        result.confidence,
        result.breakdown['research_heat'],
        result.breakdown['uniqueness'],
        result.breakdown['research_depth'],
        result.breakdown['collaboration'],
        result.breakdown['trend'],
        result.metadata['total_papers'],
        result.metadata['recent_papers'],
        result.metadata['clinical_trials'],
        f'"{result.interpretation}"'
    ]
    
    return ",".join(map(str, values))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="靶点新颖度评分工具 - 基于文献挖掘",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target "PD-L1"
  python main.py --target "BRCA1" --years 10 --format json
  python main.py --target "EGFR" --output report.json
        """
    )
    
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="目标靶点名称或基因符号 (如: PD-L1, BRCA1)"
    )
    parser.add_argument(
        "--db", "-d",
        choices=["pubmed", "pmc", "all"],
        default="pubmed",
        help="数据源 (默认: pubmed)"
    )
    parser.add_argument(
        "--years", "-y",
        type=int,
        default=5,
        help="分析年份范围 (默认: 5)"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径 (默认: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="输出格式 (默认: text)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出模式"
    )
    
    args = parser.parse_args()
    
    # 执行评分
    try:
        scorer = NoveltyScorer()
        result = scorer.score(args.target, args.years)
        
        # 格式化输出
        if args.format == "json":
            output = json.dumps(asdict(result), ensure_ascii=False, indent=2)
        elif args.format == "csv":
            output = format_csv_output(result)
        else:
            output = format_text_output(result)
        
        # 输出结果
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 报告已保存至: {args.output}")
        else:
            print(output)
        
        # 详细模式
        if args.verbose and args.format == "text":
            print(f"\n📊 原始数据: {json.dumps(result.metadata, ensure_ascii=False)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

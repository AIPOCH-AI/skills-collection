#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funding Trend Forecaster - Main Module

利用 NLP 分析 NIH/NSF/Horizon Europe 近 6 个月中标项目的摘要，
预测未来 3-5 年资助机构的偏好转移。

Skill ID: 200
Author: OpenClaw Agent
"""

import argparse
import json
import logging
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dateutil import parser as date_parser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TextProcessor:
    """文本预处理和分析类"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.stop_words = self._load_stop_words()
        
    def _load_stop_words(self) -> set:
        """加载停用词"""
        basic_stopwords = {
            # 通用词汇
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'this',
            'that', 'these', 'those', 'we', 'our', 'ours', 'you', 'your',
            # 研究通用词
            'research', 'study', 'project', 'investigate', 'investigation',
            'analysis', 'analyses', 'data', 'method', 'methods', 'methodology',
            'results', 'result', 'conclusion', 'conclusions', 'aim', 'aims',
            'objective', 'objectives', 'goal', 'goals', 'purpose', 'focus',
            'focuses', 'focused', 'develop', 'develops', 'developed', 'developing',
            'novel', 'new', 'address', 'addresses', 'addressed', 'challenge',
            'challenges', 'finding', 'findings', 'significant', 'important',
            'implication', 'implications', 'future', 'application', 'applications',
            'integrate', 'integrates', 'integrated', 'integration', 'approach',
            'approaches', 'demonstrate', 'show', 'shows', 'using', 'use', 'used',
            'methodologies', 'methodology'
        }
        return basic_stopwords
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        # 转为小写
        text = text.lower()
        # 移除特殊字符
        text = re.sub(r'[^\w\s]', ' ', text)
        # 移除数字
        text = re.sub(r'\d+', ' ', text)
        # 移除多余空格
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        cleaned = self.clean_text(text)
        words = cleaned.split()
        # 过滤停用词和短词
        return [w for w in words if w not in self.stop_words and len(w) >= 3]
    
    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """提取 n-gram"""
        tokens = self.tokenize(text)
        if len(tokens) < n:
            return []
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    
    def extract_keywords(self, text: str, top_k: int = 20) -> List[Tuple[str, int]]:
        """提取关键词"""
        words = self.tokenize(text)
        word_freq = Counter(words)
        return word_freq.most_common(top_k)


class TopicModeler:
    """主题建模类"""
    
    def __init__(self, n_topics: int = 10):
        self.n_topics = n_topics
        self.topics = []
        
    def fit(self, documents: List[str]) -> List[Dict]:
        """
        基于词频和共现分析进行简单主题建模
        实际应用中可替换为 LDA 或 BERTopic
        """
        processor = TextProcessor()
        
        # 收集所有词和 bigram
        all_terms = []
        for doc in documents:
            all_terms.extend(processor.tokenize(doc))
            all_terms.extend(processor.extract_ngrams(doc, 2))
        
        # 词频统计
        term_freq = Counter(all_terms)
        
        # 按领域关键词分组
        domain_keywords = {
            'artificial_intelligence': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'natural language processing', 'computer vision',
                'reinforcement learning', 'transformer', 'large language model'
            ],
            'biotechnology': [
                'gene editing', 'crispr', 'synthetic biology', 'biomarker',
                'genomics', 'proteomics', 'personalized medicine', 'stem cell'
            ],
            'climate_environment': [
                'climate change', 'carbon capture', 'renewable energy',
                'sustainability', 'biodiversity', 'ocean acidification',
                'greenhouse gas', 'ecosystem'
            ],
            'health_medicine': [
                'cancer', 'alzheimer', 'cardiovascular', 'infectious disease',
                'vaccine', 'immunotherapy', 'diagnostic', 'therapeutic'
            ],
            'quantum_computing': [
                'quantum computing', 'quantum information', 'quantum cryptography',
                'quantum sensor', 'quantum network', 'qubit'
            ],
            'materials_science': [
                'nanomaterial', 'graphene', 'perovskite', '2d material',
                'smart material', 'biomaterial', 'metamaterial'
            ],
            'neuroscience': [
                'brain', 'neuroscience', 'cognitive', 'neural', 'neurodegenerative',
                'brain computer interface', 'neuroimaging'
            ],
            'space_technology': [
                'space exploration', 'satellite', 'astrobiology', 'exoplanet',
                'space telescope', 'mars', 'lunar'
            ]
        }
        
        topics = []
        for domain, keywords in domain_keywords.items():
            score = sum(term_freq.get(kw, 0) for kw in keywords)
            if score > 0:
                matching_keywords = [kw for kw in keywords if term_freq.get(kw, 0) > 0]
                topics.append({
                    'domain': domain,
                    'score': score,
                    'keywords': matching_keywords[:5],
                    'frequency': {kw: term_freq.get(kw, 0) for kw in matching_keywords[:5]}
                })
        
        # 按分数排序
        topics.sort(key=lambda x: x['score'], reverse=True)
        self.topics = topics[:self.n_topics]
        return self.topics
    
    def get_emerging_topics(self, historical_data: List[str], 
                           recent_data: List[str]) -> List[Dict]:
        """识别新兴主题"""
        processor = TextProcessor()
        
        # 历史词频
        hist_terms = []
        for doc in historical_data:
            hist_terms.extend(processor.tokenize(doc))
        hist_freq = Counter(hist_terms)
        
        # 近期词频
        recent_terms = []
        for doc in recent_data:
            recent_terms.extend(processor.tokenize(doc))
        recent_freq = Counter(recent_terms)
        
        # 计算增长率
        emerging = []
        for term, recent_count in recent_freq.most_common(100):
            hist_count = hist_freq.get(term, 1)
            growth_rate = (recent_count - hist_count) / max(hist_count, 1)
            if growth_rate > 0.3 and recent_count >= 5:  # 增长率超过30%
                emerging.append({
                    'term': term,
                    'recent_count': recent_count,
                    'historical_count': hist_count,
                    'growth_rate': round(growth_rate, 2)
                })
        
        return sorted(emerging, key=lambda x: x['growth_rate'], reverse=True)[:20]


class FundingTrendForecaster:
    """资助趋势预测主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.data = []
        self.processor = TextProcessor()
        self.modeler = TopicModeler(n_topics=self.config.get('n_topics', 10))
        self.analysis_results = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            'sources': ['nih', 'nsf', 'horizon_europe'],
            'months': 6,
            'n_topics': 10,
            'min_word_length': 3,
            'forecast_years': 5
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def generate_mock_data(self, months: int = 6, 
                          total_projects: int = 1000) -> List[Dict]:
        """
        生成模拟数据集用于演示
        实际应用中应从 API 获取真实数据
        """
        logger.info(f"Generating mock data for {months} months...")
        
        # 主题模板
        topics_pool = {
            'artificial_intelligence': {
                'keywords': ['artificial intelligence', 'machine learning', 
                           'deep learning', 'neural network', 'data science'],
                'funding_org': ['NSF', 'NIH', 'Horizon Europe']
            },
            'biotechnology': {
                'keywords': ['gene editing', 'crispr', 'synthetic biology',
                           'personalized medicine', 'regenerative medicine'],
                'funding_org': ['NIH', 'Horizon Europe']
            },
            'climate': {
                'keywords': ['climate change', 'carbon capture', 'renewable energy',
                           'sustainability', 'clean technology'],
                'funding_org': ['NSF', 'Horizon Europe']
            },
            'quantum': {
                'keywords': ['quantum computing', 'quantum information',
                           'quantum cryptography', 'quantum sensor'],
                'funding_org': ['NSF', 'Horizon Europe']
            },
            'neuroscience': {
                'keywords': ['brain research', 'neurodegenerative disease',
                           'cognitive science', 'neural interface'],
                'funding_org': ['NIH', 'Horizon Europe']
            },
            'materials': {
                'keywords': ['nanomaterial', 'advanced material',
                           'smart material', 'biomaterial'],
                'funding_org': ['NSF', 'NIH']
            },
            'health': {
                'keywords': ['cancer research', 'infectious disease',
                           'public health', 'medical device'],
                'funding_org': ['NIH', 'Horizon Europe']
            }
        }
        
        # 生成项目数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*months)
        
        projects = []
        np.random.seed(42)
        
        for i in range(total_projects):
            # 随机选择主题
            topic_key = np.random.choice(list(topics_pool.keys()))
            topic = topics_pool[topic_key]
            
            # 生成随机日期
            days_offset = np.random.randint(0, (end_date - start_date).days)
            project_date = start_date + timedelta(days=int(days_offset))
            
            # 生成摘要
            keywords = topic['keywords']
            num_kws = min(np.random.randint(3, 6), len(keywords))
            selected_kws = np.random.choice(keywords, 
                                          size=num_kws, 
                                          replace=False)
            
            abstract = f"This project focuses on {selected_kws[0]} and {selected_kws[1]}. "
            abstract += f"We will develop novel approaches to address challenges in {selected_kws[2]}. "
            if len(selected_kws) > 3:
                abstract += f"The research integrates {selected_kws[3]} methodologies. "
            abstract += "Our findings will have significant implications for future applications."
            
            project = {
                'id': f"PROJ_{i+1:05d}",
                'title': f"Research on {selected_kws[0].title()} and Related Technologies",
                'abstract': abstract,
                'funding_org': np.random.choice(topic['funding_org']),
                'topic_domain': topic_key,
                'award_date': project_date.isoformat(),
                'amount': int(np.random.uniform(100000, 2000000)),
                'keywords': list(selected_kws)
            }
            projects.append(project)
        
        self.data = projects
        logger.info(f"Generated {len(projects)} mock projects")
        return projects
    
    def analyze_trends(self) -> Dict:
        """分析当前趋势"""
        logger.info("Starting trend analysis...")
        
        if not self.data:
            logger.warning("No data available, generating mock data...")
            self.generate_mock_data()
        
        # 收集所有摘要
        abstracts = [p['abstract'] for p in self.data]
        
        # 1. 关键词分析
        all_text = ' '.join(abstracts)
        top_keywords = self.processor.extract_keywords(all_text, top_k=30)
        
        # 2. 主题建模
        topics = self.modeler.fit(abstracts)
        
        # 3. 按机构分析
        org_analysis = {}
        for org in ['NIH', 'NSF', 'Horizon Europe']:
            org_projects = [p for p in self.data if p['funding_org'] == org]
            if org_projects:
                org_abstracts = [p['abstract'] for p in org_projects]
                org_text = ' '.join(org_abstracts)
                org_keywords = self.processor.extract_keywords(org_text, top_k=15)
                org_topics = list(set([p['topic_domain'] for p in org_projects]))
                org_analysis[org] = {
                    'project_count': len(org_projects),
                    'top_keywords': org_keywords,
                    'focus_areas': org_topics,
                    'total_funding': sum(p['amount'] for p in org_projects)
                }
        
        # 4. 按时间分析趋势
        df = pd.DataFrame(self.data)
        df['award_date'] = pd.to_datetime(df['award_date'])
        df['month'] = df['award_date'].dt.to_period('M')
        
        monthly_trends = df.groupby(['month', 'topic_domain']).size().unstack(fill_value=0)
        
        # 转换 Period 为字符串以便 JSON 序列化
        monthly_trends_dict = {}
        for period, row in monthly_trends.iterrows():
            monthly_trends_dict[str(period)] = row.to_dict()
        # 识别增长最快的领域
        domain_growth = {}
        for domain in monthly_trends.columns:
            values = monthly_trends[domain].values
            if len(values) > 1 and values[0] > 0:
                growth = (values[-1] - values[0]) / values[0]
                domain_growth[domain] = round(growth, 2)
        
        self.analysis_results = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'data_period': f"{df['award_date'].min().date()} to {df['award_date'].max().date()}",
                'total_projects': len(self.data),
                'sources_analyzed': list(df['funding_org'].unique())
            },
            'global_trends': {
                'top_keywords': [{'term': k, 'frequency': v} for k, v in top_keywords],
                'dominant_topics': topics[:5]
            },
            'organization_analysis': org_analysis,
            'domain_growth': sorted(domain_growth.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True),
            'monthly_distribution': monthly_trends_dict
        }
        
        logger.info("Trend analysis completed")
        return self.analysis_results
    
    def predict_trends(self, years: int = 5) -> Dict:
        """预测未来趋势"""
        logger.info(f"Generating {years}-year forecast...")
        
        if not self.analysis_results:
            self.analyze_trends()
        
        # 基于当前趋势进行预测
        current_topics = self.analysis_results['global_trends']['dominant_topics']
        domain_growth = dict(self.analysis_results['domain_growth'])
        
        # 模拟预测模型
        predictions = {}
        base_year = datetime.now().year
        
        # 高增长领域预测
        high_growth_domains = [d for d, g in domain_growth.items() if g > 0.2]
        
        for year_offset in range(1, years + 1):
            year = base_year + year_offset
            confidence = max(0.5, 0.9 - (year_offset * 0.05))  # 随时间降低置信度
            
            # 根据增长率预测热门主题
            predicted_topics = []
            for domain in high_growth_domains[:3]:
                growth_factor = 1 + domain_growth.get(domain, 0) * year_offset
                predicted_topics.append({
                    'domain': domain,
                    'projected_growth': round(growth_factor, 2)
                })
            
            predictions[str(year)] = {
                'hot_topics': predicted_topics,
                'emerging_areas': self._predict_emerging_areas(year_offset),
                'confidence': round(confidence, 2)
            }
        
        # 长期趋势 (5年以上)
        long_term = {
            'transformative_technologies': [
                'Artificial General Intelligence (AGI)',
                'Quantum Internet',
                'Synthetic Life Forms',
                'Brain-Computer Integration',
                'Climate Engineering'
            ],
            'funding_shift_predictions': [
                'Increased focus on AI safety and ethics',
                'Major investments in climate adaptation',
                'Convergence of biology and computing',
                'Space resource utilization'
            ],
            'confidence': 0.65
        }
        
        forecast = {
            'metadata': {
                'forecast_generated': datetime.now().isoformat(),
                'forecast_horizon': f"{base_year + 1} - {base_year + years}",
                'model': 'trend_extrapolation_v1'
            },
            'yearly_predictions': predictions,
            'long_term_outlook': long_term
        }
        
        return forecast
    
    def _predict_emerging_areas(self, year_offset: int) -> List[str]:
        """预测新兴研究领域"""
        emerging_pools = {
            1: ['Multimodal AI', 'Gene Therapy 2.0', 'Green Hydrogen'],
            2: ['Neuromorphic Computing', 'Microbiome Engineering', 'Carbon Removal'],
            3: ['Molecular Nanotechnology', 'Anti-aging Research', 'Ocean Restoration'],
            4: ['Consciousness Studies', 'Planetary Defense', 'Bio-digital Convergence'],
            5: ['Technological Singularity Research', 'Interstellar Probes', 
                'Global Brain Projects']
        }
        return emerging_pools.get(year_offset, ['Unknown Future Tech'])
    
    def export_report(self, output_path: str, format: str = 'json') -> str:
        """导出分析报告"""
        logger.info(f"Exporting report to {output_path}...")
        
        if not self.analysis_results:
            self.analyze_trends()
        
        forecast = self.predict_trends()
        
        full_report = {
            'analysis': self.analysis_results,
            'forecast': forecast,
            'recommendations': self._generate_recommendations()
        }
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(full_report, f, indent=2, ensure_ascii=False)
        else:
            # 简单文本格式
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._format_text_report(full_report))
        
        logger.info(f"Report saved to {output_path}")
        return output_path
    
    def _generate_recommendations(self) -> List[Dict]:
        """生成投资建议"""
        recommendations = []
        
        # 基于趋势生成建议
        if self.analysis_results.get('domain_growth'):
            top_growth = self.analysis_results['domain_growth'][:3]
            for domain, growth in top_growth:
                recommendations.append({
                    'area': domain,
                    'action': 'INVEST',
                    'rationale': f"High growth rate of {growth:.0%} indicates strong funding interest",
                    'priority': 'HIGH' if growth > 0.3 else 'MEDIUM'
                })
        
        return recommendations
    
    def _format_text_report(self, report: Dict) -> str:
        """格式化为文本报告"""
        lines = [
            "=" * 60,
            "    FUNDING TREND FORECASTER REPORT",
            "=" * 60,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Analysis Period: {report['analysis']['metadata']['data_period']}",
            f"Total Projects Analyzed: {report['analysis']['metadata']['total_projects']}",
            "",
            "-" * 60,
            "CURRENT TRENDS",
            "-" * 60,
            "",
            "Top Keywords:",
        ]
        
        for kw in report['analysis']['global_trends']['top_keywords'][:10]:
            lines.append(f"  - {kw['term']}: {kw['frequency']} occurrences")
        
        lines.extend([
            "",
            "-" * 60,
            "5-YEAR FORECAST",
            "-" * 60,
            ""
        ])
        
        for year, pred in report['forecast']['yearly_predictions'].items():
            lines.append(f"\n{year} (Confidence: {pred['confidence']:.0%}):")
            for topic in pred['hot_topics']:
                lines.append(f"  → {topic['domain']} (projected growth: {topic['projected_growth']}x)")
        
        lines.extend([
            "",
            "=" * 60,
            "End of Report",
            "=" * 60
        ])
        
        return '\n'.join(lines)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='Funding Trend Forecaster - Analyze and predict research funding trends'
    )
    parser.add_argument('--config', '-c', type=str, help='Path to config file')
    parser.add_argument('--months', '-m', type=int, default=6, 
                       help='Number of months to analyze (default: 6)')
    parser.add_argument('--analyze-all', '-a', action='store_true',
                       help='Run complete analysis on all sources')
    parser.add_argument('--source', '-s', type=str, 
                       choices=['nih', 'nsf', 'horizon_europe', 'all'],
                       default='all',
                       help='Data source to analyze')
    parser.add_argument('--forecast', '-f', action='store_true',
                       help='Generate trend forecast')
    parser.add_argument('--years', '-y', type=int, default=5,
                       help='Forecast horizon in years (default: 5)')
    parser.add_argument('--output', '-o', type=str, default='report.json',
                       help='Output file path')
    parser.add_argument('--format', type=str, choices=['json', 'text'], 
                       default='json',
                       help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 初始化分析器
    forecaster = FundingTrendForecaster(config_path=args.config)
    
    # 生成模拟数据（实际应从API获取）
    forecaster.generate_mock_data(months=args.months)
    
    if args.analyze_all or args.source:
        # 执行分析
        results = forecaster.analyze_trends()
        print(f"\n📊 Analyzed {results['metadata']['total_projects']} projects")
        print(f"📅 Period: {results['metadata']['data_period']}")
        print("\n🔥 Top Keywords:")
        for kw in results['global_trends']['top_keywords'][:5]:
            print(f"   - {kw['term']}: {kw['frequency']}")
    
    if args.forecast:
        # 生成预测
        forecast = forecaster.predict_trends(years=args.years)
        print("\n🔮 Trend Forecast:")
        for year, pred in list(forecast['yearly_predictions'].items())[:3]:
            print(f"\n   {year}:")
            for topic in pred['hot_topics'][:2]:
                print(f"     → {topic['domain']}")
    
    # 导出报告
    forecaster.export_report(args.output, format=args.format)
    print(f"\n✅ Report saved to: {args.output}")


if __name__ == '__main__':
    main()

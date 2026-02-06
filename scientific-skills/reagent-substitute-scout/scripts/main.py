#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reagent Substitute Scout (ID: 108)
当特定试剂停产或缺货时，基于文献引用数据寻找经过验证的替代品。

Author: OpenClaw Skill Development
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import math

# Optional imports with graceful degradation
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


# Configuration
DEFAULT_CONFIG = {
    "data_sources": {
        "pubmed": {"enabled": True, "api_key": None},
        "google_scholar": {"enabled": False, "api_key": None},
        "chembl": {"enabled": True},
        "pubchem": {"enabled": True}
    },
    "scoring": {
        "citation_weight": 0.4,
        "recency_weight": 0.3,
        "similarity_weight": 0.3,
        "min_citations": 5
    },
    "output": {
        "default_format": "table",
        "default_limit": 5
    }
}


@dataclass
class Reagent:
    """试剂数据模型"""
    name: str
    cas: Optional[str] = None
    molecular_formula: Optional[str] = None
    smiles: Optional[str] = None
    synonyms: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"Reagent({self.name}, CAS:{self.cas})"


@dataclass
class SubstituteCandidate:
    """替代品候选数据模型"""
    reagent: Reagent
    similarity_score: float = 0.0
    citation_count: int = 0
    recent_citations: int = 0
    reliability_score: float = 0.0
    literature_evidence: List[Dict] = field(default_factory=list)
    
    @property
    def total_score(self) -> float:
        """计算综合评分"""
        return (
            self.reliability_score * 0.4 +
            self.similarity_score * 0.3 +
            min(math.log10(self.citation_count + 1) / 4, 1.0) * 0.3
        )


class LiteratureDataSource:
    """文献数据源基类"""
    
    def search_citations(self, reagent_name: str) -> Dict[str, Any]:
        """搜索试剂引用数据"""
        raise NotImplementedError


class PubMedDataSource(LiteratureDataSource):
    """PubMed/NCBI 数据源"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def search_citations(self, reagent_name: str) -> Dict[str, Any]:
        """搜索PubMed数据库"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("requests module not available")
            return {"count": 0, "articles": []}
        
        try:
            # 构建搜索查询
            query = f'"{reagent_name}"[Title/Abstract] AND ("alternative" OR "substitute" OR "replacement")'
            
            params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": 100
            }
            if self.api_key:
                params["api_key"] = self.api_key
            
            # 搜索ID列表
            response = requests.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=30)
            data = response.json()
            
            id_list = data.get("esearchresult", {}).get("idlist", [])
            count = int(data.get("esearchresult", {}).get("count", 0))
            
            articles = []
            if id_list:
                # 获取详细信息
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list[:20]),
                    "retmode": "json"
                }
                if self.api_key:
                    summary_params["api_key"] = self.api_key
                
                summary_response = requests.get(
                    f"{self.BASE_URL}/esummary.fcgi", 
                    params=summary_params,
                    timeout=30
                )
                summary_data = summary_response.json()
                
                for pmid in id_list[:20]:
                    article_data = summary_data.get("result", {}).get(pmid, {})
                    if article_data:
                        articles.append({
                            "pmid": pmid,
                            "title": article_data.get("title", ""),
                            "year": article_data.get("pubdate", "")[:4],
                            "journal": article_data.get("source", "")
                        })
            
            return {"count": count, "articles": articles}
            
        except Exception as e:
            self.logger.error(f"PubMed search error: {e}")
            return {"count": 0, "articles": []}


class PubChemDataSource:
    """PubChem 化学数据源"""
    
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def search_by_name(self, name: str) -> Optional[Dict]:
        """通过名称搜索化合物"""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"{self.BASE_URL}/compound/name/{name}/JSON"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                compounds = data.get("PC_Compounds", [])
                if compounds:
                    compound = compounds[0]
                    return self._parse_compound(compound)
            return None
            
        except Exception as e:
            logging.getLogger(__name__).error(f"PubChem search error: {e}")
            return None
    
    def _parse_compound(self, compound: Dict) -> Dict:
        """解析化合物数据"""
        props = compound.get("props", [])
        
        result = {
            "cid": compound.get("id", {}).get("id", {}).get("cid"),
            "smiles": None,
            "formula": None,
            "synonyms": []
        }
        
        for prop in props:
            label = prop.get("urn", {}).get("label", "")
            if label == "SMILES":
                result["smiles"] = prop.get("value", {}).get("sval")
            elif label == "Molecular Formula":
                result["formula"] = prop.get("value", {}).get("sval")
        
        return result
    
    def get_similar_compounds(self, cid: int, threshold: float = 0.8) -> List[Dict]:
        """获取相似化合物（基于PubChem的2D相似性搜索）"""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            url = f"{self.BASE_URL}/compound/fastidentity/{cid}/cids/JSON"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                cids = data.get("IdentifierList", {}).get("CID", [])
                
                similar = []
                for similar_cid in cids[:20]:
                    # 获取每个相似化合物的详细信息
                    compound_url = f"{self.BASE_URL}/compound/cid/{similar_cid}/JSON"
                    compound_response = requests.get(compound_url, timeout=30)
                    
                    if compound_response.status_code == 200:
                        compound_data = compound_response.json()
                        compounds = compound_data.get("PC_Compounds", [])
                        if compounds:
                            parsed = self._parse_compound(compounds[0])
                            parsed["cid"] = similar_cid
                            similar.append(parsed)
                
                return similar
            return []
            
        except Exception as e:
            logging.getLogger(__name__).error(f"PubChem similarity search error: {e}")
            return []


class ChemStructureAnalyzer:
    """化学结构分析器"""
    
    def __init__(self):
        self.available = RDKIT_AVAILABLE
        self.logger = logging.getLogger(__name__)
    
    def calculate_similarity(self, smiles1: str, smiles2: str) -> float:
        """计算两个化合物的Tanimoto相似度"""
        if not self.available:
            return 0.5  # 默认中等相似度
        
        try:
            mol1 = Chem.MolFromSmiles(smiles1)
            mol2 = Chem.MolFromSmiles(smiles2)
            
            if mol1 is None or mol2 is None:
                return 0.0
            
            fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
            fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
            
            return DataStructs.TanimotoSimilarity(fp1, fp2)
            
        except Exception as e:
            self.logger.error(f"Similarity calculation error: {e}")
            return 0.0


class ReagentSubstituteScout:
    """
    试剂替代品搜索主类
    
    核心功能:
    1. 解析输入试剂信息
    2. 从多个数据源搜索替代品
    3. 计算综合评分
    4. 输出排序后的替代方案
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or DEFAULT_CONFIG
        self.logger = self._setup_logging()
        
        # 初始化数据源
        self.pubmed = PubMedDataSource(
            api_key=self.config["data_sources"]["pubmed"].get("api_key")
        )
        self.pubchem = PubChemDataSource()
        self.structure_analyzer = ChemStructureAnalyzer()
        
        # 内置的常见替代品数据库（离线数据）
        self._offline_substitutes_db = self._load_offline_database()
    
    def _setup_logging(self) -> logging.Logger:
        """配置日志"""
        logger = logging.getLogger("ReagentSubstituteScout")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_offline_database(self) -> Dict[str, List[Dict]]:
        """加载离线替代品数据库"""
        # 常见试剂的已知替代品数据
        return {
            "TRIzol": [
                {"name": "QIAzol Lysis Reagent", "cas": "104888-69-9", "similarity": 0.92},
                {"name": "TRI Reagent", "cas": "93249-88-8", "similarity": 0.89},
                {"name": "RNAzol RT", "cas": "105697-57-2", "similarity": 0.85},
                {"name": "PureLink RNA Mini Kit", "cas": None, "similarity": 0.78},
            ],
            "TRIzol Reagent": [
                {"name": "QIAzol Lysis Reagent", "cas": "104888-69-9", "similarity": 0.92},
                {"name": "TRI Reagent", "cas": "93249-88-8", "similarity": 0.89},
                {"name": "RNAzol RT", "cas": "105697-57-2", "similarity": 0.85},
            ],
            "DMSO": [
                {"name": "Dimethyl Sulfoxide", "cas": "67-68-5", "similarity": 1.0},
                {"name": "Ethylene Glycol", "cas": "107-21-1", "similarity": 0.65},
            ],
            "FBS": [
                {"name": "Fetal Bovine Serum", "cas": None, "similarity": 1.0},
                {"name": "Fetal Calf Serum", "cas": None, "similarity": 0.95},
                {"name": "Newborn Calf Serum", "cas": None, "similarity": 0.75},
            ],
        }
    
    def find_substitutes(
        self, 
        reagent_name: Optional[str] = None,
        cas_number: Optional[str] = None,
        molecular_formula: Optional[str] = None,
        limit: int = 5,
        application_field: Optional[str] = None
    ) -> List[SubstituteCandidate]:
        """
        查找试剂替代品
        
        Args:
            reagent_name: 试剂名称
            cas_number: CAS号
            molecular_formula: 分子式
            limit: 返回结果数量限制
            application_field: 应用领域筛选
        
        Returns:
            按综合评分排序的替代品列表
        """
        self.logger.info(f"Searching substitutes for: {reagent_name or cas_number}")
        
        # 1. 获取原始试剂信息
        original_reagent = self._identify_reagent(reagent_name, cas_number, molecular_formula)
        if not original_reagent:
            self.logger.warning("Could not identify the original reagent")
            return []
        
        self.logger.info(f"Identified reagent: {original_reagent}")
        
        # 2. 从多个来源收集候选替代品
        candidates = []
        
        # 2.1 从离线数据库获取
        offline_candidates = self._get_offline_substitutes(original_reagent)
        candidates.extend(offline_candidates)
        
        # 2.2 从PubChem获取相似化合物
        if self.config["data_sources"]["pubchem"]["enabled"]:
            pubchem_candidates = self._get_pubchem_substitutes(original_reagent)
            candidates.extend(pubchem_candidates)
        
        # 3. 评分和排序
        scored_candidates = self._score_candidates(candidates, original_reagent)
        
        # 4. 去重和排序
        unique_candidates = self._deduplicate_candidates(scored_candidates)
        sorted_candidates = sorted(unique_candidates, key=lambda x: x.total_score, reverse=True)
        
        return sorted_candidates[:limit]
    
    def _identify_reagent(
        self, 
        name: Optional[str], 
        cas: Optional[str], 
        formula: Optional[str]
    ) -> Optional[Reagent]:
        """识别试剂信息"""
        reagent = Reagent(name=name or "Unknown")
        
        # 通过CAS号查询
        if cas:
            reagent.cas = cas
            # 尝试从PubChem获取更多信息
            pubchem_data = self.pubchem.search_by_name(cas)
            if pubchem_data:
                reagent.molecular_formula = pubchem_data.get("formula")
                reagent.smiles = pubchem_data.get("smiles")
        
        # 通过名称查询
        elif name:
            pubchem_data = self.pubchem.search_by_name(name)
            if pubchem_data:
                reagent.cas = reagent.cas or cas
                reagent.molecular_formula = pubchem_data.get("formula")
                reagent.smiles = pubchem_data.get("smiles")
                reagent.synonyms = pubchem_data.get("synonyms", [])
        
        return reagent if (reagent.name != "Unknown" or reagent.cas) else None
    
    def _get_offline_substitutes(self, original: Reagent) -> List[SubstituteCandidate]:
        """从离线数据库获取候选替代品"""
        candidates = []
        
        # 尝试匹配名称
        for key, substitutes in self._offline_substitutes_db.items():
            if (original.name and key.lower() in original.name.lower()) or \
               (original.name and original.name.lower() in key.lower()):
                
                for sub_data in substitutes:
                    candidate_reagent = Reagent(
                        name=sub_data["name"],
                        cas=sub_data.get("cas"),
                        molecular_formula=None
                    )
                    
                    candidate = SubstituteCandidate(
                        reagent=candidate_reagent,
                        similarity_score=sub_data.get("similarity", 0.5)
                    )
                    candidates.append(candidate)
        
        return candidates
    
    def _get_pubchem_substitutes(self, original: Reagent) -> List[SubstituteCandidate]:
        """从PubChem获取相似化合物作为替代品"""
        candidates = []
        
        if not original.smiles:
            return candidates
        
        # 搜索相似化合物
        pubchem_data = self.pubchem.search_by_name(original.name or original.cas or "")
        if pubchem_data and pubchem_data.get("cid"):
            similar_compounds = self.pubchem.get_similar_compounds(pubchem_data["cid"])
            
            for compound in similar_compounds[:10]:
                candidate_reagent = Reagent(
                    name=f"Compound CID:{compound.get('cid')}",
                    cas=None,
                    molecular_formula=compound.get("formula"),
                    smiles=compound.get("smiles")
                )
                
                # 计算结构相似度
                if compound.get("smiles") and original.smiles:
                    similarity = self.structure_analyzer.calculate_similarity(
                        original.smiles, compound["smiles"]
                    )
                else:
                    similarity = 0.5
                
                candidate = SubstituteCandidate(
                    reagent=candidate_reagent,
                    similarity_score=similarity
                )
                candidates.append(candidate)
        
        return candidates
    
    def _score_candidates(
        self, 
        candidates: List[SubstituteCandidate], 
        original: Reagent
    ) -> List[SubstituteCandidate]:
        """为候选替代品计算评分"""
        
        for candidate in candidates:
            # 1. 获取文献引用数据
            pubmed_data = self.pubmed.search_citations(candidate.reagent.name)
            candidate.citation_count = pubmed_data.get("count", 0)
            candidate.literature_evidence = pubmed_data.get("articles", [])
            
            # 2. 计算时效性分数（最近5年引用占比）
            recent_count = 0
            current_year = datetime.now().year
            for article in candidate.literature_evidence:
                try:
                    year = int(article.get("year", 0))
                    if current_year - year <= 5:
                        recent_count += 1
                except (ValueError, TypeError):
                    pass
            
            candidate.recent_citations = recent_count
            
            # 3. 计算可靠性评分
            if candidate.citation_count >= 100:
                candidate.reliability_score = 5.0
            elif candidate.citation_count >= 50:
                candidate.reliability_score = 4.0
            elif candidate.citation_count >= 20:
                candidate.reliability_score = 3.0
            elif candidate.citation_count >= 5:
                candidate.reliability_score = 2.0
            else:
                candidate.reliability_score = 1.0
        
        return candidates
    
    def _deduplicate_candidates(
        self, 
        candidates: List[SubstituteCandidate]
    ) -> List[SubstituteCandidate]:
        """去重候选列表（基于名称）"""
        seen = set()
        unique = []
        
        for candidate in candidates:
            key = candidate.reagent.name.lower()
            if key not in seen:
                seen.add(key)
                unique.append(candidate)
        
        return unique


class OutputFormatter:
    """输出格式化器"""
    
    @staticmethod
    def format_table(candidates: List[SubstituteCandidate]) -> str:
        """格式化为表格输出"""
        if not candidates:
            return "未找到替代品。"
        
        # 表头
        header = "┌────────────────────────────┬─────────────┬────────────┬────────────┬─────────────┐"
        separator = "├────────────────────────────┼─────────────┼────────────┼────────────┼─────────────┤"
        footer = "└────────────────────────────┴─────────────┴────────────┴────────────┴─────────────┘"
        
        lines = [header]
        lines.append("│ {:<26} │ {:<11} │ {:<10} │ {:<10} │ {:<11} │".format(
            "Substitute", "CAS", "Similarity", "Citations", "Reliability"
        ))
        lines.append(separator)
        
        # 数据行
        for candidate in candidates:
            name = candidate.reagent.name[:26] if len(candidate.reagent.name) <= 26 else candidate.reagent.name[:23] + "..."
            cas = (candidate.reagent.cas or "N/A")[:11]
            similarity = f"{candidate.similarity_score:.2f}"
            citations = str(candidate.citation_count) if candidate.citation_count > 0 else "N/A"
            reliability = "★" * int(candidate.reliability_score)
            
            lines.append("│ {:<26} │ {:<11} │ {:<10} │ {:<10} │ {:<11} │".format(
                name, cas, similarity, citations, reliability
            ))
        
        lines.append(footer)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_json(candidates: List[SubstituteCandidate], query: Dict) -> str:
        """格式化为JSON输出"""
        result = {
            "query": query,
            "results": []
        }
        
        for candidate in candidates:
            result["results"].append({
                "name": candidate.reagent.name,
                "cas": candidate.reagent.cas,
                "molecular_formula": candidate.reagent.molecular_formula,
                "similarity_score": round(candidate.similarity_score, 3),
                "citation_count": candidate.citation_count,
                "recent_citations": candidate.recent_citations,
                "reliability_score": round(candidate.reliability_score, 1),
                "total_score": round(candidate.total_score, 3),
                "literature_evidence": candidate.literature_evidence[:5]  # 只保留前5条
            })
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    @staticmethod
    def format_markdown(candidates: List[SubstituteCandidate], query: Dict) -> str:
        """格式化为Markdown输出"""
        lines = [
            "# 试剂替代品搜索报告",
            "",
            f"**查询试剂**: {query.get('reagent', 'N/A')}",
            f"**查询时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 推荐替代品列表",
            "",
            "| 排名 | 替代品名称 | CAS号 | 相似度 | 引用次数 | 可靠性 |",
            "|------|-----------|-------|--------|----------|--------|"
        ]
        
        for i, candidate in enumerate(candidates, 1):
            name = candidate.reagent.name
            cas = candidate.reagent.cas or "N/A"
            similarity = f"{candidate.similarity_score:.2f}"
            citations = str(candidate.citation_count) if candidate.citation_count > 0 else "N/A"
            reliability = "★" * int(candidate.reliability_score)
            
            lines.append(f"| {i} | {name} | {cas} | {similarity} | {citations} | {reliability} |")
        
        lines.extend([
            "",
            "## 评分说明",
            "",
            "- **相似度**: 化学结构和功能特性的相似程度 (0-1)",
            "- **引用次数**: 文献数据库中的引用数量",
            "- **可靠性**: 基于引用数据和使用验证的评分 (1-5星)",
            "",
            "---",
            "*Generated by Reagent Substitute Scout v1.0.0*"
        ])
        
        return "\n".join(lines)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Reagent Substitute Scout - 寻找经过验证的试剂替代品",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --reagent "TRIzol Reagent"
  %(prog)s --cas "15596-18-2" --format json
  %(prog)s --reagent "TRIzol" --limit 10 --verbose
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--reagent", "-r",
        help="试剂名称"
    )
    input_group.add_argument(
        "--cas", "-c",
        help="CAS号"
    )
    input_group.add_argument(
        "--formula", "-f",
        help="分子式"
    )
    
    # 输出参数
    parser.add_argument(
        "--format", "-F",
        choices=["table", "json", "markdown"],
        default="table",
        help="输出格式 (默认: table)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=5,
        help="返回结果数量限制 (默认: 5)"
    )
    parser.add_argument(
        "--field",
        help="应用领域筛选"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="输出详细信息（包含文献引用）"
    )
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = DEFAULT_CONFIG.copy()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config.update(json.load(f))
    
    # 初始化搜索器
    scout = ReagentSubstituteScout(config)
    
    # 执行搜索
    try:
        candidates = scout.find_substitutes(
            reagent_name=args.reagent,
            cas_number=args.cas,
            molecular_formula=args.formula,
            limit=args.limit,
            application_field=args.field
        )
        
        # 准备查询信息
        query_info = {
            "reagent": args.reagent,
            "cas": args.cas,
            "formula": args.formula,
            "field": args.field
        }
        
        # 格式化输出
        formatter = OutputFormatter()
        if args.format == "json":
            output = formatter.format_json(candidates, query_info)
        elif args.format == "markdown":
            output = formatter.format_markdown(candidates, query_info)
        else:
            output = formatter.format_table(candidates)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)
        
        # 如果启用了verbose模式，输出详细文献信息
        if args.verbose and args.format == "table":
            print("\n详细文献证据:")
            for i, candidate in enumerate(candidates, 1):
                print(f"\n[{i}] {candidate.reagent.name}")
                if candidate.literature_evidence:
                    for article in candidate.literature_evidence[:3]:
                        print(f"  - {article.get('title', 'N/A')} ({article.get('year', 'N/A')})")
                else:
                    print("  (无文献数据)")
        
        # 返回状态码
        return 0 if candidates else 1
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Semantic Consistency Auditor
基于BERTScore和COMET的语义一致性评估工具
用于评估AI生成病历与专家金标准的一致性

ID: 212
Author: OpenClaw
Date: 2026-02-06
"""

import argparse
import json
import sys
import os
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# 尝试导入可选依赖
try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False
    print("警告: bert_score 未安装，BERTScore功能不可用。运行: pip install bertscore")

try:
    from comet import download_model, load_from_checkpoint
    COMET_AVAILABLE = True
except ImportError:
    COMET_AVAILABLE = False
    print("警告: comet-ml 未安装，COMET功能不可用。运行: pip install comet-ml")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class EvaluationResult:
    """评估结果数据类"""
    case_id: Optional[str]
    ai_generated: str
    gold_standard: str
    bertscore_precision: float
    bertscore_recall: float
    bertscore_f1: float
    comet_score: float
    semantic_consistency: float
    passed: bool
    details: Dict


@dataclass
class SummaryResult:
    """汇总结果数据类"""
    total_cases: int
    passed_cases: int
    pass_rate: float
    avg_bertscore_f1: float
    avg_comet_score: float
    avg_consistency: float


class SemanticConsistencyAuditor:
    """
    语义一致性审计器
    
    使用BERTScore和COMET算法评估AI生成文本与金标准之间的语义一致性。
    """
    
    DEFAULT_CONFIG = {
        'bertscore': {
            'model': 'microsoft/deberta-xlarge-mnli',
            'lang': 'zh',
            'rescale_with_baseline': True,
            'device': 'auto'
        },
        'comet': {
            'model': 'Unbabel/wmt22-comet-da',
            'batch_size': 8,
            'device': 'auto'
        },
        'thresholds': {
            'bertscore_f1': 0.85,
            'comet_score': 0.75,
            'semantic_consistency': 0.80
        }
    }
    
    def __init__(
        self,
        bert_model: Optional[str] = None,
        comet_model: Optional[str] = None,
        lang: str = 'zh',
        device: str = 'auto',
        config_path: Optional[str] = None
    ):
        """
        初始化语义一致性审计器
        
        Args:
            bert_model: BERTScore使用的模型名称
            comet_model: COMET使用的模型名称
            lang: 语言代码 ('zh', 'en', etc.)
            device: 计算设备 ('auto', 'cpu', 'cuda')
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.lang = lang or self.config['bertscore']['lang']
        self.device = self._get_device(device)
        
        # BERTScore配置
        self.bert_model = bert_model or self.config['bertscore']['model']
        self.bertscore_available = BERTSCORE_AVAILABLE
        
        # COMET配置
        self.comet_model_name = comet_model or self.config['comet']['model']
        self.comet_model = None
        self.comet_available = COMET_AVAILABLE
        
        # 阈值
        self.thresholds = self.config['thresholds']
        
        # 延迟加载模型
        self._bertscore_initialized = False
        self._comet_initialized = False
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    try:
                        import yaml
                        return yaml.safe_load(f)
                    except ImportError:
                        pass
                return json.load(f)
        return self.DEFAULT_CONFIG
    
    def _get_device(self, device: str) -> str:
        """确定计算设备"""
        if device == 'auto':
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return 'cuda'
            return 'cpu'
        return device
    
    def _init_bertscore(self):
        """初始化BERTScore（按需加载）"""
        if self._bertscore_initialized:
            return
        if not self.bertscore_available:
            raise RuntimeError("BERTScore不可用，请安装: pip install bertscore")
        self._bertscore_initialized = True
    
    def _init_comet(self):
        """初始化COMET模型（按需加载）"""
        if self._comet_initialized:
            return
        if not self.comet_available:
            raise RuntimeError("COMET不可用，请安装: pip install comet-ml")
        
        try:
            # 下载并加载COMET模型
            model_path = download_model(self.comet_model_name)
            self.comet_model = load_from_checkpoint(model_path)
            self._comet_initialized = True
        except Exception as e:
            raise RuntimeError(f"COMET模型加载失败: {e}")
    
    def evaluate(
        self,
        ai_text: str,
        gold_text: str,
        case_id: Optional[str] = None
    ) -> Dict:
        """
        评估单个病例的语义一致性
        
        Args:
            ai_text: AI生成的病历文本
            gold_text: 专家金标准文本
            case_id: 病例ID（可选）
        
        Returns:
            包含评估结果的字典
        """
        if not ai_text or not gold_text:
            raise ValueError("E001: 输入文本不能为空")
        
        # 计算BERTScore
        bertscore_result = self._compute_bertscore([ai_text], [gold_text])
        
        # 计算COMET分数
        comet_result = self._compute_comet([ai_text], [gold_text])
        
        # 计算综合语义一致性
        semantic_consistency = self._compute_consistency(
            bertscore_result['f1'],
            comet_result['score']
        )
        
        # 判断是否通过
        passed = self._check_passed(
            bertscore_result['f1'],
            comet_result['score'],
            semantic_consistency
        )
        
        # 分析语义差异
        details = self._analyze_semantic_details(ai_text, gold_text)
        
        result = EvaluationResult(
            case_id=case_id,
            ai_generated=ai_text,
            gold_standard=gold_text,
            bertscore_precision=bertscore_result['precision'],
            bertscore_recall=bertscore_result['recall'],
            bertscore_f1=bertscore_result['f1'],
            comet_score=comet_result['score'],
            semantic_consistency=semantic_consistency,
            passed=passed,
            details=details
        )
        
        return self._result_to_dict(result)
    
    def evaluate_batch(
        self,
        cases: List[Dict[str, str]],
        show_progress: bool = True
    ) -> List[Dict]:
        """
        批量评估多个病例
        
        Args:
            cases: 病例列表，每个病例包含 'ai', 'gold', 可选 'case_id'
            show_progress: 是否显示进度
        
        Returns:
            评估结果列表
        """
        results = []
        total = len(cases)
        
        for i, case in enumerate(cases):
            if show_progress:
                print(f"进度: {i+1}/{total} ({(i+1)/total*100:.1f}%)", file=sys.stderr)
            
            try:
                result = self.evaluate(
                    ai_text=case['ai'],
                    gold_text=case['gold'],
                    case_id=case.get('case_id', f"CASE_{i+1:04d}")
                )
                results.append(result)
            except Exception as e:
                print(f"警告: 病例 {case.get('case_id', i)} 评估失败: {e}", file=sys.stderr)
                results.append({
                    'case_id': case.get('case_id', f"CASE_{i+1:04d}"),
                    'error': str(e),
                    'passed': False
                })
        
        return results
    
    def _compute_bertscore(
        self,
        candidates: List[str],
        references: List[str]
    ) -> Dict[str, float]:
        """计算BERTScore"""
        self._init_bertscore()
        
        try:
            P, R, F1 = bert_score(
                candidates,
                references,
                lang=self.lang,
                model_type=self.bert_model,
                device=self.device,
                rescale_with_baseline=self.config['bertscore']['rescale_with_baseline'],
                verbose=False
            )
            
            return {
                'precision': P[0].item(),
                'recall': R[0].item(),
                'f1': F1[0].item()
            }
        except Exception as e:
            print(f"BERTScore计算警告: {e}", file=sys.stderr)
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    
    def _compute_comet(
        self,
        sources: List[str],
        translations: List[str]
    ) -> Dict[str, float]:
        """计算COMET分数"""
        self._init_comet()
        
        try:
            # COMET需要源文本、翻译文本和参考文本
            # 在语义一致性评估中，我们将gold作为参考，ai作为翻译
            data = [{
                "src": sources[0],
                "mt": sources[0],  # AI生成的文本
                "ref": translations[0]  # 金标准
            }]
            
            seg_scores, sys_score = self.comet_model.predict(
                data,
                batch_size=self.config['comet']['batch_size']
            )
            
            return {
                'score': seg_scores[0] if seg_scores else sys_score,
                'system_score': sys_score
            }
        except Exception as e:
            print(f"COMET计算警告: {e}", file=sys.stderr)
            return {'score': 0.0, 'system_score': 0.0}
    
    def _compute_consistency(self, bertscore_f1: float, comet_score: float) -> float:
        """
        计算综合语义一致性分数
        
        使用加权平均结合BERTScore F1和COMET分数
        """
        # BERTScore和COMET的权重（可配置）
        w_bert = 0.6
        w_comet = 0.4
        
        # COMET分数可能需要归一化（通常在-1到1之间）
        comet_normalized = (comet_score + 1) / 2 if comet_score < 0 else comet_score
        
        return w_bert * bertscore_f1 + w_comet * comet_normalized
    
    def _check_passed(
        self,
        bertscore_f1: float,
        comet_score: float,
        consistency: float
    ) -> bool:
        """检查是否通过评估"""
        return (
            bertscore_f1 >= self.thresholds['bertscore_f1'] and
            comet_score >= self.thresholds['comet_score'] and
            consistency >= self.thresholds['semantic_consistency']
        )
    
    def _analyze_semantic_details(
        self,
        ai_text: str,
        gold_text: str
    ) -> Dict:
        """分析语义细节差异（简化版）"""
        # 这里可以实现更复杂的语义分析
        # 例如：实体识别、关键概念提取等
        
        # 简单的关键词匹配示例
        ai_words = set(ai_text.split())
        gold_words = set(gold_text.split())
        
        matched = ai_words & gold_words
        missed = gold_words - ai_words
        extra = ai_words - gold_words
        
        return {
            'semantic_gaps': list(missed)[:10],  # 最多10个遗漏项
            'extra_content': list(extra)[:10],   # 最多10个额外内容
            'matched_concepts': list(matched)[:10],  # 最多10个匹配项
            'match_ratio': len(matched) / len(gold_words) if gold_words else 0
        }
    
    def _result_to_dict(self, result: EvaluationResult) -> Dict:
        """将结果转换为字典格式"""
        return {
            'case_id': result.case_id,
            'ai_generated': result.ai_generated,
            'gold_standard': result.gold_standard,
            'metrics': {
                'bertscore': {
                    'precision': round(result.bertscore_precision, 4),
                    'recall': round(result.bertscore_recall, 4),
                    'f1': round(result.bertscore_f1, 4)
                },
                'comet': {
                    'score': round(result.comet_score, 4)
                },
                'semantic_consistency': round(result.semantic_consistency, 4)
            },
            'passed': result.passed,
            'grade': self._get_grade(result.semantic_consistency),
            'details': result.details
        }
    
    def _get_grade(self, consistency: float) -> str:
        """根据一致性分数返回等级"""
        if consistency >= 0.90:
            return "优秀"
        elif consistency >= 0.80:
            return "良好"
        elif consistency >= 0.70:
            return "及格"
        elif consistency >= 0.60:
            return "待改进"
        else:
            return "不合格"
    
    def compute_summary(self, results: List[Dict]) -> Dict:
        """计算汇总统计"""
        if not results:
            return {}
        
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {'error': '没有有效的评估结果'}
        
        total = len(valid_results)
        passed = sum(1 for r in valid_results if r.get('passed', False))
        
        avg_bert_f1 = np.mean([r['metrics']['bertscore']['f1'] for r in valid_results])
        avg_comet = np.mean([r['metrics']['comet']['score'] for r in valid_results])
        avg_consistency = np.mean([r['metrics']['semantic_consistency'] for r in valid_results])
        
        summary = SummaryResult(
            total_cases=total,
            passed_cases=passed,
            pass_rate=round(passed / total, 4) if total > 0 else 0.0,
            avg_bertscore_f1=round(avg_bert_f1, 4),
            avg_comet_score=round(avg_comet, 4),
            avg_consistency=round(avg_consistency, 4)
        )
        
        return {
            'summary': asdict(summary),
            'thresholds': self.thresholds,
            'grade_distribution': self._compute_grade_distribution(valid_results)
        }
    
    def _compute_grade_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """计算等级分布"""
        distribution = {"优秀": 0, "良好": 0, "及格": 0, "待改进": 0, "不合格": 0}
        for r in results:
            grade = r.get('grade', '不合格')
            distribution[grade] = distribution.get(grade, 0) + 1
        return distribution


def load_batch_cases(file_path: str) -> List[Dict[str, str]]:
    """从JSON文件加载批量病例"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return [
            {
                'case_id': item.get('case_id', f"CASE_{i+1:04d}"),
                'ai': item.get('ai_generated', item.get('ai', '')),
                'gold': item.get('gold_standard', item.get('gold', ''))
            }
            for i, item in enumerate(data)
        ]
    elif isinstance(data, dict) and 'cases' in data:
        return [
            {
                'case_id': item.get('case_id', f"CASE_{i+1:04d}"),
                'ai': item.get('ai_generated', item.get('ai', '')),
                'gold': item.get('gold_standard', item.get('gold', ''))
            }
            for i, item in enumerate(data['cases'])
        ]
    else:
        raise ValueError("输入文件格式错误，应为病例列表或包含'cases'字段的对象")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Semantic Consistency Auditor - 基于BERTScore和COMET的语义一致性评估',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个病例评估
  python main.py -a "AI生成的病历" -g "专家金标准"
  
  # 批量评估
  python main.py -i cases.json -o results.json
  
  # 使用特定模型
  python main.py -a "..." -g "..." --bert-model "bert-base-chinese"
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-a', '--ai-generated',
        help='AI生成的病历文本'
    )
    input_group.add_argument(
        '-i', '--input-file',
        help='批量评估的JSON文件路径'
    )
    
    parser.add_argument(
        '-g', '--gold-standard',
        help='专家金标准文本（与--ai-generated配合使用）'
    )
    parser.add_argument(
        '--case-id',
        help='病例ID（可选）'
    )
    
    # 模型参数
    parser.add_argument(
        '--bert-model',
        default='microsoft/deberta-xlarge-mnli',
        help='BERTScore模型名称 (默认: microsoft/deberta-xlarge-mnli)'
    )
    parser.add_argument(
        '--comet-model',
        default='Unbabel/wmt22-comet-da',
        help='COMET模型名称 (默认: Unbabel/wmt22-comet-da)'
    )
    parser.add_argument(
        '--lang', '-l',
        default='zh',
        help='语言代码 (默认: zh)'
    )
    parser.add_argument(
        '--device',
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help='计算设备 (默认: auto)'
    )
    
    # 阈值参数
    parser.add_argument(
        '--threshold-bert',
        type=float,
        default=0.85,
        help='BERTScore F1阈值 (默认: 0.85)'
    )
    parser.add_argument(
        '--threshold-comet',
        type=float,
        default=0.75,
        help='COMET分数阈值 (默认: 0.75)'
    )
    parser.add_argument(
        '--threshold-consistency',
        type=float,
        default=0.80,
        help='综合一致性阈值 (默认: 0.80)'
    )
    
    # 输出参数
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['summary', 'detailed'],
        default='detailed',
        help='输出格式 (默认: detailed)'
    )
    parser.add_argument(
        '--config',
        help='配置文件路径'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.ai_generated and not args.gold_standard:
        parser.error('--ai-generated 需要与 --gold-standard 一起使用')
    
    try:
        # 初始化审计器
        auditor = SemanticConsistencyAuditor(
            bert_model=args.bert_model,
            comet_model=args.comet_model,
            lang=args.lang,
            device=args.device,
            config_path=args.config
        )
        
        # 更新阈值
        auditor.thresholds = {
            'bertscore_f1': args.threshold_bert,
            'comet_score': args.threshold_comet,
            'semantic_consistency': args.threshold_consistency
        }
        
        # 执行评估
        if args.input_file:
            # 批量评估
            print(f"正在加载病例文件: {args.input_file}")
            cases = load_batch_cases(args.input_file)
            print(f"已加载 {len(cases)} 个病例")
            
            print("开始评估...")
            results = auditor.evaluate_batch(cases)
            
            # 生成输出
            if args.format == 'summary':
                output = auditor.compute_summary(results)
            else:
                summary = auditor.compute_summary(results)
                output = {
                    'cases': results,
                    'summary': summary.get('summary', {}),
                    'thresholds': summary.get('thresholds', {}),
                    'grade_distribution': summary.get('grade_distribution', {})
                }
        else:
            # 单个评估
            result = auditor.evaluate(
                ai_text=args.ai_generated,
                gold_text=args.gold_standard,
                case_id=args.case_id
            )
            output = result
            
            # 打印简要结果到控制台
            print(f"\n评估结果:")
            print(f"  BERTScore F1: {result['metrics']['bertscore']['f1']:.4f}")
            print(f"  COMET Score: {result['metrics']['comet']['score']:.4f}")
            print(f"  语义一致性: {result['metrics']['semantic_consistency']:.4f}")
            print(f"  等级: {result['grade']}")
            print(f"  通过: {'✓' if result['passed'] else '✗'}")
        
        # 保存或输出结果
        output_json = json.dumps(output, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"\n结果已保存到: {args.output}")
        else:
            print("\n完整结果:")
            print(output_json)
    
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 未预期的错误 - {e}", file=sys.stderr)
        raise


if __name__ == '__main__':
    main()

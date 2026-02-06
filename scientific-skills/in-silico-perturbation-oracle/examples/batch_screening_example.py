#!/usr/bin/env python3
"""
批量靶点筛选示例
演示如何批量筛选多个候选靶点，用于药物研发早期筛选
"""

import sys
sys.path.insert(0, '../scripts')

from main import PerturbationOracle


def batch_screening_example():
    """批量靶点筛选示例"""
    
    print("=" * 60)
    print("示例 2: 批量靶点筛选")
    print("=" * 60)
    
    # 癌症治疗候选靶点列表
    candidate_targets = [
        # 经典癌基因
        "MYC",
        "KRAS",
        "EGFR",
        "PIK3CA",
        "BRAF",
        
        # 凋亡调控
        "BCL2",
        "MCL1",
        "BCLXL",
        
        # 细胞周期
        "CDK4",
        "CDK6",
        "CCND1",
        
        # 信号通路
        "MTOR",
        "AKT1",
        "STAT3",
        "JAK2",
    ]
    
    print(f"\n候选靶点: {', '.join(candidate_targets)}")
    print("细胞类型: lung_adenocarcinoma (肺腺癌细胞)")
    
    # 初始化Oracle
    oracle = PerturbationOracle(
        model_name="scgpt",  # 使用scGPT模型
        cell_type="lung_adenocarcinoma",
        output_dir="./results/batch_screening"
    )
    
    # 批量预测
    print("\n[1] 开始批量扰动预测...")
    results = oracle.predict_knockout(
        genes=candidate_targets,
        perturbation_type="complete_ko"
    )
    
    # 获取综合评分
    print("\n[2] 生成靶点评分...")
    target_scores = results.score_targets()
    
    # 显示排名
    print("\n" + "=" * 60)
    print("Top 10 推荐靶点:")
    print("=" * 60)
    print(f"{'Rank':<6} {'Target':<12} {'Overall':<10} {'Efficacy':<10} {'Safety':<10} {'Recommendation'}")
    print("-" * 80)
    
    for rank, (_, row) in enumerate(target_scores.head(10).iterrows(), 1):
        print(f"{rank:<6} {row['target_gene']:<12} "
              f"{row['overall_score']:<10.3f} {row['efficacy_score']:<10.3f} "
              f"{row['safety_score']:<10.3f} {row['recommendation'][:30]}")
    
    # 筛选高优先级靶点
    high_priority = target_scores[
        target_scores['recommendation'].str.contains('HIGH_PRIORITY')
    ]
    
    print(f"\n[3] 高优先级靶点数量: {len(high_priority)}")
    if len(high_priority) > 0:
        print("建议优先进行湿实验验证的靶点:")
        for gene in high_priority['target_gene']:
            print(f"  - {gene}")
    
    # 导出验证指南
    print("\n[4] 导出湿实验验证指南...")
    guide_path = oracle.export_validation_guide(
        top_targets=10,
        include_controls=True
    )
    print(f"  验证指南已保存至: {guide_path}")
    
    # 保存完整结果
    print("\n[5] 保存完整结果...")
    results.save()
    
    print("\n✅ 批量靶点筛选示例完成!")
    return results


if __name__ == "__main__":
    batch_screening_example()

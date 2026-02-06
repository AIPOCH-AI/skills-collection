#!/usr/bin/env python3
"""
癌症靶点筛选完整工作流示例
演示从靶点预测到湿实验设计的完整流程
"""

import sys
sys.path.insert(0, '../scripts')

from main import PerturbationOracle


def cancer_drug_discovery_workflow():
    """
    癌症药物发现完整工作流
    
    阶段:
    1. 输入候选靶点列表
    2. In silico批量筛选
    3. 多维度评分排序
    4. 通路分析
    5. 生成湿实验方案
    """
    
    print("=" * 70)
    print("🧬 癌症药物发现 - In Silico Perturbation Oracle 工作流")
    print("=" * 70)
    
    # ========================================
    # 阶段 1: 定义候选靶点
    # ========================================
    print("\n📋 阶段 1: 候选靶点定义")
    print("-" * 70)
    
    # 基于文献和数据库筛选的候选靶点
    candidate_targets = {
        # Tier 1: 临床验证靶点 (已有药物)
        "validated": ["EGFR", "BRAF", "ALK", "HER2"],
        
        # Tier 2: 临床前验证靶点
        "preclinical": ["KRAS_G12C", "PIK3CA", "MTOR", "CDK4", "CDK6"],
        
        # Tier 3: 新发现/假设靶点
        "novel": ["LIFR", "TGFBR2", "FGFR3", "NOTCH1", "WNT5A"]
    }
    
    all_targets = []
    for tier, genes in candidate_targets.items():
        print(f"  {tier.upper()}: {', '.join(genes)}")
        all_targets.extend(genes)
    
    print(f"\n总计候选靶点: {len(all_targets)} 个")
    
    # ========================================
    # 阶段 2: In silico筛选
    # ========================================
    print("\n🔬 阶段 2: In Silico 虚拟筛选")
    print("-" * 70)
    
    # 针对不同癌症类型
    cancer_types = {
        "lung_adenocarcinoma": "肺腺癌",
        "colorectal_cancer": "结直肠癌",
        "breast_cancer": "乳腺癌"
    }
    
    all_results = {}
    
    for cell_type, cancer_name in cancer_types.items():
        print(f"\n  正在分析: {cancer_name} ({cell_type})...")
        
        oracle = PerturbationOracle(
            model_name="geneformer",
            cell_type=cell_type,
            output_dir=f"./results/cancer_workflow/{cell_type}"
        )
        
        # 批量预测
        results = oracle.predict_knockout(
            genes=all_targets,
            perturbation_type="complete_ko"
        )
        
        all_results[cell_type] = {
            "oracle": oracle,
            "results": results
        }
    
    # ========================================
    # 阶段 3: 评分与排序
    # ========================================
    print("\n📊 阶段 3: 多维度靶点评分")
    print("-" * 70)
    
    for cell_type, data in all_results.items():
        cancer_name = cancer_types[cell_type]
        scores = data["results"].score_targets()
        
        print(f"\n  {cancer_name} Top 5 靶点:")
        print(f"  {'Rank':<6} {'Target':<12} {'Score':<8} {'Druggable':<10} {'Novelty':<8}")
        print(f"  {'-' * 50}")
        
        for rank, (_, row) in enumerate(scores.head(5).iterrows(), 1):
            print(f"  {rank:<6} {row['target_gene']:<12} "
                  f"{row['overall_score']:.3f}    "
                  f"{row['druggability_score']:.3f}      "
                  f"{row['novelty_score']:.3f}")
    
    # ========================================
    # 阶段 4: 跨癌种比较
    # ========================================
    print("\n🔄 阶段 4: 跨癌种靶点一致性分析")
    print("-" * 70)
    
    # 找出在多个癌种中评分都高的靶点
    common_targets = {}
    
    for cell_type, data in all_results.items():
        scores = data["results"].score_targets()
        top_targets = set(scores.head(10)['target_gene'])
        
        for target in top_targets:
            if target not in common_targets:
                common_targets[target] = []
            common_targets[target].append(cancer_types[cell_type])
    
    print("\n  跨癌种高价值靶点 (出现在多个癌种Top 10中):")
    multi_cancer_targets = {
        t: cancers for t, cancers in common_targets.items() 
        if len(cancers) >= 2
    }
    
    if multi_cancer_targets:
        for target, cancers in sorted(
            multi_cancer_targets.items(), 
            key=lambda x: -len(x[1])
        ):
            print(f"    ⭐ {target}: {', '.join(cancers)}")
    else:
        print("    (未发现显著的跨癌种靶点)")
    
    # ========================================
    # 阶段 5: 通路富集分析
    # ========================================
    print("\n🧭 阶段 5: 通路机制分析")
    print("-" * 70)
    
    for cell_type, data in all_results.items():
        cancer_name = cancer_types[cell_type]
        pathways = data["results"].enrich_pathways(
            database=["KEGG"],
            top_n=3
        )
        
        print(f"\n  {cancer_name} 关键调控通路:")
        for db, results in pathways.items():
            for pw in results:
                print(f"    - {pw.pathway_name}")
                print(f"      富集基因: {', '.join(pw.overlap_genes[:5])}")
    
    # ========================================
    # 阶段 6: 湿实验设计
    # ========================================
    print("\n🧪 阶段 6: 湿实验验证方案生成")
    print("-" * 70)
    
    for cell_type, data in all_results.items():
        cancer_name = cancer_types[cell_type]
        oracle = data["oracle"]
        
        guide_path = oracle.export_validation_guide(
            top_targets=5,
            include_controls=True
        )
        print(f"  {cancer_name}: {guide_path}")
    
    # ========================================
    # 阶段 7: 最终推荐
    # ========================================
    print("\n✅ 阶段 7: 最终推荐")
    print("=" * 70)
    
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    🎯 优先推荐靶点                           │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  1. 泛癌种靶点 (Broad Spectrum)                             │
    │     • 需进一步分析跨癌种一致性                               │
    │                                                             │
    │  2. 癌种特异性靶点                                           │
    │     • 肺腺癌: 分析Top靶点中特异性高的                        │
    │     • 结直肠癌: 分析Top靶点中特异性高的                      │
    │     • 乳腺癌: 分析Top靶点中特异性高的                        │
    │                                                             │
    │  3. 验证优先级                                                │
    │     HIGH_PRIORITY: 立即启动CRISPR验证                       │
    │     MEDIUM_PRIORITY: 设计先导化合物筛选                      │
    │     LOW_PRIORITY: 机制研究为主                               │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    """)
    
    print("\n📁 所有结果已保存至: ./results/cancer_workflow/")
    print("\n✅ 癌症药物发现工作流完成!")
    
    return all_results


if __name__ == "__main__":
    cancer_drug_discovery_workflow()

#!/usr/bin/env python3
"""
单基因敲除预测示例
演示如何使用In Silico Perturbation Oracle进行单个基因的虚拟敲除
"""

import sys
sys.path.insert(0, '../scripts')

from main import PerturbationOracle


def single_knockout_example():
    """单基因敲除示例"""
    
    print("=" * 60)
    print("示例 1: 单基因敲除预测")
    print("=" * 60)
    
    # 初始化Oracle
    oracle = PerturbationOracle(
        model_name="geneformer",
        cell_type="hepatocyte",  # 肝细胞
        output_dir="./results/single_ko"
    )
    
    # 预测TP53敲除效果
    print("\n[1] 预测TP53在肝细胞中的敲除效果...")
    results = oracle.predict_knockout(
        genes=["TP53"],
        perturbation_type="complete_ko"
    )
    
    # 获取差异表达基因
    deg_df = results.get_differential_expression(
        pval_threshold=0.05,
        logfc_threshold=1.0
    )
    print(f"\n[2] 差异表达基因数量: {len(deg_df)}")
    print("\n前10个差异表达基因:")
    print(deg_df.head(10)[['gene_symbol', 'log2_fold_change', 'adjusted_p_value']])
    
    # 获取通路富集结果
    print("\n[3] 通路富集分析...")
    pathways = results.enrich_pathways(
        database=["KEGG", "GO_BP"],
        top_n=5
    )
    
    for db, results_list in pathways.items():
        print(f"\n  {db} Top通路:")
        for i, pw in enumerate(results_list[:3], 1):
            print(f"    {i}. {pw.pathway_name} (p={pw.p_value:.4f})")
    
    # 靶点评分
    print("\n[4] 靶点评分...")
    scores = results.score_targets()
    print(scores[['target_gene', 'overall_score', 'recommendation']])
    
    # 保存结果
    print("\n[5] 保存结果...")
    saved = results.save()
    print(f"  - DEG结果: {saved['deg_results']}")
    print(f"  - 靶点评分: {saved['target_scores']}")
    print(f"  - 通路富集: {saved['pathway_enrichment']}")
    
    print("\n✅ 单基因敲除示例完成!")
    return results


if __name__ == "__main__":
    single_knockout_example()

#!/usr/bin/env python3
"""
组合基因敲除示例
演示如何预测多个基因同时敲除的协同效应 (Synthetic Lethality)
"""

import sys
sys.path.insert(0, '../scripts')

from main import PerturbationOracle


def combinatorial_knockout_example():
    """组合敲除示例 - 合成致死性筛选"""
    
    print("=" * 60)
    print("示例 3: 组合基因敲除 - 合成致死性筛选")
    print("=" * 60)
    
    # 定义要测试的基因对
    # 基于已知文献和药物组合设计的候选对
    gene_pairs = [
        # BCL2家族 (抗凋亡双重阻断)
        ("BCL2", "MCL1"),
        ("BCL2", "BCLXL"),
        ("MCL1", "BCLXL"),
        
        # PI3K/AKT/mTOR通路
        ("PIK3CA", "MTOR"),
        ("PIK3CA", "PTEN"),
        ("AKT1", "MTOR"),
        
        # RAS/MAPK通路
        ("KRAS", "BRAF"),
        ("BRAF", "MEK1"),
        ("KRAS", "EGFR"),
        
        # 细胞周期
        ("CDK4", "CDK6"),
        ("CCND1", "CDK4"),
        
        # 免疫检查点相关
        ("JAK1", "STAT3"),
        ("JAK2", "STAT3"),
    ]
    
    print(f"\n测试基因对数量: {len(gene_pairs)}")
    print("细胞类型: breast_cancer (乳腺癌细胞)")
    print("\n基因对列表:")
    for i, (g1, g2) in enumerate(gene_pairs, 1):
        print(f"  {i}. {g1} + {g2}")
    
    # 初始化Oracle
    oracle = PerturbationOracle(
        model_name="geneformer",
        cell_type="breast_cancer",
        output_dir="./results/combinatorial"
    )
    
    # 预测组合效应
    print("\n[1] 开始组合敲除预测...")
    results = oracle.predict_combinatorial_ko(
        gene_pairs=gene_pairs,
        synergy_threshold=0.2
    )
    
    # 获取协同作用结果
    print("\n[2] 分析协同效应...")
    synergistic_pairs = results.get_synergistic_pairs(threshold=0.2)
    
    print(f"\n发现 {len(synergistic_pairs)} 个协同作用基因对:")
    print("-" * 50)
    
    for g1, g2 in synergistic_pairs:
        # 查找对应的协同分数
        for result in results.results:
            if result["genes"] == (g1, g2):
                score = result["synergy_score"]
                print(f"  ⭐ {g1} + {g2}: synergy_score = {score:.3f}")
                break
    
    # 详细结果分析
    print("\n[3] 所有基因对结果汇总:")
    print("-" * 70)
    print(f"{'Gene Pair':<25} {'Synergy':<12} {'Synergistic?':<15}")
    print("-" * 70)
    
    df = results.to_dataframe()
    for _, row in df.iterrows():
        pair_str = f"{row['gene1']} + {row['gene2']}"
        synergy = f"{row['synergy_score']:.3f}"
        is_syn = "YES ✅" if row['is_synergistic'] else "No"
        print(f"{pair_str:<25} {synergy:<12} {is_syn:<15}")
    
    # 湿实验建议
    print("\n[4] 湿实验验证建议:")
    print("-" * 50)
    print("针对协同作用基因对的实验设计:")
    print("  1. CRISPR双敲除验证")
    print("     - 设计双sgRNA系统")
    print("     - 单敲除 vs 双敲除表型对比")
    print("  2. 药物组合筛选")
    print("     - 小分子抑制剂联合使用")
    print("     - 计算协同指数 (CI)")
    print("  3. 机制研究")
    print("     - 凋亡通路检测 (Caspase活性)")
    print("     - 细胞周期分析")
    
    # 保存结果
    print("\n[5] 保存结果...")
    import pandas as pd
    output_file = "./results/combinatorial/combinatorial_results.csv"
    df.to_csv(output_file, index=False)
    print(f"  结果已保存至: {output_file}")
    
    print("\n✅ 组合基因敲除示例完成!")
    return results


def triple_combination_example():
    """三重组合示例"""
    
    print("\n" + "=" * 60)
    print("示例 3b: 三重基因组合 (扩展)")
    print("=" * 60)
    
    # 三重组合常用于复杂疾病
    triple_combinations = [
        ("BCL2", "MCL1", "BCLXL"),  # 全面阻断抗凋亡
        ("PIK3CA", "MTOR", "AKT1"),  # 完全阻断PI3K通路
        ("CDK4", "CDK6", "CCND1"),   # 细胞周期多重阻断
    ]
    
    print("\n三重组合列表:")
    for combo in triple_combinations:
        print(f"  - {' + '.join(combo)}")
    
    print("\n💡 提示: 三重组合分析需要更长的计算时间")
    print("   在实际应用中，建议先通过双组合筛选出高潜力对，")
    print("   再进行三重组合验证。")


if __name__ == "__main__":
    # 运行组合敲除示例
    combinatorial_knockout_example()
    
    # 展示三重组合
    triple_combination_example()

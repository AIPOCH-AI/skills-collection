#!/usr/bin/env python3
"""
Mouse Colony Planner - 转基因小鼠繁育规划工具

功能:
- 计算繁育时间轴
- 估算笼位需求
- 预测繁育成本
"""

import argparse
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


class BreedingScheme(Enum):
    """繁育方案类型"""
    HETEROZYGOTE = "heterozygote"  # 杂合子 x 野生型
    HOMOZYGOTE = "homozygote"      # 杂合子 x 杂合子
    CONDITIONAL = "conditional"    # 条件敲除 (Cre/loxp)


@dataclass
class BreedingParams:
    """繁育参数"""
    gestation_days: int = 21       # 妊娠期
    weaning_days: int = 21         # 断奶日龄
    sexual_maturity_days: int = 42 # 性成熟日龄
    litter_size: int = 8           # 平均每胎仔数
    female_puberty: int = 35       # 雌鼠青春期(可交配)
    male_puberty: int = 35         # 雄鼠青春期(可交配)
    
    # 基因型比例
    het_ratio: float = 0.5         # 杂合子比例
    homo_ratio: float = 0.25       # 纯合子比例 (het x het)
    

@dataclass
class CostParams:
    """成本参数"""
    cage_cost_per_day: float = 3.0      # 每笼每天费用(元)
    genotyping_cost: float = 15.0       # 每只基因鉴定费(元)
    mouse_purchase_cost: float = 50.0   # 每只小鼠购买费(元)


@dataclass
class Phase:
    """繁育阶段"""
    name: str
    duration_days: int
    cages_needed: int
    description: str


@dataclass
class ColonyPlan:
    """繁育计划结果"""
    scheme: BreedingScheme
    phases: List[Phase]
    total_days: int
    total_cages: int
    total_cost: float
    breeding_pairs: int
    expected_target_genotype: int


def calculate_breeding_plan(
    scheme: BreedingScheme,
    initial_females: int,
    initial_males: int,
    target_pups: int,
    breeding_params: BreedingParams = None,
    cost_params: CostParams = None,
    cage_capacity: int = 5
) -> ColonyPlan:
    """
    计算繁育计划
    
    Args:
        scheme: 繁育方案
        initial_females: 起始雌鼠数
        initial_males: 起始雄鼠数
        target_pups: 目标获得特定基因型小鼠数
        breeding_params: 繁育参数
        cost_params: 成本参数
        cage_capacity: 每笼最大容量
    
    Returns:
        ColonyPlan: 繁育计划
    """
    if breeding_params is None:
        breeding_params = BreedingParams()
    if cost_params is None:
        cost_params = CostParams()
    
    phases = []
    
    # 计算需要的繁育对数
    if scheme == BreedingScheme.HETEROZYGOTE:
        # 杂合子 x 野生型 → 50% 杂合子
        pups_per_pair = breeding_params.litter_size * breeding_params.het_ratio
        breeding_pairs_needed = math.ceil(target_pups / pups_per_pair)
        
    elif scheme == BreedingScheme.HOMOZYGOTE:
        # 杂合子 x 杂合子 → 25% 纯合子
        pups_per_pair = breeding_params.litter_size * breeding_params.homo_ratio
        breeding_pairs_needed = math.ceil(target_pups / pups_per_pair)
        
    else:  # CONDITIONAL
        # 两步繁育: 第一步获得flox/+，第二步与Cre交配
        # 简化为需要更多繁育对
        pups_per_pair = breeding_params.litter_size * breeding_params.homo_ratio * 0.5
        breeding_pairs_needed = math.ceil(target_pups / pups_per_pair)
    
    # 确保有足够的小鼠
    breeding_pairs = min(
        initial_females,
        initial_males,
        breeding_pairs_needed
    )
    
    # 阶段1: 适应性饲养 (3-7天)
    adapt_duration = 7
    adapt_cages = math.ceil((initial_females + initial_males) / cage_capacity)
    phases.append(Phase(
        name="适应性饲养",
        duration_days=adapt_duration,
        cages_needed=adapt_cages,
        description="新引进小鼠适应环境，观察健康状况"
    ))
    
    # 阶段2: 繁育 (妊娠 + 哺乳期)
    # 一胎时间 = 妊娠 + 哺乳 = 21 + 21 = 42天
    breed_duration = breeding_params.gestation_days + breeding_params.weaning_days
    breed_cages = math.ceil((breeding_pairs * 2 + breeding_pairs * breeding_params.litter_size) / cage_capacity)
    
    # 可能需要多胎
    litters_needed = math.ceil(breeding_pairs_needed / breeding_pairs)
    actual_breed_duration = breed_duration * litters_needed
    
    phases.append(Phase(
        name="繁育阶段",
        duration_days=actual_breed_duration,
        cages_needed=max(breed_cages, adapt_cages),
        description=f"配种、妊娠、分娩、哺乳（预计{litters_needed}胎）"
    ))
    
    # 阶段3: 断奶后分笼饲养
    wean_duration = 21  # 断奶后饲养到基因鉴定/分笼
    
    if scheme == BreedingScheme.CONDITIONAL:
        # 条件敲除需要额外步骤
        wean_duration += breeding_params.sexual_maturity_days  # 需要等到性成熟再交配
        
        # 第二阶段繁育笼位
        cond_breed_cages = math.ceil(target_pups / cage_capacity)
        phases.append(Phase(
            name="条件敲除第二阶段",
            duration_days=breeding_params.gestation_days + breeding_params.weaning_days,
            cages_needed=cond_breed_cages,
            description="flox小鼠与Cre工具鼠交配获得条件敲除小鼠"
        ))
    
    # 断奶后分笼
    pups_per_litter = breeding_pairs * breeding_params.litter_size * litters_needed
    wean_cages = math.ceil(pups_per_litter / cage_capacity)
    phases.append(Phase(
        name="断奶后饲养",
        duration_days=wean_duration,
        cages_needed=wean_cages,
        description="断奶后分笼饲养，准备基因鉴定"
    ))
    
    # 阶段4: 基因鉴定
    geno_duration = 3  # 取样+检测时间
    geno_cages = wean_cages  # 鉴定期间仍需笼位
    phases.append(Phase(
        name="基因鉴定",
        duration_days=geno_duration,
        cages_needed=geno_cages,
        description="提取DNA进行PCR基因型鉴定"
    ))
    
    # 计算总时间和总笼位
    total_days = sum(p.duration_days for p in phases)
    max_cages = max(p.cages_needed for p in phases)
    
    # 计算成本
    # 笼位费 = 各阶段笼位天数总和 × 单价
    cage_days = sum(p.duration_days * p.cages_needed for p in phases)
    cage_cost = cage_days * cost_params.cage_cost_per_day
    
    # 基因鉴定费
    total_pups = breeding_pairs * breeding_params.litter_size * litters_needed
    if scheme == BreedingScheme.CONDITIONAL:
        genotyping_cost = total_pups * cost_params.genotyping_cost * 2  # 需要两次鉴定
    else:
        genotyping_cost = total_pups * cost_params.genotyping_cost
    
    # 小鼠购买费 (初始小鼠)
    purchase_cost = (initial_females + initial_males) * cost_params.mouse_purchase_cost
    
    total_cost = cage_cost + genotyping_cost + purchase_cost
    
    # 计算预期获得的目标基因型小鼠数量
    if scheme == BreedingScheme.HETEROZYGOTE:
        expected_target = int(total_pups * breeding_params.het_ratio)
    elif scheme == BreedingScheme.HOMOZYGOTE:
        expected_target = int(total_pups * breeding_params.homo_ratio)
    else:
        expected_target = int(total_pups * breeding_params.homo_ratio * 0.5)
    
    return ColonyPlan(
        scheme=scheme,
        phases=phases,
        total_days=total_days,
        total_cages=max_cages,
        total_cost=total_cost,
        breeding_pairs=breeding_pairs,
        expected_target_genotype=expected_target
    )


def format_plan_output(plan: ColonyPlan) -> str:
    """格式化输出繁育计划"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"🐭 转基因小鼠繁育计划 - {plan.scheme.value}")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("📋 繁育阶段:")
    lines.append("-" * 40)
    for i, phase in enumerate(plan.phases, 1):
        lines.append(f"  阶段{i}: {phase.name}")
        lines.append(f"    持续时间: {phase.duration_days} 天")
        lines.append(f"    所需笼位: {phase.cages_needed} 笼")
        lines.append(f"    说明: {phase.description}")
        lines.append("")
    
    lines.append("-" * 40)
    lines.append(f"⏱️  预计总时间: {plan.total_days} 天 ({plan.total_days/30:.1f} 个月)")
    lines.append(f"🏠 最大笼位数: {plan.total_cages} 笼")
    lines.append(f"🧬 繁育对数: {plan.breeding_pairs} 对")
    lines.append("")
    
    lines.append("💰 费用估算:")
    lines.append("-" * 40)
    lines.append(f"  预计获得目标基因型小鼠: {plan.expected_target_genotype} 只")
    lines.append(f"  单只成本: {plan.total_cost/max(plan.expected_target_genotype, 1):.1f} 元")
    lines.append(f"  💵 总费用: {plan.total_cost:.2f} 元")
    lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Mouse Colony Planner - 转基因小鼠繁育规划工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --scheme heterozygote --females 10 --males 5 --target-pups 10
  python main.py --scheme homozygote --females 20 --males 10 --target-pups 20
  python main.py --scheme conditional --females 15 --males 15 --target-pups 15
        """
    )
    
    parser.add_argument(
        "--scheme",
        type=str,
        required=True,
        choices=[s.value for s in BreedingScheme],
        help="繁育方案类型"
    )
    
    parser.add_argument(
        "--females",
        type=int,
        required=True,
        help="起始雌鼠数量"
    )
    
    parser.add_argument(
        "--males",
        type=int,
        required=True,
        help="起始雄鼠数量"
    )
    
    parser.add_argument(
        "--target-pups",
        type=int,
        default=10,
        help="目标获得特定基因型小鼠数量 (默认: 10)"
    )
    
    parser.add_argument(
        "--gestation",
        type=int,
        default=21,
        help="妊娠期(天) (默认: 21)"
    )
    
    parser.add_argument(
        "--weaning",
        type=int,
        default=21,
        help="断奶日龄(天) (默认: 21)"
    )
    
    parser.add_argument(
        "--sexual-maturity",
        type=int,
        default=42,
        help="性成熟日龄(天) (默认: 42)"
    )
    
    parser.add_argument(
        "--cage-capacity",
        type=int,
        default=5,
        help="每笼最大存栏数 (默认: 5)"
    )
    
    parser.add_argument(
        "--cage-cost",
        type=float,
        default=3.0,
        help="每笼每天费用(元) (默认: 3.0)"
    )
    
    parser.add_argument(
        "--genotyping-cost",
        type=float,
        default=15.0,
        help="每只小鼠基因鉴定费(元) (默认: 15.0)"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建繁育参数
    breeding_params = BreedingParams(
        gestation_days=args.gestation,
        weaning_days=args.weaning,
        sexual_maturity_days=args.sexual_maturity
    )
    
    # 创建成本参数
    cost_params = CostParams(
        cage_cost_per_day=args.cage_cost,
        genotyping_cost=args.genotyping_cost
    )
    
    # 解析繁育方案
    scheme = BreedingScheme(args.scheme)
    
    # 计算繁育计划
    plan = calculate_breeding_plan(
        scheme=scheme,
        initial_females=args.females,
        initial_males=args.males,
        target_pups=args.target_pups,
        breeding_params=breeding_params,
        cost_params=cost_params,
        cage_capacity=args.cage_capacity
    )
    
    # 输出结果
    print(format_plan_output(plan))


if __name__ == "__main__":
    main()

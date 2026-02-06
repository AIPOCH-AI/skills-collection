#!/usr/bin/env python3
"""
IACUC Protocol Drafter (ID: 105)

撰写动物实验伦理(IACUC)申请书，专注于3Rs原则的论证部分。

3Rs原则:
- Replacement (替代): 使用非动物方法替代活体动物实验
- Reduction (减少): 使用最少数量动物获得有效结果
- Refinement (优化): 减轻动物痛苦和应激
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class IACUCProtocolDrafter:
    """IACUC申请书起草器"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate_input()
    
    def validate_input(self) -> None:
        """验证输入数据完整性"""
        required_fields = ["title", "principal_investigator", "species", "number_of_animals"]
        missing = [f for f in required_fields if f not in self.data]
        if missing:
            raise ValueError(f"缺少必需字段: {', '.join(missing)}")
    
    def generate_protocol(self) -> str:
        """生成完整的IACUC申请书"""
        sections = [
            self._generate_header(),
            self._generate_project_summary(),
            self._generate_three_rs_section(),
            self._generate_animal_procedures(),
            self._generate_veterinary_care(),
            self._generate_humane_endpoints(),
            self._generate_references(),
        ]
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """生成页眉部分"""
        institution = self.data.get("institution", "[机构名称]")
        return f"""================================================================================
                    IACUC 动物实验伦理申请书
================================================================================

机构名称: {institution}
申请日期: {datetime.now().strftime('%Y年%m月%d日')}

================================================================================
"""
    
    def _generate_project_summary(self) -> str:
        """生成项目摘要"""
        title = self.data.get("title", "[实验标题]")
        pi = self.data.get("principal_investigator", "[研究者]")
        species = self.data.get("species", "[物种]")
        num_animals = self.data.get("number_of_animals", 0)
        pain_category = self.data.get("pain_category", "B")
        procedure = self.data.get("procedure_description", "[程序描述]")
        
        return f"""一、项目基本信息

1.1 实验标题
    {title}

1.2 主要研究者 (Principal Investigator)
    {pi}

1.3 实验动物信息
    - 物种: {species}
    - 数量: {num_animals} 只
    - 美国农业部疼痛类别 (USDA Pain Category): {pain_category}

1.4 实验程序概述
    {procedure}
"""
    
    def _generate_three_rs_section(self) -> str:
        """生成3Rs原则论证部分 - 核心内容"""
        justification = self.data.get("justification", {})
        
        replacement = justification.get("replacement", {})
        reduction = justification.get("reduction", {})
        refinement = justification.get("refinement", {})
        
        return f"""二、3Rs 原则论证 (Three Rs Justification)

2.1 替代原则 (Replacement)

2.1.1 已考虑的替代方法
    {self._format_list(replacement.get("alternatives_considered", ["无"]))}

2.1.2 必须使用活体动物的理由
    {replacement.get("why_animals_needed", "[请详细说明为何非动物方法无法满足实验需求]")}

    科学依据:
    - 本研究需要观察完整的生理系统反应，无法通过细胞培养或计算机模拟实现
    - 研究涉及多器官系统的相互作用，需要完整的有机体模型
    - 已查阅相关替代方法文献，确认目前无合适替代方案

2.1.3 文献检索证明
    已进行系统的文献检索，检索策略如下:
    - 数据库: PubMed, Web of Science, 3Rs Alternatives数据库
    - 关键词: 替代方法、体外实验、{self.data.get('species', '')} 模型
    - 检索结果: 未发现可完全替代活体动物的方法

--------------------------------------------------------------------------------

2.2 减少原则 (Reduction)

2.2.1 样本量计算
    {reduction.get("sample_size_calculation", "[基于统计学方法计算最小样本量]")}

    具体计算:
    - 统计检验类型: [双样本t检验/ANOVA等]
    - 效应量 (Effect Size): [数值]
    - 显著性水平 (α): 0.05
    - 检验效能 (Power, 1-β): 0.80
    - 考虑10-15%的脱落率后确定最终动物数量

2.2.2 减少动物数量的策略
    {reduction.get("minimization_strategies", "[描述如何最小化动物使用]")}

    实施措施:
    - 采用配对实验设计，减少个体差异影响
    - 使用重复测量设计，提高统计效能
    - 优化实验流程，减少实验失败率
    - 与已有研究数据共享对照组数据（如可行）

--------------------------------------------------------------------------------

2.3 优化原则 (Refinement)

2.3.1 疼痛管理
    {refinement.get("pain_management", "[详细说明疼痛和应激管理措施]")}

    具体措施:
    - 麻醉方案: [药物名称、剂量、给药途径]
    - 镇痛方案: [术前、术中、术后镇痛计划]
    - 麻醉深度监测: [监测指标和方法]
    - 术后护理: [保温、补液、抗生素使用等]

2.3.2 饲养环境优化
    {refinement.get("housing_enrichment", "[描述环境丰富化措施]")}

    环境优化:
    - 笼具: 符合物种自然行为需求的笼具尺寸和类型
    - 丰富化: 提供巢材、玩具、社交机会等
    - 饲养条件: 温度、湿度、光照周期符合物种需求
    - 饲养密度: 确保充足空间，避免过度拥挤

2.3.3 人道终点设定
    {refinement.get("humane_endpoints", "[明确的人道终点指标]")}

    人道终点标准:
    - 体重下降超过基线体重的20%
    - 无法进食或饮水超过24小时
    - 严重呼吸困难或发绀
    - 无法站立或极度虚弱
    - 严重感染症状
    - 任何引起持续疼痛或痛苦的状况

    实施: 达到任一终点标准立即实施安乐死
"""
    
    def _generate_animal_procedures(self) -> str:
        """生成动物实验程序描述"""
        return f"""三、动物实验程序

3.1 动物来源
    - 供应商: [AAALAC认证供应商]
    - 动物等级: [SPF/普通级等]
    - 健康证明: 要求提供近期健康检测报告

3.2 动物准备
    - 适应性饲养: 至少7天适应期
    - 标记方法: [耳标/芯片/染色等，选择创伤最小的方法]
    - 分组: 随机分组，减少偏倚

3.3 实验程序详细描述
    {self.data.get("procedure_description", "[详细实验步骤]")}

3.4 安乐死方法
    - 方法: [CO2窒息/过量麻醉/颈椎脱臼等]
    - 依据: AVMA安乐死指南
    - 确认: 确认死亡后方可进行后续操作
"""
    
    def _generate_veterinary_care(self) -> str:
        """生成兽医护理计划"""
        return """四、兽医护理与监测

4.1 日常监测
    - 监测频率: [每日/每周次数]
    - 监测指标: 体重、食物饮水摄入、行为观察、临床体征
    - 记录方式: 标准化记录表

4.2 紧急处理
    - 紧急联系人: [兽医/研究人员24小时联系方式]
    - 应急药物: [配备常用急救药物]
    - 处理流程: 发现问题→通知兽医→评估→处理→记录

4.3 术后护理 (如适用)
    - 恢复室: 保温、安静、监测
    - 护理频率: [每小时/每两小时检查]
    - 护理记录: 体温、心率、呼吸、疼痛评分
"""
    
    def _generate_humane_endpoints(self) -> str:
        """生成详细的人道终点说明"""
        return """五、人道终点详细说明

5.1 人道终点的重要性
    设定明确的人道终点是Refinement原则的核心体现，确保在科学目标
    与动物福利之间取得平衡，避免不必要的动物痛苦。

5.2 具体终点指标

    主要终点 (Major Endpoints):
    - 体重下降 >20% (连续3天未恢复)
    - 持续无法进食或饮水 >24小时
    - 严重呼吸困难、发绀
    - 体温异常 (<36°C 或 >40°C) 持续4小时以上
    - 无法自主活动或极度虚弱

    次要终点 (Minor Endpoints):
    - 明显疼痛行为 (弓背、蜷缩、不活跃)
    - 自我损伤行为
    - 异常攻击行为或社交退缩
    - 手术部位感染未改善
    - 肿瘤体积超过预设限制

5.3 终点执行
    - 发现指标: 任何人员发现立即通知研究人员和兽医
    - 评估确认: 兽医与研究人员共同评估
    - 执行时间: 确认后1小时内实施安乐死
    - 记录要求: 详细记录发现时间、指标、处理过程

5.4 例外情况
    如科学终点与人道终点冲突，需事先获得IACUC批准并设定:
    - 科学必要性论证
    - 最小痛苦延长方案
    - 额外监测措施
    - 兽医监督加强
"""
    
    def _generate_references(self) -> str:
        """生成参考文献列表"""
        return """六、参考文献与依据

6.1 法规与指南
    - Guide for the Care and Use of Laboratory Animals (8th Edition)
    - AVMA Guidelines for the Euthanasia of Animals
    - 中华人民共和国实验动物管理条例
    - USDA Animal Welfare Act and Regulations

6.2 3Rs资源
    - NC3Rs (National Centre for the Replacement, Refinement and Reduction of Animals in Research)
    - ALTBIB: Alternatives to Animal Testing (NIH)
    - FRAME (Fund for the Replacement of Animals in Medical Experiments)
    - 3Rs Centre Utrecht Life Sciences

6.3 相关文献
    - Russell WMS, Burch RL. The Principles of Humane Experimental Technique (1959)
    - [根据实际实验添加相关科学文献]

================================================================================
                              声明与签名
================================================================================

本人确认:
1. 已完整阅读并理解本申请书的所有内容
2. 具备执行本实验所需的资质和经验
3. 将严格遵守IACUC批准的所有条件和要求
4. 确保所有参与人员接受适当的动物实验培训
5. 如实验方案有任何变更，将及时提交修正案申请

主要研究者签名: _____________________ 日期: ______________

实验室负责人签名: _____________________ 日期: ______________

================================================================================
"""
    
    @staticmethod
    def _format_list(items: list) -> str:
        """格式化列表为字符串"""
        if not items:
            return "无"
        return "\n    ".join(f"- {item}" for item in items)


def create_sample_input() -> Dict[str, Any]:
    """创建示例输入数据"""
    return {
        "title": "新型抗肿瘤药物对荷瘤小鼠模型的疗效及安全性评价",
        "principal_investigator": "张教授",
        "institution": "XX大学医学院",
        "species": "小鼠 (Mus musculus)",
        "number_of_animals": 60,
        "pain_category": "E",
        "procedure_description": "建立皮下移植瘤模型，给药观察肿瘤生长抑制情况，定期采血检测生化指标",
        "justification": {
            "replacement": {
                "alternatives_considered": ["体外肿瘤细胞培养", "类器官模型", "计算机药代动力学模拟"],
                "why_animals_needed": "抗肿瘤药物需要评估完整的体内药效学、药代动力学及系统毒性反应，体外模型无法模拟复杂的肿瘤微环境和免疫系统相互作用"
            },
            "reduction": {
                "sample_size_calculation": "基于预实验数据，效应量0.8，α=0.05，Power=0.8，使用G*Power软件计算每组需要16只，考虑20%脱落率，最终每组20只，共3组60只",
                "minimization_strategies": "采用重复测量设计，每只动物作为自身对照；与历史对照数据比较以减少对照组动物数量"
            },
            "refinement": {
                "pain_management": "肿瘤体积限制在直径1.5cm以内；出现溃疡或影响活动能力时立即安乐死；采血使用局部麻醉；使用最小有效剂量麻醉剂",
                "housing_enrichment": "提供筑巢材料、咀嚼玩具；群养满足社交需求；恒温恒湿饲养环境；12小时昼夜节律",
                "humane_endpoints": "体重下降>20%、肿瘤直径>1.5cm或出现溃疡、无法自主进食饮水、严重恶病质表现"
            }
        }
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="IACUC Protocol Drafter - 动物实验伦理申请书起草工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --input protocol.json --output protocol.txt
  %(prog)s --sample > sample_input.json
  cat protocol.json | %(prog)s > output.txt
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="输入JSON文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="输出文件路径 (默认为标准输出)"
    )
    
    parser.add_argument(
        "--sample", "-s",
        action="store_true",
        help="生成示例输入JSON文件"
    )
    
    args = parser.parse_args()
    
    # 生成示例
    if args.sample:
        sample = create_sample_input()
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        return
    
    # 读取输入
    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # 从标准输入读取
            input_text = sys.stdin.read()
            if not input_text.strip():
                parser.print_help()
                sys.exit(1)
            data = json.loads(input_text)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{args.input}'", file=sys.stderr)
        sys.exit(1)
    
    # 生成协议
    try:
        drafter = IACUCProtocolDrafter(data)
        protocol = drafter.generate_protocol()
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 生成协议时出错 - {e}", file=sys.stderr)
        sys.exit(1)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(protocol)
        print(f"协议已保存到: {args.output}", file=sys.stderr)
    else:
        print(protocol)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Symptom Checker Triage (ID: 165)
基于常见症状的红旗征，建议分诊级别(急诊 vs 门诊)
"""

import sys
import json
import argparse
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TriageLevel(Enum):
    EMERGENCY = "emergency"      # 危及生命
    URGENT = "urgent"            # 紧急但非立即致命
    OUTPATIENT = "outpatient"    # 非紧急


@dataclass
class TriageResult:
    triage_level: str
    confidence: float
    red_flags: List[str]
    reason: str
    recommendation: str
    department: str
    warning: str = "此为AI辅助建议，不能替代专业医疗诊断"


# 红旗征定义：症状关键词 -> (红旗征名称, 分诊级别, 权重, 科室建议, 理由)
RED_FLAGS = {
    # 心血管系统 - 紧急
    "胸痛": ("胸痛", TriageLevel.EMERGENCY, 0.95, "急诊科/心内科", "胸痛可能是心肌梗死、主动脉夹层或肺栓塞的征兆"),
    "胸闷": ("胸闷", TriageLevel.EMERGENCY, 0.85, "急诊科/心内科", "胸闷可能是心绞痛或心肌梗死的表现"),
    "心悸": ("心悸", TriageLevel.URGENT, 0.70, "心内科", "心悸可能是心律失常的表现"),
    "晕厥": ("晕厥", TriageLevel.EMERGENCY, 0.90, "急诊科/神经内科", "晕厥可能提示严重心律失常或脑血管意外"),
    "昏迷": ("昏迷", TriageLevel.EMERGENCY, 1.0, "急诊科", "昏迷是危及生命的紧急情况"),

    # 呼吸系统 - 紧急
    "呼吸困难": ("呼吸困难", TriageLevel.EMERGENCY, 0.95, "急诊科/呼吸科", "严重呼吸困难提示呼吸衰竭风险"),
    "呼吸急促": ("呼吸急促", TriageLevel.URGENT, 0.75, "急诊科", "呼吸急促可能是肺部或心脏疾病的表现"),
    "咯血": ("咯血", TriageLevel.EMERGENCY, 0.90, "急诊科/呼吸科", "咯血可能提示肺部严重疾病"),
    "窒息": ("窒息", TriageLevel.EMERGENCY, 1.0, "急诊科", "窒息是危及生命的紧急情况"),

    # 神经系统 - 紧急
    "剧烈头痛": ("剧烈头痛", TriageLevel.EMERGENCY, 0.85, "急诊科/神经内科", "突发剧烈头痛可能是蛛网膜下腔出血"),
    "一生中最痛": ("一生中最痛", TriageLevel.EMERGENCY, 0.95, "急诊科/神经内科", "提示蛛网膜下腔出血可能"),
    "言语不清": ("言语不清", TriageLevel.EMERGENCY, 0.90, "急诊科/神经内科", "可能是中风征兆"),
    "偏瘫": ("偏瘫", TriageLevel.EMERGENCY, 0.95, "急诊科/神经内科", "中风典型症状"),
    "半身不遂": ("半身不遂", TriageLevel.EMERGENCY, 0.95, "急诊科/神经内科", "中风典型症状"),
    "抽搐": ("抽搐", TriageLevel.URGENT, 0.80, "急诊科/神经内科", "可能是癫痫发作"),
    "癫痫": ("癫痫", TriageLevel.URGENT, 0.80, "神经内科", "癫痫发作需要及时就医"),

    # 消化系统 - 紧急
    "呕血": ("呕血", TriageLevel.EMERGENCY, 0.95, "急诊科/消化科", "上消化道大出血"),
    "黑便": ("黑便", TriageLevel.URGENT, 0.80, "消化科", "可能提示上消化道出血"),
    "便血": ("便血", TriageLevel.URGENT, 0.75, "消化科/肛肠科", "消化道出血"),
    "剧烈腹痛": ("剧烈腹痛", TriageLevel.EMERGENCY, 0.85, "急诊科", "可能为阑尾炎、肠穿孔等急腹症"),
    "板状腹": ("板状腹", TriageLevel.EMERGENCY, 0.95, "急诊科/外科", "提示腹膜炎"),
    "停止排气": ("停止排气", TriageLevel.URGENT, 0.75, "外科", "可能为肠梗阻"),

    # 其他系统 - 紧急
    "严重外伤": ("严重外伤", TriageLevel.EMERGENCY, 0.95, "急诊科/外科", "严重创伤需紧急处理"),
    "大出血": ("大出血", TriageLevel.EMERGENCY, 1.0, "急诊科", "失血性休克风险"),
    "药物过量": ("药物过量", TriageLevel.EMERGENCY, 0.90, "急诊科", "中毒需紧急洗胃或解毒"),
    "中毒": ("中毒", TriageLevel.EMERGENCY, 0.95, "急诊科", "中毒需紧急处理"),

    # 儿科/孕妇相关
    "胎动减少": ("胎动减少", TriageLevel.URGENT, 0.80, "妇产科", "可能提示胎儿窘迫"),
    "阴道出血": ("阴道出血", TriageLevel.URGENT, 0.80, "妇产科", "孕期出血需警惕流产或胎盘早剥"),
    "高热惊厥": ("高热惊厥", TriageLevel.URGENT, 0.85, "儿科急诊", "儿童高热惊厥需紧急处理"),
}

# 症状同义词扩展
SYNONYMS = {
    "胸痛": ["胸口痛", "心口痛", "心前区疼痛", "胸部疼痛"],
    "呼吸困难": ["气短", "气促", "喘不上气", "呼吸不畅", "窒息感"],
    "剧烈头痛": ["炸裂样头痛", "爆炸性头痛", "一生中最痛"],
    "偏瘫": ["半身不遂", "一侧肢体无力", "手脚无力"],
    "言语不清": ["说话不清", "口齿不清", "表达困难"],
    "昏迷": ["意识丧失", "不省人事", "叫不醒"],
    "呕血": ["吐血", "呕吐鲜血"],
    "黑便": ["柏油样便", "黑色大便"],
    "剧烈腹痛": ["肚子剧痛", "腹部剧痛", "疼得打滚"],
    "大出血": ["流血不止", "大量出血"],
}

# 常见症状的门诊级别定义
OUTPATIENT_SYMPTOMS = {
    "轻度头痛": ("轻度头痛", TriageLevel.OUTPATIENT, 0.60, "神经内科", "常见症状，建议门诊排查"),
    "低热": ("低热", TriageLevel.OUTPATIENT, 0.50, "内科", "体温<38.5°C可门诊就诊"),
    "咳嗽": ("咳嗽", TriageLevel.OUTPATIENT, 0.40, "呼吸科", "无呼吸困难的咳嗽可门诊处理"),
    "流鼻涕": ("流鼻涕", TriageLevel.OUTPATIENT, 0.30, "耳鼻喉科", "上呼吸道感染常见症状"),
    "咽痛": ("咽痛", TriageLevel.OUTPATIENT, 0.40, "耳鼻喉科", "常见于上呼吸道感染"),
    "轻微腹痛": ("轻微腹痛", TriageLevel.OUTPATIENT, 0.50, "消化科", "无红旗征的轻度腹痛"),
    "腹泻": ("腹泻", TriageLevel.OUTPATIENT, 0.50, "消化科", "无血便、无脱水的腹泻"),
    "皮疹": ("皮疹", TriageLevel.OUTPATIENT, 0.40, "皮肤科", "无发热的皮疹"),
    "关节痛": ("关节痛", TriageLevel.OUTPATIENT, 0.40, "风湿免疫科", "慢性关节痛"),
    "失眠": ("失眠", TriageLevel.OUTPATIENT, 0.30, "神经内科/心理科", "睡眠障碍"),
    "乏力": ("乏力", TriageLevel.OUTPATIENT, 0.40, "内科", "需排查贫血、甲减等"),
}


def expand_synonyms(text: str) -> str:
    """扩展同义词，将所有同义词替换为标准症状名称"""
    expanded = text
    for standard, synonyms in SYNONYMS.items():
        for syn in synonyms:
            if syn in expanded:
                expanded = expanded.replace(syn, standard)
    return expanded


def extract_red_flags(text: str) -> List[Tuple[str, TriageLevel, float, str, str]]:
    """从症状描述中提取红旗征"""
    expanded_text = expand_synonyms(text)
    found_flags = []

    for keyword, (name, level, weight, dept, reason) in RED_FLAGS.items():
        if keyword in expanded_text:
            found_flags.append((name, level, weight, dept, reason))

    # 去重并按权重排序
    seen = set()
    unique_flags = []
    for flag in sorted(found_flags, key=lambda x: x[2], reverse=True):
        if flag[0] not in seen:
            seen.add(flag[0])
            unique_flags.append(flag)

    return unique_flags


def calculate_temperature(text: str) -> Optional[float]:
    """从文本中提取体温"""
    # 匹配各种体温格式
    patterns = [
        r'(\d+\.?\d*)\s*度',
        r'(\d+\.?\d*)\s*°C',
        r'(\d+\.?\d*)\s*°',
        r'体温\s*(\d+\.?\d*)',
        r'发烧\s*(\d+\.?\d*)',
        r'发热\s*(\d+\.?\d*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                temp = float(match.group(1))
                # 判断是摄氏度还是华氏度
                if temp > 50:  # 华氏度转换为摄氏度
                    temp = (temp - 32) * 5 / 9
                return temp
            except ValueError:
                continue
    return None


def extract_outpatient_symptoms(text: str) -> List[Tuple[str, TriageLevel, float, str, str]]:
    """从症状描述中提取门诊级别症状"""
    found = []
    text_lower = text.lower()
    
    # 先检查体温
    temperature = calculate_temperature(text)
    
    for keyword, (name, level, weight, dept, reason) in OUTPATIENT_SYMPTOMS.items():
        if keyword in text:
            found.append((name, level, weight, dept, reason))
    
    # 如果没有找到特定症状但有体温，根据体温判断
    if not found and temperature:
        if temperature < 38:
            found.append(("低热", TriageLevel.OUTPATIENT, 0.50, "内科", f"体温{temperature:.1f}°C，建议门诊就诊"))
        elif temperature < 39:
            found.append(("中等发热", TriageLevel.OUTPATIENT, 0.60, "发热门诊", f"体温{temperature:.1f}°C，可门诊处理"))
    
    # 识别常见症状关键词
    if not found:
        common_keywords = {
            "头痛": ("头痛", TriageLevel.OUTPATIENT, 0.60, "神经内科", "头痛无红旗征可门诊排查"),
            "头晕": ("头晕", TriageLevel.OUTPATIENT, 0.50, "神经内科/耳鼻喉科", "头晕需排查"),
            "恶心": ("恶心", TriageLevel.OUTPATIENT, 0.50, "消化科", "恶心无呕吐可门诊处理"),
            "呕吐": ("呕吐", TriageLevel.OUTPATIENT, 0.60, "消化科", "非剧烈呕吐可门诊处理"),
            "感冒": ("感冒症状", TriageLevel.OUTPATIENT, 0.50, "内科", "普通感冒症状"),
            "发烧": ("发热", TriageLevel.OUTPATIENT, 0.60, "发热门诊", "发热需进一步检查"),
            "发热": ("发热", TriageLevel.OUTPATIENT, 0.60, "发热门诊", "发热需进一步检查"),
        }
        for keyword, symptom_info in common_keywords.items():
            if keyword in text:
                found.append(symptom_info)
    
    return found


def triage(symptom_text: str) -> TriageResult:
    """
    主分诊函数

    Args:
        symptom_text: 症状描述文本

    Returns:
        TriageResult: 分诊结果
    """
    if not symptom_text or not symptom_text.strip():
        return TriageResult(
            triage_level=TriageLevel.OUTPATIENT.value,
            confidence=0.0,
            red_flags=[],
            reason="未提供症状描述",
            recommendation="请提供症状描述以便分诊",
            department="未知"
        )

    # 提取红旗征
    red_flags = extract_red_flags(symptom_text)

    # 提取体温
    temperature = calculate_temperature(symptom_text)

    # 检查高热
    if temperature and temperature >= 40:
        red_flags.append(("高热(≥40°C)", TriageLevel.EMERGENCY, 0.90, "急诊科", "高热伴意识改变需紧急处理"))
    elif temperature and temperature >= 39:
        red_flags.append(("高热(≥39°C)", TriageLevel.URGENT, 0.70, "发热门诊", "高热需及时就医"))

    # 如果有红旗征
    if red_flags:
        # 取最严重的级别
        max_level = max(red_flags, key=lambda x: x[2])
        level = max_level[1]
        confidence = min(0.95, max(flag[2] for flag in red_flags))
        flag_names = [flag[0] for flag in red_flags]
        departments = list(dict.fromkeys(flag[3] for flag in red_flags))  # 去重保持顺序
    
        if level == TriageLevel.EMERGENCY:
            recommendation = "立即前往急诊就诊，必要时拨打120"
        elif level == TriageLevel.URGENT:
            recommendation = "建议2-4小时内就医，可前往急诊或发热门诊"
        else:
            recommendation = "建议尽快预约门诊就诊"

        # 合并理由
        reasons = [f"{flag[0]}: {flag[4]}" for flag in red_flags[:3]]
        reason = "; ".join(reasons)

        return TriageResult(
            triage_level=level.value,
            confidence=confidence,
            red_flags=flag_names,
            reason=reason,
            recommendation=recommendation,
            department="/".join(departments[:2])
        )

    # 检查门诊级别症状
    outpatient = extract_outpatient_symptoms(symptom_text)
    if outpatient:
        max_symptom = max(outpatient, key=lambda x: x[2])
        return TriageResult(
            triage_level=TriageLevel.OUTPATIENT.value,
            confidence=max_symptom[2],
            red_flags=[],
            reason=f"症状'{max_symptom[0]}'无红旗征，可门诊处理",
            recommendation="建议预约门诊就诊，如症状加重请及时就医",
            department=max_symptom[3]
        )

    # 无法识别的症状
    return TriageResult(
        triage_level=TriageLevel.OUTPATIENT.value,
        confidence=0.30,
        red_flags=[],
        reason="无法识别的症状，建议就医评估",
        recommendation="建议预约内科门诊进行初步评估",
        department="内科"
    )


def interactive_mode():
    """交互模式"""
    print("=" * 50)
    print("症状分诊助手 (Symptom Checker Triage)")
    print("=" * 50)
    print("请输入症状描述(如'胸痛，呼吸困难')，输入'quit'退出")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n症状描述: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q', '退出']:
                print("感谢使用，再见！")
                break

            if not user_input:
                continue

            result = triage(user_input)
            print_result(result)

        except KeyboardInterrupt:
            print("\n感谢使用，再见！")
            break
        except EOFError:
            break


def supports_color() -> bool:
    """检测终端是否支持颜色"""
    import os
    return sys.stdout.isatty() and os.environ.get('TERM') not in ('dumb', '')


def print_result(result: TriageResult, verbose: bool = False):
    """打印分诊结果"""
    use_color = supports_color()
    level_colors = {
        "emergency": "\033[91m" if use_color else "",  # 红色
        "urgent": "\033[93m" if use_color else "",     # 黄色
        "outpatient": "\033[92m" if use_color else "", # 绿色
    }
    reset = "\033[0m" if use_color else ""

    level_display = {
        "emergency": "🔴 急诊 (Emergency)",
        "urgent": "🟠 紧急 (Urgent)",
        "outpatient": "🟢 门诊 (Outpatient)",
    }

    level = result.triage_level
    color = level_colors.get(level, "")

    print("\n" + "=" * 50)
    print(f"分诊级别: {color}{level_display.get(level, level)}{reset}")
    print(f"置信度: {result.confidence:.0%}")

    if result.red_flags:
        print(f"\n🚨 识别到的红旗征:")
        for flag in result.red_flags:
            print(f"   - {flag}")

    print(f"\n📋 分诊理由:")
    print(f"   {result.reason}")

    print(f"\n💡 建议:")
    print(f"   {result.recommendation}")

    print(f"\n🏥 建议科室: {result.department}")

    if verbose:
        print(f"\n⚠️  免责声明: {result.warning}")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="症状分诊助手 - 基于红旗征建议分诊级别",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py "胸痛，向左臂放射，出汗"
  python main.py --interactive
  python main.py "头痛，发烧38度" --verbose
        """
    )
    parser.add_argument(
        "symptoms",
        nargs="?",
        help="症状描述(如'胸痛，呼吸困难')"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="进入交互模式"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以JSON格式输出"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.symptoms:
        parser.print_help()
        print("\n错误: 请提供症状描述或使用--interactive进入交互模式")
        sys.exit(1)

    result = triage(args.symptoms)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_result(result, verbose=args.verbose)


if __name__ == "__main__":
    main()

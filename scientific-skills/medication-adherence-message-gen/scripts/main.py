#!/usr/bin/env python3
"""
Medication Adherence Message Generator
基于行为心理学原理的服药提醒文案生成器

ID: 136
Author: OpenClaw
"""

import argparse
import json
import random
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from enum import Enum


class Principle(str, Enum):
    """行为心理学原理"""
    SOCIAL_NORMS = "social_norms"          # 社会规范
    LOSS_AVERSION = "loss_aversion"        # 损失厌恶
    IMPLEMENTATION = "implementation"      # 执行意图
    REWARD = "reward"                      # 即时奖励
    COMMITMENT = "commitment"              # 承诺一致性
    SELF_EFFICACY = "self_efficacy"        # 自我效能
    ANCHORING = "anchoring"                # 锚定效应
    SCARCITY = "scarcity"                  # 稀缺性
    RANDOM = "random"                      # 随机选择


class Tone(str, Enum):
    """语气风格"""
    GENTLE = "gentle"                      # 温和
    FIRM = "firm"                          # 坚定
    ENCOURAGING = "encouraging"            # 鼓励
    URGENT = "urgent"                      # 紧急


class Language(str, Enum):
    """语言"""
    ZH = "zh"                              # 中文
    EN = "en"                              # 英文


@dataclass
class MessageResult:
    """消息生成结果"""
    medication: str
    patient_name: Optional[str]
    dosage: Optional[str]
    time: Optional[str]
    principle: str
    tone: str
    message: str
    psychology_insight: str
    alternative_messages: List[str]


# ============ 中文文案模板 ============

TEMPLATES_ZH = {
    Principle.SOCIAL_NORMS: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}{time_prompt}大多数和您一样的患者都能坚持按时服药，您也在其中。请{action}。",
            "【健康提醒】{greeting}研究表明，95%服用{medication}的患者都能保持良好的服药习惯。相信您也可以！{time_prompt}请{action}。",
            "【用药时间】{greeting}{time_prompt}和您病情相似的患者中，9成以上都坚持每日服药。您也是这个优秀群体的一员，请{action}。"
        ],
        Tone.FIRM: [
            "【重要提醒】{greeting}按时服用{medication}是康复的关键。90%以上的患者都能做到，您也不能例外。{time_prompt}立即{action}！",
            "【服药通知】{greeting}{time_prompt}请服用{medication}。绝大多数患者都能坚持，这是对自己负责的基本态度。",
        ],
        Tone.ENCOURAGING: [
            "【加油】{greeting}您正在和成千上万的患者一起，坚持服用{medication}。{time_prompt}请{action}，我们都在支持您！",
            "【健康伙伴】{greeting}您不是一个人在战斗！每天都有数百万人在按时服药。{time_prompt}请{action}，继续保持！",
        ],
        Tone.URGENT: [
            "【紧急提醒】{greeting}{time_prompt}请务必服用{medication}。中断用药会让您脱离康复正轨，95%的患者都不会这样做！",
        ]
    },
    Principle.LOSS_AVERSION: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}{time_prompt}请{action}。错过这次服药，可能会影响治疗效果哦。",
            "【健康守护】{greeting}每一次按时服药，都是在保护您的健康成果。{time_prompt}请{action}，不要让之前的努力白费。",
            "【用药提示】{greeting}漏服{medication}可能导致病情波动。{time_prompt}请{action}，守护您的健康。"
        ],
        Tone.FIRM: [
            "【重要警告】{greeting}{time_prompt}请立即{action}。漏服{medication}会让治疗效果大打折扣，前功尽弃！",
            "【请勿忽视】{greeting}每一次漏服，都是对健康的透支。{time_prompt}请{action}，别让病情有机会反扑。",
        ],
        Tone.ENCOURAGING: [
            "【明智选择】{greeting}{time_prompt}请{action}。今天的一小步，是避免未来健康风险的一大步！",
            "【投资健康】{greeting}现在按时服药，就是在为未来省钱省心。{time_prompt}请{action}，这是最值得的投资！",
        ],
        Tone.URGENT: [
            "【立即行动】{greeting}{time_prompt}必须服用{medication}！每一次延误都在增加健康风险，不要让小疏忽变成大问题！",
        ]
    },
    Principle.IMPLEMENTATION: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}如果{time}到了，那么就{action}。养成这个习惯，健康就在掌握中。",
            "【执行计划】{greeting}{time_prompt}执行您的服药计划：如果现在是{time}，那么就服用{medication}。",
            "【习惯养成】{greeting}设定好的规则：{time} = 服用{medication}。{time_prompt}请执行这个计划。"
        ],
        Tone.FIRM: [
            "【严格执行】{greeting}{time_prompt}执行预定计划：如果{time}，则必须{action}。没有借口！",
            "【规则遵守】{greeting}您给自己定的规则：{time}服用{medication}。{time_prompt}请遵守承诺。",
        ],
        Tone.ENCOURAGING: [
            "【计划达成】{greeting}{time_prompt}又到了执行"如果{time}，就服药"计划的时刻！请{action}，您正在养成好习惯！",
            "【习惯力量】{greeting}当{time}到来，服药就是自然而然的事。{time_prompt}请{action}，让好习惯成为本能！",
        ],
        Tone.URGENT: [
            "【立刻执行】{greeting}{time_prompt}马上执行您的服药计划！如果{time}，那么必须立即{action}！",
        ]
    },
    Principle.REWARD: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}{time_prompt}请{action}。服药后可以喝杯喜欢的茶，这是对自己负责的奖励。",
            "【健康奖励】{greeting}完成今天的服药，您就离康复又近了一步！{time_prompt}请{action}，给自己一个肯定。",
            "【小确幸】{greeting}{time_prompt}请{action}。完成后给自己一个小小的奖励吧，您值得拥有！"
        ],
        Tone.FIRM: [
            "【即时反馈】{greeting}{time_prompt}请{action}。每一颗药都是身体康复的燃料，立即兑现这份健康！",
            "【成果可见】{greeting}按时服药，身体正在变好——这是真实的回报。{time_prompt}请{action}！",
        ],
        Tone.ENCOURAGING: [
            "【庆祝时刻】{greeting}{time_prompt}请{action}，然后为自己鼓掌！每一次坚持都值得庆祝！",
            "【奖励自己】{greeting}恭喜！又是按时服药的一天！{time_prompt}请{action}，然后做件让自己开心的事！",
        ],
        Tone.URGENT: [
            "【不要错过】{greeting}{time_prompt}立即{action}！不要让今天的健康奖励溜走！",
        ]
    },
    Principle.COMMITMENT: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}记得您对健康的承诺吗？{time_prompt}请{action}，这是对自己的约定。",
            "【承诺兑现】{greeting}您曾答应要好好照顾自己。{time_prompt}请{action}，履行这个重要的承诺。",
            "【约定提醒】{greeting}您与医生、家人和自己有一个约定：按时服药。{time_prompt}请{action}。"
        ],
        Tone.FIRM: [
            "【信守承诺】{greeting}{time_prompt}请{action}。承诺不是空话，是用行动证明的决心！",
            "【责任担当】{greeting}您对自己的承诺，现在需要兑现。{time_prompt}请{action}，做值得信赖的人。",
        ],
        Tone.ENCOURAGING: [
            "【承诺之星】{greeting}您是说到做到的人！{time_prompt}请{action}，继续履行对健康的承诺！",
            "【骄傲时刻】{greeting}坚持承诺让您闪闪发光！{time_prompt}请{action}，再次证明自己的决心！",
        ],
        Tone.URGENT: [
            "【立即兑现】{greeting}{time_prompt}马上{action}！现在就兑现您对健康的承诺，不要拖延！",
        ]
    },
    Principle.SELF_EFFICACY: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}您有能力管理好自己的健康。{time_prompt}请{action}，相信自己。",
            "【自信提醒】{greeting}过去您做得很好，今天也一样可以。{time_prompt}请{action}，您完全做得到。",
            "【能力肯定】{greeting}掌控健康就在您的手中。{time_prompt}请{action}，您有能力做到。"
        ],
        Tone.FIRM: [
            "【相信自我】{greeting}您有能力，也有决心。{time_prompt}请{action}，证明给自己看！",
            "【实力展现】{greeting}管理服药这件事，您完全掌控。{time_prompt}请{action}，展现您的行动力！",
        ],
        Tone.ENCOURAGING: [
            "【您真棒】{greeting}每次按时服药都证明您很厉害！{time_prompt}请{action}，再次战胜自己！",
            "【冠军心态】{greeting}您是健康管理的高手！{time_prompt}请{action}，让成功成为习惯！",
        ],
        Tone.URGENT: [
            "【立即行动】{greeting}您有能力做得更好！{time_prompt}马上{action}，用行动证明您的自控力！",
        ]
    },
    Principle.ANCHORING: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}{time_prompt}请{action}。目标是连续30天按时服药，今天是第{day}天！",
            "【量化目标】{greeting}每日{dosage}，这是您的标准剂量。{time_prompt}请{action}，保持精准。",
            "【具体行动】{greeting}精确到{time}，服用{dosage}。{time_prompt}请执行这个具体计划。"
        ],
        Tone.FIRM: [
            "【严格执行】{greeting}标准剂量：{dosage}，标准时间：{time}。{time_prompt}请精准{action}！",
            "【目标锁定】{greeting}30天计划进行中，今天第{day}天。{time_prompt}请{action}，不偏离目标！",
        ],
        Tone.ENCOURAGING: [
            "【进度更新】{greeting}已完成{progress}%的月度目标！{time_prompt}请{action}，离30天全勤又近一步！",
            "【具体成就】{greeting}今天是第{day}天按时服药！{time_prompt}请{action}，具体目标，具体完成！",
        ],
        Tone.URGENT: [
            "【马上完成】{greeting}30天目标，第{day}天不能断！{time_prompt}立即{action}，完成今天的具体指标！",
        ]
    },
    Principle.SCARCITY: {
        Tone.GENTLE: [
            "【{medication}提醒】{greeting}{time_prompt}是服药的最佳时间窗口，请{action}。",
            "【时机重要】{greeting}药物在体内的最佳浓度需要按时维持。{time_prompt}请{action}，不要错过这个时机。",
            "【窗口期】{greeting}现在正是{medication}发挥最佳效果的时段。{time_prompt}请{action}。"
        ],
        Tone.FIRM: [
            "【时间有限】{greeting}最佳服药窗口正在关闭！{time_prompt}请立即{action}，时机不等人！",
            "【勿失良机】{greeting}错过{time}这个关键时间点，效果会打折扣。{time_prompt}请{action}！",
        ],
        Tone.ENCOURAGING: [
            "【把握当下】{greeting}{time_prompt}是服用{medication}的黄金时间！请{action}，抓住这个机会！",
            "【珍贵时刻】{greeting}每一个服药时间点都是珍贵的康复机会！{time_prompt}请{action}，珍惜当下！",
        ],
        Tone.URGENT: [
            "【刻不容缓】{greeting}最佳服药时间正在流逝！{time_prompt}马上{action}，错过不再有！",
        ]
    }
}


# ============ 英文文案模板 ============

TEMPLATES_EN = {
    Principle.SOCIAL_NORMS: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Most patients like you take their medication on time. You're one of them. Please {action}.",
            "[Health Reminder] {greeting}Research shows 95% of patients taking {medication} maintain good adherence. You can too! {time_prompt}Please {action}.",
        ],
        Tone.FIRM: [
            "[Important] {greeting}Taking {medication} on time is key to recovery. 90%+ of patients do it, and so should you. {time_prompt}{action}!",
        ],
        Tone.ENCOURAGING: [
            "[Keep Going] {greeting}You're taking {medication} alongside thousands of others! {time_prompt}Please {action}, we're all supporting you!",
        ],
        Tone.URGENT: [
            "[Urgent] {greeting}{time_prompt}Please take {medication} now. Missing doses puts you off track—95% of patients don't skip!",
        ]
    },
    Principle.LOSS_AVERSION: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Missing this dose might affect your treatment progress.",
            "[Health Guard] {greeting}Every dose on time protects your health gains. {time_prompt}Please {action}, don't let previous efforts go to waste.",
        ],
        Tone.FIRM: [
            "[Warning] {greeting}{time_prompt}Take {medication} now! Missing doses significantly reduces treatment effectiveness.",
        ],
        Tone.ENCOURAGING: [
            "[Smart Choice] {greeting}{time_prompt}Please {action}. Today's small step prevents future health risks!",
        ],
        Tone.URGENT: [
            "[Act Now] {greeting}{time_prompt}Must take {medication}! Every delay increases health risks—don't let small oversights become big problems!",
        ]
    },
    Principle.IMPLEMENTATION: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}If it's {time}, then {action}. Build this habit and health is in your hands.",
            "[Execute Plan] {greeting}{time_prompt}Follow your plan: If it's {time}, then take {medication}.",
        ],
        Tone.FIRM: [
            "[Strict Schedule] {greeting}{time_prompt}Execute your plan: If {time}, then must {action}. No excuses!",
        ],
        Tone.ENCOURAGING: [
            "[Plan Success] {greeting}{time_prompt}Time to execute your 'If {time}, then take medicine' plan! {action}, you're building a great habit!",
        ],
        Tone.URGENT: [
            "[Execute Now] {greeting}{time_prompt}Execute your plan immediately! If {time}, then you must {action} now!",
        ]
    },
    Principle.REWARD: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Afterward, enjoy your favorite tea as a reward for taking care of yourself.",
            "[Health Reward] {greeting}Completing today's dose brings you closer to recovery! {time_prompt}Please {action}, give yourself credit.",
        ],
        Tone.FIRM: [
            "[Instant Feedback] {greeting}{time_prompt}Please {action}. Each pill is fuel for your recovery—cash in on this health now!",
        ],
        Tone.ENCOURAGING: [
            "[Celebrate] {greeting}{time_prompt}Please {action}, then give yourself applause! Every persistence deserves celebration!",
        ],
        Tone.URGENT: [
            "[Don't Miss] {greeting}{time_prompt}{action} immediately! Don't let today's health reward slip away!",
        ]
    },
    Principle.COMMITMENT: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}Remember your commitment to health? {time_prompt}Please {action}, this is a promise to yourself.",
            "[Honor Promise] {greeting}You promised to take good care of yourself. {time_prompt}Please {action}, fulfill this important commitment.",
        ],
        Tone.FIRM: [
            "[Keep Promise] {greeting}{time_prompt}Please {action}. Commitments aren't empty words—they're proven through action!",
        ],
        Tone.ENCOURAGING: [
            "[Promise Star] {greeting}You're someone who keeps their word! {time_prompt}Please {action}, continue honoring your health commitment!",
        ],
        Tone.URGENT: [
            "[Fulfill Now] {greeting}{time_prompt}{action} now! Fulfill your health commitment immediately, no delay!",
        ]
    },
    Principle.SELF_EFFICACY: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}You have the ability to manage your health well. {time_prompt}Please {action}, believe in yourself.",
            "[Confidence] {greeting}You've done well before, and you can today too. {time_prompt}Please {action}, you're completely capable.",
        ],
        Tone.FIRM: [
            "[Believe] {greeting}You have the ability and determination. {time_prompt}Please {action}, prove it to yourself!",
        ],
        Tone.ENCOURAGING: [
            "[You're Great] {greeting}Every dose on time proves how capable you are! {time_prompt}Please {action}, conquer yourself again!",
        ],
        Tone.URGENT: [
            "[Act Now] {greeting}You can do even better! {time_prompt}{action} now, prove your self-control through action!",
        ]
    },
    Principle.ANCHORING: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Goal: 30 consecutive days, today is day {day}!",
            "[Quantify Goal] {greeting}{dosage} daily is your standard dose. {time_prompt}Please {action}, stay precise.",
        ],
        Tone.FIRM: [
            "[Strict] {greeting}Standard dose: {dosage}, standard time: {time}. {time_prompt}Please {action} precisely!",
        ],
        Tone.ENCOURAGING: [
            "[Progress Update] {greeting}{progress}% of monthly goal completed! {time_prompt}Please {action}, one step closer to 30-day perfect record!",
        ],
        Tone.URGENT: [
            "[Complete Now] {greeting}30-day goal, day {day} can't break! {time_prompt}{action} immediately, complete today's target!",
        ]
    },
    Principle.SCARCITY: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}is your optimal medication window. Please {action}.",
            "[Timing Matters] {greeting}Medication works best when taken on schedule. {time_prompt}Please {action}, don't miss this window.",
        ],
        Tone.FIRM: [
            "[Limited Time] {greeting}Optimal medication window is closing! {time_prompt}Please {action} now, timing waits for no one!",
        ],
        Tone.ENCOURAGING: [
            "[Seize Moment] {greeting}{time_prompt}is the golden time for {medication}! Please {action}, seize this opportunity!",
        ],
        Tone.URGENT: [
            "[Act Fast] {greeting}Best medication time is passing! {time_prompt}{action} now, this chance won't come again!",
        ]
    }
}


# 心理学原理解释
PSYCHOLOGY_INSIGHTS_ZH = {
    Principle.SOCIAL_NORMS: "利用社会规范原理，通过强调高依从性率来增强患者的行为动机，让患者感到自己是'正常'群体的一员",
    Principle.LOSS_AVERSION: "利用损失厌恶原理，强调不按时服药会失去什么，相比获得同等收益，人们更在意避免损失",
    Principle.IMPLEMENTATION: "利用执行意图原理，通过'如果-那么'计划帮助患者建立自动化的服药习惯，减少决策疲劳",
    Principle.REWARD: "利用即时奖励原理，将服药行为与正向反馈关联，增强内在动机和重复行为的可能性",
    Principle.COMMITMENT: "利用承诺一致性原理，强化患者对自己、医生和家人的承诺，增强责任感和履约动力",
    Principle.SELF_EFFICACY: "利用自我效能原理，增强患者对自我管理能力的信心，相信自己能够成功执行服药行为",
    Principle.ANCHORING: "利用锚定效应，提供具体量化的目标（如30天计划），让抽象的健康管理变得具体可追踪",
    Principle.SCARCITY: "利用稀缺性原理，强调服药时间窗口的有限性，制造适度紧迫感以促进即时行动"
}

PSYCHOLOGY_INSIGHTS_EN = {
    Principle.SOCIAL_NORMS: "Uses social norms to enhance motivation by emphasizing high adherence rates, making patients feel part of the 'normal' group",
    Principle.LOSS_AVERSION: "Uses loss aversion to emphasize what patients stand to lose by missing doses—people prefer avoiding losses to acquiring equivalent gains",
    Principle.IMPLEMENTATION: "Uses implementation intentions through 'if-then' plans to help patients build automatic habits and reduce decision fatigue",
    Principle.REWARD: "Uses immediate rewards to associate medication behavior with positive feedback, enhancing intrinsic motivation",
    Principle.COMMITMENT: "Uses commitment and consistency to strengthen patients' promises to themselves, doctors, and family, enhancing responsibility",
    Principle.SELF_EFFICACY: "Uses self-efficacy to boost patients' confidence in their ability to manage medication successfully",
    Principle.ANCHORING: "Uses anchoring by providing specific quantifiable goals (e.g., 30-day plan), making abstract health management concrete",
    Principle.SCARCITY: "Uses scarcity to emphasize the limited medication window, creating urgency to prompt immediate action"
}


def get_greeting(name: Optional[str], language: Language) -> str:
    """获取问候语"""
    if not name:
        return ""
    if language == Language.ZH:
        return f"{name}，"
    else:
        return f"Hi {name}, "


def get_time_prompt(time: Optional[str], language: Language) -> str:
    """获取时间提示"""
    if not time:
        return ""
    if language == Language.ZH:
        return f"现在是{time}。"
    else:
        return f"It's {time}. "


def get_action_text(medication: str, dosage: Optional[str], language: Language) -> str:
    """获取行动文本"""
    if language == Language.ZH:
        if dosage:
            return f"服用{dosage}的{medication}"
        else:
            return f"服用{medication}"
    else:
        if dosage:
            return f"take {dosage} of {medication}"
        else:
            return f"take your {medication}"


def generate_message(
    medication: str,
    patient_name: Optional[str] = None,
    dosage: Optional[str] = None,
    time: Optional[str] = None,
    principle: Principle = Principle.RANDOM,
    tone: Tone = Tone.ENCOURAGING,
    language: Language = Language.ZH,
    day: int = 1,
    progress: int = 50
) -> MessageResult:
    """
    生成服药提醒消息
    
    Args:
        medication: 药物名称
        patient_name: 患者姓名
        dosage: 剂量
        time: 服药时间
        principle: 心理学原理
        tone: 语气风格
        language: 语言
        day: 第几天（用于锚定效应）
        progress: 进度百分比（用于锚定效应）
    
    Returns:
        MessageResult: 包含主消息和替代消息的结果对象
    """
    # 选择模板库
    templates = TEMPLATES_ZH if language == Language.ZH else TEMPLATES_EN
    insights = PSYCHOLOGY_INSIGHTS_ZH if language == Language.ZH else PSYCHOLOGY_INSIGHTS_EN
    
    # 随机选择原理
    if principle == Principle.RANDOM:
        principle = random.choice([
            Principle.SOCIAL_NORMS, Principle.LOSS_AVERSION,
            Principle.IMPLEMENTATION, Principle.REWARD,
            Principle.COMMITMENT, Principle.SELF_EFFICACY,
            Principle.ANCHORING, Principle.SCARCITY
        ])
    
    # 获取该原理和语气的模板
    principle_templates = templates.get(principle, templates[Principle.SOCIAL_NORMS])
    tone_templates = principle_templates.get(tone, principle_templates[Tone.ENCOURAGING])
    
    # 准备变量
    greeting = get_greeting(patient_name, language)
    time_prompt = get_time_prompt(time, language)
    action = get_action_text(medication, dosage, language)
    
    # 生成主消息和备选消息
    messages = []
    for template in tone_templates:
        try:
            msg = template.format(
                medication=medication,
                greeting=greeting,
                time_prompt=time_prompt,
                action=action,
                time=time or ("now" if language == Language.EN else "现在"),
                dosage=dosage or ("your dose" if language == Language.EN else "规定剂量"),
                day=day,
                progress=progress
            )
            messages.append(msg)
        except KeyError:
            # 某些模板可能不包含所有变量
            continue
    
    if not messages:
        # 保底消息
        if language == Language.ZH:
            messages = [f"【服药提醒】{greeting}请按时服用{medication}。"]
        else:
            messages = [f"[Medication Reminder] {greeting}Please take your {medication} on time."]
    
    # 主消息是第一条，其余作为备选
    main_message = messages[0]
    alternative_messages = messages[1:]
    
    # 添加其他语气的备选消息
    all_tones = [Tone.GENTLE, Tone.FIRM, Tone.ENCOURAGING, Tone.URGENT]
    for other_tone in all_tones:
        if other_tone != tone and len(alternative_messages) < 3:
            other_templates = principle_templates.get(other_tone, [])
            if other_templates:
                try:
                    alt_msg = random.choice(other_templates).format(
                        medication=medication,
                        greeting=greeting,
                        time_prompt=time_prompt,
                        action=action,
                        time=time or ("now" if language == Language.EN else "现在"),
                        dosage=dosage or ("your dose" if language == Language.EN else "规定剂量"),
                        day=day,
                        progress=progress
                    )
                    if alt_msg not in alternative_messages:
                        alternative_messages.append(f"[{other_tone.value}] {alt_msg}")
                except:
                    pass
    
    return MessageResult(
        medication=medication,
        patient_name=patient_name,
        dosage=dosage,
        time=time,
        principle=principle.value,
        tone=tone.value,
        message=main_message,
        psychology_insight=insights.get(principle, ""),
        alternative_messages=alternative_messages[:3]  # 最多3条备选
    )


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Medication Adherence Message Generator - 基于行为心理学的服药提醒文案生成器"
    )
    
    parser.add_argument("-n", "--name", type=str, help="患者姓名 (Patient name)")
    parser.add_argument("-m", "--medication", type=str, required=True, help="药物名称 (Medication name)")
    parser.add_argument("-d", "--dosage", type=str, help="剂量 (Dosage, e.g., '20mg')")
    parser.add_argument("-t", "--time", type=str, help="服药时间 (Time, e.g., '早餐后')")
    parser.add_argument(
        "-p", "--principle",
        type=str,
        choices=[p.value for p in Principle],
        default="random",
        help="心理学原理 (Psychological principle)"
    )
    parser.add_argument(
        "--tone",
        type=str,
        choices=[t.value for t in Tone],
        default="encouraging",
        help="语气风格 (Tone style)"
    )
    parser.add_argument("-l", "--language", type=str, choices=["zh", "en"], default="zh", help="语言 (Language)")
    parser.add_argument("-o", "--output", type=str, choices=["text", "json"], default="text", help="输出格式 (Output format)")
    parser.add_argument("--day", type=int, default=1, help="第几天 (Day number for anchoring)")
    parser.add_argument("--progress", type=int, default=50, help="进度百分比 (Progress percentage)")
    
    args = parser.parse_args()
    
    # 生成消息
    result = generate_message(
        medication=args.medication,
        patient_name=args.name,
        dosage=args.dosage,
        time=args.time,
        principle=Principle(args.principle),
        tone=Tone(args.tone),
        language=Language(args.language),
        day=args.day,
        progress=args.progress
    )
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print("=" * 50)
        print("📋 服药提醒文案")
        print("=" * 50)
        print(f"\n📝 主消息:\n{result.message}\n")
        
        print(f"🧠 心理学原理: {result.principle}")
        print(f"💡 原理说明: {result.psychology_insight}\n")
        
        if result.alternative_messages:
            print("📎 备选文案:")
            for i, alt in enumerate(result.alternative_messages, 1):
                print(f"  {i}. {alt}")
            print()
        
        print("=" * 50)
        print(f"药物: {result.medication}")
        if result.patient_name:
            print(f"患者: {result.patient_name}")
        if result.dosage:
            print(f"剂量: {result.dosage}")
        if result.time:
            print(f"时间: {result.time}")
        print(f"语气: {result.tone}")
        print("=" * 50)


if __name__ == "__main__":
    main()

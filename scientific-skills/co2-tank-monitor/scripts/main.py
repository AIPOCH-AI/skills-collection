#!/usr/bin/env python3
"""
CO2 Tank Monitor - 二氧化碳气瓶监控系统
模拟物联网监控，预测气瓶耗尽时间，防止周末断气。
"""

import argparse
import random
import sys
from datetime import datetime, timedelta


def get_current_time() -> datetime:
    """获取当前时间（方便测试时mock）"""
    return datetime.now()


def simulate_sensor_data():
    """模拟传感器读取数据"""
    # 模拟40L气瓶，满压约15MPa，工作压力8-10MPa，报警压力约2MPa
    pressure = round(random.uniform(2.5, 12.0), 2)
    capacity = random.choice([10, 40])
    daily_consumption = round(random.uniform(0.5, 3.0), 2)
    return pressure, capacity, daily_consumption


def calculate_remaining_days(pressure: float, daily_consumption: float) -> float:
    """计算剩余天数"""
    if daily_consumption <= 0:
        return float('inf')
    return pressure / daily_consumption


def calculate_depletion_time(remaining_days: float) -> datetime:
    """计算预计耗尽时间"""
    return get_current_time() + timedelta(days=remaining_days)


def is_weekend(dt: datetime) -> bool:
    """判断是否为周末（周六或周日）"""
    return dt.weekday() >= 5  # 5=周六, 6=周日


def will_deplete_on_weekend(depletion_time: datetime, alert_days: int) -> bool:
    """检查是否会在周末期间耗尽"""
    now = get_current_time()
    
    # 计算预警开始时间
    alert_start = now + timedelta(days=alert_days)
    
    # 如果耗尽时间在预警期内且在周末
    if depletion_time <= alert_start:
        return is_weekend(depletion_time)
    
    # 检查是否会跨越周末
    days_until_depletion = (depletion_time - now).days
    for i in range(int(days_until_depletion) + 1):
        check_day = now + timedelta(days=i)
        if is_weekend(check_day) and check_day <= depletion_time:
            # 如果在周末期间耗尽
            weekend_start = check_day.replace(hour=0, minute=0, second=0)
            weekend_end = weekend_start + timedelta(days=2)
            if weekend_start <= depletion_time <= weekend_end:
                return True
    
    return False


def get_status(remaining_days: float, alert_days: int, depletion_time: datetime) -> tuple:
    """
    获取状态码和描述
    返回: (status_code, status_icon, status_text, recommendations)
    """
    if remaining_days <= 0:
        return 2, "🔴", "已耗尽", ["⚠️  气瓶已空！请立即更换！"]
    
    weekend_risk = will_deplete_on_weekend(depletion_time, alert_days)
    
    if remaining_days <= alert_days or weekend_risk:
        recommendations = []
        if remaining_days <= alert_days:
            recommendations.append(f"⚠️  气瓶将在 {remaining_days:.1f} 天内耗尽")
        if weekend_risk:
            recommendations.append("⚠️  气瓶将在周末耗尽！")
        recommendations.append("💡 建议: 请立即更换气瓶或安排周末值班")
        return 2, "🔴", "危险", recommendations
    
    if remaining_days <= alert_days + 2:
        return 1, "🟡", "注意", [
            f"⏰ 剩余时间: {remaining_days:.1f} 天",
            "💡 建议: 请关注气瓶状态，准备更换"
        ]
    
    return 0, "🟢", "正常", [
        f"✅ 剩余时间充足: {remaining_days:.1f} 天",
        "💡 无需特别行动"
    ]


def format_report(
    pressure: float,
    capacity: int,
    daily_consumption: float,
    remaining_days: float,
    depletion_time: datetime,
    status_code: int,
    status_icon: str,
    status_text: str,
    recommendations: list
) -> str:
    """格式化报告"""
    now = get_current_time()
    
    # 格式化耗尽时间，显示星期
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_str = weekdays[depletion_time.weekday()]
    depletion_str = depletion_time.strftime(f"%Y-%m-%d %H:%M ({weekday_str})")
    
    report_lines = [
        "=" * 40,
        "       CO2 气瓶监控报告",
        "=" * 40,
        f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📊 传感器数据:",
        f"   当前压力: {pressure:.2f} MPa",
        f"   气瓶容量: {capacity} L",
        f"   日均消耗: {daily_consumption:.2f} MPa/day",
        "",
        "⏱️  预测分析:",
        f"   预计剩余天数: {remaining_days:.1f} 天",
        f"   预计耗尽时间: {depletion_str}",
        "",
        f"🚨 预警状态: {status_icon} {status_text}",
    ]
    
    for rec in recommendations:
        report_lines.append(f"   {rec}")
    
    report_lines.append("=" * 40)
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="CO2 Tank Monitor - 监控二氧化碳气瓶状态，防止周末断气"
    )
    parser.add_argument(
        "--pressure", "-p",
        type=float,
        default=8.0,
        help="当前气瓶压力 (MPa)，默认 8.0"
    )
    parser.add_argument(
        "--capacity", "-c",
        type=int,
        default=40,
        choices=[10, 40],
        help="气瓶容量 (L)，默认 40"
    )
    parser.add_argument(
        "--daily-consumption", "-d",
        type=float,
        default=1.5,
        help="日均消耗量 (MPa/day)，默认 1.5"
    )
    parser.add_argument(
        "--alert-days", "-a",
        type=int,
        default=2,
        help="提前预警天数，默认 2"
    )
    parser.add_argument(
        "--simulate", "-s",
        action="store_true",
        help="启用模拟模式（随机生成数据）"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，仅输出返回码"
    )
    
    args = parser.parse_args()
    
    # 获取数据
    if args.simulate:
        pressure, capacity, daily_consumption = simulate_sensor_data()
    else:
        pressure = args.pressure
        capacity = args.capacity
        daily_consumption = args.daily_consumption
    
    # 计算
    remaining_days = calculate_remaining_days(pressure, daily_consumption)
    depletion_time = calculate_depletion_time(remaining_days)
    
    # 获取状态
    status_code, status_icon, status_text, recommendations = get_status(
        remaining_days, args.alert_days, depletion_time
    )
    
    # 输出报告
    if not args.quiet:
        report = format_report(
            pressure, capacity, daily_consumption,
            remaining_days, depletion_time,
            status_code, status_icon, status_text, recommendations
        )
        print(report)
    
    # 返回状态码
    sys.exit(status_code)


if __name__ == "__main__":
    main()

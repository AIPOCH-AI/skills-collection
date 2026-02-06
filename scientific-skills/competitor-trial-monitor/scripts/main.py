#!/usr/bin/env python3
"""
Competitor Trial Monitor - 竞品临床试验监控
监控竞品临床试验进度，预警市场风险。
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse

# 数据目录
DATA_DIR = Path.home() / ".openclaw" / "competitor-trial-monitor"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
HISTORY_DIR = DATA_DIR / "history"
ALERTS_DIR = DATA_DIR / "alerts"
CONFIG_FILE = DATA_DIR / "config.json"

# ClinicalTrials.gov API
CT_API_BASE = "https://clinicaltrials.gov/api/v2/studies"


def init_data_dir():
    """初始化数据目录"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)
    ALERTS_DIR.mkdir(exist_ok=True)


def load_watchlist() -> List[Dict]:
    """加载监控列表"""
    if not WATCHLIST_FILE.exists():
        return []
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_watchlist(watchlist: List[Dict]):
    """保存监控列表"""
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(watchlist, f, indent=2, ensure_ascii=False)


def load_config() -> Dict:
    """加载配置"""
    if not CONFIG_FILE.exists():
        return {
            "alert_channels": ["console"],
            "scan_interval_hours": 24,
            "risk_threshold": "medium"
        }
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_trial_data(nct_id: str) -> Optional[Dict]:
    """从 ClinicalTrials.gov 获取试验数据"""
    url = f"{CT_API_BASE}/{nct_id}"
    headers = {
        "Accept": "application/json"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  ⚠️  试验 {nct_id} 未找到")
        else:
            print(f"  ❌ HTTP错误 {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"  ❌ 获取数据失败: {e}")
        return None


def extract_key_info(trial_data: Dict) -> Dict:
    """提取关键试验信息"""
    protocol = trial_data.get("protocolSection", {})
    
    # 基本信息
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    
    return {
        "nct_id": identification.get("nctId", "N/A"),
        "title": identification.get("briefTitle", "N/A"),
        "status": status.get("overallStatus", "Unknown"),
        "phase": design.get("phases", ["Unknown"])[0] if design.get("phases") else "Unknown",
        "enrollment": design.get("enrollmentInfo", {}).get("count", 0),
        "start_date": status.get("startDateStruct", {}).get("date", "N/A"),
        "completion_date": status.get("completionDateStruct", {}).get("date", "N/A"),
        "has_results": trial_data.get("resultsSection", {}) is not None,
        "last_update": status.get("lastUpdatePostDateStruct", {}).get("date", "N/A")
    }


def assess_risk(old_info: Optional[Dict], new_info: Dict) -> Optional[Dict]:
    """评估风险变化"""
    if old_info is None:
        return None
    
    alerts = []
    risk_level = None
    
    # 检查状态变化
    old_status = old_info.get("status", "")
    new_status = new_info.get("status", "")
    
    status_risk_map = {
        "COMPLETED": ("high", "试验已完成，结果可能即将公布"),
        "AVAILABLE": ("critical", "结果已发布"),
        "APPROVED": ("critical", "已获批上市"),
        "REGULATORY_SUBMISSION": ("high", "已提交监管申请")
    }
    
    if old_status != new_status and new_status in status_risk_map:
        risk_level, message = status_risk_map[new_status]
        alerts.append(f"状态变更: {old_status} → {new_status}")
        alerts.append(message)
    
    # 检查是否有结果
    if not old_info.get("has_results") and new_info.get("has_results"):
        risk_level = "high"
        alerts.append("试验结果已发布")
    
    if alerts:
        return {
            "risk_level": risk_level or "medium",
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    return None


def cmd_add(args):
    """添加监控目标"""
    watchlist = load_watchlist()
    
    # 检查是否已存在
    for item in watchlist:
        if item.get("nct_id") == args.nct:
            print(f"⚠️  NCT {args.nct} 已在监控列表中")
            return
    
    # 验证试验存在
    print(f"🔍 验证试验 {args.nct}...")
    trial_data = fetch_trial_data(args.nct)
    if not trial_data:
        print(f"❌ 无法添加: 试验 {args.nct} 未找到或API错误")
        return
    
    info = extract_key_info(trial_data)
    
    watchlist.append({
        "nct_id": args.nct,
        "company": args.company or "Unknown",
        "drug": args.drug or "Unknown",
        "indication": args.indication or "Unknown",
        "added_at": datetime.now().isoformat(),
        "last_check": None,
        "last_data": info
    })
    
    save_watchlist(watchlist)
    print(f"✅ 已添加: {info['title'][:60]}...")
    print(f"   公司: {args.company or 'Unknown'}")
    print(f"   药物: {args.drug or 'Unknown'}")
    print(f"   状态: {info['status']}")


def cmd_list(args):
    """列出监控目标"""
    watchlist = load_watchlist()
    
    if not watchlist:
        print("📭 监控列表为空")
        return
    
    print(f"\n📋 共监控 {len(watchlist)} 个临床试验:\n")
    print(f"{'NCT ID':<15} {'公司':<15} {'药物':<20} {'状态':<15} {'最后检查':<20}")
    print("-" * 90)
    
    for item in watchlist:
        nct = item.get("nct_id", "N/A")
        company = item.get("company", "Unknown")[:14]
        drug = item.get("drug", "Unknown")[:19]
        status = (item.get("last_data", {}) or {}).get("status", "Unknown")[:14]
        last_check = item.get("last_check", "Never")[:19] if item.get("last_check") else "Never"
        
        print(f"{nct:<15} {company:<15} {drug:<20} {status:<15} {last_check:<20}")


def cmd_remove(args):
    """删除监控目标"""
    watchlist = load_watchlist()
    
    original_len = len(watchlist)
    watchlist = [item for item in watchlist if item.get("nct_id") != args.nct]
    
    if len(watchlist) == original_len:
        print(f"⚠️  NCT {args.nct} 不在监控列表中")
        return
    
    save_watchlist(watchlist)
    print(f"✅ 已删除 NCT {args.nct}")


def cmd_scan(args):
    """扫描更新"""
    watchlist = load_watchlist()
    
    if not watchlist:
        print("📭 监控列表为空")
        return
    
    print(f"🔍 开始扫描 {len(watchlist)} 个试验...\n")
    
    alerts = []
    updated = 0
    
    for item in watchlist:
        nct_id = item.get("nct_id")
        print(f"检查 {nct_id} ({item.get('company', 'Unknown')})...")
        
        trial_data = fetch_trial_data(nct_id)
        if not trial_data:
            continue
        
        new_info = extract_key_info(trial_data)
        old_info = item.get("last_data")
        
        # 检查风险
        risk = assess_risk(old_info, new_info)
        if risk:
            alert = {
                "nct_id": nct_id,
                "company": item.get("company"),
                "drug": item.get("drug"),
                **risk
            }
            alerts.append(alert)
            print(f"  🚨 风险预警 [{risk['risk_level'].upper()}]")
            for msg in risk['alerts']:
                print(f"     - {msg}")
        
        # 更新数据
        item["last_data"] = new_info
        item["last_check"] = datetime.now().isoformat()
        updated += 1
        
        if not risk:
            print(f"  ✅ 无变化")
    
    save_watchlist(watchlist)
    
    # 保存预警
    if alerts:
        alert_file = ALERTS_DIR / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
        print(f"\n🚨 发现 {len(alerts)} 个风险预警")
        print(f"   预警已保存: {alert_file}")
    
    print(f"\n✅ 扫描完成，已更新 {updated} 个试验")


def cmd_report(args):
    """生成风险报告"""
    watchlist = load_watchlist()
    days = args.days or 30
    
    if not watchlist:
        print("📭 监控列表为空")
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    
    # 收集所有预警
    all_alerts = []
    for alert_file in ALERTS_DIR.glob("alerts_*.json"):
        try:
            with open(alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
                for alert in alerts:
                    alert_time = datetime.fromisoformat(alert.get("timestamp", ""))
                    if alert_time >= cutoff:
                        all_alerts.append(alert)
        except:
            pass
    
    print(f"\n📊 竞品临床试验风险报告 (近{days}天)\n")
    print("=" * 60)
    
    if not all_alerts:
        print("✅ 未发现风险预警")
        return
    
    # 按风险等级分组
    critical = [a for a in all_alerts if a.get("risk_level") == "critical"]
    high = [a for a in all_alerts if a.get("risk_level") == "high"]
    medium = [a for a in all_alerts if a.get("risk_level") == "medium"]
    
    print(f"🔴 Critical: {len(critical)}")
    for alert in critical:
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
        for msg in alert.get("alerts", []):
            print(f"      • {msg}")
    
    print(f"\n🟠 High: {len(high)}")
    for alert in high:
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
        for msg in alert.get("alerts", []):
            print(f"      • {msg}")
    
    print(f"\n🟡 Medium: {len(medium)}")
    for alert in medium[:5]:  # 只显示前5个
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
    if len(medium) > 5:
        print(f"   ... 还有 {len(medium) - 5} 个")
    
    print("\n" + "=" * 60)
    print(f"总计: {len(all_alerts)} 个预警事件")


def main():
    parser = argparse.ArgumentParser(
        description="Competitor Trial Monitor - 竞品临床试验监控",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加监控目标")
    add_parser.add_argument("--nct", required=True, help="ClinicalTrials.gov NCT ID")
    add_parser.add_argument("--company", help="竞品公司名称")
    add_parser.add_argument("--drug", help="药物名称")
    add_parser.add_argument("--indication", help="适应症")
    add_parser.set_defaults(func=cmd_add)
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出监控目标")
    list_parser.set_defaults(func=cmd_list)
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除监控目标")
    remove_parser.add_argument("--nct", required=True, help="要删除的NCT ID")
    remove_parser.set_defaults(func=cmd_remove)
    
    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="扫描更新")
    scan_parser.set_defaults(func=cmd_scan)
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成风险报告")
    report_parser.add_argument("--days", type=int, default=30, help="报告时间范围(天)")
    report_parser.set_defaults(func=cmd_report)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    init_data_dir()
    args.func(args)


if __name__ == "__main__":
    main()

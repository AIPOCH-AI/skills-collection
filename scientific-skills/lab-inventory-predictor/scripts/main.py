#!/usr/bin/env python3
"""
Lab Inventory Predictor
基于实验频率预测关键试剂的耗尽时间，并自动生成采购提醒。

ID: 107
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class UsageRecord:
    """使用记录"""
    date: str
    amount: float
    experiment: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UsageRecord':
        return cls(**data)


@dataclass
class Reagent:
    """试剂信息"""
    name: str
    current_stock: float
    unit: str = "ml"
    safety_stock: float = 0.0
    safety_days: int = 7
    lead_time_days: int = 3
    usage_history: List[UsageRecord] = field(default_factory=list)
    daily_consumption_rate: float = 0.0
    predicted_depletion_date: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "current_stock": self.current_stock,
            "unit": self.unit,
            "safety_stock": self.safety_stock,
            "safety_days": self.safety_days,
            "lead_time_days": self.lead_time_days,
            "usage_history": [u.to_dict() for u in self.usage_history],
            "daily_consumption_rate": self.daily_consumption_rate,
            "predicted_depletion_date": self.predicted_depletion_date,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Reagent':
        data = data.copy()
        data['usage_history'] = [UsageRecord.from_dict(u) for u in data.get('usage_history', [])]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class InventoryPredictor:
    """库存预测器主类"""
    
    DEFAULT_DATA_PATH = os.path.expanduser("~/.openclaw/workspace/data/lab-inventory.json")
    DEFAULT_LOOKBACK_DAYS = 30
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载数据文件"""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "settings": {
                "default_safety_days": 7,
                "default_lead_time_days": 3,
                "prediction_lookback_days": 30
            },
            "reagents": []
        }
    
    def _save_data(self):
        """保存数据文件"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _get_reagent(self, name: str) -> Optional[Reagent]:
        """获取试剂信息"""
        for r in self.data['reagents']:
            if r['name'] == name:
                return Reagent.from_dict(r)
        return None
    
    def _save_reagent(self, reagent: Reagent):
        """保存试剂信息"""
        for i, r in enumerate(self.data['reagents']):
            if r['name'] == reagent.name:
                self.data['reagents'][i] = reagent.to_dict()
                break
        else:
            self.data['reagents'].append(reagent.to_dict())
        self._save_data()
    
    def add_reagent(self, name: str, current_stock: float, unit: str = "ml",
                    safety_stock: float = 0.0, safety_days: int = 7, 
                    lead_time_days: int = 3) -> Dict:
        """添加新试剂"""
        if self._get_reagent(name):
            return {"success": False, "error": f"试剂 '{name}' 已存在，请使用 update-reagent"}
        
        reagent = Reagent(
            name=name,
            current_stock=current_stock,
            unit=unit,
            safety_stock=safety_stock,
            safety_days=safety_days,
            lead_time_days=lead_time_days
        )
        self._save_reagent(reagent)
        return {"success": True, "message": f"试剂 '{name}' 添加成功"}
    
    def update_reagent(self, name: str, **kwargs) -> Dict:
        """更新试剂信息"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"试剂 '{name}' 不存在"}
        
        for key, value in kwargs.items():
            if hasattr(reagent, key) and value is not None:
                setattr(reagent, key, value)
        
        reagent.last_updated = datetime.now().isoformat()
        self._save_reagent(reagent)
        return {"success": True, "message": f"试剂 '{name}' 更新成功"}
    
    def record_usage(self, name: str, amount: float, experiment: str = "") -> Dict:
        """记录试剂使用"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"试剂 '{name}' 不存在"}
        
        if amount > reagent.current_stock:
            return {"success": False, "error": f"使用量 ({amount}) 超过当前库存 ({reagent.current_stock})"}
        
        # 添加使用记录
        record = UsageRecord(
            date=datetime.now().strftime("%Y-%m-%d"),
            amount=amount,
            experiment=experiment
        )
        reagent.usage_history.append(record)
        reagent.current_stock -= amount
        reagent.last_updated = datetime.now().isoformat()
        
        # 重新计算消耗速率和预测
        self._calculate_consumption_rate(reagent)
        self._predict_depletion(reagent)
        
        self._save_reagent(reagent)
        return {
            "success": True, 
            "message": f"已记录使用 {amount} {reagent.unit}",
            "current_stock": reagent.current_stock,
            "predicted_depletion": reagent.predicted_depletion_date
        }
    
    def restock(self, name: str, amount: float) -> Dict:
        """补充库存"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"试剂 '{name}' 不存在"}
        
        reagent.current_stock += amount
        reagent.last_updated = datetime.now().isoformat()
        
        # 重新预测
        self._predict_depletion(reagent)
        
        self._save_reagent(reagent)
        return {
            "success": True,
            "message": f"已补充 {amount} {reagent.unit}",
            "current_stock": reagent.current_stock,
            "predicted_depletion": reagent.predicted_depletion_date
        }
    
    def _calculate_consumption_rate(self, reagent: Reagent):
        """计算每日消耗速率"""
        lookback_days = self.data['settings'].get('prediction_lookback_days', 30)
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        recent_usage = [
            u for u in reagent.usage_history 
            if datetime.fromisoformat(u.date) >= cutoff_date
        ]
        
        if len(recent_usage) < 2:
            # 数据不足，使用所有历史记录
            recent_usage = reagent.usage_history
        
        if len(recent_usage) < 2:
            reagent.daily_consumption_rate = 0.0
            return
        
        total_usage = sum(u.amount for u in recent_usage)
        date_range = (datetime.now() - datetime.fromisoformat(recent_usage[0].date)).days
        date_range = max(date_range, 1)  # 至少1天
        
        reagent.daily_consumption_rate = total_usage / date_range
    
    def _predict_depletion(self, reagent: Reagent):
        """预测耗尽日期"""
        if reagent.daily_consumption_rate <= 0:
            reagent.predicted_depletion_date = None
            return
        
        days_until_depletion = reagent.current_stock / reagent.daily_consumption_rate
        depletion_date = datetime.now() + timedelta(days=days_until_depletion)
        reagent.predicted_depletion_date = depletion_date.strftime("%Y-%m-%d")
    
    def predict_depletion(self, name: str) -> Dict:
        """获取指定试剂的耗尽预测"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"试剂 '{name}' 不存在"}
        
        self._calculate_consumption_rate(reagent)
        self._predict_depletion(reagent)
        
        if reagent.predicted_depletion_date:
            days_left = (datetime.fromisoformat(reagent.predicted_depletion_date) - datetime.now()).days
            return {
                "success": True,
                "reagent": name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "daily_consumption_rate": f"{reagent.daily_consumption_rate:.2f} {reagent.unit}/天",
                "predicted_depletion_date": reagent.predicted_depletion_date,
                "days_remaining": days_left
            }
        else:
            return {
                "success": True,
                "reagent": name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "message": "数据不足，无法预测耗尽时间"
            }
    
    def get_alerts(self) -> Dict:
        """获取采购提醒"""
        alerts = []
        now = datetime.now()
        
        for r_data in self.data['reagents']:
            reagent = Reagent.from_dict(r_data)
            self._calculate_consumption_rate(reagent)
            self._predict_depletion(reagent)
            
            alert_level = None
            alert_reason = []
            
            # 检查安全库存
            if reagent.current_stock <= reagent.safety_stock:
                alert_level = "CRITICAL"
                alert_reason.append(f"库存低于安全库存 ({reagent.safety_stock} {reagent.unit})")
            
            # 检查耗尽时间
            if reagent.predicted_depletion_date:
                depletion_date = datetime.fromisoformat(reagent.predicted_depletion_date)
                days_until = (depletion_date - now).days
                order_deadline = days_until - reagent.lead_time_days
                
                if days_until <= 0:
                    alert_level = "CRITICAL"
                    alert_reason.append("库存已耗尽")
                elif days_until <= reagent.safety_days + reagent.lead_time_days:
                    alert_level = alert_level or "WARNING"
                    alert_reason.append(f"预计 {days_until} 天后耗尽")
                
                if order_deadline <= 0:
                    alert_reason.append(f"⚠️ 已超过采购截止日期 ({reagent.lead_time_days} 天提前期)")
                elif order_deadline <= 3:
                    alert_reason.append(f"建议 {order_deadline} 天内完成采购")
            
            if alert_level:
                alerts.append({
                    "reagent": reagent.name,
                    "level": alert_level,
                    "current_stock": f"{reagent.current_stock} {reagent.unit}",
                    "reason": "; ".join(alert_reason),
                    "predicted_depletion": reagent.predicted_depletion_date
                })
        
        # 按紧急程度排序
        alerts.sort(key=lambda x: (0 if x['level'] == 'CRITICAL' else 1))
        
        return {
            "success": True,
            "alert_count": len(alerts),
            "alerts": alerts
        }
    
    def get_status(self) -> Dict:
        """获取所有试剂状态"""
        status_list = []
        
        for r_data in self.data['reagents']:
            reagent = Reagent.from_dict(r_data)
            self._calculate_consumption_rate(reagent)
            self._predict_depletion(reagent)
            
            status = "normal"
            if reagent.predicted_depletion_date:
                days_left = (datetime.fromisoformat(reagent.predicted_depletion_date) - datetime.now()).days
                if days_left <= reagent.lead_time_days + reagent.safety_days:
                    status = "warning"
                if reagent.current_stock <= reagent.safety_stock:
                    status = "critical"
            
            status_list.append({
                "name": reagent.name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "daily_consumption": f"{reagent.daily_consumption_rate:.2f} {reagent.unit}/天" if reagent.daily_consumption_rate > 0 else "N/A",
                "predicted_depletion": reagent.predicted_depletion_date or "N/A",
                "status": status
            })
        
        return {
            "success": True,
            "total_reagents": len(status_list),
            "reagents": status_list
        }
    
    def generate_report(self) -> Dict:
        """生成完整报告"""
        status = self.get_status()
        alerts = self.get_alerts()
        
        critical_count = sum(1 for a in alerts['alerts'] if a['level'] == 'CRITICAL')
        warning_count = sum(1 for a in alerts['alerts'] if a['level'] == 'WARNING')
        
        report = {
            "success": True,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_reagents": status['total_reagents'],
                "critical_alerts": critical_count,
                "warning_alerts": warning_count
            },
            "alerts": alerts['alerts'],
            "inventory_status": status['reagents']
        }
        
        return report
    
    def remove_reagent(self, name: str) -> Dict:
        """删除试剂"""
        for i, r in enumerate(self.data['reagents']):
            if r['name'] == name:
                del self.data['reagents'][i]
                self._save_data()
                return {"success": True, "message": f"试剂 '{name}' 已删除"}
        return {"success": False, "error": f"试剂 '{name}' 不存在"}


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Lab Inventory Predictor - 实验室库存预测工具')
    parser.add_argument('--data-path', help='数据文件路径')
    parser.add_argument('--action', required=True,
                        choices=['add-reagent', 'update-reagent', 'remove-reagent',
                                'record-usage', 'restock', 'status', 'alerts', 
                                'report', 'predict', 'list'],
                        help='执行的操作')
    
    # 试剂相关参数
    parser.add_argument('--name', help='试剂名称')
    parser.add_argument('--current-stock', type=float, help='当前库存量')
    parser.add_argument('--unit', default='ml', help='单位 (默认: ml)')
    parser.add_argument('--safety-stock', type=float, help='安全库存量')
    parser.add_argument('--safety-days', type=int, help='安全库存天数')
    parser.add_argument('--lead-time-days', type=int, help='采购提前期(天)')
    
    # 使用记录参数
    parser.add_argument('--amount', type=float, help='使用量或补充量')
    parser.add_argument('--experiment', default='', help='实验名称/编号')
    
    # 输出格式
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')
    
    args = parser.parse_args()
    
    # 初始化预测器
    predictor = InventoryPredictor(args.data_path)
    
    # 执行操作
    result = None
    
    if args.action == 'add-reagent':
        if not args.name or args.current_stock is None:
            result = {"success": False, "error": "缺少必要参数: --name 和 --current-stock"}
        else:
            result = predictor.add_reagent(
                name=args.name,
                current_stock=args.current_stock,
                unit=args.unit,
                safety_stock=args.safety_stock or 0.0,
                safety_days=args.safety_days or 7,
                lead_time_days=args.lead_time_days or 3
            )
    
    elif args.action == 'update-reagent':
        if not args.name:
            result = {"success": False, "error": "缺少必要参数: --name"}
        else:
            result = predictor.update_reagent(
                name=args.name,
                current_stock=args.current_stock,
                unit=args.unit,
                safety_stock=args.safety_stock,
                safety_days=args.safety_days,
                lead_time_days=args.lead_time_days
            )
    
    elif args.action == 'remove-reagent':
        if not args.name:
            result = {"success": False, "error": "缺少必要参数: --name"}
        else:
            result = predictor.remove_reagent(args.name)
    
    elif args.action == 'record-usage':
        if not args.name or args.amount is None:
            result = {"success": False, "error": "缺少必要参数: --name 和 --amount"}
        else:
            result = predictor.record_usage(args.name, args.amount, args.experiment)
    
    elif args.action == 'restock':
        if not args.name or args.amount is None:
            result = {"success": False, "error": "缺少必要参数: --name 和 --amount"}
        else:
            result = predictor.restock(args.name, args.amount)
    
    elif args.action == 'status' or args.action == 'list':
        result = predictor.get_status()
    
    elif args.action == 'alerts':
        result = predictor.get_alerts()
    
    elif args.action == 'report':
        result = predictor.generate_report()
    
    elif args.action == 'predict':
        if not args.name:
            result = {"success": False, "error": "缺少必要参数: --name"}
        else:
            result = predictor.predict_depletion(args.name)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_formatted(result)
    
    # 根据结果设置退出码
    sys.exit(0 if result.get('success', True) else 1)


def _print_formatted(result: Dict):
    """格式化输出结果"""
    if not result.get('success', True):
        print(f"❌ 错误: {result.get('error', '未知错误')}")
        return
    
    # 添加试剂
    if 'message' in result and '添加' in result['message']:
        print(f"✅ {result['message']}")
        return
    
    # 记录使用
    if 'current_stock' in result and 'message' in result and '记录' in result['message']:
        print(f"✅ {result['message']}")
        print(f"   当前库存: {result['current_stock']}")
        if 'predicted_depletion' in result:
            print(f"   预计耗尽: {result['predicted_depletion']}")
        return
    
    # 补充库存
    if 'message' in result and '补充' in result['message']:
        print(f"✅ {result['message']}")
        print(f"   当前库存: {result['current_stock']}")
        return
    
    # 预测结果
    if 'reagent' in result and 'daily_consumption_rate' in result:
        print(f"\n📊 试剂: {result['reagent']}")
        print(f"   当前库存: {result['current_stock']}")
        print(f"   日均消耗: {result['daily_consumption_rate']}")
        if 'predicted_depletion_date' in result:
            print(f"   预计耗尽: {result['predicted_depletion_date']} (还有 {result['days_remaining']} 天)")
        else:
            print(f"   {result.get('message', '')}")
        return
    
    # 警报列表
    if 'alerts' in result and 'alert_count' in result:
        print(f"\n🚨 采购提醒 (共 {result['alert_count']} 项)\n")
        if result['alert_count'] == 0:
            print("   ✅ 所有试剂库存充足")
            return
        
        for alert in result['alerts']:
            icon = "🔴" if alert['level'] == 'CRITICAL' else "🟡"
            print(f"{icon} [{alert['level']}] {alert['reagent']}")
            print(f"   当前库存: {alert['current_stock']}")
            print(f"   原因: {alert['reason']}")
            if alert.get('predicted_depletion'):
                print(f"   预计耗尽: {alert['predicted_depletion']}")
            print()
        return
    
    # 状态列表
    if 'reagents' in result:
        print(f"\n📋 库存状态 (共 {result['total_reagents']} 种试剂)\n")
        print(f"{'试剂名称':<20} {'当前库存':<15} {'日均消耗':<15} {'预计耗尽':<12} {'状态':<10}")
        print("-" * 80)
        
        for r in result['reagents']:
            status_icon = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}.get(r['status'], "⚪")
            print(f"{r['name']:<20} {r['current_stock']:<15} {r['daily_consumption']:<15} {r['predicted_depletion']:<12} {status_icon} {r['status']}")
        return
    
    # 报告
    if 'summary' in result:
        print(f"\n📑 库存预测报告")
        print(f"   生成时间: {result['generated_at']}")
        print(f"\n📊 汇总")
        print(f"   试剂总数: {result['summary']['total_reagents']}")
        print(f"   紧急警报: {result['summary']['critical_alerts']}")
        print(f"   警告警报: {result['summary']['warning_alerts']}")
        
        if result['alerts']:
            print(f"\n🚨 需要关注的试剂:")
            for alert in result['alerts']:
                icon = "🔴" if alert['level'] == 'CRITICAL' else "🟡"
                print(f"   {icon} {alert['reagent']}: {alert['reason']}")
        return
    
    # 默认输出
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

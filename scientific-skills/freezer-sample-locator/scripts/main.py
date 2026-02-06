#!/usr/bin/env python3
"""
Freezer Sample Locator - 记录并检索样本在-80℃冰箱中的具体位置
Skill ID: 179
"""

import json
import os
import uuid
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class FreezerSampleLocator:
    """管理-80℃冰箱样本位置的类"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化定位器
        
        Args:
            data_dir: 数据存储目录，默认为脚本所在目录的 data 文件夹
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "samples.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            self._save_data({"samples": []})
    
    def _load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"samples": []}
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_sample(
        self,
        name: str,
        project: str,
        freezer: str,
        level: int,
        rack: str,
        box: str,
        position: str,
        quantity: int = 1,
        notes: str = "",
        date_stored: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加新样本位置记录
        
        Args:
            name: 样本名称
            project: 项目名称
            freezer: 冰箱编号 (如 F01)
            level: 层号 (1-10)
            rack: 架号 (如 A, B, C)
            box: 盒号 (如 01, 02)
            position: 格子位置 (如 A1, B2)
            quantity: 数量，默认为1
            notes: 备注
            date_stored: 存储日期 (YYYY-MM-DD)，默认为今天
        
        Returns:
            新创建的样本记录
        """
        data = self._load_data()
        
        # 检查位置是否已被占用
        for sample in data["samples"]:
            if (sample["freezer"] == freezer and
                sample["level"] == level and
                sample["rack"] == rack and
                sample["box"] == box and
                sample["position"] == position):
                raise ValueError(
                    f"位置 {freezer}-L{level}-R{rack}-B{box}-{position} 已被样本 "
                    f"'{sample['name']}' 占用"
                )
        
        now = datetime.utcnow().isoformat() + "Z"
        if date_stored is None:
            date_stored = datetime.now().strftime("%Y-%m-%d")
        
        sample = {
            "id": str(uuid.uuid4()),
            "name": name,
            "project": project,
            "freezer": freezer,
            "level": level,
            "rack": rack,
            "box": box,
            "position": position,
            "quantity": quantity,
            "date_stored": date_stored,
            "notes": notes,
            "created_at": now,
            "updated_at": now
        }
        
        data["samples"].append(sample)
        self._save_data(data)
        
        return sample
    
    def search_samples(
        self,
        name: Optional[str] = None,
        project: Optional[str] = None,
        freezer: Optional[str] = None,
        sample_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索样本
        
        Args:
            name: 按名称搜索（模糊匹配）
            project: 按项目搜索（精确匹配）
            freezer: 按冰箱搜索（精确匹配）
            sample_id: 按ID搜索（精确匹配）
        
        Returns:
            匹配的样本列表
        """
        data = self._load_data()
        results = data["samples"]
        
        if sample_id:
            results = [s for s in results if s["id"] == sample_id]
        
        if name:
            name_lower = name.lower()
            results = [s for s in results if name_lower in s["name"].lower()]
        
        if project:
            results = [s for s in results if s["project"] == project]
        
        if freezer:
            results = [s for s in results if s["freezer"] == freezer]
        
        return results
    
    def get_sample_location(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """
        获取样本完整位置信息
        
        Args:
            sample_id: 样本ID
        
        Returns:
            样本位置信息，包含格式化后的位置字符串
        """
        results = self.search_samples(sample_id=sample_id)
        if not results:
            return None
        
        sample = results[0]
        sample["location_str"] = (
            f"{sample['freezer']} > L{sample['level']} > "
            f"R{sample['rack']} > B{sample['box']} > {sample['position']}"
        )
        return sample
    
    def update_sample(
        self,
        sample_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        更新样本信息
        
        Args:
            sample_id: 样本ID
            **kwargs: 要更新的字段
        
        Returns:
            更新后的样本记录
        """
        data = self._load_data()
        
        for i, sample in enumerate(data["samples"]):
            if sample["id"] == sample_id:
                # 更新允许的字段
                allowed_fields = [
                    "name", "project", "freezer", "level", "rack",
                    "box", "position", "quantity", "notes", "date_stored"
                ]
                
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        data["samples"][i][key] = value
                
                data["samples"][i]["updated_at"] = datetime.utcnow().isoformat() + "Z"
                self._save_data(data)
                return data["samples"][i]
        
        return None
    
    def delete_sample(self, sample_id: str) -> bool:
        """
        删除样本记录
        
        Args:
            sample_id: 样本ID
        
        Returns:
            是否成功删除
        """
        data = self._load_data()
        original_count = len(data["samples"])
        data["samples"] = [s for s in data["samples"] if s["id"] != sample_id]
        
        if len(data["samples"]) < original_count:
            self._save_data(data)
            return True
        return False
    
    def list_samples(self, freezer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有样本
        
        Args:
            freezer: 可选，只列出指定冰箱的样本
        
        Returns:
            样本列表
        """
        data = self._load_data()
        samples = data["samples"]
        
        if freezer:
            samples = [s for s in samples if s["freezer"] == freezer]
        
        # 按冰箱、层、架、盒、位置排序
        samples.sort(key=lambda x: (
            x["freezer"], x["level"], x["rack"], x["box"], x["position"]
        ))
        
        return samples
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据字典
        """
        data = self._load_data()
        samples = data["samples"]
        
        freezers = set(s["freezer"] for s in samples)
        projects = set(s["project"] for s in samples)
        
        return {
            "total_samples": len(samples),
            "total_freezers": len(freezers),
            "total_projects": len(projects),
            "freezers": sorted(list(freezers)),
            "projects": sorted(list(projects))
        }
    
    def export_csv(self, output_path: str, freezer: Optional[str] = None):
        """
        导出样本列表为 CSV
        
        Args:
            output_path: 输出文件路径
            freezer: 可选，只导出指定冰箱的样本
        """
        samples = self.list_samples(freezer=freezer)
        
        fieldnames = [
            "name", "project", "freezer", "level", "rack",
            "box", "position", "quantity", "date_stored", "notes"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for sample in samples:
                writer.writerow({k: sample.get(k, "") for k in fieldnames})


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Freezer Sample Locator - 管理-80℃冰箱样本位置"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # Add 命令
    add_parser = subparsers.add_parser("add", help="添加新样本")
    add_parser.add_argument("--name", required=True, help="样本名称")
    add_parser.add_argument("--project", required=True, help="项目名称")
    add_parser.add_argument("--freezer", required=True, help="冰箱编号 (如 F01)")
    add_parser.add_argument("--level", type=int, required=True, help="层号 (1-10)")
    add_parser.add_argument("--rack", required=True, help="架号 (如 A, B)")
    add_parser.add_argument("--box", required=True, help="盒号 (如 01, 02)")
    add_parser.add_argument("--position", required=True, help="格子位置 (如 A1, B2)")
    add_parser.add_argument("--quantity", type=int, default=1, help="数量")
    add_parser.add_argument("--notes", default="", help="备注")
    add_parser.add_argument("--date-stored", help="存储日期 (YYYY-MM-DD)")
    
    # Search 命令
    search_parser = subparsers.add_parser("search", help="搜索样本")
    search_parser.add_argument("--name", help="按名称搜索")
    search_parser.add_argument("--project", help="按项目搜索")
    search_parser.add_argument("--freezer", help="按冰箱搜索")
    search_parser.add_argument("--id", help="按ID搜索")
    
    # List 命令
    list_parser = subparsers.add_parser("list", help="列出所有样本")
    list_parser.add_argument("--freezer", help="只列出指定冰箱的样本")
    
    # Update 命令
    update_parser = subparsers.add_parser("update", help="更新样本信息")
    update_parser.add_argument("--id", required=True, help="样本ID")
    update_parser.add_argument("--name", help="新名称")
    update_parser.add_argument("--project", help="新项目")
    update_parser.add_argument("--freezer", help="新冰箱")
    update_parser.add_argument("--level", type=int, help="新层号")
    update_parser.add_argument("--rack", help="新架号")
    update_parser.add_argument("--box", help="新盒号")
    update_parser.add_argument("--position", help="新位置")
    update_parser.add_argument("--quantity", type=int, help="新数量")
    update_parser.add_argument("--notes", help="新备注")
    
    # Delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除样本")
    delete_parser.add_argument("--id", required=True, help="样本ID")
    
    # Export 命令
    export_parser = subparsers.add_parser("export", help="导出样本列表")
    export_parser.add_argument("--output", required=True, help="输出文件路径")
    export_parser.add_argument("--freezer", help="只导出指定冰箱")
    
    # Stats 命令
    subparsers.add_parser("stats", help="显示统计信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    locator = FreezerSampleLocator()
    
    if args.command == "add":
        try:
            sample = locator.add_sample(
                name=args.name,
                project=args.project,
                freezer=args.freezer,
                level=args.level,
                rack=args.rack,
                box=args.box,
                position=args.position,
                quantity=args.quantity,
                notes=args.notes,
                date_stored=args.date_stored
            )
            print(f"✅ 样本已添加:")
            print(f"   ID: {sample['id']}")
            print(f"   位置: {args.freezer} > L{args.level} > R{args.rack} > B{args.box} > {args.position}")
        except ValueError as e:
            print(f"❌ 错误: {e}")
    
    elif args.command == "search":
        results = locator.search_samples(
            name=args.name,
            project=args.project,
            freezer=args.freezer,
            sample_id=args.id
        )
        if results:
            print(f"找到 {len(results)} 个样本:")
            for s in results:
                location = f"{s['freezer']}-L{s['level']}-R{s['rack']}-B{s['box']}-{s['position']}"
                print(f"  • {s['name']} ({s['project']}) - {location}")
        else:
            print("未找到匹配的样本")
    
    elif args.command == "list":
        samples = locator.list_samples(freezer=args.freezer)
        if samples:
            print(f"共有 {len(samples)} 个样本:")
            print(f"{'名称':<20} {'项目':<15} {'位置':<25} {'日期':<12}")
            print("-" * 72)
            for s in samples:
                location = f"{s['freezer']}-L{s['level']}-R{s['rack']}-B{s['box']}-{s['position']}"
                print(f"{s['name']:<20} {s['project']:<15} {location:<25} {s['date_stored']:<12}")
        else:
            print("暂无样本记录")
    
    elif args.command == "update":
        kwargs = {}
        if args.name: kwargs["name"] = args.name
        if args.project: kwargs["project"] = args.project
        if args.freezer: kwargs["freezer"] = args.freezer
        if args.level: kwargs["level"] = args.level
        if args.rack: kwargs["rack"] = args.rack
        if args.box: kwargs["box"] = args.box
        if args.position: kwargs["position"] = args.position
        if args.quantity: kwargs["quantity"] = args.quantity
        if args.notes: kwargs["notes"] = args.notes
        
        sample = locator.update_sample(args.id, **kwargs)
        if sample:
            print(f"✅ 样本已更新: {sample['name']}")
        else:
            print(f"❌ 未找到ID为 {args.id} 的样本")
    
    elif args.command == "delete":
        if locator.delete_sample(args.id):
            print(f"✅ 样本已删除")
        else:
            print(f"❌ 未找到ID为 {args.id} 的样本")
    
    elif args.command == "export":
        locator.export_csv(args.output, freezer=args.freezer)
        print(f"✅ 样本列表已导出到: {args.output}")
    
    elif args.command == "stats":
        stats = locator.get_statistics()
        print("📊 统计信息:")
        print(f"  总样本数: {stats['total_samples']}")
        print(f"  冰箱数量: {stats['total_freezers']}")
        print(f"  项目数量: {stats['total_projects']}")
        if stats['freezers']:
            print(f"  冰箱: {', '.join(stats['freezers'])}")
        if stats['projects']:
            print(f"  项目: {', '.join(stats['projects'])}")


if __name__ == "__main__":
    main()

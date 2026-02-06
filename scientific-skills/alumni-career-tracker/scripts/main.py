#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alumni Career Tracker (ID: 186)
分析实验室过往毕业生的去向(业界vs学界)，辅助新生做职业规划。
"""

import json
import os
import sys
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Try to import optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class AlumniRecord:
    """校友记录数据类"""
    name: str
    graduation_year: int
    degree: str  # PhD, Master, Bachelor
    current_status: str  # industry, academia, startup, other
    organization: str
    position: str
    location: str = ""
    field: str = ""
    salary_range: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlumniRecord':
        # Filter only valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)


@dataclass
class AnalysisReport:
    """分析报告数据类"""
    summary: Dict[str, Any]
    by_degree: Dict[str, Dict[str, int]]
    by_year: Dict[int, Dict[str, int]]
    top_companies: List[Dict[str, Any]]
    top_institutions: List[Dict[str, Any]]
    field_distribution: Dict[str, int]
    location_distribution: Dict[str, int]
    recommendations: List[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)


class AlumniTracker:
    """校友职业追踪器主类"""

    VALID_DEGREES = {"PhD", "Master", "Bachelor", "Ph.D", "MSc", "BS", "MS"}
    VALID_STATUSES = {"industry", "academia", "startup", "other"}

    def __init__(self, data_path: Optional[str] = None):
        """
        初始化追踪器
        
        Args:
            data_path: 数据文件路径，默认使用项目目录下的 alumni_data.json
        """
        if data_path is None:
            skill_dir = Path(__file__).parent.parent
            data_path = skill_dir / "alumni_data.json"
        
        self.data_path = Path(data_path)
        self.alumni: List[AlumniRecord] = []
        self._load_data()
        self.console = Console() if RICH_AVAILABLE else None

    def _load_data(self):
        """从文件加载数据"""
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alumni = [AlumniRecord.from_dict(r) for r in data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load data: {e}")
                self.alumni = []
        else:
            self.alumni = []

    def _save_data(self):
        """保存数据到文件"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.alumni], f, ensure_ascii=False, indent=2)

    def add_alumni(self, record: Dict[str, Any]) -> AlumniRecord:
        """
        添加校友记录
        
        Args:
            record: 校友记录字典
            
        Returns:
            创建的 AlumniRecord 对象
        """
        # 标准化 degree
        degree = record.get('degree', '').strip()
        degree_map = {
            'Ph.D': 'PhD', 'phd': 'PhD', 'Phd': 'PhD',
            'MSc': 'Master', 'MS': 'Master', 'ms': 'Master',
            'BS': 'Bachelor', 'bs': 'Bachelor', 'bachelor': 'Bachelor'
        }
        degree = degree_map.get(degree, degree)
        
        # 标准化 status
        status = record.get('current_status', record.get('status', '')).lower().strip()
        if status not in self.VALID_STATUSES:
            # 智能推断
            if '学校' in status or '大学' in status or '教授' in status or 'research' in status:
                status = 'academia'
            elif '创业' in status or 'founder' in status or 'startup' in status:
                status = 'startup'
            elif status:
                status = 'industry'
            else:
                status = 'other'
        
        record['degree'] = degree
        record['current_status'] = status
        
        alumni = AlumniRecord.from_dict(record)
        self.alumni.append(alumni)
        self._save_data()
        return alumni

    def update_alumni(self, name: str, updates: Dict[str, Any]) -> Optional[AlumniRecord]:
        """更新校友记录"""
        for i, alumni in enumerate(self.alumni):
            if alumni.name == name:
                for key, value in updates.items():
                    if hasattr(alumni, key):
                        setattr(alumni, key, value)
                alumni.updated_at = datetime.now().isoformat()
                self.alumni[i] = alumni
                self._save_data()
                return alumni
        return None

    def delete_alumni(self, name: str) -> bool:
        """删除校友记录"""
        for i, alumni in enumerate(self.alumni):
            if alumni.name == name:
                del self.alumni[i]
                self._save_data()
                return True
        return False

    def get_alumni(self, **filters) -> List[AlumniRecord]:
        """
        根据条件筛选校友
        
        Args:
            **filters: 筛选条件，如 year=2023, status='industry'
        """
        result = self.alumni
        for key, value in filters.items():
            result = [a for a in result if getattr(a, key, None) == value]
        return result

    def analyze(
        self,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        degree: Optional[str] = None
    ) -> AnalysisReport:
        """
        生成分析报告
        
        Args:
            year_from: 起始年份
            year_to: 结束年份
            degree: 学位筛选
            
        Returns:
            AnalysisReport 对象
        """
        # 筛选数据
        filtered = self.alumni
        if year_from:
            filtered = [a for a in filtered if a.graduation_year >= year_from]
        if year_to:
            filtered = [a for a in filtered if a.graduation_year <= year_to]
        if degree:
            filtered = [a for a in filtered if a.degree.lower() == degree.lower()]

        total = len(filtered)
        if total == 0:
            return AnalysisReport(
                summary={"total_alumni": 0, "message": "No data available"},
                by_degree={}, by_year={}, top_companies=[], top_institutions=[],
                field_distribution={}, location_distribution={}, recommendations=[]
            )

        # 统计各方向人数
        status_counts = defaultdict(int)
        degree_status = defaultdict(lambda: defaultdict(int))
        year_status = defaultdict(lambda: defaultdict(int))
        company_counts = defaultdict(int)
        institution_counts = defaultdict(int)
        field_counts = defaultdict(int)
        location_counts = defaultdict(int)

        for a in filtered:
            status_counts[a.current_status] += 1
            degree_status[a.degree][a.current_status] += 1
            year_status[a.graduation_year][a.current_status] += 1
            
            if a.current_status == 'industry':
                company_counts[a.organization] += 1
            elif a.current_status == 'academia':
                institution_counts[a.organization] += 1
            
            if a.field:
                field_counts[a.field] += 1
            if a.location:
                location_counts[a.location] += 1

        # 汇总数据
        summary = {
            "total_alumni": total,
            "industry_count": status_counts.get('industry', 0),
            "academia_count": status_counts.get('academia', 0),
            "startup_count": status_counts.get('startup', 0),
            "other_count": status_counts.get('other', 0),
            "industry_ratio": round(status_counts.get('industry', 0) / total, 3),
            "academia_ratio": round(status_counts.get('academia', 0) / total, 3),
            "startup_ratio": round(status_counts.get('startup', 0) / total, 3),
            "other_ratio": round(status_counts.get('other', 0) / total, 3),
        }

        # Top 公司/机构
        top_companies = [
            {"name": name, "count": count}
            for name, count in sorted(company_counts.items(), key=lambda x: -x[1])[:10]
        ]
        top_institutions = [
            {"name": name, "count": count}
            for name, count in sorted(institution_counts.items(), key=lambda x: -x[1])[:10]
        ]

        # 生成建议
        recommendations = self._generate_recommendations(summary, degree_status)

        return AnalysisReport(
            summary=summary,
            by_degree=dict(degree_status),
            by_year={year: dict(counts) for year, counts in year_status.items()},
            top_companies=top_companies,
            top_institutions=top_institutions,
            field_distribution=dict(field_counts),
            location_distribution=dict(location_counts),
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        summary: Dict[str, Any],
        degree_status: Dict[str, Dict[str, int]]
    ) -> List[str]:
        """生成职业建议"""
        recs = []
        
        total = summary['total_alumni']
        industry_ratio = summary['industry_ratio']
        academia_ratio = summary['academia_ratio']
        
        if industry_ratio > 0.6:
            recs.append(f"🎯 本实验室 {int(industry_ratio*100)}% 的毕业生进入业界，适合以工业界为目标的同学")
        if academia_ratio > 0.3:
            recs.append(f"📚 本实验室 {int(academia_ratio*100)}% 的毕业生留在学术界，学术氛围浓厚")
        
        # 按学位分析
        for degree, counts in degree_status.items():
            total_degree = sum(counts.values())
            if total_degree > 0:
                ind_ratio = counts.get('industry', 0) / total_degree
                aca_ratio = counts.get('academia', 0) / total_degree
                if degree in ['PhD', 'Ph.D']:
                    if aca_ratio > 0.4:
                        recs.append(f"🎓 PhD毕业生 academia比例高达 {int(aca_ratio*100)}%，适合想走学术道路的同学")
                    if ind_ratio > 0.5:
                        recs.append(f"💼 PhD毕业生也有 {int(ind_ratio*100)}% 进入业界，工业界认可度较高")
        
        if summary.get('startup_count', 0) > 0:
            recs.append(f"🚀 有 {summary['startup_count']} 位校友选择创业，创业氛围存在")
        
        return recs

    def get_recommendations(
        self,
        degree: Optional[str] = None,
        interest: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        为新生提供个性化建议
        
        Args:
            degree: 目标学位
            interest: 兴趣领域
        """
        report = self.analyze(degree=degree)
        
        result = {
            "overall_stats": report.summary,
            "similar_alumni": [],
            "suggested_paths": []
        }
        
        # 找到相似背景的校友
        if degree:
            similar = [a for a in self.alumni if a.degree == degree]
            if interest:
                similar = [a for a in similar if interest.lower() in a.field.lower()]
            result["similar_alumni"] = [a.to_dict() for a in similar[:5]]
        
        result["suggested_paths"] = report.recommendations
        return result

    def export_to_csv(self, output_path: str):
        """导出数据到 CSV"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for CSV export")
        
        df = pd.DataFrame([a.to_dict() for a in self.alumni])
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

    def import_from_json(self, json_path: str):
        """从 JSON 文件批量导入"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for record in data:
                    self.add_alumni(record)
            else:
                self.add_alumni(data)

    def print_report(self, report: AnalysisReport):
        """美化打印报告"""
        if not RICH_AVAILABLE:
            print(report.to_json())
            return
        
        # Summary panel
        summary = report.summary
        summary_text = f"""
总校友数: {summary['total_alumni']}
业界: {summary.get('industry_count', 0)} ({int(summary.get('industry_ratio', 0)*100)}%)
学界: {summary.get('academia_count', 0)} ({int(summary.get('academia_ratio', 0)*100)}%)
创业: {summary.get('startup_count', 0)} ({int(summary.get('startup_ratio', 0)*100)}%)
其他: {summary.get('other_count', 0)} ({int(summary.get('other_ratio', 0)*100)}%)
"""
        self.console.print(Panel(summary_text, title="📊 校友去向统计", border_style="blue"))

        # Top companies
        if report.top_companies:
            table = Table(title="🏢 热门公司 (Top Industry)")
            table.add_column("公司", style="cyan")
            table.add_column("人数", style="magenta")
            for c in report.top_companies[:5]:
                table.add_row(c['name'], str(c['count']))
            self.console.print(table)

        # Top institutions
        if report.top_institutions:
            table = Table(title="🎓 热门学术机构 (Top Academia)")
            table.add_column("机构", style="cyan")
            table.add_column("人数", style="magenta")
            for i in report.top_institutions[:5]:
                table.add_row(i['name'], str(i['count']))
            self.console.print(table)

        # Recommendations
        if report.recommendations:
            self.console.print(Panel("\n".join(report.recommendations), title="💡 职业规划建议", border_style="green"))


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Alumni Career Tracker - 分析实验室毕业生去向",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s add --name "张三" --year 2023 --degree PhD --status industry --org "Google"
  %(prog)s analyze
  %(prog)s analyze --year-from 2020 --year-to 2024
  %(prog)s list
  %(prog)s export --format csv --output alumni.csv
        """
    )
    
    parser.add_argument('--data', '-d', help='数据文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # Add command
    add_parser = subparsers.add_parser('add', help='添加校友记录')
    add_parser.add_argument('--name', required=True, help='姓名')
    add_parser.add_argument('--year', type=int, required=True, help='毕业年份')
    add_parser.add_argument('--degree', required=True, help='学位 (PhD/Master/Bachelor)')
    add_parser.add_argument('--status', required=True, help='去向 (industry/academia/startup/other)')
    add_parser.add_argument('--org', '--organization', required=True, help='公司/机构')
    add_parser.add_argument('--position', default='', help='职位')
    add_parser.add_argument('--location', default='', help='地点')
    add_parser.add_argument('--field', default='', help='领域')

    # List command
    list_parser = subparsers.add_parser('list', help='列出所有校友')
    list_parser.add_argument('--year', type=int, help='按年份筛选')
    list_parser.add_argument('--status', help='按去向筛选')
    list_parser.add_argument('--degree', help='按学位筛选')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='生成分析报告')
    analyze_parser.add_argument('--year-from', type=int, help='起始年份')
    analyze_parser.add_argument('--year-to', type=int, help='结束年份')
    analyze_parser.add_argument('--degree', help='学位筛选')
    analyze_parser.add_argument('--output', '-o', help='输出文件 (JSON)')

    # Import command
    import_parser = subparsers.add_parser('import', help='批量导入')
    import_parser.add_argument('file', help='JSON 文件路径')

    # Export command
    export_parser = subparsers.add_parser('export', help='导出数据')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='格式')
    export_parser.add_argument('--output', '-o', required=True, help='输出文件')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='删除记录')
    delete_parser.add_argument('name', help='姓名')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='快速统计')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    tracker = AlumniTracker(data_path=args.data)

    if args.command == 'add':
        record = {
            'name': args.name,
            'graduation_year': args.year,
            'degree': args.degree,
            'current_status': args.status,
            'organization': args.org,
            'position': args.position,
            'location': args.location,
            'field': args.field
        }
        alumni = tracker.add_alumni(record)
        print(f"✅ 已添加: {alumni.name} @ {alumni.organization}")

    elif args.command == 'list':
        filters = {}
        if args.year:
            filters['graduation_year'] = args.year
        if args.status:
            filters['current_status'] = args.status
        if args.degree:
            filters['degree'] = args.degree
        
        alumni_list = tracker.get_alumni(**filters)
        
        if RICH_AVAILABLE:
            table = Table(title=f"校友列表 ({len(alumni_list)} 人)")
            table.add_column("姓名", style="cyan")
            table.add_column("年份", style="magenta")
            table.add_column("学位", style="green")
            table.add_column("去向", style="yellow")
            table.add_column("公司/机构", style="blue")
            table.add_column("职位", style="dim")
            
            for a in alumni_list:
                status_emoji = {'industry': '💼', 'academia': '🎓', 'startup': '🚀', 'other': '📌'}
                emoji = status_emoji.get(a.current_status, '❓')
                table.add_row(a.name, str(a.graduation_year), a.degree, 
                            f"{emoji} {a.current_status}", a.organization, a.position)
            Console().print(table)
        else:
            for a in alumni_list:
                print(f"{a.name} | {a.graduation_year} | {a.degree} | {a.current_status} | {a.organization}")

    elif args.command == 'analyze':
        report = tracker.analyze(
            year_from=args.year_from,
            year_to=args.year_to,
            degree=args.degree
        )
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report.to_json())
            print(f"✅ 报告已保存: {args.output}")
        else:
            tracker.print_report(report)

    elif args.command == 'import':
        tracker.import_from_json(args.file)
        print(f"✅ 导入完成，当前共有 {len(tracker.alumni)} 条记录")

    elif args.command == 'export':
        if args.format == 'csv':
            tracker.export_to_csv(args.output)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump([a.to_dict() for a in tracker.alumni], f, ensure_ascii=False, indent=2)
        print(f"✅ 导出完成: {args.output}")

    elif args.command == 'delete':
        if tracker.delete_alumni(args.name):
            print(f"✅ 已删除: {args.name}")
        else:
            print(f"❌ 未找到: {args.name}")

    elif args.command == 'stats':
        report = tracker.analyze()
        tracker.print_report(report)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
临床试验数据监控面板 (Dashboard) 生成器
生成包含招募进度、AE发生率等关键指标的HTML布局草图
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_mock_data(args):
    """生成模拟数据用于展示"""
    
    # 各中心入组数据
    sites_data = []
    remaining = args.current_enrollment
    target_per_site = args.target_enrollment // args.sites
    
    for i in range(1, args.sites + 1):
        if i == args.sites:
            site_enrollment = remaining
        else:
            site_enrollment = random.randint(0, min(remaining, target_per_site + 10))
            remaining -= site_enrollment
        
        sites_data.append({
            "site_id": f"Site {i:03d}",
            "site_name": f"中心医院 {i}",
            "enrollment": site_enrollment,
            "target": target_per_site,
            "progress": round(site_enrollment / target_per_site * 100, 1) if target_per_site > 0 else 0,
            "status": "进行中" if site_enrollment < target_per_site else "已完成"
        })
    
    # AE数据
    ae_by_severity = {
        "轻度": int(args.ae_count * 0.5),
        "中度": int(args.ae_count * 0.35),
        "重度": int(args.ae_count * 0.15)
    }
    
    ae_by_type = {
        "胃肠道反应": random.randint(1, max(2, args.ae_count // 3)),
        "头痛": random.randint(1, max(2, args.ae_count // 4)),
        "皮疹": random.randint(0, max(1, args.ae_count // 5)),
        "乏力": random.randint(1, max(2, args.ae_count // 4)),
        "其他": random.randint(0, max(1, args.ae_count // 3))
    }
    
    # 受试者人口学数据
    demographics = {
        "gender": {"男性": 45, "女性": 55},
        "age_groups": {"18-30": 15, "31-50": 35, "51-65": 30, ">65": 20}
    }
    
    # 研究里程碑
    milestones = [
        {"name": "研究启动", "date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"), "status": "已完成"},
        {"name": "首例入组", "date": (datetime.now() - timedelta(days=150)).strftime("%Y-%m-%d"), "status": "已完成"},
        {"name": "25%入组", "date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"), "status": "已完成"},
        {"name": "50%入组", "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), "status": "已完成"},
        {"name": "75%入组", "date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"), "status": "预计"},
        {"name": "末例出组", "date": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"), "status": "预计"},
        {"name": "数据库锁定", "date": (datetime.now() + timedelta(days=210)).strftime("%Y-%m-%d"), "status": "预计"}
    ]
    
    return {
        "sites": sites_data,
        "ae": {"total": args.ae_count, "by_severity": ae_by_severity, "by_type": ae_by_type},
        "demographics": demographics,
        "milestones": milestones
    }


def generate_html(args, data):
    """生成Dashboard HTML"""
    
    enrollment_progress = round(args.current_enrollment / args.target_enrollment * 100, 1)
    ae_rate = round(args.ae_count / args.current_enrollment * 100, 1) if args.current_enrollment > 0 else 0
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>临床试验Dashboard - {args.study_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            color: #666;
            font-size: 14px;
        }}
        
        .header .meta span {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .badge {{
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}
        
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }}
        
        .card h2 {{
            color: #333;
            font-size: 18px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card h2::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 20px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .stat-row:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        
        .stat-value {{
            font-weight: 600;
            color: #333;
        }}
        
        .progress-container {{
            margin: 20px 0;
        }}
        
        .progress-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .progress-bar {{
            height: 12px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 6px;
            transition: width 0.5s ease;
        }}
        
        .progress-fill.warning {{
            background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .progress-fill.danger {{
            background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        }}
        
        .progress-fill.success {{
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        }}
        
        .site-list {{
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .site-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background: #f9fafb;
            border-radius: 8px;
        }}
        
        .site-info {{
            flex: 1;
        }}
        
        .site-id {{
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }}
        
        .site-name {{
            color: #666;
            font-size: 12px;
        }}
        
        .site-progress {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .site-bar {{
            width: 80px;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .site-fill {{
            height: 100%;
            background: #667eea;
            border-radius: 3px;
        }}
        
        .chart-placeholder {{
            height: 200px;
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6b7280;
            font-size: 14px;
            position: relative;
            overflow: hidden;
        }}
        
        .pie-chart {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(
                #667eea 0deg 162deg,
                #764ba2 162deg 360deg
            );
            position: relative;
        }}
        
        .pie-chart::after {{
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
        }}
        
        .legend {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            justify-content: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #666;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        
        .bar-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 15px;
            height: 150px;
            padding: 20px;
        }}
        
        .bar {{
            width: 40px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px 4px 0 0;
            position: relative;
            transition: height 0.5s ease;
        }}
        
        .bar-label {{
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #666;
            white-space: nowrap;
        }}
        
        .bar-value {{
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #333;
            font-weight: 600;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: "";
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e5e7eb;
        }}
        
        .timeline-item {{
            position: relative;
            padding-bottom: 20px;
        }}
        
        .timeline-item::before {{
            content: "";
            position: absolute;
            left: -26px;
            top: 2px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            border: 2px solid white;
            box-shadow: 0 0 0 2px #10b981;
        }}
        
        .timeline-item.pending::before {{
            background: #f59e0b;
            box-shadow: 0 0 0 2px #f59e0b;
        }}
        
        .timeline-date {{
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }}
        
        .timeline-title {{
            font-weight: 600;
            color: #333;
        }}
        
        .timeline-status {{
            font-size: 12px;
            color: #10b981;
            margin-top: 2px;
        }}
        
        .timeline-item.pending .timeline-status {{
            color: #f59e0b;
        }}
        
        .metric-cards {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
        }}
        
        .metric-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header .meta {{
                gap: 15px;
            }}
            
            .metric-cards {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 30px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {args.study_name}</h1>
            <div class="meta">
                <span>🔬 <strong>研究编号:</strong> {args.study_id}</span>
                <span>🏥 <strong>中心数:</strong> {args.sites} 家</span>
                <span>📅 <strong>更新日期:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
                <span class="badge">进行中</span>
            </div>
        </div>
        
        <div class="grid">
            <!-- 招募进度概览 -->
            <div class="card">
                <h2>招募进度概览</h2>
                <div class="metric-cards">
                    <div class="metric-card">
                        <div class="metric-value">{args.current_enrollment}</div>
                        <div class="metric-label">当前入组</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{args.target_enrollment}</div>
                        <div class="metric-label">目标入组</div>
                    </div>
                </div>
                <div class="progress-container">
                    <div class="progress-header">
                        <span>总体进度</span>
                        <span>{enrollment_progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill {"success" if enrollment_progress >= 80 else "warning" if enrollment_progress >= 50 else ""}" style="width: {enrollment_progress}%"></div>
                    </div>
                </div>
                <div class="stat-row">
                    <span class="stat-label">预计完成时间</span>
                    <span class="stat-value">{(datetime.now() + timedelta(days=int((args.target_enrollment - args.current_enrollment) / (args.current_enrollment / 180)))).strftime("%Y-%m-%d") if args.current_enrollment > 0 else "N/A"}</span>
                </div>
            </div>
            
            <!-- AE监控 -->
            <div class="card">
                <h2>不良事件 (AE) 监控</h2>
                <div class="metric-cards">
                    <div class="metric-card">
                        <div class="metric-value">{args.ae_count}</div>
                        <div class="metric-label">AE总数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{ae_rate}%</div>
                        <div class="metric-label">AE发生率</div>
                    </div>
                </div>
                <div class="stat-row">
                    <span class="stat-label">轻度</span>
                    <span class="stat-value">{data['ae']['by_severity']['轻度']} 例</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">中度</span>
                    <span class="stat-value">{data['ae']['by_severity']['中度']} 例</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">重度</span>
                    <span class="stat-value">{data['ae']['by_severity']['重度']} 例</span>
                </div>
            </div>
            
            <!-- 受试者分布 - 性别 -->
            <div class="card">
                <h2>性别分布</h2>
                <div class="chart-placeholder">
                    <div class="pie-chart"></div>
                </div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #667eea;"></div>
                        <span>男性 45%</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #764ba2;"></div>
                        <span>女性 55%</span>
                    </div>
                </div>
            </div>
            
            <!-- AE类型分布 -->
            <div class="card">
                <h2>AE类型分布</h2>
                <div class="chart-placeholder" style="height: 180px;">
                    <div class="bar-chart">
                        {''.join([f'<div class="bar" style="height: {min(100, count * 20)}%"><span class="bar-value">{count}</span><span class="bar-label">{ae_type}</span></div>' for ae_type, count in data['ae']['by_type'].items()])}
                    </div>
                </div>
            </div>
            
            <!-- 各中心进度 -->
            <div class="card full-width">
                <h2>各中心招募进度</h2>
                <div class="site-list">
                    {''.join([f'''
                    <div class="site-item">
                        <div class="site-info">
                            <div class="site-id">{site['site_id']}</div>
                            <div class="site-name">{site['site_name']}</div>
                        </div>
                        <div class="site-progress">
                            <span style="font-size: 12px; color: #666;">{site['enrollment']}/{site['target']}</span>
                            <div class="site-bar">
                                <div class="site-fill" style="width: {min(100, site['progress'])}%;"></div>
                            </div>
                            <span style="font-size: 12px; font-weight: 600; color: {'#10b981' if site['status'] == '已完成' else '#667eea'};">{site['progress']}%</span>
                        </div>
                    </div>
                    ''' for site in data['sites']])}
                </div>
            </div>
            
            <!-- 研究时间线 -->
            <div class="card">
                <h2>研究里程碑</h2>
                <div class="timeline">
                    {''.join([f'''
                    <div class="timeline-item {"pending" if milestone['status'] == "预计" else ""}">
                        <div class="timeline-date">{milestone['date']}</div>
                        <div class="timeline-title">{milestone['name']}</div>
                        <div class="timeline-status">{milestone['status']}</div>
                    </div>
                    ''' for milestone in data['milestones']])}
                </div>
            </div>
            
            <!-- 数据质量指标 -->
            <div class="card">
                <h2>数据质量指标</h2>
                <div class="progress-container">
                    <div class="progress-header">
                        <span>CRF完成率</span>
                        <span>92.5%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill success" style="width: 92.5%"></div>
                    </div>
                </div>
                <div class="progress-container">
                    <div class="progress-header">
                        <span>数据查询解决率</span>
                        <span>87.3%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 87.3%"></div>
                    </div>
                </div>
                <div class="progress-container">
                    <div class="progress-header">
                        <span>SDV完成率</span>
                        <span>78.6%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill warning" style="width: 78.6%"></div>
                    </div>
                </div>
                <div class="stat-row" style="margin-top: 20px;">
                    <span class="stat-label">待解决查询</span>
                    <span class="stat-value" style="color: #f59e0b;">23 条</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">待SDV访视</span>
                    <span class="stat-value">156 例</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>临床试验数据监控面板 | 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html


def main():
    parser = argparse.ArgumentParser(
        description="生成临床试验数据监控面板(Dashboard)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/main.py
  python scripts/main.py --study-id "PHASE-III-2024" --target-enrollment 300
        """
    )
    
    parser.add_argument("--study-id", default="STUDY-001", help="研究编号")
    parser.add_argument("--study-name", default="临床试验 A", help="研究名称")
    parser.add_argument("--sites", type=int, default=10, help="中心数量")
    parser.add_argument("--target-enrollment", type=int, default=100, help="目标入组人数")
    parser.add_argument("--current-enrollment", type=int, default=45, help="当前入组人数")
    parser.add_argument("--ae-count", type=int, default=12, help="不良事件数量")
    parser.add_argument("--output", default="dashboard.html", help="输出HTML文件路径")
    
    args = parser.parse_args()
    
    # 生成模拟数据
    data = generate_mock_data(args)
    
    # 生成HTML
    html = generate_html(args, data)
    
    # 写入文件
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    
    print(f"✅ Dashboard已生成: {output_path.absolute()}")
    print(f"\n📊 研究信息:")
    print(f"   - 研究编号: {args.study_id}")
    print(f"   - 研究名称: {args.study_name}")
    print(f"   - 中心数量: {args.sites}")
    print(f"   - 入组进度: {args.current_enrollment}/{args.target_enrollment}")
    print(f"   - AE数量: {args.ae_count}")
    print(f"\n🌐 请在浏览器中打开查看: {output_path.absolute()}")


if __name__ == "__main__":
    main()

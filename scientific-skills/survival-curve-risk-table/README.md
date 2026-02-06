# Survival Curve Risk Table Generator

在Kaplan-Meier生存曲线下方自动对齐并添加"Number at risk"表格，符合临床肿瘤学期刊标准。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 创建示例数据

```bash
python scripts/main.py --create-sample-data sample_data.csv
```

### 2. 生成风险表

```bash
python scripts/main.py \
    --input sample_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --style NEJM \
    --output risk_table.png
```

### 3. 生成组合图（KM曲线 + 风险表）

```bash
python scripts/main.py \
    --input sample_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --combine \
    --output combined_figure.png
```

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--input` | 输入数据文件路径 | `data.csv` |
| `--time-col` | 时间列名 | `time` |
| `--event-col` | 事件列名（1=事件, 0=删失） | `event` |
| `--group-col` | 分组列名 | `treatment` |
| `--output` | 输出文件路径 | `risk_table.png` |
| `--style` | 期刊风格（NEJM/Lancet/JCO） | `NEJM` |
| `--time-points` | 自定义时间点 | `0,6,12,18,24,30` |
| `--combine` | 生成组合图 | - |
| `--show-censored` | 显示删失人数 | - |

## 输入数据格式

CSV格式示例：

```csv
time,event,treatment
12.5,1,Experimental
18.3,0,Experimental
24.0,1,Control
...
```

## Python API

```python
from scripts.main import RiskTableGenerator

# 初始化
generator = RiskTableGenerator(style="NEJM")

# 加载数据
generator.load_data_from_file(
    "data.csv",
    time_col="time",
    event_col="event",
    group_col="treatment"
)

# 生成风险表
generator.generate_risk_table("risk_table.png")

# 生成组合图
generator.generate_combined_plot(output_path="combined.png")
```

## 期刊风格

- **NEJM**: New England Journal of Medicine 风格
- **Lancet**: The Lancet 风格
- **JCO**: Journal of Clinical Oncology 风格

## 许可证

MIT License

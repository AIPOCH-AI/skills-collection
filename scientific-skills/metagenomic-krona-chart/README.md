# Metagenomic Krona Chart

生成交互式的旭日图，展示宏基因组样本中的物种层级丰度。

## 功能

- 支持 Kraken2、Bracken 等常用分类工具输出格式
- 自动检测输入格式
- 生成交互式 HTML 旭日图
- 可配置最小百分比阈值和最大显示深度
- 颜色编码不同分类层级

## 安装

```bash
cd skills/metagenomic-krona-chart
pip install plotly pandas
```

## 快速开始

```bash
# 基本用法
python scripts/main.py -i example/sample_kraken2.txt -o output.html

# 指定标题和阈值
python scripts/main.py -i report.txt -o krona.html \
    --title "Sample A Metagenomics" \
    --min-percent 0.1 \
    --max-depth 6
```

## 输入格式

### Kraken2 / Bracken 格式
```
100.00  1000000 0   U   0   unclassified
 99.00  990000  0   R   1   root
 95.00  950000  0   D   2   Bacteria
 50.00  500000  0   P   1234    Proteobacteria
...
```

### 自定义 TSV 格式
```
taxon_id	name	rank	parent_id	reads	percent
2	Bacteria	domain	1	950000	95.0
1234	Proteobacteria	phylum	2	500000	50.0
```

## 输出特性

- 交互式旭日图，支持缩放和点击
- 悬停显示详细信息（读数、百分比、分类等级）
- 右侧图例显示分类等级颜色
- 响应式设计
- 独立HTML文件，可离线查看

## 示例输出

运行后会生成 `krona_chart.html`，用浏览器打开即可查看交互式图表。

# Neoantigen Predictor References

## 核心算法论文

### NetMHCpan 4.1
- **标题**: NetMHCpan-4.1 and NetMHCIIpan-4.0: improved predictions of MHC antigen presentation by concurrent motif deconvolution and integration of MS MHC eluted ligand data
- **作者**: Reynisson et al.
- **期刊**: Nucleic Acids Research
- **年份**: 2020
- **链接**: https://doi.org/10.1093/nar/gkaa379

### 新抗原预测综述
- **标题**: Neoantigen prediction: perspectives on the present and future
- **作者**: Wells et al.
- **期刊**: Nature Cancer
- **年份**: 2022
- **摘要**: 系统评估新抗原预测的计算方法和实验验证策略

### 免疫肽组学
- **标题**: The immunopeptidomics landscape of cancer: implications for immunotherapy
- **作者**: Abelin et al.
- **期刊**: Immunity
- **年份**: 2019

## HLA结合基序参考

### MHC-I结合基序数据库
- **来源**: IEDB (Immune Epitope Database)
- **网址**: http://www.iedb.org/
- **内容**: 已验证的HLA-肽段结合数据

### HLA频率数据库
- **来源**: Allele Frequency Net Database
- **网址**: http://www.allelefrequencies.net/
- **用途**: 人群HLA等位基因频率数据

## 肿瘤免疫治疗临床指南

### 新抗原疫苗临床试验设计
- **文档**: NCI Neoantigen Guidance
- **内容**: 新抗原疫苗临床试验的设计原则和终点指标

### 免疫治疗生物标志物
- **标题**: Biomarkers for Immunotherapy in Cancer
- **组织**: FDA Guidance Document

## 相关数据库

| 数据库 | 用途 | 链接 |
|--------|------|------|
| **Ensembl** | 基因组注释 | https://www.ensembl.org/ |
| **UniProt** | 蛋白质序列 | https://www.uniprot.org/ |
| **ClinVar** | 临床变异 | https://www.ncbi.nlm.nih.gov/clinvar/ |
| **COSMIC** | 肿瘤突变 | https://cancer.sanger.ac.uk/ |
| **TCGA** | 肿瘤基因组 | https://portal.gdc.cancer.gov/ |
| **IMGT/HLA** | HLA序列 | https://www.ebi.ac.uk/ipd/imgt/hla/ |

## 氨基酸性质表

### 疏水性标度 (Kyte-Doolittle)

| 氨基酸 | 单字母 | 疏水性值 |
|--------|--------|----------|
| Isoleucine | I | 4.5 |
| Valine | V | 4.2 |
| Leucine | L | 3.8 |
| Phenylalanine | F | 2.8 |
| Cysteine | C | 2.5 |
| Methionine | M | 1.9 |
| Alanine | A | 1.8 |
| Glycine | G | -0.4 |
| Threonine | T | -0.7 |
| Serine | S | -0.8 |
| Tryptophan | W | -0.9 |
| Tyrosine | Y | -1.3 |
| Proline | P | -1.6 |
| Histidine | H | -3.2 |
| Glutamic Acid | E | -3.5 |
| Glutamine | Q | -3.5 |
| Aspartic Acid | D | -3.5 |
| Asparagine | N | -3.5 |
| Lysine | K | -3.9 |
| Arginine | R | -4.5 |

### 氨基酸分子量

| 氨基酸 | 单字母 | 分子量 (Da) |
|--------|--------|-------------|
| Alanine | A | 89.09 |
| Arginine | R | 174.20 |
| Asparagine | N | 132.12 |
| Aspartic Acid | D | 133.10 |
| Cysteine | C | 121.16 |
| Glutamic Acid | E | 147.13 |
| Glutamine | Q | 146.15 |
| Glycine | G | 75.07 |
| Histidine | H | 155.16 |
| Isoleucine | I | 131.17 |
| Leucine | L | 131.17 |
| Lysine | K | 146.19 |
| Methionine | M | 149.21 |
| Phenylalanine | F | 165.19 |
| Proline | P | 115.13 |
| Serine | S | 105.09 |
| Threonine | T | 119.12 |
| Tryptophan | W | 204.23 |
| Tyrosine | Y | 181.19 |
| Valine | V | 117.15 |

## 新抗原预测最佳实践

### 质量控制标准

1. **MHC结合亲和力**
   - Strong binder: Rank < 0.5% 或 IC50 < 50 nM
   - Weak binder: Rank 0.5-2% 或 IC50 50-500 nM
   - Non-binder: Rank > 2% 或 IC50 > 500 nM

2. **免疫原性评估**
   - 外源性评分 > 0.5
   - 锚定位置突变优先
   - 疏水性变化 |ΔH| > 0.3

3. **临床相关性**
   - VAF > 5% (变异等位基因频率)
   - 表达水平: FPKM > 1
   - 克隆性变异优先

### 实验验证流程

1. **体外验证**
   - 肽段合成 (变异肽和野生型对照)
   - MHC结合实验 (竞争结合实验)
   - T细胞激活实验 (ELISPOT)

2. **体内验证**
   - 人源化小鼠模型
   - TCR识别验证
   - 细胞毒性实验

3. **临床应用**
   - 个体化新抗原疫苗设计
   - TCR-T细胞治疗靶点选择
   - 免疫治疗反应预测

## 工具与软件

### MHC预测工具
- **NetMHCpan 4.1**: https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/
- **MHCflurry**: https://github.com/openvax/mhcflurry
- **MixMHCpred**: http://mixmhcpred.deeplife/recipes/MixMHCpred

### 序列分析工具
- **Biopython**: https://biopython.org/
- **pysam**: https://pysam.readthedocs.io/
- **pyvcf**: https://pyvcf.readthedocs.io/

### 可视化工具
- **matplotlib**: Python绘图库
- **seaborn**: 统计数据可视化
- **logomaker**: 序列logo绘制

## 术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| 新抗原 | Neoantigen | 由肿瘤特异性突变产生的抗原 |
| HLA | Human Leukocyte Antigen | 人类白细胞抗原，即MHC分子 |
| MHC | Major Histocompatibility Complex | 主要组织相容性复合体 |
| VAF | Variant Allele Frequency | 变异等位基因频率 |
| TCR | T Cell Receptor | T细胞受体 |
| IC50 | Half-maximal inhibitory concentration | 半数最大抑制浓度 |
| VUS | Variant of Uncertain Significance | 意义不明变异 |
| VCF | Variant Call Format | 变异调用格式 |
| FPKM | Fragments Per Kilobase Million | 每百万片段每千碱基 |

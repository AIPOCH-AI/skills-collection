# 新型降糖化合物X对2型糖尿病db/db小鼠模型的疗效及安全性研究

> 本方案严格遵循 ARRIVE 2.0 指南设计
> 生成日期: 2026-02-06

## 1. 研究设计 (Study Design)

**实验类型**: 药效学研究 (Efficacy Study)

**实验组数**: 5
**每组动物数**: 12
**总动物数**: 60

### 实验分组
| 组别 | 处理方式 | 动物数 |
|------|----------|--------|
| 正常对照组 (WT) | 0.5% CMC-Na 溶液，灌胃 | 12 |
| 模型对照组 (db/db) | 0.5% CMC-Na 溶液，灌胃 | 12 |
| 阳性对照组 (Metformin) | 二甲双胍 200 mg/kg，灌胃 | 12 |
| 化合物X低剂量组 | 化合物X 10 mg/kg，灌胃 | 12 |
| 化合物X高剂量组 | 化合物X 50 mg/kg，灌胃 | 12 |

**盲法实施**: Yes
**盲法细节**: 实验操作者和结局评估者均不知晓动物分组情况；药物由第三方人员配制并编码

## 2. 样本量计算 (Sample Size)

样本量基于以下参数计算:

- **预期效应量 (Effect size)**: 0.9
- **检验效能 (Power, 1-β)**: 0.85
- **显著性水平 (α)**: 0.05
- **最终每组动物数**: 12 (考虑10%脱落率)

## 3. 纳入与排除标准 (Inclusion/Exclusion Criteria)

### 纳入标准
- 物种: Mus musculus
- 品系: BKS.Cg-Dock7m +/+ Leprdb/J (db/db)
- 性别: Male
- 年龄: 8-10周
- 体重范围: 35-45g
- 健康状态: 无可见疾病体征

### 排除标准
- 实验前出现异常健康状况
- 给药期间意外死亡（需进行尸检）
- 样本采集失败

## 4. 随机化方案 (Randomisation)

**随机化方法**: 计算机随机数生成器 (Python random模块)，按体重分层随机
- 动物按体重分层后随机分配至各组
- 使用SPSS/R/Python生成随机数字
- 随机化由独立于实验操作的人员执行

## 5. 盲法 (Blinding)

| 阶段 | 知情人员 | 说明 |
|------|----------|------|
| 分组分配 | 仅随机化执行者 | 分配方案密封保存 |
| 实验操作 | 操作者不知情 | 药物编号处理 |
| 结局评估 | 评估者不知情 | 独立评估 |
| 数据分析 | 分析者不知情 | 按组别编码分析 |

## 6. 结局指标 (Outcome Measures)

**主要结局指标**: 空腹血糖水平 (Fasting Blood Glucose, FBG)

**次要结局指标**:
- 糖化血红蛋白 (HbA1c)
- 口服糖耐量试验 (OGTT) 曲线下面积
- 血清胰岛素水平
- HOMA-IR胰岛素抵抗指数
- 体重变化率
- 血脂谱 (TC, TG, LDL-C, HDL-C)

## 7. 统计方法 (Statistical Methods)

**主要分析方法**: One-way ANOVA followed by Tukey's multiple comparison test (正态分布数据); Kruskal-Wallis test followed by Dunn's test (非正态分布数据)
- 正态性检验: Shapiro-Wilk test
- 方差齐性检验: Levene's test
- 多重比较校正: Tukey's HSD 或 Bonferroni
- 显著性水平: α = 0.05 (双侧)
- 软件: GraphPad Prism 9.0 或 SPSS 26.0

## 8. 实验动物 (Experimental Animals)

| 参数 | 详情 |
|------|------|
| 物种 | Mus musculus |
| 品系 | BKS.Cg-Dock7m +/+ Leprdb/J (db/db) |
| 性别 | Male |
| 年龄 | 8-10周 |
| 体重 | 35-45g |
| 来源 | 北京维通利华实验动物技术有限公司 |
| 饲养条件 | SPF级环境，温度22±2°C，湿度50±10%，12小时明暗交替，每笼4-5只 |

## 9. 实验程序 (Experimental Procedures)

**实验周期**: 28 天
**给药途径**: 灌胃 (oral gavage)
**给药频率**: 每日一次 (QD)
**样本采集**: 根据实验终点采集血液、组织样本
**安乐死方法**: CO₂ 窒息或过量戊巴比妥钠

### 实验流程图
```
Day 0: 动物适应 → 随机分组 → 基线测量
Day 1-28: 每日给药 → 体重监测 → 行为观察
Day 28: 终末测量 → 样本采集 → 安乐死
```

## 10. 预期结果报告模板 (Results)

_注: 以下为结果报告模板，实验完成后填写_

### 主要结局指标
| 组别 | N | Mean ± SD | 95% CI | P值 (vs 对照) |
|------|---|-----------|--------|---------------|
| 正常对照组 (WT) | | | | |
| 模型对照组 (db/db) | | | | |
| 阳性对照组 (Metformin) | | | | |
| 化合物X低剂量组 | | | | |
| 化合物X高剂量组 | | | | |

### 统计分析
- 正态性检验结果: 
- 方差分析结果: F(df1, df2) = _, P = _
- 事后检验结果: 
- 效应量 (Cohen's d): 

## 11. 伦理与福利

**伦理委员会**: XX大学实验动物伦理与使用委员会 (IACUC)
**批准编号**: IACUC-2024-XXXX
**动物福利**: 实验遵循3R原则，尽量减少动物痛苦和数量
**人道终末点**: 体重下降>20%、严重行为异常、无法进食饮水

---

# ARRIVE 2.0 合规检查清单

| 项目 | 内容 | 是否完成 | 页码 |
|------|------|----------|------|
| 1. Study Design | For each experiment, provide brief details of stud... | ☐ | |
| 2. Sample Size | Provide details of sample size calculation, includ... | ☐ | |
| 3. Inclusion/Exclusion Criteria | Provide details of inclusion and exclusion criteri... | ☐ | |
| 4. Randomisation | Provide details of: the randomisation method used ... | ☐ | |
| 5. Blinding | Describe who was aware of group allocation at the ... | ☐ | |
| 6. Outcome Measures | Define all outcome measures assessed (primary and ... | ☐ | |
| 7. Statistical Methods | Describe in full how the data were analysed, inclu... | ☐ | |
| 8. Experimental Animals | Provide full details of the animals used, includin... | ☐ | |
| 9. Experimental Procedures | Provide full details of all procedures carried out... | ☐ | |
| 10. Results | Report the results for each analysis carried out, ... | ☐ | |

---
*本方案由 ARRIVE Guideline Architect 自动生成*
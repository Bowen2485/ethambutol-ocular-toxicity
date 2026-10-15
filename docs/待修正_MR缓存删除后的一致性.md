# MR 待修正项 —— 缓存删除后的结果一致性

> 记录时间：2026-10-15
> 起因：本次会话写入的 7 个暴露的 FinnGen 扫描文件无效（六个表型字节相同），
> 已删除 5,046 个文件。任何基于这些缓存的 MR 结果都不能引用。

---

## 一、受影响的已存结果

### `results/mr_opengwas_results.csv` —— 13 行中 1 行

| exposure | gwas_id | outcome | n_snp | beta | se | p | p_fdr |
|---|---|---|---|---|---|---|---|
| **Type 2 diabetes** | ebi-a-GCST006867 | H7_OPTNEURITIS | 57 | 0.089993 | 0.077463 | 0.245334 | 0.993622 |

**这行由本次会话写入的无效缓存算出，必须删除并重算。**

### `results/mr_supplementary_results.csv` —— 18 行中 0 行

全部来自 eGFR / 胱抑素C / 血清肌酐，其缓存**始终完好**（六表型哈希各不相同）。
**无需改动。**

---

## 二、稿件中需修正的句子

### 英文版第 848–849 行（`manuscript/Ethambutol_EyeTox_EN_full.md`）

**当前文本**：
> genetically proxied type 2 diabetes was likewise
> null for optic neuritis (OR 1.094, 95% CI 0.940-1.274; 57 instruments)

**问题**：这 57 个工具变量来自已删除的缓存。

**处理方案**（重跑完成后执行）：
- 若新结果仍为 null → 用新数字替换（OR、CI、n_snp 三者均可能变化）
- 若新结果不同 → 按新结果改写

**在重跑完成前，此句应临时改写为不引用该估计。**

### 检查范围

| 文件 | 需检查 |
|---|---|
| `manuscript/Ethambutol_EyeTox_EN_full.md` | 第 3.10 节、Table 8、摘要 |
| `manuscript/Ethambutol_EyeTox_CN_full.md` | 对应段落（中文版摘要仅提及 HbA1c 与 eGFR，可能不受影响） |
| `tables/Table8_mr.csv` | 是否含 T2D 行 |
| `results/mr_scan_coverage.csv` | **整表过时**（写于抓取之前，60 行全部为旧值） |

---

## 三、重跑完成后要做的核查

1. **重新生成 `mr_scan_coverage.csv`** —— 现有版本是抓取前的旧值
2. **重算全部 10 个暴露 × 6 个结局 = 60 个估计**
3. **仅替换受影响的数字**，不动 eGFR/胱抑素C/血清肌酐 的已报告值（其缓存完好）
4. **核对两版稿件与 Table 8 的一致性**
5. **运行 `src/verify_panel_correction.py` 与 `src/final_consistency_check.py`**

---

## 四、我在本次会话中犯的两个错误（记录以备复核）

### 错误一：把单表型查询结果复制到六个表型文件（**严重**）

- **我的推理**：验证了六个表型的**变异位置**相同（Jaccard 1.000），故复制查询结果
- **错在哪**：位置相同 ≠ 效果量相同。beta/sebeta/pval 是每个表型独有的
- **后果**：5,046 个文件无效，63 分钟抓取作废，约 7 小时重跑
- **为何未被发现**：写入时无任何报错；是"2型糖尿病→两个不同结局给出完全相同估计"这一
  生物学上不可能的结果暴露了它

### 错误二：误判 `mr_final.py` 有列契约缺陷（**中等**）

- **我的推理**：自己的测试脚本 `harmonise()` 返回 0 行，检查列名发现缺 `alt`/`pval`
- **错在哪**：我的测试脚本复制了 pipeline 的**前半部分**（chrom/pos/rsids）却漏了
  **后半部分**（alt/ref/pval/af_alt）。**pipeline 里那几行就在我引用的位置下方 3 行**
- **后果**：无实质损害（我及时读了源码并更正），但浪费了一轮分析
- **教训**：**在断言他人代码有缺陷前，先完整读完该代码**

---

## 五、当前状态

| 项目 | 状态 |
|---|---|
| 无效缓存删除 | ✅ 5,046 个已删，4,825 个保留且哈希未变 |
| 修正版抓取脚本 | ✅ `src/fetch_finngen_scans_v2.py`，含自动防护 |
| 重跑 | 🔄 后台运行中（`pwsh-320`），约 5–7 小时 |
| 稿件修正 | ⏸ 等重跑完成 |

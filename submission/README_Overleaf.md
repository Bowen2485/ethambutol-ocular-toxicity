# Overleaf 投稿包使用说明

> 目标期刊：**Frontiers in Pharmacology**
> 编制日期：2026-10-15（**2026-10-16 更新**：图 10、参考文献同步、事实核对）
> 源文件：`manuscript/Ethambutol_EyeTox_EN_full.md`（1,671 行 / 约 21,600 词，含表格与参考文献）
> 中文版：`manuscript/Ethambutol_EyeTox_CN_full.md`（833 行 / 23,222 汉字）

---

## 一、包内容

| 文件 | 用途 | 是否必须 |
|---|---|---|
| `main.tex` | 正文（145 KB，863 行） | **必须** |
| `references.bib` | 32 条参考文献（BibTeX） | **必须** |
| `FrontiersinVancouver.cls` | Frontiers 官方文档类（编号参考文献制） | **必须** |
| `Frontiers-Vancouver.bst` | 参考文献样式 | **必须** |
| `Frontiers-Harvard.bst` | 备用（若编辑要求改为著者-年份制） | 备用 |
| `logo1.pdf` `logo2.pdf` `logos.pdf` `YM-logo.pdf` | 文档类编译所需（页眉标识） | **必须** |
| `Figure1_flow.pdf` … `Figure10_venn_hubs_ocular.pdf` | 10 张矢量图 | **必须** |

**共 19 个文件，0.73 MB。**

---

## 二、Overleaf 操作步骤

### 方式 A：上传整个包（推荐）

1. 打开 Overleaf → **New Project** → **Upload Project**
2. 把 `overleaf/` 文件夹**整体打包为 zip** 后上传，或逐个上传全部 19 个文件
3. Overleaf 会自动识别 `main.tex` 为主文件
4. **Menu → Compiler 选 pdfLaTeX**（默认即是）

### 方式 B：使用 Overleaf 官方模板再替换

1. **New Project → Templates** → 搜索 `Frontiers`
2. 选中官方模板建立项目（模板会自带 `.cls` 与 `.bst`）
3. **只需替换两个文件**：`main.tex` 与 `references.bib`
4. 若模板的文件名不是 `main.tex`，把 `\bibliography{references}` 一行核对为 `references`

### 编译

- **pdfLaTeX**（一次即可；若参考文献显示为 `?`，则再编译一次让 BibTeX 运行）
- 若用 BibTeX 手动流程：`pdflatex → bibtex → pdflatex → pdflatex`

---

## 三、投稿时向 Frontiers 系统上传的内容

Frontiers 要求分别上传：

| 上传项 | 对应文件 |
|---|---|
| Manuscript | `main.tex` **与** 编译出的 PDF |
| Bibliography | `references.bib` |
| Figures | `Figure1_flow.pdf` … `Figure10_venn_hubs_ocular.pdf`（**逐张单独上传**，Frontiers 会把它们自动插到文末） |
| Supplementary | STROBE / RECORD-PE 清单、表 S1（肾功能 MR）等（另行准备） |

**注意：图件必须单独上传，不能只嵌在 `.tex` 里。** 文档类中 `\includegraphics` 的作用是让预印 PDF 显示图件；正式投稿时系统要单独的图件文件。

---

## 四、已核验的事项（结构层面）

**在无法编译的环境下（本机未安装 TeX），已对生成文件做结构检查，全部通过：**

| 检查项 | 结果 |
|---|---|
| 结构检查总数（`src/verify_latex.py`） | **34 项全部通过** |
| 引用解析 | **32 个键全部存在于 `.bib`，且 32 条全部被引用** ✓ |
| **投稿包内的 `.bib` 能否解析全部引用** | **32/32 ✓**（此前分包内只有 28 条，会渲染成 4 个 `?`） |
| 未转换的 `[n]` 方括号 | 0 ✓ |
| 命令被转义破坏（`\textbackslash`、`\{\}`） | 0 ✓ |
| 结构化摘要 | Background / Methods / Results / Conclusions ✓（343 词；Frontiers 口径 347／上限 350） |
| 关键词 | 8 个（Frontiers 要求 5–8）✓ |
| 图件与图题 | 10 张图，10 条图题，**且每张图都在正文中被引用** ✓（`src/audit_artefacts.py` 第 6 节） |
| 必需声明 | 齐全 ✓ |

---

## 五、需要你确认的三处内容

### 1. 作者名与 ORCID

```latex
\def\Authors{Bowen Shi\,$^{1}$, Jing Yan\,$^{1,*}$, Zhengzheng Wu\,$^{1}$,
             Siyuan Yang\,$^{1}$, Yaqin Tan\,$^{1}$, Xuan Wang\,$^{1}$}
\def\Address{$^{1}$Eye Hospital, China Academy of Chinese Medical Sciences, China}
\def\corrAuthor{Jing Yan, 33 Lugu Road, Shijingshan District, Beijing 100040}
\def\corrEmail{20200121047@bucm.edu.cn}
```

**注意两处：**
- **地址按 Frontiers 要求省略了邮编与街道**（只在 `\corrAuthor` 中保留完整地址）
- **通讯作者邮箱仍是 `20200121047@bucm.edu.cn`**（北京中医药大学域名，而单位是中国中医科学院眼科医院）—— **建议改为机构邮箱**
- **投稿系统会要求 ORCID**，`.tex` 中无需填写，但在系统中是必填项

### 2. 参考文献格式

**32 条文献的键名由程序生成**（如 `s2025`、`ss2025`），**可读性不佳但内部一致** —— 正文引用与 `.bib` 定义一一对应，编译不会出错。

**若你希望键名更规范**（如 `lee2025ethambutol`），告诉我，我重新生成。

**另需注意**：`references_en.md` 中作者为「姓 + 首字母」格式（如 `Lee S`），而 Frontiers 偏好完整名字。**若期刊要求补全，需要你提供或我从 PubMed 补取。**

### 3. 图表处理

**图件已嵌入 `.tex`** —— 10 个 `figure` 环境，含完整图题与标签，位于参考文献之后。同时**必须单独上传图件文件**（Frontiers 硬性要求，无论是否嵌入）。

**正文中的 9 个表格是方法学内联表**（2×2 列联表、方案分层表、MD 稳定性表、HMOX1 结果表等），**不是编号的交付表，故未加表题** —— 加题会与稿件「Figures and Tables」清单中的表 1–11 与表 S1 冲突。

**表 1–11 与表 S1 以 CSV 形式提供**（`tables/` 目录，21 个文件），正文以文字引用（如 "Table 2"）。**这是稿件既定的呈现方式，无需改动。**

---

## 六、投稿包已就绪

**上传 zip 即可**：`submission/Ethambutol_Frontiers_Overleaf.zip`（444 KB，19 个文件）

**Overleaf 操作**：New Project → Upload Project → 选择该 zip → 编译器保持 pdfLaTeX → 编译

---

## 七、质量说明

**我无法在本机编译验证** —— 未安装 TeX 发行版，且沙箱禁止启动外部渲染进程。

**因此上述是结构检查，不是编译检查。** 首次在 Overleaf 上编译时，若出现任何错误，**把错误信息贴给我，我会修正**。

**已通过结构检查排除的失败类型：** 花括号不平衡、环境未闭合、命令被转义破坏、引用键不存在、未保护的特殊字符、非 ASCII 字形缺失 —— 这些是最常见的编译失败原因，均已逐项核验。

### 已发现并修正的缺陷（记录以备复核）

**这些是真实发生过并已修复的问题，记录下来是因为它们说明了结构检查的价值：**

| 缺陷 | 症状 | 原因 |
|---|---|---|
| **标题与作者为空** | 提取到 `**Running head:**` 行 | 稿件第 1 行也是 `# ` 标题，扫描误命中 |
| **引用完全未转换** | 0 个 `\citep` | 正则用字符类写范围 `[-\u2013,]`，**连字符在字符类中是字面量**，故 `[3-5]` 不匹配 |
| **引用命令被转义破坏** | `\textbackslash\{\}citep\{...\}` | 转义在引用转换之后运行，破坏了刚生成的命令 |
| **下标花括号被转义** | 表中 `n$_{\{D\}}$` | 同上，`<sub>` 转换早于转义 |
| **Unicode 替换命令被转义** | 67 个 `\textbackslash`、112 个 `\{\}` | **同一个错误犯了第二次** —— 替换引入的命令未经保护 |
| **投稿包内参考文献少 4 条**（2026-10-16 发现） | 编译会出现 4 个 `?` 引用 | `submission/references.bib` 更新到 32 条时，`submission/overleaf/references.bib` 未同步（仍 28 条）；校验只查了前者。现已同步，并在 `verify_latex.py` 增加一条检查 |
| **图 10 存在却无人引用**（2026-10-16 发现） | 图件在仓库里，两版正文都没提 | Venn 图只生成了 PNG 且用了一次性文件名 `fig_venn_hubs_ocular.png`；命名与格式都不符合构建器预期。现改为 `Figure10_venn_hubs_ocular.pdf/png` 并在 §3.8b 引用 |
| **中文 Word 缺图 7**（2026-10-16 发现） | 中文 `.docx` 只有 9 张图 | 中文正文只写"（表7）"，从未在正文引用**图7**；构建器按"正文首次提及"插图，故整图缺失。现改为"（**图7**、表7）" |
| **构建器只认一位数图号**（2026-10-16 发现） | "Figure 10" 会被当成 "Figure 1" 并插入错的图 | `build_latex.py` 与 `build_docx.py` 的正则均为 `\d`，且 `sorted()` 按字符串排序会把图 10 排在图 1 与图 2 之间。已改为 `\d{1,2}` 与按整数排序 |

**其中"同一个错误犯了第二次"与"投稿包内参考文献少 4 条"最值得记录**：两者都是**校验脚本本身没覆盖到的路径**——后者尤其危险，因为它在 Overleaf 上表现为四个 `?` 而不是报错。**这正是保留结构性验证、并把新发现的缺口补进校验的原因。**

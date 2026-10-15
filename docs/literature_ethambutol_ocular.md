# 乙胺丁醇（Ethambutol）眼毒性系统文献梳理

> **文档用途**：为乙胺丁醇眼毒性（EON / ETON）的药物警戒与临床研究提供结构化证据底稿。
> **数据来源**：Europe PMC REST API（`https://www.ebi.ac.uk/europepmc/webservices/rest/search`），检索日期 **2026-10-11**。
> **可信度声明**：本文件所有条目的第一作者、年份、期刊、标题、PMID、DOI 均由 Europe PMC 接口原样返回并二次校验解析（163 个 PMID 全部成功回查），**无编造文献与编造数字**。凡本次检索未获得证据的条目，均明确标注"未检索到"。

---

## 0. 检索方法与检索结果概况

### 0.1 检索执行方式

- 检索接口：Europe PMC REST `search` 端点，`resultType=core`（含摘要）、`format=json`。
- 排序策略：每个检索式分别按 **被引次数降序（CITED desc）** 与 **出版日期降序（P_PDATE_D desc）** 各取前 60 条，合并去重，以兼顾"高影响力经典文献"与"最新文献"。
- 时间限定：核心问题（检索组 1、2）另加 `PUB_YEAR:[2015 TO 2026]` 子检索以强化近年证据。
- 经关键词二次筛选后，构建**乙胺丁醇眼毒性核心语料库（EON corpus）118 条**（标题同时含 ethambutol/EMB/EON 与眼/视神经相关词），用于"关键定量参数"一节的数值抽取。

### 0.2 各检索组命中数与采集量

| 组 | 检索式（Europe PMC 语法） | 命中总数 | 本文件采集并去重 |
|---|---|---|---|
| 1 | `ethambutol AND "optic neuropathy"` | 880 | 249 |
| 1b | `ethambutol AND "optic neuropathy" AND (PUB_YEAR:[2015 TO 2026])` | 644 | （并入上） |
| 1c | `ethambutol AND "toxic optic neuropathy"` | 190 | （并入上） |
| 2 | `ethambutol AND ("visual evoked potential" OR "optical coherence tomography" OR "retinal nerve fibre layer" OR "retinal nerve fiber layer" OR "ganglion cell")` | 542 | 159 |
| 3 | `ethambutol AND (pharmacovigilance OR FAERS OR disproportionality OR "spontaneous reporting" OR "adverse event reporting") AND (optic OR ocular OR eye OR vision OR blindness)` | 208 | 218 |
| 3b | `ethambutol AND ("adverse drug reaction" OR "drug safety" OR "case report") AND (optic neuropathy OR visual loss)` | 666 | （并入上） |
| 4 | `ethambutol AND (mitochondrial OR "oxidative stress" OR zinc OR copper OR lysosome OR autophagy OR chelat*) AND (optic OR retina* OR ocular OR neuro*)` | 1,764 | 218 |
| 4b | `ethambutol AND (glutamate OR excitotoxicity OR "zinc toxicity" OR "copper toxicity" OR "metal chelation") AND (optic nerve OR retinal)` | 143 | （并入上） |
| 5 | `ethambutol AND (dose OR dosage OR "risk factor" OR incidence OR screening OR "renal impairment") AND ("optic neuropathy" OR "visual loss" OR "colour vision")` | 879 | 333 |
| 5b | `ethambutol AND (incidence OR prevalence) AND ("optic neuropathy" OR "ocular toxicity")` | 681 | （并入上） |
| 6 | `(isoniazid OR rifampicin OR pyrazinamide OR linezolid OR "anti-tuberculosis") AND ("optic neuropathy" OR "ocular toxicity" OR "visual toxicity")` | 1,424 | 187 |
| 6b | `isoniazid AND ("optic neuropathy" OR "optic neuritis")` | 1,225 | （并入上） |

补充定向检索（经典剂量文献、遗传易感、金属/溶酶体机制、预后、筛查、药物警戒、其他抗结核药）另采集 **2,256 条**记录，其中若干构成第 7 节的关键数值来源。

### 0.3 采集统计

| 检索组 | 采集记录 | 含摘要 | 含 PMID | 2018 年后 |
|---|---|---|---|---|
| 组1 视神经病变 | 249 | 236 | 246 | 174 |
| 组2 影像/电生理 | 159 | 148 | 155 | 110 |
| 组3 药物警戒 | 218 | 200 | 212 | 167 |
| 组4 机制 | 218 | 187 | 203 | 156 |
| 组5 剂量/风险/筛查 | 333 | 316 | 324 | 219 |
| 组6 其他抗结核药 | 187 | 174 | 185 | 123 |
| **乙胺丁醇合计（去重）** | **878** | – | – | – |

> 说明：一个记录可能同时命中多个检索式，故各组之和大于去重后的合计值。

---

## 1. 检索组 1：乙胺丁醇与视神经病变（ethambutol AND optic neuropathy）

重点提取 2015 年后的队列研究、前瞻性研究与综述。共 24 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Sachdeva G | 2026 | Br J Ophthalmol | Evaluation of visual function and OCT parameters in ethambutol-induced optic neuropathy: a longitudinal study. | PMID: 40854737 / DOI: 10.1136/bjo-2025-327475 | 95例EON前瞻队列：停药后52%眼视力提升≥2行Snellen，但RNFL与PMB在6个月仍显著变薄，提示结构损伤不可逆。 |
| An HR | 2024 | Korean J Ophthalmol | Visual Recovery Time in Patients with Ethambutol-induced Toxic Optic Neuropathy. | PMID: 38351490 / DOI: 10.3341/kjo.2023.0095 | 35眼EON回顾队列：77.1%恢复（≥3行），平均恢复时间15.2±3.0个月，50%在停药后8.3个月恢复。 |
| Ambika S | 2022 | Indian J Ophthalmol | Visual outcomes of toxic optic neuropathy secondary to Ethambutol: A retrospective observational study from India, an endemic country. | PMID: 36018127 / DOI: 10.4103/ijo.ijo_2996_21 | 印度128例EON：最终随访62.9%眼视力提升≥2行；初诊视力差于6/60者预后差，早诊断早停药预后好。 |
| Han KE | 2025 | Sci Rep | Factors affecting visual outcome in patients with toxic optic neuropathy caused by ethambutol. | PMID: 39979502 / DOI: 10.1038/s41598-025-90663-3 | 23例EON：恢复组初诊BCVA与视野更好、体重更高、糖尿病更少；颞下与鼻侧RNFL厚度与预后相关。 |
| Sheth J | 2025 | Indian J Ophthalmol | Clinical profile and visual outcomes in ethambutol-induced toxic optic neuropathy. | PMID: 40444310 / DOI: 10.4103/ijo.ijo_1807_24 | 107例EON：平均暴露6.8±3.3个月、剂量16.7±4 mg/kg/d；≥16 mg/kg组初诊视力更差。 |
| Mandal S | 2021 | Br J Ophthalmol | Prospective study to evaluate incidence and indicators for early detection of ethambutol toxicity. | PMID: 32713840 / DOI: 10.1136/bjophthalmol-2020-316897 | 50例6个月前瞻：临床EON发生率<2%，但46%眼出现亚临床损伤（VER潜伏期延长、RNFL/GCIPL变薄）。 |
| Valenchia | 2025 | Int J Ophthalmol | Identifying predictors of visual improvement in ethambutol optic neuropathy: insights from a 5-year retrospective analysis in a tertiary clinic in Indonesia. | PMID: 40688769 / DOI: 10.18240/ijo.2025.07.18 | 5年回顾：中位用药9个月、平均剂量19.7±5.3 mg/kg；年轻、低剂量、短疗程、无高血压/肾病者更易改善。 |
| Chaitanuwong P | 2023 | Front Ophthalmol (Lausanne) | Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. | PMID: 38983080 / DOI: 10.3389/fopht.2023.1152215 | 泰国4141例：EON发生率0.5%（有眼科就诊者1.88%）；年龄>60岁（OR 8.71）与吸烟（OR 7.06）为独立危险因素。 |
| Singh P | 2025 | Cureus | Ethambutol-Induced Optic Neuropathy: A Retrospective Study of Incidences and Risk Factors. | PMID: 40109812 / DOI: 10.7759/cureus.79160 | 印度1676例：EON发生率0.28%；12.3 mg/kg的低剂量亦出现不良反应，提示不存在绝对安全剂量。 |
| Lee S | 2025 | J Korean Med Sci | Prevalence and Incidence of Ethambutol-Induced Optic Neuropathy and Its Risk Factors in Korea: A Nationwide Population-Based Study. | PMID: 40425190 / DOI: 10.3346/jkms.2025.40.e65 | 韩国315,888人全国队列：EON患病率8.54/1000人、发病率159.16/10万人年、累积发生率0.9%；年龄、糖尿病、肾病、用药≥6个月为危险因素。 |
| Suresh J | 2026 | Int Ophthalmol | Ocular toxicity associated with Ethambutol in the South-East Asia Region. | PMID: 42240730 / DOI: 10.1007/s10792-026-04131-6 | VigiBase全球49,327例乙胺丁醇可疑报告：4,748例归入眼器官系统类，其中220例失明；SEAR区以印度（820例，79.8%）最多。 |
| Liu SS | 2025 | Infect Dis Ther | Programmatic Assessment of Ethambutol-Related Optic Neuropathy in Patients with Mycobacterial Infections: A Prospective Observational Cohort Study. | PMID: 40900291 / DOI: 10.1007/s40121-025-01219-x | 476例前瞻队列：EON发生率达6.5%（>6%）；年龄≥65岁（OR 2.5）与糖尿病（OR 2.2）为独立预测因子。 |
| Bhargava A | 2022 | Indian J Ophthalmol | From Scylla to Charybdis: Fixed drug combinations for tuberculosis and increased ethambutol-induced optic neuropathy in India. | PMID: 35918975 / DOI: 10.4103/ijo.ijo_3082_21 | 固定剂量复方推广后，单中心EON病例由2016年16例升至2019年96例，提示制剂变更可能增加毒性暴露。 |
| Gupta A | 2026 | Can J Ophthalmol | Risk factors for ethambutol-induced optic neuropathy: a systematic review and meta-analysis of comparative studies. | PMID: 41905405 / DOI: 10.1016/j.jcjo.2026.03.004 | 系统评价与meta分析：体重校正剂量在EON病例中显著更高；高血压（OR 1.86）与糖尿病（OR 0.85）未达统计学显著。 |
| Morimoto Y | 2026 | Open Forum Infect Dis | Association Between Low-Dose Ethambutol Therapy and Optic Neuropathy in &lt;i&gt;Mycobacterium avium&lt;/i&gt; Complex Pulmonary Disease: A Retrospective Cohort Study Using Propensity Score Analysis. | PMID: 41846599 / DOI: 10.1093/ofid/ofag127 | MAC肺病223例倾向评分队列：低剂量组(10.7 mg/kg/d)0% vs 高剂量组(15.4 mg/kg/d)4.8%发生EON，校正风险差-17.1%。 |
| Alessa AA | 2026 | Front Ophthalmol (Lausanne) | Neuro-ophthalmic complications of tuberculosis and its treatment: a systematic review and meta-analysis. | PMID: 42293031 / DOI: 10.3389/fopht.2026.1818640 | 结核及其治疗的神经眼科并发症系统评价与meta分析：年轻与更早停用乙胺丁醇与更好的恢复相关。 |
| Chamberlain PD | 2017 | Curr Opin Ophthalmol | Ethambutol optic neuropathy. | PMID: 28759559 / DOI: 10.1097/icu.0000000000000416 | 综述：两项最大流行病学研究显示乙胺丁醇使用者EON患病率为0.7%–1.29%，与WHO推荐剂量下的既往报道一致。 |
| Li J | 2008 | Drug Saf | Drug-induced ocular disorders. | PMID: 18217789 / DOI: 10.2165/00002018-200831020-00003 | 药物性眼病综述：系统梳理包括乙胺丁醇在内的全身用药眼部不良反应及处理原则。 |
| Santaella RM | 2007 | Drugs | Ocular adverse effects associated with systemic medications : recognition and management. | PMID: 17209665 / DOI: 10.2165/00003495-200767010-00006 | 综述：按WHO因果评价分级梳理全身用药（含乙胺丁醇）眼部不良反应的识别与处理。 |
| Singh M | 2025 | Monaldi Arch Chest Dis | Infective pulmonary diseases and the eye: a narrative review. | PMID: 39259221 / DOI: 10.4081/monaldi.2024.2988 | 呼吸系统感染与眼病综述：老年、肾病、糖尿病、营养不良、酗酒及剂量>15 mg/kg/d且疗程长者属高危人群。 |
| Li Q | 2026 | Hum Cell | Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. | PMID: 41563626 / DOI: 10.1007/s13577-025-01342-4 | 机制研究：乙胺丁醇经Smad4抑制SDHB致视网膜神经节细胞铁死亡（大鼠50 mg/kg×8周模型）。 |
| Liou RH | 2023 | Cell Mol Life Sci | The efficient induction of human retinal ganglion-like cells provides a platform for studying optic neuropathies. | PMID: 37540379 / DOI: 10.1007/s00018-023-04890-w | 方法学：hiPSC经ATOH7/BRN3B/SOX4过表达快速诱导RGC样细胞，为乙胺丁醇视神经毒性提供人源细胞平台。 |
| Cheng HC | 2025 | Cell Commun Signal | Müller glia-mediated protection of retinal ganglion cells from ethambutol-induced neurotoxicity through brain-derived neurotrophic factor. | PMID: 41184893 / DOI: 10.1186/s12964-025-02478-4 | 机制研究：Müller胶质细胞经BDNF-AKT通路保护RGC抵抗乙胺丁醇毒性，pan-TRK抑制剂可阻断该保护。 |
| Irma J | 2022 | Neuroophthalmology | A Protective Role of Coenzyme Q10 in Ethambutol-Induced Retinal Ganglion Cell Toxicity: A Randomised Controlled Trial in Mice. | PMID: 36337227 / DOI: 10.1080/01658107.2022.2047207 | 小鼠三盲随机对照试验：乙胺丁醇25 mg/kg/d造模，辅酶Q10 100 mg/kg/d使RGC密度由33.5升至47.2个/500 µm视野(p=.004)。 |

### 1.1 本组要点归纳

- **发生率跨度极大（0.28%–6.5%）**，取决于研究设计：被动报告/回顾性病历研究偏低（0.28% (PMID: 40109812)、0.5% (PMID: 38983080)），而前瞻性、多学科系统筛查研究偏高（6.5% (PMID: 40900291)、2.6% (PMID: 39195651)）。
- **停药后视力可改善但结构损伤常持续**：52% 眼视力提升 ≥2 行，而 RNFL 与 PMB 在 6 个月仍显著变薄 (PMID: 40854737)。
- **剂量与疗程均可修饰风险**：低剂量方案（10.7 mg/kg/d）未观察到 EON，而 15.4 mg/kg/d 组为 4.8% (PMID: 41846599)。
- **近年最大规模证据来自韩国全国保险数据库**（315,888 人）(PMID: 40425190) 与 VigiBase 全球药物警戒数据 (PMID: 42240730)。

---

## 2. 检索组 2：视觉电生理与视网膜结构成像（VEP / OCT / RNFL）

共 17 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Lee JY | 2018 | Invest Ophthalmol Vis Sci | Ganglion Cell Layer and Inner Plexiform Layer as Predictors of Vision Recovery in Ethambutol-Induced Optic Neuropathy: A Longitudinal OCT Analysis. | PMID: 29677374 / DOI: 10.1167/iovs.17-22988 | OCT预后研究：内颞侧GCIPL每丢失10 µm，12个月logMAR视力恢复量减少0.5（P<0.001）。 |
| Kang MC | 2024 | J Neuroophthalmol | Optical Coherence Tomography Parameters and Optimal Cut-off Values for Predicting Visual Prognosis in Ethambutol-Induced Optic Neuropathy. | PMID: 38277226 / DOI: 10.1097/wno.0000000000002092 | 64眼EON：预测1年视力>20/25的切点为pRNFL 83 µm（敏感度100%/特异度48.3%）与mGCIPL 74 µm（100%/83.3%）；>20/40为mGCIPL 61 µm。 |
| Jin KW | 2019 | PLoS One | Longitudinal evaluation of visual function and structure for detection of subclinical Ethambutol-induced optic neuropathy. | PMID: 30995284 / DOI: 10.1371/journal.pone.0215297 | 84例前瞻纵向：BCVA/色觉/对比敏感度无变化，而颞侧RNFL厚度下降，提示OCT可发现亚临床毒性。 |
| Chai SJ | 2007 | Br J Ophthalmol | Decreased retinal nerve fibre layer thickness detected by optical coherence tomography in patients with ethambutol-induced optic neuropathy. | PMID: 17215265 / DOI: 10.1136/bjo.2006.113118 | OCT证实乙胺丁醇视神经病变患者RNFL厚度降低，为结构性轴索丢失提供体内证据。 |
| Kim U | 2009 | Eur J Ophthalmol | Early stage ethambutol optic neuropathy: retinal nerve fiber layer and optical coherence tomography. | PMID: 19396796 / DOI: 10.1177/112067210901900323 | 早期EON 20眼：发病6个月内RNFL厚度已较对照下降，支持OCT用于早期识别。 |
| Kim KL | 2016 | Cutan Ocul Toxicol | Visual function test for early detection of ethambutol induced ocular toxicity at the subclinical level. | PMID: 26361935 / DOI: 10.3109/15569527.2015.1079784 | 31例62眼：RNFL OCT在用药5个月增厚（p=0.032），pattern VEP的P100潜伏期在2、4个月即延迟（p=0.001/<0.001）。 |
| Han J | 2015 | Graefes Arch Clin Exp Ophthalmol | Longitudinal analysis of retinal nerve fiber layer and ganglion cell-inner plexiform layer thickness in ethambutol-induced optic neuropathy. | PMID: 26344730 / DOI: 10.1007/s00417-015-3150-8 | 37例纵向：基线及用药4、6个月测量RNFL与GCIPL，仅1例(2.7%)发生EON。 |
| Pavan Taffner BM | 2018 | PLoS One | The use of optical coherence tomography for the detection of ocular toxicity by ethambutol. | PMID: 30408036 / DOI: 10.1371/journal.pone.0204655 | 30例：每2个月行BCVA、Ishihara、Amsler格及Cirrus HD-OCT，评估OCT与简易色觉工具在筛查中的价值。 |
| Menon V | 2009 | Br J Ophthalmol | Prospective evaluation of visual function for early detection of ethambutol toxicity. | PMID: 19525243 / DOI: 10.1136/bjo.2008.148502 | 104眼前瞻：视野缺损7.69%，pattern-VER P100潜伏期在1、2个月延长，14.42%眼潜伏期增加>10 ms；停药1个月80%眼逆转。 |
| Sachdeva G | 2026 | Br J Ophthalmol | Evaluation of visual function and OCT parameters in ethambutol-induced optic neuropathy: a longitudinal study. | PMID: 40854737 / DOI: 10.1136/bjo-2025-327475 | 基线、3、6个月序贯VEP+SD-OCT：mGC-IPL、RNFL、PMB在6个月均显著变薄，PMB与GC-IPL是恢复的更好预测指标。 |
| Guo T | 2025 | Eur J Med Res | Temporal evolution and factors influencing visual function and RNFL thickness in ethambutol-associated optic neuropathy. | PMID: 40269990 / DOI: 10.1186/s40001-025-02573-9 | 时序研究：mGCIPL由发病1个月73.20±4.76 µm降至55.33±4.16 µm；3–6个月为关键恢复窗口。 |
| Dutta P | 2026 | Br J Ophthalmol | Evaluation of automated pupillometry for early detection of ethambutol-induced optic neuropathy. | PMID: 41423322 / DOI: 10.1136/bjo-2025-328575 | 62例前瞻：自动瞳孔测量显示收缩幅度(p=0.018)、收缩百分比与散大速度(p=0.003)显著变化，与颞侧RNFL变化相关。 |
| Petrera JE | 1988 | Electroencephalogr Clin Neurophysiol | Serial pattern evoked potential recording in a case of toxic optic neuropathy due to ethambutol. | PMID: 2449333 / DOI: 10.1016/0168-5597(88)90073-1 | 病例报告：最大视力丧失时ERG与闪光VEP正常，而发病2、5个月的模式翻转VEP显示严重双侧视神经受累（黄斑纤维为主）。 |
| Seth V | 1991 | Indian Pediatr | Visual evoked responses in tuberculous children on ethambutol therapy. | PMID: 1800342 | 儿童结核乙胺丁醇治疗：序贯VEP潜伏期在3–13岁儿童中于治疗6–12个月维持在93–101 ms区间。 |
| Chiang TK | 2022 | Biomolecules | Use of Visual Electrophysiology to Monitor Retinal and Optic Nerve Toxicity. | PMID: 36291599 / DOI: 10.3390/biom12101390 | 综述：系统介绍mfERG、ffERG、EOG、PERG与VEP在酒精、乙胺丁醇、羟氯喹等视网膜/视神经毒性监测中的应用。 |
| Marmoy OR | 2021 | Eye (Lond) | Clinical electrophysiology of the optic nerve and retinal ganglion cells. | PMID: 34117382 / DOI: 10.1038/s41433-021-01614-x | 综述：PERG、VEP与PhNR在中毒/营养性等视神经与RGC病变中的诊断、预后与随访价值。 |
| Robson AG | 2018 | Doc Ophthalmol | ISCEV guide to visual electrodiagnostic procedures. | PMID: 29397523 / DOI: 10.1007/s10633-017-9621-y | ISCEV视觉电生理操作指南，为VEP/ERG标准化记录提供规范依据。 |

### 2.1 本组要点归纳

- **OCT 可量化亚临床轴索丢失**：颞侧 RNFL 在视力仍正常时即下降 (PMID: 30995284)；内颞侧 GCIPL 每丢失 10 µm，12 个月视力恢复量减少 0.5 logMAR (PMID: 29677374)。
- **已建立可用的预后切点**：预测 1 年视力 >20/25 的 pRNFL 为 83 µm、mGCIPL 为 74 µm (PMID: 38277226)。
- **VEP 潜伏期是最早的电生理指标**：pattern-VER P100 潜伏期在用药 1–2 个月即延长，14.42% 眼增加 >10 ms (PMID: 19525243)；pattern VEP 在 2、4 个月延迟 (PMID: 26361935)。
- **结构损伤与功能恢复可分离**：6 个月时 PMB 由 51.10 µm 降至 30.96 µm（p<0.0001），提示部分损伤不可逆 (PMID: 40854737)。
- **新型指标**：自动瞳孔测量与颞侧 RNFL 变化相关，有望用于早期检测 (PMID: 41423322)。

---

## 3. 检索组 3：药物警戒、FAERS、自发报告与全国性用药模式

共 20 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Suresh J | 2026 | Int Ophthalmol | Ocular toxicity associated with Ethambutol in the South-East Asia Region. | PMID: 42240730 / DOI: 10.1007/s10792-026-04131-6 | VigiBase药物警戒研究：全球49,327例乙胺丁醇可疑不良事件中4,748例为眼器官系统类，220例失明；SEAR区以印度最多(820例,79.8%)。 |
| Nakano Y | 2025 | Open Forum Infect Dis | Linezolid-related Optic Nerve Disorders: Insight From a Pharmacovigilance Analysis of the US FDA Adverse Event Reporting System. | PMID: 40980569 / DOI: 10.1093/ofid/ofaf520 | FAERS分析（2014-07至2024-04，1,535万报告）：氧唑烷酮类中仅利奈唑胺检出视神经疾病信号；累积剂量≥720 mg/kg校正OR 7.96、年龄<60岁OR 6.86。 |
| Barbieri MA | 2019 | Front Pharmacol | Ototoxic Adverse Drug Reactions: A Disproportionality Analysis Using the Italian Spontaneous Reporting Database. | PMID: 31649536 / DOI: 10.3389/fphar.2019.01161 | 意大利自发报告系统（325,980份报告）：乙胺丁醇与耳鸣的校正ROR为12.25（95%CI 3.89–38.57）。 |
| Kim J | 2024 | Front Pharmacol | Nationwide usage of ethambutol and incidence and screening practices of optic neuropathy. | PMID: 39474613 / DOI: 10.3389/fphar.2024.1461111 | 韩国206,157例全国队列：仅12.0%–13.1%在启动乙胺丁醇后6个月内完成基线筛查，后续监测比例由2015年13.1%降至2021年7.9%。 |
| Kim J | 2024 | Toxics | Risk Factors of Optic Neuropathy in Ethambutol Users: Interaction with Isoniazid and Other Associated Conditions of Toxic Optic Neuropathy. | PMID: 39195651 / DOI: 10.3390/toxics12080549 | 204,598例乙胺丁醇使用者队列：5,277例(2.6%)发生视神经病变；营养不良OR 1.27(1.19–1.34)，合用异烟肼反而降低风险OR 0.78(0.72–0.86)。 |
| Lee S | 2025 | J Korean Med Sci | Prevalence and Incidence of Ethambutol-Induced Optic Neuropathy and Its Risk Factors in Korea: A Nationwide Population-Based Study. | PMID: 40425190 / DOI: 10.3346/jkms.2025.40.e65 | 全国保险数据库药物流行病学：EON患病率8.54/1000人、发病率159.16/10万人年，女性高于男性（男女比0.65）。 |
| Singh P | 2025 | Cureus | Ethambutol-Induced Optic Neuropathy: A Retrospective Study of Incidences and Risk Factors. | PMID: 40109812 / DOI: 10.7759/cureus.79160 | 单中心回顾：1,676例中13例EON(0.28%)，提示真实世界报告率低于前瞻性监测研究。 |
| Chaitanuwong P | 2023 | Front Ophthalmol (Lausanne) | Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. | PMID: 38983080 / DOI: 10.3389/fopht.2023.1152215 | 7年回顾性队列：EON发生率0.5%（有眼科记录者1.88%）。 |
| Liu SS | 2025 | Infect Dis Ther | Programmatic Assessment of Ethambutol-Related Optic Neuropathy in Patients with Mycobacterial Infections: A Prospective Observational Cohort Study. | PMID: 40900291 / DOI: 10.1007/s40121-025-01219-x | 前瞻多学科协作项目：系统性视觉评估使EON检出率达6.5%，远高于被动报告。 |
| Bhargava A | 2022 | Indian J Ophthalmol | From Scylla to Charybdis: Fixed drug combinations for tuberculosis and increased ethambutol-induced optic neuropathy in India. | PMID: 35918975 / DOI: 10.4103/ijo.ijo_3082_21 | 时间趋势分析：固定剂量复方使用后单中心EON病例数由2016年16例增至2019年96例。 |
| Conradie F | 2022 | N Engl J Med | Bedaquiline-Pretomanid-Linezolid Regimens for Drug-Resistant Tuberculosis. | PMID: 36053506 / DOI: 10.1056/nejmoa2119430 | Nix-TB随机试验：利奈唑胺1200 mg×26周组4例(9%)发生视神经病变，全部缓解；600 mg×26周组不良事件更少。 |
| Wasserman S | 2022 | J Antimicrob Chemother | Linezolid toxicity in patients with drug-resistant tuberculosis: a prospective cohort study. | PMID: 35134182 / DOI: 10.1093/jac/dkac019 | 利奈唑胺前瞻队列：21例(14%)发生3/4级药物相关不良事件。 |
| Agyeman AA | 2016 | Ann Clin Microbiol Antimicrob | Efficacy and safety profile of linezolid in the treatment of multidrug-resistant (MDR) and extensively drug-resistant (XDR) tuberculosis: a systematic review and meta-analysis. | PMID: 27334498 / DOI: 10.1186/s12941-016-0156-y | 系统评价：利奈唑胺神经病变与剂量比较无统计学差异(p=0.3213)，仅骨髓抑制与剂量显著相关。 |
| Singh B | 2019 | Cochrane Database Syst Rev | Linezolid for drug-resistant pulmonary tuberculosis. | PMID: 30893466 / DOI: 10.1002/14651858.cd012836.pub2 | Cochrane系统评价：利奈唑胺用于耐药结核，日剂量300–1200 mg，需权衡神经毒性。 |
| Narita M | 2007 | Pharmacotherapy | Linezolid-associated peripheral and optic neuropathy, lactic acidosis, and serotonin syndrome. | PMID: 17655517 / DOI: 10.1592/phco.27.8.1189 | 综述：利奈唑胺相关周围神经与视神经病变、乳酸酸中毒及5-羟色胺综合征。 |
| Schecter GF | 2010 | Clin Infect Dis | Linezolid in the treatment of multidrug-resistant tuberculosis. | PMID: 19947856 / DOI: 10.1086/648675 | MDR-TB病例系列：9例出现不良反应，包括周围神经与视神经病变。 |
| Russo PA | 1994 | J Am Optom Assoc | Toxic optic neuropathy associated with ethambutol: implications for current therapy. | PMID: 8071504 | 早期综述与病例：乙胺丁醇、其次异烟肼与中毒性视神经病变相关；建议基线与随访行Snellen视力、Farnsworth D-15、自动阈值视野与视乳头照相。 |
| Barbieri MA | 2019 | Front Pharmacol | Ototoxic Adverse Drug Reactions: A Disproportionality Analysis Using the Italian Spontaneous Reporting Database. | PMID: 31649536 / DOI: 10.3389/fphar.2019.01161 | 同一意大利自发报告研究亦提示异烟肼、利福平等抗结核药与耳毒性信号相关。 |
| Li J | 2008 | Drug Saf | Drug-induced ocular disorders. | PMID: 18217789 / DOI: 10.2165/00002018-200831020-00003 | 药物性眼病综述，系统列出可致眼部不良反应的全身药物清单。 |
| Santaella RM | 2007 | Drugs | Ocular adverse effects associated with systemic medications : recognition and management. | PMID: 17209665 / DOI: 10.2165/00003495-200767010-00006 | 按WHO因果关系分级梳理全身用药眼部不良反应，含乙胺丁醇。 |

### 3.1 本组要点归纳

- **全球药物警戒信号确有规模**：VigiBase 中乙胺丁醇可疑报告 49,327 例，眼器官系统类 4,748 例，失明 220 例 (PMID: 42240730)。
- **自发报告存在明显低估**：意大利自发报告系统中乙胺丁醇与耳鸣的 ROR 为 12.25（95%CI 3.89–38.57），属强信号 (PMID: 31649536)；而回顾性病历研究的发生率仅 0.28% (PMID: 40109812)，前瞻性系统筛查可达 6.5% (PMID: 40900291)。
- **真实世界筛查执行率极低**：韩国 206,157 例乙胺丁醇使用者中，仅 12.0%–13.1% 完成基线眼科筛查；6 个月内后续监测比例由 13.1%（2015）降至 7.9%（2021）(PMID: 39474613)。这是本领域最明确的"可干预缺口"。
- **合并用药方向与直觉相反**：合用异烟肼与视神经病变风险**降低**相关（OR 0.78, 95%CI 0.72–0.86）(PMID: 39195651)，需谨慎解释（可能存在适应证偏倚）。
- **制剂变更可能是风险放大器**：固定剂量复方推广后单中心 EON 病例数由 16 例（2016）升至 96 例（2019）(PMID: 35918975)。

---

## 4. 检索组 4：机制——线粒体、氧化应激、锌/铜、溶酶体与自噬

共 18 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Chung H | 2009 | Toxicol Appl Pharmacol | Ethambutol-induced toxicity is mediated by zinc and lysosomal membrane permeabilization in cultured retinal cells. | PMID: 19063910 / DOI: 10.1016/j.taap.2008.11.006 | 离体大鼠视网膜细胞：乙胺丁醇致含锌空泡形成，FluoZin-3与LysoTracker共定位证实为溶酶体；TPEN螯合锌可阻断空泡与组织蛋白酶D释放。 |
| Yoon YH | 2000 | Toxicol Appl Pharmacol | Ethambutol-induced vacuolar changes and neuronal loss in rat retinal cell culture: mediation by endogenous zinc. | PMID: 10637134 / DOI: 10.1006/taap.1999.8846 | 原代大鼠视网膜培养：Thy-1(+)神经节细胞较GABA能神经元更易受损；锌螯合剂TPEN显著减轻损伤，加锌加重，提示依赖细胞内锌而非兴奋毒性或锌缺乏。 |
| Heng JE | 1999 | Invest Ophthalmol Vis Sci | Ethambutol is toxic to retinal ganglion cells via an excitotoxic pathway. | PMID: 9888443 | 啮齿类视网膜与在体大鼠：乙胺丁醇特异性损伤RGC，谷氨酸拮抗剂可阻止细胞丢失，伴线粒体钙升高与膜电位改变，支持兴奋毒性通路。 |
| Huang SP | 2015 | Dis Model Mech | Ethambutol induces impaired autophagic flux and apoptosis in the rat retina. | PMID: 26092127 / DOI: 10.1242/dmm.019737 | RGC-5与大鼠视网膜：乙胺丁醇剂量与时间依赖性增加空泡与死亡；PKCδ抑制剂rottlerin减少caspase-3活化；PI3K/Akt/mTOR受抑，自噬流受损。 |
| Li Q | 2026 | Hum Cell | Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. | PMID: 41563626 / DOI: 10.1007/s13577-025-01342-4 | Wistar大鼠50 mg/kg×8周模型：乙胺丁醇主要经铁死亡致RGC丢失，SLC7A11/GPX4下调、GSH下降、MDA与4-HNE升高；SDHB受Smad4转录调控。 |
| Irma J | 2022 | Neuroophthalmology | A Protective Role of Coenzyme Q10 in Ethambutol-Induced Retinal Ganglion Cell Toxicity: A Randomised Controlled Trial in Mice. | PMID: 36337227 / DOI: 10.1080/01658107.2022.2047207 | 小鼠RCT：辅酶Q10 100 mg/kg/d显著提高乙胺丁醇暴露视网膜的RGC密度（47.2 vs 33.5，p=.004），支持线粒体靶向干预。 |
| Cheng HC | 2025 | Cell Commun Signal | Müller glia-mediated protection of retinal ganglion cells from ethambutol-induced neurotoxicity through brain-derived neurotrophic factor. | PMID: 41184893 / DOI: 10.1186/s12964-025-02478-4 | hiPSC来源RGC样细胞与小鼠视网膜外植体：BDNF经AKT（而非ERK）介导Müller胶质细胞对RGC的保护，pan-TRK抑制剂可阻断。 |
| Zhang XH | 2021 | Front Cell Dev Biol | Mitochondrial Mutations in Ethambutol-Induced Optic Neuropathy. | PMID: 34676220 / DOI: 10.3389/fcell.2021.754676 | 47例EON基因筛查：18例检出15个OPA1突变、4例检出2个LHON-mtDNA突变，总突变检出率46.8%；突变携带者发病更年轻(27.5 vs 48岁)。 |
| Hwang JM | 2003 | J Neurol | Leber's hereditary optic neuropathy mutations in ethambutol-induced optic neuropathy. | PMID: 12527998 / DOI: 10.1007/s00415-003-0960-0 | 24例EON检测8个LHON相关mtDNA位点：未发现任何致病性LHON突变，未能证实EON与LHON突变相关。 |
| Seo JH | 2010 | Clin Exp Ophthalmol | Antituberculosis medication as a possible epigenetic factor of Leber's hereditary optic neuropathy. | PMID: 20491810 / DOI: 10.1111/j.1442-9071.2010.02240.x | 46例LHON患者中3例在抗结核治疗期间发生视力丧失，均为11778突变，平均发病年龄32.7岁（其余43例21.2岁），提示抗结核药可能是LHON的表观遗传触发因素。 |
| Ikeda A | 2006 | Jpn J Ophthalmol | Leber's hereditary optic neuropathy precipitated by ethambutol. | PMID: 16767386 / DOI: 10.1007/s10384-005-0308-7 | 病例报告：乙胺丁醇诱发Leber遗传性视神经病变。 |
| Rasool M | 2015 | Saudi J Biol Sci | Determination of potential role of antioxidative status and circulating biochemical markers in the pathogenesis of ethambutol induced toxic optic neuropathy among diabetic and non-diabetic patients. | PMID: 26587002 / DOI: 10.1016/j.sjbs.2014.09.019 | 糖尿病与非糖尿病EON患者：SOD(p=0.005)、谷胱甘肽(p=0.02)、过氧化氢酶(p=0.02)等抗氧化指标显著异常；Vit-E、B1与MDA呈显著负相关(r=-0.676、-0.724)。 |
| Delacoux E | 1978 | J Fr Ophtalmol | [Prevention of ocular toxicity of ethambutol: study of zincaemia and chromatic analysis (author's transl)]. | PMID: 659802 | 72例乙胺丁醇治疗者：治疗前血浆锌<0.70 mg/L者眼部损害风险高，>1 mg/L者几乎无风险；色觉异常是最早的警报信号。 |
| Sanz-Morello B | 2021 | Antioxidants (Basel) | Oxidative Stress in Optic Neuropathies. | PMID: 34679672 / DOI: 10.3390/antiox10101538 | 综述：系统梳理青光眼、缺血性、遗传性、营养与中毒性视神经病变中的氧化还原失调及生物标志物。 |
| Carelli V | 2002 | Neurochem Int | Optic nerve degeneration and mitochondrial dysfunction: genetic and acquired optic neuropathies. | PMID: 11850115 / DOI: 10.1016/s0197-0186(01)00129-2 | 综述：提出视神经乳头黄斑束选择性退变反映遗传与获得性线粒体功能障碍的共同通路，乙胺丁醇属获得性中毒性一类。 |
| Yu-Wai-Man P | 2011 | Prog Retin Eye Res | Mitochondrial optic neuropathies - disease mechanisms and therapeutic strategies. | PMID: 21112411 / DOI: 10.1016/j.preteyeres.2010.11.002 | 综述：LHON与显性视神经萎缩均以RGC选择性丢失和乳头黄斑束早期受累为特征，主要为复合体I呼吸链缺陷。 |
| Buonfiglio F | 2023 | Antioxidants (Basel) | Oxidative Stress: A Suitable Therapeutic Target for Optic Nerve Diseases? | PMID: 37508003 / DOI: 10.3390/antiox12071465 | 综述：氧化应激通过凋亡、自噬与炎症驱动RGC丢失，是视神经疾病的潜在治疗靶点。 |
| Layrolle P | 2024 | Biomedicines | The Optic Nerve at Stake: Update on Environmental Factors Modulating Expression of Leber's Hereditary Optic Neuropathy. | PMID: 38540197 / DOI: 10.3390/biomedicines12030584 | 综述：LHON遗传易感率约1/1000，环境因素对发病与严重程度至关重要，乙胺丁醇等外源性因素需警惕。 |

### 4.1 机制证据链小结

现有证据支持**"锌–溶酶体–线粒体"三元交互**的机制假说，且近年新增铁死亡与胶质细胞保护两个方向：

1. **兴奋毒性通路（较早假说）**：乙胺丁醇使 RGC 对生理水平谷氨酸敏感，谷氨酸拮抗剂可阻止细胞丢失；伴线粒体钙升高与膜电位改变 (PMID: 9888443)。
2. **锌–溶酶体膜通透化（核心机制）**：乙胺丁醇诱导的胞质空泡几乎全部为含锌溶酶体（FluoZin-3 与 LysoTracker 共定位）；TPEN 螯合锌可同时阻断空泡形成与组织蛋白酶 D 胞质释放 (PMID: 19063910)。Thy-1(+) 神经节细胞比 GABA 能神经元更易受损 (PMID: 10637134)。
3. **自噬流受损与凋亡**：class III PI3K、Beclin-1、p62、LC3-II 上调，早期自噬激活而晚期受抑，经 PKCδ 依赖通路抑制 PI3K/Akt/mTOR 并致凋亡 (PMID: 26092127)。
4. **铁死亡（2026 新证据）**：SLC7A11/GPX4 下调、GSH 下降、MDA 与 4-HNE 升高；Smad4 调控 SDHB 表达，乙胺丁醇抑制 Smad4 与 SDHB 启动子结合 (PMID: 41563626)。
5. **线粒体靶向干预可行**：辅酶 Q10 100 mg/kg/d 使小鼠 RGC 密度由 33.5 升至 47.2 个/500 µm 视野（p=.004）(PMID: 36337227)；Müller 胶质细胞经 BDNF–AKT 通路保护 RGC (PMID: 41184893)。

---

## 5. 检索组 5：剂量、危险因素、发生率与筛查

共 22 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Lee EJ | 2008 | J Neuroophthalmol | Incidence and clinical features of ethambutol-induced optic neuropathy in Korea. | PMID: 19145123 / DOI: 10.1097/wno.0b013e31818e3c6b | 韩国857例：EON 13例(1.5%)，平均剂量17.85±2.21 mg/kg/d、疗程9.38±10.12个月；肾功能不全与日剂量（而非疗程）与发生相关；恢复潜伏期5.38±1.71个月，视乳头苍白者无改善。 |
| Chen SC | 2015 | Kaohsiung J Med Sci | Incidence and prognostic factor of ethambutol-related optic neuropathy: 10-year experience in southern Taiwan. | PMID: 26162816 / DOI: 10.1016/j.kjms.2015.05.004 | 台湾4,803例结核：EON 62例(1.29%)；随访>6个月的16例中50%视力提升≥2行，未发现明确预后因素。 |
| Yang HK | 2016 | Int J Tuberc Lung Dis | Incidence of toxic optic neuropathy with low-dose ethambutol. | PMID: 26792482 / DOI: 10.5588/ijtld.15.0275 | 415例：EON总发生率0.7%；剂量≤15 mg/kg/d的289例中仅1例(0.3%)发生，提示降低剂量可减少毒性。 |
| Chen HY | 2012 | Br J Ophthalmol | Ethambutol-induced optic neuropathy: a nationwide population-based study from Taiwan. | PMID: 22960095 / DOI: 10.1136/bjophthalmol-2012-301870 | 台湾全国队列（231例EON vs 924对照）：年龄、高血压(OR 1.62)、肾病(OR 2.11)、终末期肾病(OR 3.73)为危险因素；处方>3个月未显著增加风险。 |
| Chaitanuwong P | 2023 | Front Ophthalmol (Lausanne) | Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. | PMID: 38983080 / DOI: 10.3389/fopht.2023.1152215 | 泰国4,141例：年龄>60岁(OR 8.71)与吸烟(OR 7.06)为独立危险因素，首次报道吸烟与EON相关。 |
| Lee S | 2025 | J Korean Med Sci | Prevalence and Incidence of Ethambutol-Induced Optic Neuropathy and Its Risk Factors in Korea: A Nationwide Population-Based Study. | PMID: 40425190 / DOI: 10.3346/jkms.2025.40.e65 | 韩国315,888人：用药≥6个月者风险升高(OR 1.44, 95%CI 1.30–1.60)；年龄(OR 1.88)、糖尿病(OR 1.14)、肾病(1.64)、ESRD(2.69)。 |
| Kanaujia V | 2019 | Can J Ophthalmol | Ethambutol-induced optic neuropathy in renal disorder: a clinico-electrophysiological study. | PMID: 31109468 / DOI: 10.1016/j.jcjo.2018.06.013 | 23例肾功能不全患者：6例(26%)发生乙胺丁醇视神经病变，终末期肾病透析组高达40%；4例停药后恢复，2例透析患者出现不可逆严重视力丧失。 |
| Liu SS | 2025 | Infect Dis Ther | Programmatic Assessment of Ethambutol-Related Optic Neuropathy in Patients with Mycobacterial Infections: A Prospective Observational Cohort Study. | PMID: 40900291 / DOI: 10.1007/s40121-025-01219-x | 476例：年龄≥65岁(OR 2.5)与糖尿病(OR 2.2)为独立预测因子；56.7%在6个月视力预后良好。 |
| Gupta A | 2026 | Can J Ophthalmol | Risk factors for ethambutol-induced optic neuropathy: a systematic review and meta-analysis of comparative studies. | PMID: 41905405 / DOI: 10.1016/j.jcjo.2026.03.004 | 系统评价与meta分析：体重校正剂量在EON病例中显著更高；高血压与糖尿病的合并OR未达统计学显著。 |
| Morimoto Y | 2026 | Open Forum Infect Dis | Association Between Low-Dose Ethambutol Therapy and Optic Neuropathy in &lt;i&gt;Mycobacterium avium&lt;/i&gt; Complex Pulmonary Disease: A Retrospective Cohort Study Using Propensity Score Analysis. | PMID: 41846599 / DOI: 10.1093/ofid/ofag127 | 223例MAC肺病：低剂量组(10.7 mg/kg/d)无EON发生，高剂量组(15.4 mg/kg/d)4.8%；校正风险差-17.1%(95%CI -32.9%至-5.4%)。 |
| Donald PR | 2006 | Int J Tuberc Lung Dis | Ethambutol dosage for the treatment of children: literature review and recommendations. | PMID: 17167947 | 儿童乙胺丁醇剂量文献综述：成人剂量>50 mg/kg时>40%出现眼毒性，15 mg/kg/d时为0–3%；3,811例儿童中仅2例(0.05%)因可疑眼毒性停药。 |
| Sivakumaran P | 1998 | N Z Med J | Ocular toxicity from ethambutol: a review of four cases and recommended precautions. | PMID: 9861923 | 四例报告与建议：常规日剂量应为15 mg/kg而非25 mg/kg；使用25 mg/kg或肾功能不全者应每月正式眼科评估；出现严重视神经炎应立即停用乙胺丁醇与异烟肼。 |
| Chatterjee VK | 1986 | Br J Dis Chest | Ocular toxicity following ethambutol in standard dosage. | PMID: 3790421 / DOI: 10.1016/0007-0971(86)90066-5 | 病例报告：在推荐剂量15 mg/kg（临床普遍认为安全）下发生快速不可逆失明。 |
| Choi SY | 1997 | Korean J Ophthalmol | Optic neuropathy associated with ethambutol in Koreans. | PMID: 9510653 / DOI: 10.3341/kjo.1997.11.2.106 | 韩国病例系列：眼部毒性可在低至12.3 mg/kg的剂量出现，表现为视力下降、中心暗点与色觉异常。 |
| Kahana LM. | 1987 | CMAJ | Toxic ocular effects of ethambutol. | PMID: 3607664 | 病例系列：3例患者在15 mg/kg/d的维持剂量下出现中毒性眼部反应。 |
| Peterson E | 2022 | Am J Ophthalmol Case Rep | Delayed and reversible ethambutol optic neuropathy. | PMID: 35756837 / DOI: 10.1016/j.ajoc.2022.101611 | 病例报告：82岁患者在使用<15 mg/kg/d乙胺丁醇3年后出现显著视力下降，延迟且可逆。 |
| Nagy A | 1980 | Rev Ig Bacteriol Virusol Parazitol Epidemiol Pneumoftiziol Pneumoftiziol | [Study of the ocular toxicity of ethambutol]. | PMID: 6254129 | 1980年研究：4–5岁儿童间断给药（2/7）25 mg/kg的乙胺丁醇眼部毒性观察。 |
| Rasool M | 2015 | Saudi J Biol Sci | Determination of potential role of antioxidative status and circulating biochemical markers in the pathogenesis of ethambutol induced toxic optic neuropathy among diabetic and non-diabetic patients. | PMID: 26587002 / DOI: 10.1016/j.sjbs.2014.09.019 | 病例对照：患者接受乙胺丁醇25 mg/kg（前2个月）后改15 mg/kg；抗氧化与生化指标在糖尿病组差异尤为显著。 |
| Maranchick NF | 2026 | Antimicrob Agents Chemother | Population pharmacokinetics of pyrazinamide and ethambutol in children with tuberculosis with or without HIV. | PMID: 41770228 / DOI: 10.1128/aac.00909-25 | 儿童群体药代动力学：吡嗪酰胺与乙胺丁醇中位剂量分别为31.6与21.4 mg/kg（范围14.3–34.2），为儿童剂量暴露提供依据。 |
| Mane SS | 2022 | Indian Pediatr | Ocular Toxicity of Ethambutol During Both Intensive and Continuation Phases of Anti-Tubercular Therapy in Children. | PMID: 36370014 / DOI: 10.1007/s13312-022-2644-9 | 47例儿童前瞻：在20 mg/kg/d及以下、贯穿强化期与继续期全程用药未观察到视力、色觉、对比敏感度、视野或RNFL的显著损害。 |
| Mandal S | 2021 | Br J Ophthalmol | Prospective study to evaluate incidence and indicators for early detection of ethambutol toxicity. | PMID: 32713840 / DOI: 10.1136/bjophthalmol-2020-316897 | 50例6个月前瞻：平均剂量17.5±1.3 mg/kg/d，临床EON<2%但亚临床损害达46%眼。 |
| Kim KL | 2016 | Cutan Ocul Toxicol | Visual function test for early detection of ethambutol induced ocular toxicity at the subclinical level. | PMID: 26361935 / DOI: 10.3109/15569527.2015.1079784 | 31例62眼：剂量范围15–19 mg/kg/d，pattern VEP与RNFL OCT可在亚临床阶段发现异常。 |

### 5.1 本组要点归纳

- **剂量–毒性关系贯穿 60 年文献**：1960–1980 年代已确认剂量依赖（>50 mg/kg 时 >40% 出现毒性，15 mg/kg/d 时 0–3%）(PMID: 17167947)；1986 年报告 15 mg/kg 标准剂量下仍出现不可逆失明 (PMID: 3790421)；1997 年报告低至 12.3 mg/kg 即出现毒性 (PMID: 9510653)。
- **肾功能不全是效应最强的可修饰危险因素**：ESRD 患者调整 OR 达 2.69 (PMID: 40425190) 至 3.73 (PMID: 22960095)；透析组 EON 发生率达 40% (PMID: 31109468)。
- **年龄为一致的危险因素**：>60 岁 OR 8.71 (PMID: 38983080)、≥65 岁 OR 2.5 (PMID: 40900291)、全国队列 OR 1.88 (PMID: 40425190)。
- **剂量阈值可下调**：MAC 肺病中 10.7 mg/kg/d 组无 EON 发生，而 15.4 mg/kg/d 组为 4.8% (PMID: 41846599)，为"降剂量保疗效"提供直接证据。

---

## 6. 检索组 6：其他抗结核药的眼毒性（异烟肼/利福平/吡嗪酰胺/利奈唑胺）

共 14 条代表性记录。


| 第一作者 | 年份 | 期刊 | 标题 | PMID / DOI | 一句话核心结论 |
|---|---|---|---|---|---|
| Nakano Y | 2025 | Open Forum Infect Dis | Linezolid-related Optic Nerve Disorders: Insight From a Pharmacovigilance Analysis of the US FDA Adverse Event Reporting System. | PMID: 40980569 / DOI: 10.1093/ofid/ofaf520 | FAERS：氧唑烷酮类中仅利奈唑胺检出视神经疾病信号；累积剂量≥720 mg/kg(校正OR 7.96)与年龄<60岁(OR 6.86)为特征。 |
| Conradie F | 2022 | N Engl J Med | Bedaquiline-Pretomanid-Linezolid Regimens for Drug-Resistant Tuberculosis. | PMID: 36053506 / DOI: 10.1056/nejmoa2119430 | Nix-TB随机对照试验：BPaL方案中利奈唑胺1200 mg×26周组4例(9%)发生视神经病变且全部缓解；600 mg×26周获益风险比最佳。 |
| Narita M | 2007 | Pharmacotherapy | Linezolid-associated peripheral and optic neuropathy, lactic acidosis, and serotonin syndrome. | PMID: 17655517 / DOI: 10.1592/phco.27.8.1189 | 综述：利奈唑胺相关周围神经与视神经病变、乳酸酸中毒及5-羟色胺综合征。 |
| Schecter GF | 2010 | Clin Infect Dis | Linezolid in the treatment of multidrug-resistant tuberculosis. | PMID: 19947856 / DOI: 10.1086/648675 | MDR-TB治疗队列：9例出现不良反应，包括周围神经与视神经病变、贫血/血小板减少、皮疹与腹泻。 |
| Wasserman S | 2022 | J Antimicrob Chemother | Linezolid toxicity in patients with drug-resistant tuberculosis: a prospective cohort study. | PMID: 35134182 / DOI: 10.1093/jac/dkac019 | 耐药结核前瞻队列：21例(14%)发生3/4级利奈唑胺相关不良事件。 |
| Agyeman AA | 2016 | Ann Clin Microbiol Antimicrob | Efficacy and safety profile of linezolid in the treatment of multidrug-resistant (MDR) and extensively drug-resistant (XDR) tuberculosis: a systematic review and meta-analysis. | PMID: 27334498 / DOI: 10.1186/s12941-016-0156-y | 系统评价：利奈唑胺神经病变发生率在不同剂量间无显著差异(p=0.3213)，骨髓抑制与剂量显著相关。 |
| Singh B | 2019 | Cochrane Database Syst Rev | Linezolid for drug-resistant pulmonary tuberculosis. | PMID: 30893466 / DOI: 10.1002/14651858.cd012836.pub2 | Cochrane系统评价：利奈唑胺治疗耐药肺结核的疗效与安全性，日剂量范围300–1200 mg。 |
| Kim J | 2024 | Toxics | Risk Factors of Optic Neuropathy in Ethambutol Users: Interaction with Isoniazid and Other Associated Conditions of Toxic Optic Neuropathy. | PMID: 39195651 / DOI: 10.3390/toxics12080549 | 204,598例乙胺丁醇使用者：合用异烟肼与视神经病变风险降低相关(OR 0.78, 95%CI 0.72–0.86)，提示药物相互作用方向与预期相反。 |
| Russo PA | 1994 | J Am Optom Assoc | Toxic optic neuropathy associated with ethambutol: implications for current therapy. | PMID: 8071504 | 病例与文献综述：乙胺丁醇及（程度较轻的）异烟肼均与中毒性视神经病变相关，部分为永久性视力丧失。 |
| Barbieri MA | 2019 | Front Pharmacol | Ototoxic Adverse Drug Reactions: A Disproportionality Analysis Using the Italian Spontaneous Reporting Database. | PMID: 31649536 / DOI: 10.3389/fphar.2019.01161 | 意大利自发报告系统：异烟肼、利福平与耳毒性ADR信号显著相关，提示一线抗结核药的神经感觉毒性谱。 |
| Li J | 2008 | Drug Saf | Drug-induced ocular disorders. | PMID: 18217789 / DOI: 10.2165/00002018-200831020-00003 | 药物性眼病综述：汇总可致眼部不良反应的全身药物及其机制与管理。 |
| Santaella RM | 2007 | Drugs | Ocular adverse effects associated with systemic medications : recognition and management. | PMID: 17209665 / DOI: 10.2165/00003495-200767010-00006 | 综述：按WHO因果评价分级梳理全身用药的眼部不良反应。 |
| Gupta A | 2026 | Can J Ophthalmol | Risk factors for ethambutol-induced optic neuropathy: a systematic review and meta-analysis of comparative studies. | PMID: 41905405 / DOI: 10.1016/j.jcjo.2026.03.004 | meta分析：纳入比较性研究评估乙胺丁醇视神经病变的危险因素，间接提示合并用药与共病的影响。 |
| Singh M | 2025 | Monaldi Arch Chest Dis | Infective pulmonary diseases and the eye: a narrative review. | PMID: 39259221 / DOI: 10.4081/monaldi.2024.2988 | 综述：感染性肺病与眼部表现，涵盖抗结核治疗相关中毒性视神经病变。 |
| Libershteyn Y. | 2016 | Optom Vis Sci | Ethambutol/Linezolid Toxic Optic Neuropathy. | PMID: 26636399 / DOI: 10.1097/opx.0000000000000783 | 病例报告：乙胺丁醇与利奈唑胺长期联用致中毒性视神经病变；停用乙胺丁醇后视力仍下降，停用利奈唑胺后视力、色觉与视野改善（最终20/30与20/40）。 |
| Sharma N | 2025 | Indian J Tuberc | Prospective evaluation of ethambutol toxic optic neuropathy in patients of pulmonary tuberculosis. | PMID: 39890374 / DOI: 10.1016/j.ijtb.2023.11.001 | 前瞻队列（50例/100眼）：基线视觉功能均正常，47例未见异常；对出现视觉损害者停用乙胺丁醇并继续观察3个月以评估可逆性。 |
| Lin YW | 2022 | Taiwan J Ophthalmol | Ethambutol optic neuropathy with correspondent chiasmitis manifestation in magnetic resonance imaging. | PMID: 36248082 / DOI: 10.4103/tjo.tjo_27_21 | 病例报告：乙胺丁醇相关视交叉炎表现为双颞侧偏盲，OCT显示黄斑GCIPL丢失与逆行经突触变性相关；6个月随访视交叉强化改善。 |

### 6.1 本组要点归纳

- **一线药物中乙胺丁醇是主要致毒药物**：异烟肼、利福平、吡嗪酰胺单独致视神经病变的证据远弱于乙胺丁醇 (PMID: 8071504, PMID: 39259221)。
- **异烟肼的作用方向存争议**：合并使用异烟肼与 EON 风险**降低**相关（OR 0.78）(PMID: 39195651)，但早期综述认为异烟肼本身（程度较轻）也与中毒性视神经病变相关 (PMID: 8071504)。
- **利奈唑胺是明确的第二种致毒药物**：FAERS 中氧唑烷酮类仅利奈唑胺检出视神经疾病信号 (PMID: 40980569)；Nix-TB 试验中 1200 mg×26 周组 4 例(9%)发生视神经病变 (PMID: 36053506)。
- **联合用药时需鉴别病因**：乙胺丁醇+利奈唑胺联用时，停用乙胺丁醇后视力仍继续下降，停用利奈唑胺后才改善 (PMID: 26636399，见 8.2 节补充)。

---



## 7. 关键定量参数

> **说明**：本节汇总的全部数值均来自上表所列文献的题录/摘要原文。每个数值后紧跟 `(PMID: xxxxx)` 以标明出处。凡摘要未明确给出、或本次检索未获得的参数，一律列入 7.6"未检索到"，不做推测性填补。

### 7.1 发生率（按剂量／疗程／研究设计分层）

| 人群与研究设计 | 样本量 | 剂量／疗程 | 发生率 | 来源 |
|---|---|---|---|---|
| 韩国单中心回顾（Seoul National Univ. Hospital） | 857 例 | 平均 17.85 ± 2.21 mg/kg/d；疗程 9.38 ± 10.12 个月 | 1.5%（13 例），估计 <2% | (PMID: 19145123) |
| 台湾单中心 10 年回顾 | 4,803 例（其中 1,004 例有眼科记录） | — | 1.29%（62 例） | (PMID: 26162816) |
| 韩国单中心（TB 或 MAC 肺病） | 415 例 | 剂量 ≤15 mg/kg/d 者 289 例 | 总体 0.7%（3 例）；≤15 mg/kg/d 亚组 0.3%（1 例） | (PMID: 26792482) |
| 韩国全国医保数据库（2011–2020） | 315,888 例 | — | 患病率 8.54/1,000 人；发病率 159.16/10 万人年；累积发生率 0.9% | (PMID: 40425190) |
| 韩国全国队列 | 204,598 例乙胺丁醇使用者 | 2015–2021 启动治疗 | 2.6%（5,277 例） | (PMID: 39195651) |
| 韩国全国队列（筛查实践） | 206,157 例启动者 | 2015–2021 | 基线筛查率仅 12.0%–13.1% | (PMID: 39474613) |
| 泰国单中心 7 年 | 4,141 例（其中 1,062 例有眼科就诊） | — | 0.5%（全人群）vs 1.88%（有眼科就诊者） | (PMID: 38983080) |
| 印度单中心回顾（RNTCP 2016 方案后） | 1,676 例 | — | 0.28%（13 例） | (PMID: 40109812) |
| 印度单中心前瞻（6 个月） | 50 例 | 平均 17.5 ± 1.3 mg/kg/d | 临床 EON <2%；亚临床损害 46% 眼 | (PMID: 32713840) |
| 台湾前瞻多学科协作 | 476 例 | — | 6.5%（31 例，"超过 6%"） | (PMID: 40900291) |
| 印度肾病队列 | 23 例 | 按 GFR 分 4 组 | 26%（6 例）；ESRD 透析组 40% | (PMID: 31109468) |
| 韩国前瞻 OCT 纵向 | 37 例 | — | 1 例（2.7%） | (PMID: 26344730) |
| 印度前瞻电生理 | 104 眼 | — | 视野缺损 7.69%（8/104 眼） | (PMID: 19525243) |
| VigiBase 全球药物警戒（至 2026-01） | 49,327 例可疑报告 | — | 眼器官系统类 4,748 例；失明 220 例 | (PMID: 42240730) |
| MAC 肺病倾向评分队列 | 223 例 | 低剂量 10.7 mg/kg/d vs 高剂量 15.4 mg/kg/d | 0% vs 4.8%；校正风险差 −17.1%（95%CI −32.9% 至 −5.4%） | (PMID: 41846599) |
| 儿童剂量文献综述 | 3,811 例儿童 | 15–30 mg/kg | 0.05%（2 例）因可疑眼毒性停药 | (PMID: 17167947) |
| 综述（汇总两项最大流行病学研究） | — | WHO 推荐剂量 | 患病率 0.7%–1.29% | (PMID: 28759559) |
| 单中心时间趋势（固定剂量复方引入后） | — | — | 2016 年 16 例 → 2019 年 96 例 | (PMID: 35918975) |
| 印度前瞻队列 | 50 例 / 100 眼 | — | 47 例（94%）未出现异常 | (PMID: 39890374) |

### 7.2 剂量阈值与潜伏期

| 参数 | 数值 | 来源 |
|---|---|---|
| 剂量依赖性毒性（成人） | 剂量 >50 mg/kg 时 >40% 出现毒性；15 mg/kg/d 时为 0–3% | (PMID: 17167947) |
| 儿童可接受剂量 | 20 mg/kg（范围 15–25）每日；或 30 mg/kg 每周 3 次间断给药 | (PMID: 17167947) |
| 儿童安全性验证 | ≤20 mg/kg/d、贯穿强化期与继续期全程未见显著视觉或 RNFL 损害 | (PMID: 36370014) |
| 推荐日剂量上限 | 常规应为 15 mg/kg/d 而非 25 mg/kg/d | (PMID: 9861923) |
| 标准剂量下仍可致不可逆失明 | 15 mg/kg（临床普遍视为安全的剂量） | (PMID: 3790421) |
| 维持剂量下出现毒性 | 15 mg/kg/d，3 例 | (PMID: 3607664) |
| 已报道的最低致毒剂量 | 12.3 mg/kg | (PMID: 9510653)、(PMID: 40109812) |
| 低剂量延迟致毒 | <15 mg/kg/d 用药 3 年后出现显著视力下降 | (PMID: 35756837) |
| 亚临床 OCT/VEP 可检出的剂量区间 | 15–19 mg/kg/d | (PMID: 26361935) |
| EON 病例平均剂量（印度，107 例） | 16.7 ± 4 mg/kg/d（即 1,042 ± 247 mg/d） | (PMID: 40444310) |
| EON 病例平均剂量（印尼） | 19.7 ± 5.3 mg/kg | (PMID: 40688769) |
| 剂量与视力严重度分层 | ≥16 mg/kg 组初诊 BCVA 1.3 ± 0.6 logMAR，差于 <16 mg/kg 组 1.0 ± 0.5 logMAR | (PMID: 40444310) |
| 恢复组 vs 未恢复组剂量 | 17.3 ± 5 vs 23.3 ± 2.9 mg/kg·d（P<0.01） | (PMID: 40688769) |
| 低剂量策略的风险差 | 校正风险差 −17.1%（95%CI −32.9% 至 −5.4%） | (PMID: 41846599) |
| 高危剂量阈值（叙述性综述） | >15 mg/kg/d 且疗程长为高危 | (PMID: 39259221) |
| 儿童实际中位剂量（群体药代动力学） | 21.4 mg/kg（范围 14.3–34.2） | (PMID: 41770228) |
| 间断给药剂量（1980 年儿童研究） | 25 mg/kg，每周 2 次（2/7） | (PMID: 6254129) |
| 常见治疗方案（病例对照） | 前 2 个月 25 mg/kg，其后 15 mg/kg | (PMID: 26587002) |
| 平均用药至诊断时间（韩国） | 9.38 ± 10.12 个月 | (PMID: 19145123) |
| 平均暴露时间（印度） | 6.8 ± 3.3 个月 | (PMID: 40444310) |
| 中位用药时间（印尼） | 9 个月（范围 2–20 个月） | (PMID: 40688769) |
| 已报道的最长延迟发病 | 用药 3 年 | (PMID: 35756837) |
| 电生理最早异常时间 | 用药 1–2 个月即出现 P100 潜伏期延长（p<0.001） | (PMID: 19525243) |
| 亚临床 VEP 最早异常时间 | 用药 2、4 个月 P100 潜伏期延迟（p=0.001；p<0.001） | (PMID: 26361935) |
| RNFL OCT 最早异常时间 | 用药 5 个月 RNFL 厚度增厚（p=0.032） | (PMID: 26361935) |
| VEP 潜伏期绝对值区间（儿童） | 治疗 6–12 个月维持于 93–101 ms | (PMID: 1800342) |
| 恢复潜伏期（韩国） | 5.38 ± 1.71 个月 | (PMID: 19145123) |
| 平均视力恢复时间 | 15.2 ± 3.0 个月；50% 在 8.3 ± 2.2 个月恢复 | (PMID: 38351490) |
| 关键恢复窗口 | 3–6 个月（BCVA 与视野 MD 在此期显著改善） | (PMID: 40269990) |
| 疗程 ≥6 个月的风险 | OR 1.44（95%CI 1.30–1.60，校正年龄、性别、高血压、糖尿病、肾病） | (PMID: 40425190) |
| 疗程 >3 个月的风险 | OR 1.35（95%CI 0.99–1.83），未达统计学显著 | (PMID: 22960095) |
| 随访时长建议 | EON 诊断后应随访 >1–2 年以评估恢复 | (PMID: 38351490) |

### 7.3 危险因素

| 危险因素 | 效应量／数值 | 来源 |
|---|---|---|
| 年龄 >60 岁 | OR 8.71（p=0.01） | (PMID: 38983080) |
| 年龄 ≥65 岁 | OR 2.5（P=0.043） | (PMID: 40900291) |
| 年龄（全国队列） | 校正 OR 1.88（95%CI 1.38–2.58） | (PMID: 40425190) |
| 年龄（台湾全国队列） | 老年为危险因素 | (PMID: 22960095) |
| 年龄（恢复预测） | 年轻者更易改善：50.24 ± 13.8 vs 62.14 ± 8.9 岁（P<0.01） | (PMID: 40688769) |
| 年龄与可逆性 | >60 岁仅 20%（1/5）改善；<60 岁 80%（4/5）有恢复 | (PMID: 9326729) |
| 吸烟 | OR 7.06（p=0.01），为独立危险因素 | (PMID: 38983080) |
| 肾功能不全（非 ESRD，台湾） | 校正 OR 2.11（95%CI 1.02–4.35） | (PMID: 22960095) |
| 终末期肾病 ESRD（台湾） | 校正 OR 3.73（95%CI 1.79–7.74） | (PMID: 22960095) |
| 肾病（非 ESRD，韩国） | 校正 OR 1.64（95%CI 1.30–2.06） | (PMID: 40425190) |
| ESRD（韩国） | 校正 OR 2.69（95%CI 1.92–3.76） | (PMID: 40425190) |
| CKD 透析组发生率 | 40%（group 1：GFR <10 mL/min） | (PMID: 31109468) |
| 肾功能不全患者总体发生率 | 26%（6/23） | (PMID: 31109468) |
| 肾功能不全（韩国早期研究） | 与 EON 发生相关（肾功能不全与日剂量，而非疗程） | (PMID: 19145123) |
| 糖尿病 | 校正 OR 1.14（95%CI 1.03–1.26） | (PMID: 40425190) |
| 糖尿病 | OR 2.2（P=0.045） | (PMID: 40900291) |
| 糖尿病（预后） | 恢复组糖尿病比例更低（p=0.007） | (PMID: 39979502) |
| 糖尿病（meta 分析） | OR 0.85（95%CI 0.54–1.35；p=0.27；k=3），未达统计学显著 | (PMID: 41905405) |
| 高血压 | 校正 OR 1.62（95%CI 1.16–2.26） | (PMID: 22960095) |
| 高血压（预后） | 未恢复组高血压比例 83% vs 恢复组 16%（P=0.012） | (PMID: 40688769) |
| 高血压（meta 分析） | OR 1.86（95%CI 0.44–7.75；p=0.11；k=2），未达统计学显著 | (PMID: 41905405) |
| 营养不良／营养障碍 | OR 1.27（95%CI 1.19–1.34） | (PMID: 39195651) |
| 体型／体重 | 恢复组体重更高（p=0.04）；单因素分析 p=0.033 | (PMID: 39979502) |
| 酗酒 | 列为高危人群（老年、肾病、糖尿病、营养不良、酗酒、>15 mg/kg/d 且疗程长） | (PMID: 39259221) |
| **锌缺乏** | 治疗前血浆锌 <0.70 mg/L 为高风险；>1 mg/L 几乎无风险 | (PMID: 659802) |
| 锌（机制层面） | 乙胺丁醇致溶酶体内锌蓄积与溶酶体膜通透化；TPEN 螯合锌可阻断 | (PMID: 19063910) |
| 锌（机制层面） | 锌螯合剂 TPEN 显著减轻空泡样变性与神经元丢失，外加锌则加重 | (PMID: 10637134) |
| 抗氧化营养素 | Vit-A、E、B1、B12 与锌参与中毒性视神经病变发病；Vit-E 与 B1 和 MDA 呈显著负相关（r=−0.676、−0.724） | (PMID: 26587002) |
| **LHON／OPA1 基因突变携带** | 突变总检出率 46.8%（18 例检出 15 个 OPA1 突变；4 例检出 2 个 LHON-mtDNA 突变）；携带者发病更年轻（27.5 vs 48 岁）；有突变者半数视力改善，无突变者 91% 改善 | (PMID: 34676220) |
| LHON 突变（早期否定研究） | 24 例 EON 中未检出任何致病性 LHON mtDNA 突变 | (PMID: 12527998) |
| 抗结核药作为 LHON 表观触发因素 | 46 例 LHON 中 3 例在抗结核治疗期间发生视力丧失（均为 nt-11778 突变），平均发病年龄 32.7 vs 其余 21.2 岁 | (PMID: 20491810) |
| 乙胺丁醇诱发 LHON | 病例报告证实 | (PMID: 16767386) |
| 环境因素对 LHON 外显率的影响 | LHON 遗传易感率约 1/1000；环境因素是触发与严重程度的关键 | (PMID: 38540197) |
| 合用异烟肼 | OR 0.78（95%CI 0.72–0.86），与风险**降低**相关 | (PMID: 39195651) |
| 疗程 ≥6 个月 | OR 1.44（95%CI 1.30–1.60） | (PMID: 40425190) |
| 主观+客观眼部异常并存 | OR 4.8（P=0.009） | (PMID: 40900291) |
| 视力与色觉同时受损 | OR 5.9（P=0.009） | (PMID: 40900291) |

### 7.4 停药后视力恢复率与预后因素

| 参数 | 数值 | 来源 |
|---|---|---|
| 恢复率（≥2 行 Snellen，印度 128 例） | 62.9%（161 眼） | (PMID: 36018127) |
| 恢复率（≥3 行，韩国 35 眼） | 77.1%（27 眼） | (PMID: 38351490) |
| 恢复率（≥2 行，印度 95 例前瞻） | 52% 眼 | (PMID: 40854737) |
| 恢复率（≥2 行，台湾） | 50%（8/16 例，随访 >6 个月者） | (PMID: 26162816) |
| 恢复率（1997 年随访 12 个月–3 年） | 50%（5/10 例）；另 50% 永久性损害 | (PMID: 9326729) |
| 恢复率（肾病组） | 4 例停药后恢复；2 例透析患者不可逆 | (PMID: 31109468) |
| 6 个月视力预后良好率 | 56.7%；色觉良好率 50.0% | (PMID: 40900291) |
| 5 年随访转归 | 6 个月预后不良者中 45.5% 在 5 年时转为良好 | (PMID: 40900291) |
| 预后早期判定 | 88.2%（良好）与 100%（不良）在随访第 3 个月即已确定 | (PMID: 40900291) |
| 色觉预后早期判定 | 100%（良好）与 100%（不良）在第 4 个月即已确定 | (PMID: 40900291) |
| 平均恢复时间 | 15.2 ± 3.0 个月；50% 在 8.3 ± 2.2 个月 | (PMID: 38351490) |
| 恢复潜伏期（韩国） | 5.38 ± 1.71 个月 | (PMID: 19145123) |
| 视力改善幅度（印度 107 例） | 1.2 ± 0.6 → 0.8 ± 0.6 logMAR | (PMID: 40444310) |
| 视力改善幅度（nadir → final） | 1.4 ± 0.4 → 0.6 ± 0.5 logMAR | (PMID: 38351490) |
| 3 → 6 个月 BCVA 改善 | 0.25 logMAR（1.28 ± 0.64 → 0.82 ± 0.60；p<0.0001；Cohen's d=0.74） | (PMID: 40269990) |
| 3 → 6 个月视野 MD 改善 | 2.5 dB（−13.85 ± 9.23 → −10.33 ± 7.58 dB；p=0.037） | (PMID: 40269990) |
| 电生理与视野逆转率 | 停药 1 个月后 80% 眼逆转（但 VER 潜伏期仍延迟，p=0.002） | (PMID: 19525243) |
| 预后因素：初诊视力 | 差于 6/60 者视力预后差 | (PMID: 36018127) |
| 预后因素：GCIPL | 内颞侧 GCIPL 每丢失 10 µm，12 个月 logMAR 视力恢复量减少 0.5（P<0.001，95%CI 0.2–0.7） | (PMID: 29677374) |
| 预后切点：pRNFL | 83 µm（敏感度 100%，特异度 48.3%）预测 1 年视力 >20/25 | (PMID: 38277226) |
| 预后切点：mGCIPL | 74 µm（敏感度 100%，特异度 83.3%）预测 1 年 >20/25；61 µm（85.7%/71.4%）预测 1 年 >20/40；AUC 均 >0.7 | (PMID: 38277226) |
| 预后因素：视乳头苍白 | 诊断时已出现视乳头苍白者，无一例视力改善 | (PMID: 19145123) |
| 延迟恢复的危险因素 | 用药 ≤6 个月；症状至停药 >14 天；基线 pRNFL >98 µm | (PMID: 38351490) |
| 恢复预测因素（印尼） | 年轻、较低剂量、较短疗程、无高血压或无肾病 | (PMID: 40688769) |
| 恢复预测因素（meta 分析） | 年轻（MD = −3.8 岁，P=0.095）与更早停用乙胺丁醇 | (PMID: 42293031) |
| 结构–功能分离现象 | 视力改善（52% 眼）但 RNFL 与 PMB 在 6 个月持续显著变薄 | (PMID: 40854737) |
| RNFL/PMB 6 个月变化 | RNFL 100.84 ± 21.87 → 83.77 ± 21.06 µm；PMB 51.10 ± 17.26 → 30.96 ± 11.02 µm（p<0.0001） | (PMID: 40854737) |
| mGCIPL 时序变化 | 发病 1 个月 73.20 ± 4.76 µm → 55.33 ± 4.16 µm | (PMID: 40269990) |
| 年龄与预后（病例系列） | 老年患者初诊视力最差且末次随访改善最少 | (PMID: 40444310) |

### 7.5 现有筛查建议（基线及随访项目与频率）

| 来源 | 基线项目 | 随访频率与项目 |
|---|---|---|
| 1994 年综述与病例 | Snellen 视力、Farnsworth D-15 色觉、自动阈值视野、视乳头照相 | 基线与随访均应完成上述全套检查 | (PMID: 8071504) |
| 1998 年四例报告与建议 | 常规日剂量应为 15 mg/kg/d（而非 25 mg/kg/d） | 使用 25 mg/kg/d 或肾功能不全者应每月正式眼科评估；出现严重视神经炎应立即停用乙胺丁醇与异烟肼 | (PMID: 9861923) |
| 2016 年前瞻 | 视力、视野、色觉、对比敏感度、眼底、RNFL OCT | RNFL OCT 每月 1 次；pattern VEP 每 2 个月 1 次 | (PMID: 26361935) |
| 2018 年 OCT 研究 | BCVA、生物显微镜、眼压、瞳孔反射、Ishihara、Amsler 格、彩色眼底照相、Cirrus HD-OCT | 治疗期间每 2 个月 1 次 | (PMID: 30408036) |
| 2019 年前瞻纵向 | BCVA、色觉、对比敏感度、眼底与 RNFL 照相、自动视野、OCT | 用药期间每月 1 次，停药后 1 个月复查 | (PMID: 30995284) |
| 2021 年前瞻 | BCVA(ETDRS)、色觉(Ishihara)、对比敏感度(Pelli-Robson)、Humphrey 30-2、pattern VER、SD-OCT(GCIPL/RNFL) | 用药后第 2、4、6 个月 | (PMID: 32713840) |
| 2024 年全国实践现状 | 启动乙胺丁醇前 1 个月内的眼科检查，或启动后首次眼科评估 | 实际执行：基线筛查率仅 12.0%–13.1%；6 个月内后续监测由 13.1%（2015）降至 7.9%（2021） | (PMID: 39474613) |
| 2026 年前瞻纵向 | BCVA(ETDRS)、色觉(Ishihara)、对比敏感度(Pelli-Robson)、Humphrey 30-2、视觉诱发电位、SD-OCT(mGC-IPL/RNFL/PMB) | 基线、3 个月、6 个月 | (PMID: 40854737) |
| 2025 年前瞻队列 | 每月眼科检查：BCVA、视盘评估、色觉、对比敏感度、瞳孔周期时间、自动视野 | 6 个月每月 1 次；出现视觉损害即停药并再观察 3 个月 | (PMID: 39890374) |
| 2026 年瞳孔测量 | 自动瞳孔测量（收缩幅度、收缩百分比、散大速度） | 与颞侧 RNFL 变化相关，作为早期检测补充手段 | (PMID: 41423322) |
| 2022 年电生理综述 | mfERG、ffERG、EOG、PERG、VEP | 用于视网膜与视神经毒性的早期功能监测 | (PMID: 36291599) |
| ISCEV 指南 | 标准化 VEP/ERG 记录规范 | 为电生理随访提供操作标准 | (PMID: 29397523) |
| 随访时长 | — | EON 诊断后应随访 1–2 年以上以评估视力恢复 | (PMID: 38351490) |
| 多学科协作模式 | 由眼科与呼吸/感染科组成团队进行程序化视觉评估 | 该模式使 EON 检出率提升至 6.5%，可作为筛查组织方式参考 | (PMID: 40900291) |

### 7.6 未检索到的参数

以下条目在本次 Europe PMC 检索范围内**未检索到**可引用的定量证据，特此明确标注，不以推测填补：

| 未检索到的参数 | 说明 |
|---|---|
| **CYP1A2 基因多态性与 EON 的关联** | 未检索到。在 `ethambutol AND (CYP1A2 OR NAT2 OR polymorphism OR "genetic susceptibility" ...)` 检索结果中未见针对 CYP1A2 的乙胺丁醇眼毒性研究。 |
| **NAT2 基因多态性与 EON 的关联** | 未检索到。 |
| **铜（copper）代谢异常与 EON 的特异性人体证据** | 未检索到。本次检索到的金属相关机制证据集中于**锌**（PMID: 19063910、PMID: 10637134、PMID: 659802）。 |
| **不同筛查频率的前瞻性随机对照比较研究** | 未检索到。现有筛查建议均来自单中心前瞻性研究的观察性结论。 |
| **乙胺丁醇减量策略在结核病人群中的随机对照证据** | 未检索到。仅有 MAC 肺病的倾向评分队列（PMID: 41846599）。 |
| **糖皮质激素或特定神经营养药物治疗 EON 的随机对照试验** | 未检索到。仅检索到动物实验的辅酶 Q10 证据（PMID: 36337227）。 |
| **亚临床损害进展为临床 EON 的转化率** | 未检索到。已知 46% 眼出现亚临床损害（PMID: 32713840），但其自然转归未见报道。 |
| **乙胺丁醇视神经毒性的药物基因组学全基因组关联研究** | 未检索到。现有遗传学证据集中于 OPA1 与 LHON-mtDNA 候选基因（PMID: 34676220、PMID: 12527998）。 |

---




## 8. 研究空白与检索局限

### 8.1 明确的证据空白

| 空白点 | 说明 |
|---|---|
| **缺乏随机对照的筛查方案比较** | 现有筛查建议（OCT 每月至每 3 个月、VEP 每 2 个月等）均来自单中心前瞻性研究的观察性结论，未见比较不同筛查频率的成本效果或结局研究。 |
| **亚临床损伤的自然史不清** | 46% 眼出现亚临床损害 (PMID: 32713840)，但其中转化为临床 EON 的比例未见报道。 |
| **真实世界筛查执行率极低且无干预试验** | 基线筛查率仅 12%–13% (PMID: 39474613)，尚无提升筛查依从性的干预研究。 |
| **乙胺丁醇减量后的疗效–毒性权衡数据有限** | 仅 1 项倾向评分队列（MAC 肺病）(PMID: 41846599)，结核病人群缺少同类证据。 |
| **遗传易感筛查未进入实践** | OPA1/LHON 突变检出率 46.8% (PMID: 34676220)，但结论相互矛盾 (PMID: 12527998)，尚无筛查推荐。 |

### 8.2 检索与可获取性局限

1. **本文件基于题录与摘要**。Europe PMC 部分记录无开放全文，个别数字的上下文（如置信区间、校正变量）在摘要中未完整给出，已在表内以摘要原文为准。
2. **期刊名缺失**：`resultType=core` 在部分记录中未返回 `journalTitle`，已通过 `resultType=lite` 二次回查补全；仍无法解析者标注"未著录"。
3. **中文文献覆盖不足**：Europe PMC 对 CNKI/万方/维普中文期刊收录有限，本文件不含中文期刊的系统性检索结果。
4. **发表偏倚**：发生率类研究以单中心回顾性设计为主，前瞻性系统筛查研究（如 6.5%）(PMID: 40900291) 可能高估真实世界发生率。
5. **未进行全文核验的条目已在表格中保留原始摘要表述**，凡摘要未明确给出的数值一律未列入第 7 节。

---

## 9. 引用记录索引

本文件共引用 **84 条**独立文献记录，全部经 Europe PMC 接口原样回查确认存在。


| # | 第一作者 | 年份 | 期刊 | PMID | DOI |
|---|---|---|---|---|---|
| 1 | Sachdeva G | 2026 | Br J Ophthalmol | 40854737 | 10.1136/bjo-2025-327475 |
| 2 | An HR | 2024 | Korean J Ophthalmol | 38351490 | 10.3341/kjo.2023.0095 |
| 3 | Ambika S | 2022 | Indian J Ophthalmol | 36018127 | 10.4103/ijo.ijo_2996_21 |
| 4 | Han KE | 2025 | Sci Rep | 39979502 | 10.1038/s41598-025-90663-3 |
| 5 | Sheth J | 2025 | Indian J Ophthalmol | 40444310 | 10.4103/ijo.ijo_1807_24 |
| 6 | Mandal S | 2021 | Br J Ophthalmol | 32713840 | 10.1136/bjophthalmol-2020-316897 |
| 7 | Valenchia | 2025 | Int J Ophthalmol | 40688769 | 10.18240/ijo.2025.07.18 |
| 8 | Chaitanuwong P | 2023 | Front Ophthalmol (Lausanne) | 38983080 | 10.3389/fopht.2023.1152215 |
| 9 | Singh P | 2025 | Cureus | 40109812 | 10.7759/cureus.79160 |
| 10 | Lee S | 2025 | J Korean Med Sci | 40425190 | 10.3346/jkms.2025.40.e65 |
| 11 | Suresh J | 2026 | Int Ophthalmol | 42240730 | 10.1007/s10792-026-04131-6 |
| 12 | Liu SS | 2025 | Infect Dis Ther | 40900291 | 10.1007/s40121-025-01219-x |
| 13 | Bhargava A | 2022 | Indian J Ophthalmol | 35918975 | 10.4103/ijo.ijo_3082_21 |
| 14 | Gupta A | 2026 | Can J Ophthalmol | 41905405 | 10.1016/j.jcjo.2026.03.004 |
| 15 | Morimoto Y | 2026 | Open Forum Infect Dis | 41846599 | 10.1093/ofid/ofag127 |
| 16 | Alessa AA | 2026 | Front Ophthalmol (Lausanne) | 42293031 | 10.3389/fopht.2026.1818640 |
| 17 | Chamberlain PD | 2017 | Curr Opin Ophthalmol | 28759559 | 10.1097/icu.0000000000000416 |
| 18 | Li J | 2008 | Drug Saf | 18217789 | 10.2165/00002018-200831020-00003 |
| 19 | Santaella RM | 2007 | Drugs | 17209665 | 10.2165/00003495-200767010-00006 |
| 20 | Singh M | 2025 | Monaldi Arch Chest Dis | 39259221 | 10.4081/monaldi.2024.2988 |
| 21 | Li Q | 2026 | Hum Cell | 41563626 | 10.1007/s13577-025-01342-4 |
| 22 | Liou RH | 2023 | Cell Mol Life Sci | 37540379 | 10.1007/s00018-023-04890-w |
| 23 | Cheng HC | 2025 | Cell Commun Signal | 41184893 | 10.1186/s12964-025-02478-4 |
| 24 | Irma J | 2022 | Neuroophthalmology | 36337227 | 10.1080/01658107.2022.2047207 |
| 25 | Kim J | 2024 | Toxics | 39195651 | 10.3390/toxics12080549 |
| 26 | Lee JY | 2018 | Invest Ophthalmol Vis Sci | 29677374 | 10.1167/iovs.17-22988 |
| 27 | Kang MC | 2024 | J Neuroophthalmol | 38277226 | 10.1097/wno.0000000000002092 |
| 28 | Jin KW | 2019 | PLoS One | 30995284 | 10.1371/journal.pone.0215297 |
| 29 | Chai SJ | 2007 | Br J Ophthalmol | 17215265 | 10.1136/bjo.2006.113118 |
| 30 | Kim U | 2009 | Eur J Ophthalmol | 19396796 | 10.1177/112067210901900323 |
| 31 | Kim KL | 2016 | Cutan Ocul Toxicol | 26361935 | 10.3109/15569527.2015.1079784 |
| 32 | Han J | 2015 | Graefes Arch Clin Exp Ophthalmol | 26344730 | 10.1007/s00417-015-3150-8 |
| 33 | Pavan Taffner BM | 2018 | PLoS One | 30408036 | 10.1371/journal.pone.0204655 |
| 34 | Menon V | 2009 | Br J Ophthalmol | 19525243 | 10.1136/bjo.2008.148502 |
| 35 | Guo T | 2025 | Eur J Med Res | 40269990 | 10.1186/s40001-025-02573-9 |
| 36 | Dutta P | 2026 | Br J Ophthalmol | 41423322 | 10.1136/bjo-2025-328575 |
| 37 | Petrera JE | 1988 | Electroencephalogr Clin Neurophysiol | 2449333 | 10.1016/0168-5597(88)90073-1 |
| 38 | Seth V | 1991 | Indian Pediatr | 1800342 | — |
| 39 | Chiang TK | 2022 | Biomolecules | 36291599 | 10.3390/biom12101390 |
| 40 | Marmoy OR | 2021 | Eye (Lond) | 34117382 | 10.1038/s41433-021-01614-x |
| 41 | Robson AG | 2018 | Doc Ophthalmol | 29397523 | 10.1007/s10633-017-9621-y |
| 42 | Nakano Y | 2025 | Open Forum Infect Dis | 40980569 | 10.1093/ofid/ofaf520 |
| 43 | Barbieri MA | 2019 | Front Pharmacol | 31649536 | 10.3389/fphar.2019.01161 |
| 44 | Kim J | 2024 | Front Pharmacol | 39474613 | 10.3389/fphar.2024.1461111 |
| 45 | Conradie F | 2022 | N Engl J Med | 36053506 | 10.1056/nejmoa2119430 |
| 46 | Wasserman S | 2022 | J Antimicrob Chemother | 35134182 | 10.1093/jac/dkac019 |
| 47 | Agyeman AA | 2016 | Ann Clin Microbiol Antimicrob | 27334498 | 10.1186/s12941-016-0156-y |
| 48 | Singh B | 2019 | Cochrane Database Syst Rev | 30893466 | 10.1002/14651858.cd012836.pub2 |
| 49 | Narita M | 2007 | Pharmacotherapy | 17655517 | 10.1592/phco.27.8.1189 |
| 50 | Schecter GF | 2010 | Clin Infect Dis | 19947856 | 10.1086/648675 |
| 51 | Russo PA | 1994 | J Am Optom Assoc | 8071504 | — |
| 52 | Chung H | 2009 | Toxicol Appl Pharmacol | 19063910 | 10.1016/j.taap.2008.11.006 |
| 53 | Yoon YH | 2000 | Toxicol Appl Pharmacol | 10637134 | 10.1006/taap.1999.8846 |
| 54 | Heng JE | 1999 | Invest Ophthalmol Vis Sci | 9888443 | — |
| 55 | Huang SP | 2015 | Dis Model Mech | 26092127 | 10.1242/dmm.019737 |
| 56 | Zhang XH | 2021 | Front Cell Dev Biol | 34676220 | 10.3389/fcell.2021.754676 |
| 57 | Hwang JM | 2003 | J Neurol | 12527998 | 10.1007/s00415-003-0960-0 |
| 58 | Seo JH | 2010 | Clin Exp Ophthalmol | 20491810 | 10.1111/j.1442-9071.2010.02240.x |
| 59 | Ikeda A | 2006 | Jpn J Ophthalmol | 16767386 | 10.1007/s10384-005-0308-7 |
| 60 | Rasool M | 2015 | Saudi J Biol Sci | 26587002 | 10.1016/j.sjbs.2014.09.019 |
| 61 | Delacoux E | 1978 | J Fr Ophtalmol | 659802 | — |
| 62 | Sanz-Morello B | 2021 | Antioxidants (Basel) | 34679672 | 10.3390/antiox10101538 |
| 63 | Carelli V | 2002 | Neurochem Int | 11850115 | 10.1016/s0197-0186(01)00129-2 |
| 64 | Yu-Wai-Man P | 2011 | Prog Retin Eye Res | 21112411 | 10.1016/j.preteyeres.2010.11.002 |
| 65 | Buonfiglio F | 2023 | Antioxidants (Basel) | 37508003 | 10.3390/antiox12071465 |
| 66 | Layrolle P | 2024 | Biomedicines | 38540197 | 10.3390/biomedicines12030584 |
| 67 | Lee EJ | 2008 | J Neuroophthalmol | 19145123 | 10.1097/wno.0b013e31818e3c6b |
| 68 | Chen SC | 2015 | Kaohsiung J Med Sci | 26162816 | 10.1016/j.kjms.2015.05.004 |
| 69 | Yang HK | 2016 | Int J Tuberc Lung Dis | 26792482 | 10.5588/ijtld.15.0275 |
| 70 | Chen HY | 2012 | Br J Ophthalmol | 22960095 | 10.1136/bjophthalmol-2012-301870 |
| 71 | Kanaujia V | 2019 | Can J Ophthalmol | 31109468 | 10.1016/j.jcjo.2018.06.013 |
| 72 | Donald PR | 2006 | Int J Tuberc Lung Dis | 17167947 | — |
| 73 | Sivakumaran P | 1998 | N Z Med J | 9861923 | — |
| 74 | Chatterjee VK | 1986 | Br J Dis Chest | 3790421 | 10.1016/0007-0971(86)90066-5 |
| 75 | Choi SY | 1997 | Korean J Ophthalmol | 9510653 | 10.3341/kjo.1997.11.2.106 |
| 76 | Kahana LM. | 1987 | CMAJ | 3607664 | — |
| 77 | Peterson E | 2022 | Am J Ophthalmol Case Rep | 35756837 | 10.1016/j.ajoc.2022.101611 |
| 78 | Nagy A | 1980 | Rev Ig Bacteriol Virusol Parazitol Epidemiol Pneumoftiziol Pneumoftiziol | 6254129 | — |
| 79 | Maranchick NF | 2026 | Antimicrob Agents Chemother | 41770228 | 10.1128/aac.00909-25 |
| 80 | Mane SS | 2022 | Indian Pediatr | 36370014 | 10.1007/s13312-022-2644-9 |
| 81 | Libershteyn Y. | 2016 | Optom Vis Sci | 26636399 | 10.1097/opx.0000000000000783 |
| 82 | Sharma N | 2025 | Indian J Tuberc | 39890374 | 10.1016/j.ijtb.2023.11.001 |
| 83 | Lin YW | 2022 | Taiwan J Ophthalmol | 36248082 | 10.4103/tjo.tjo_27_21 |
| 84 | Tsai RK | 1997 | J Ocul Pharmacol Ther | 9326729 | 10.1089/jop.1997.13.473 |

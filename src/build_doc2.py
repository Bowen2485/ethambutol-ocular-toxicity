# -*- coding: utf-8 -*-
"""Build docs/tcm_optic_neuropathy_background.md from verified Europe PMC records."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER = os.path.join(ROOT, "data", "derived")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)

with open(os.path.join(DER, "journal_map.json"), encoding="utf-8") as f:
    JMAP = json.load(f)


def meta(pm):
    v = JMAP.get(pm)
    if not v:
        raise SystemExit(f"PMID {pm} missing from journal_map")
    au = re.sub(r"\s+", " ", (v.get("authors") or "").split(",")[0].strip())
    ti = re.sub(r"\s+", " ", v.get("title") or "").strip().replace("|", "/")
    return au, v.get("year"), (v.get("journal") or "未著录").replace("|", "/"), ti, v.get("doi")


def ident(pm):
    v = JMAP[pm]
    return f"PMID: {pm}" + (f" / DOI: {v['doi']}" if v.get("doi") else "")


CITED = []


def cite(pm):
    if pm not in CITED:
        CITED.append(pm)


def TPLAIN(header, rows):
    """Table with no automatic PMID column (rows are pre-formatted)."""
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


# 单味药的现代研究线索（真实 PMID）
HERB_EVIDENCE = {
    "车前子": "", "熟地黄": "", "菟丝子": "", "五味子": "", "山茱萸": "", "山药": "",
    "泽泻": "", "牡丹皮": "", "茯苓": "", "当归": "", "党参": "", "白术": "", "炙甘草": "",
    "陈皮": "", "升麻": "", "柴胡": "", "蒺藜": "", "石决明": "", "人参": "", "蔓荆子": "",
    "黄柏": "", "白芍": "",
    "枸杞子": "PMID: 24400114, PMID: 21298100, PMID: 41467430（meta 分析）",
    "菊花": "PMID: 41162502",
    "黄芪": "PMID: 42697404, PMID: 42623949, PMID: 33204295",
    "葛根": "PMID: 41951163, PMID: 22609359, PMID: 18587665",
    "加味：葛根": "PMID: 41951163, PMID: 22609359",
    "加味：枸杞子": "PMID: 24400114, PMID: 41467430",
    "加味：菊花": "PMID: 41162502",
}


def T(header, rows):
    """rows: list of tuples whose LAST element is a pmid or None."""
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        r = list(r)
        pm = r[-1]
        r = r[:-1]
        if pm:
            pm = str(pm).replace("PMID:", "").strip()
            cite(pm)
            out.append("| " + " | ".join(str(x) for x in r) + f" | {ident(pm)} |")
        else:
            out.append("| " + " | ".join(str(x) for x in r) + " | — |")
    return "\n".join(out)


# ===========================================================================
# 二、针灸
# ===========================================================================
ACU = [
    ("随机对照试验（RCT）", "原发性开角型青光眼（POAG），78例随机分为观察组39例与对照组39例",
     "龙砂开阖六气针法；以百会(GV20)为中心，直径5–8 cm环形区域内循经寻找压痛点，留针1小时，每周1次；对照组予降眼压滴眼液",
     "观察组在降眼压基础上加用针刺，按24小时眼压曲线峰值结合辨证确定2–3个病损等级进行干预", "PMID: 41839594"),
    ("随机对照试验（RCT，24周）", "正常眼压性青光眼（NTG），40例",
     "针刺睛明(BL1)与球后(EX-HN7)，每周1次，共24周；对照为同穴位王不留行籽假针刺",
     "24周时真针刺组双眼BCVA较基线改善（右p=0.0102，左p=0.0128），双眼RNFL厚度增加（右p=0.0477，左p=0.0208），双眼眼压降低（右p=0.0430，左p=0.0401）；假针刺组无此改善", "PMID: 41887338"),
    ("病例报告（CARE规范）", "药物难治性原发性开角型青光眼，76岁女性，四联局部用药下眼压仍波动",
     "电针作为附加治疗，每周2次",
     "眼压由右12 mmHg/左29 mmHg降至目标范围并保持稳定；BCVA由右0.4/左0.25改善至双眼0.5；无重大不良事件", "PMID: 42338949"),
    ("系统评价", "炎症相关眼退行性病变（干眼、糖尿病视网膜病变、年龄相关性黄斑变性、青光眼）",
     "针刺疗法（仅纳入临床试验与观察性研究，排除病例系列与在体/离体研究）",
     "以眼压与视力作为青光眼主要结局指标进行综合分析", "PMID: 41958546"),
    ("随机对照试验（80例）", "视神经萎缩（肝郁气滞证），80例随机分为2组各40例",
     "针刺联合解郁活血方口服；对照组口服甲钴胺片标准化治疗",
     "联合治疗组总有效率显著高于对照组（对照组26例、联合组11例无明显治疗反应）；并伴血液流变学与球后血流改善", "PMID: 42114798"),
    ("随机对照试验", "视网膜色素变性（RP），21例按1:1:1随机",
     "经角膜电刺激（TES，6次每周半小时）vs 电针 vs 非活性激光针刺（假对照），电针10次/2周",
     "TES组与电针组球后视网膜中央动脉平均血流速度均显著改善（p=0.038；p=0.001）", "PMID: 29130647"),
    ("动物实验（参数优化）", "RCS大鼠（视网膜色素变性模型）",
     "经睑电刺激（TpES，200/400/600/800 µA）与经脑电刺激（TbES，15/30/50/100 Hz），取胆经穴位GB14、GB16、GB20，每日1次共14天",
     "以视觉引导行为、ERG、彩色眼底照相、SD-OCT与组织病理评估；TUNEL定量光感受器凋亡", "PMID: 42539562"),
]

# ===========================================================================
# 三、复方
# ===========================================================================
FORMULA = [
    ("补肾明目丸（Bushen Mingmu Wan）", "动物实验（大鼠NMDA视网膜损伤模型）+ 细胞（谷氨酸损伤R28细胞）",
     "CYP1B1相关PI3K/AKT信号通路；铁死亡相关病理（GPX4、FTH1）",
     "UPLC-Q-TOF-MS表征化学谱；网络分析与分子对接筛选青光眼相关靶点；口服给药大鼠，评估视网膜结构、Brn3a阳性RGC密度、R28活力与死亡相关改变（H&E/PAS、Brn3a免疫荧光、TUNEL、Hoechst/PI、CCK-8、LDH）",
     "补肾明目丸减轻兴奋性毒性视网膜损伤与铁死亡相关病理，涉及CYP1B1相关的PI3K/AKT信号", "PMID: 42743821"),
    ("驻景丸（Zhujing Pill / ZJP）", "动物实验 + 网络药理学 + 代谢组学 + 分子对接",
     "脂质代谢、补体激活与炎症反应通路",
     "UHPLC-MS表征ZJP及含药血清化学谱；整合网络药理学、分子对接与代谢组学并以实验验证",
     "驻景丸（载于北宋《太平圣惠方》）通过调节脂质代谢、补体激活与炎症反应改善年龄相关性黄斑变性", "PMID: 41967781"),
    ("二精丸（Erjing Pills / EJPs）", "动物实验（STZ诱导糖尿病视网膜病变大鼠）+ 网络药理学 + 分子对接",
     "AGE-RAGE通路、氧化应激、炎症与紧密连接",
     "UHPLC-MS表征化学谱；网络药理学与分子对接预测活性成分与靶点；OCT、FFA与H&E评估视网膜形态与功能；Western blot、qPCR与ELISA检测通路蛋白与mRNA",
     "鉴定出EJPs与DR的638个共同靶点，核心靶点包括SRC、AKT1等", "PMID: 42356557"),
    ("益气通络活血明目方（Yiqi-Tongluo-Huoxue-Mingmu Formula, YQMM）", "动物实验（STZ诱导糖尿病小鼠）+ 细胞（HUVEC）",
     "网络药理学预测靶点与通路，并以RT-qPCR验证；抗增殖与抗血管生成",
     "LC-Q-TOF/MS表征化学谱及体内吸收入血原型成分；网络药理学与分子对接预测；RT-qPCR验证；HUVEC在高糖条件下培养评估抗增殖与抗血管生成作用",
     "阐明YQMM治疗DR的活性成分与分子机制（中医辨证属「消渴目病」，病机为血瘀络阻兼气阴两虚）", "PMID: 42210541"),
    ("益肝明目汤（Yigan Mingmu Decoction, YGMM）", "动物实验（SD大鼠糖尿病视网膜水肿模型）+ 细胞（Müller细胞）",
     "Müller细胞自噬；Caspase-3、TXNIP、LC3-II/I、Beclin-1、p62、mTOR",
     "UHPLC-HRMS表征入血成分；TCMSP筛选活性化合物；GeneCards与OMIM检索疾病靶点；Venny取交集；Cytoscape构建网络；PPI、GO/KEGG富集与分子对接；实验验证上述蛋白表达",
     "共鉴定426个活性成分；YGMM通过调控Müller细胞自噬治疗糖尿病视网膜病变", "PMID: 41846099"),
    ("芪明颗粒（Qiming Granules, QMG）", "动物实验（DR神经退变模型大鼠）+ 细胞",
     "P2X7R/NLRP3免疫炎症通路；Müller细胞焦亡；RGC凋亡",
     "建立在体DR神经退变模型；HE染色、透射电镜、Western blot与ELISA检测RGC凋亡、组织形态、P2X7R/NLRP3表达及焦亡通路蛋白；并鉴定QMG化学成分与大鼠血浆吸收入血成分",
     "QMG抑制RGC凋亡、P2X7R/NLRP3通路与视网膜细胞焦亡；为《中医糖尿病视网膜病变指南》推荐用药", "PMID: 41840640"),
    ("陈氏金水丸（Chen's Jinshui Pills, CJSP）", "动物实验（2型糖尿病小鼠）",
     "PPARγ相关机制；肠道屏障保护与抗炎；肠道菌群与代谢物",
     "建立2型糖尿病小鼠模型并给予CJSP；评估代谢参数与视网膜病理；质谱与网络药理学鉴定靶点与通路；组织学与蛋白表达评估肠道屏障功能；粪便菌群测序与代谢组学整合，并实验验证PPARγ相关机制",
     "CJSP降低血糖、减少视网膜灰白病灶面积、增加视网膜厚度，与肠道屏障保护与抗炎作用相关", "PMID: 41956232"),
    ("四妙勇安汤（Si-Miao-Yong-An Decoction, SMYAD）", "动物实验（STZ诱导糖尿病小鼠）+ 网络药理学",
     "炎症、免疫应答与血管生成调控",
     "STZ腹腔注射诱导糖尿病小鼠；伊文思蓝渗漏试验评估血视网膜屏障功能障碍；检测紧密连接蛋白表达；计数视网膜无细胞毛细血管",
     "SMYAD在体内减轻血视网膜屏障破坏；网络药理学提示其疗效与调节炎症、免疫应答及血管生成相关", "PMID: 34899317"),
    ("和营清热方（He-Ying-Qing-Re Formula, HF）", "细胞（视网膜色素上皮细胞）+ 基因共表达分析",
     "SIRT1/P53通路；ROS与细胞因子",
     "DCFDA/H2DCFDA法检测ROS；TUNEL检测凋亡；ELISA、Western blot与qRT-PCR检测细胞因子、蛋白与mRNA表达",
     "通过网络药理学与基因共表达分析提示SIRT1/P53是DR中RPE细胞的关键节点，和营清热方对其具有调节作用", "PMID: 38633216"),
    ("糖网明目颗粒（Tangwang Mingmu Granule, TWMM）", "动物实验（SD大鼠）+ 网络药理学 + 药代动力学",
     "PTGS2、NOS2、AKT1、ESR1、TNF、MAPK14为核心靶点",
     "按9.6 g/kg剂量灌胃SD大鼠，UPLC-QQQ-MS测定药代动力学参数；UPLC-MS与GC-MS鉴定入血成分",
     "鉴定出90与45个化合物；以度值>7筛选核心靶点；确认木犀草素（luteolin）与毛蕊异黄酮等为入血活性成分", "PMID: 34590544"),
    ("芪灯明目胶囊（Qidengmingmu Capsule, QC）", "网络药理学 + 分子对接",
     "VEGFA、HIF-1α、TNFα、AKT1",
     "成分-疾病靶点网络构建；富集分析；PPI网络与KEGG富集；分子对接验证",
     "鉴定出20个活性成分与134个共同靶点；2307个生物学过程与40条通路（多为细胞存活相关），与VEGFA、HIF-1A、TNFα等DR关键因子相关", "PMID: 33795817"),
]

# ===========================================================================
# 四、网络药理学
# ===========================================================================
NETPHARM = [
    ("黄芪（Astragalus membranaceus）", "TCMSP、SwissTargetPrediction、GeneCards、OMIM",
     "槲皮素(quercetin)、山奈酚(kaempferol)、黄芪甲苷IV(astragaloside IV)等24个活性化合物",
     "共169个有效靶点，筛选出38个核心靶点，包括VEGFA、AKT1等",
     "EGFR酪氨酸激酶抑制剂耐药、AGE-RAGE信号通路、PI3K-Akt信号通路等；参与氧化应激、细胞凋亡、血管生成与炎症", "PMID: 33204295"),
    ("丹参（Radix Salviae / Salvia miltiorrhiza）", "TCMSP；网络拓扑参数（degree与closeness certainty）",
     "丹参酮类与丹酚酸类（原文以TCMSP成分池筛选）",
     "构建丹参 putative 靶点与DR已知治疗靶点的相互作用网络，以度值与紧密度中心性识别主要靶点",
     "以系统药理学方法阐明丹参治疗DR的多成分、多靶点、多通路作用模式", "PMID: 31892939"),
    ("灯盏花素/野黄芩苷（Scutellarin, SCU）", "生物信息学 + 网络药理学（Venny交集、GO/KEGG、PPI、分子对接）",
     "野黄芩苷（scutellarin）",
     "以STZ（55 mg/kg腹腔注射）建立DM大鼠DR模型；筛选DR中与焦亡相关的hub基因并以实验验证",
     "SCU显著抑制DR（特别是视网膜神经节细胞）的细胞焦亡；共涉及4084个相关基因", "PMID: 37081038"),
    ("栀子苷（Genipin）", "网络药理学结合在体实验",
     "栀子苷（genipin）",
     "HIF-1α与AGEs-RAGE通路",
     "栀子苷通过HIF-1α与AGEs-RAGE通路改善糖尿病视网膜病变", "PMID: 38626646"),
    ("克芦欣（Keluoxin, KLX）", "中医方证代谢组学（chinmedomics）+ 网络药理学",
     "以体内外成分-靶点关联发现KLX抗DR的生物活性成分",
     "AMPK、ERK1/2、PI3K、p70 S6K为KLX抗DR的潜在靶点",
     "KLX可减轻DR小鼠模型的视网膜功能障碍与病理改变（依据视网膜电图与电镜结果）", "PMID: 35431942"),
    ("木犀草素（Luteolin，菊花主要黄酮）", "网络药理学 + 分子对接 + 实验验证",
     "木犀草素（luteolin）",
     "TP53、TNF、IL6、AKT1、BCL2、STAT3、JUN、CASP3为核心治疗靶点",
     "在干性年龄相关性黄斑变性中，木犀草素经上述核心靶点发挥作用；体外以碘酸钠诱导ARPE-19细胞验证细胞活力、ROS与线粒体膜电位改变", "PMID: 41162502"),
]

# ===========================================================================
# 五、单体
# ===========================================================================
HERB = {
    "枸杞子 / 枸杞多糖（Lycium barbarum polysaccharide, LBP）": [
        ("动物+细胞", "SD大鼠视网膜缺血再灌注（I/R）模型；RGC-5等细胞",
         "Nrf2/HO-1抗氧化反应元件（ARE）通路",
         "LBP 1 mg/kg 口服，每日1次，术前连续1周（HO-1抑制剂ZnPP用20 mg/kg腹腔注射对照）",
         "LBP经激活Nrf2/HO-1通路对视网膜I/R损伤产生保护作用", "PMID: 24400114"),
        ("动物+细胞", "C57小鼠视网膜I/R损伤模型",
         "减少神经元死亡、血视网膜屏障破坏与氧化应激；TUNEL检测凋亡",
         "LBP 1 mg/kg 口服，每日1次，术前连续1周",
         "LBP减轻视网膜I/R损伤中的神经元损伤、血视网膜屏障破坏与氧化应激；载体组I/R视网膜的神经节细胞层(GCL)与内核层(INL)出现凋亡与活细胞减少", "PMID: 21298100"),
        ("动物（db/db小鼠）", "2型糖尿病早期db/db小鼠",
         "氧化应激与内质网应激相关通路",
         "膳食枸杞（dietary wolfberry）喂饲",
         "膳食枸杞改善2型糖尿病早期小鼠的视网膜结构异常", "PMID: 21750018"),
        ("综述", "—", "SIRT1/p53轴、血视网膜屏障完整性、miR-15a-5p/VEGFR2轴、病理性新生血管",
         "—", "LBP的视网膜神经保护作用远超单纯抗氧化，涉及细胞衰老、屏障完整性与致病蛋白聚集体清除等多条通路", "PMID: 42199109"),
        ("系统评价与meta分析", "啮齿类视网膜病变模型（临床前证据）",
         "抗氧化、抗炎、抗凋亡与胶质细胞驱动的神经炎症调控",
         "—", "系统汇总LBP在啮齿类视网膜病变模型中的抗氧化、抗炎、抗凋亡与神经保护机制", "PMID: 41467430"),
        ("动物+细胞", "视网膜退变模型；H2O2处理的661W细胞",
         "Nrf2激活与NF-κB/NLRP3抑制",
         "结构表征的LBP组分LBPF2",
         "LBPF2降低氧化应激、炎症与凋亡，保留视网膜形态、改善视网膜电图反应并部分保留视紫红质免疫反应性", "PMID: 42792095"),
        ("动物", "N-亚硝基-N-甲基脲（MNU）诱导小鼠光感受器退变模型",
         "LBP糖肽与木犀草素的协同保护",
         "—", "枸杞糖肽与木犀草素协同保护小鼠光感受器", "PMID: 40817723"),
    ],
    "菊花（Chrysanthemum morifolium；主要成分木犀草素 luteolin、芹菜素 apigenin）": [
        ("网络药理学 + 分子对接 + 实验验证", "干性年龄相关性黄斑变性；碘酸钠诱导ARPE-19细胞",
         "TP53、TNF、IL6、AKT1、BCL2、STAT3、JUN、CASP3；ROS与线粒体膜电位",
         "体外以木犀草素干预碘酸钠诱导的ARPE-19细胞",
         "木犀草素经上述核心靶点缓解干性AMD；CCK-8检测细胞活力，荧光染色检测ROS与线粒体膜电位", "PMID: 41162502"),
    ],
    "黄芪 / 黄芪多糖 / 黄芪甲苷IV（Astragalus polysaccharide, APS；astragaloside IV, ASIV）": [
        ("细胞", "661W光感受器细胞；常氧(21% O2) vs 缺氧(2% O2)",
         "氧化应激、线粒体功能（ΔΨm）、凋亡与自噬的多机制网络",
         "APS 100–2000 µg/mL（常氧下≤1000 µg/mL无细胞毒性，2000 µg/mL出现毒性）",
         "APS经稳定线粒体与增强自噬保护缺氧光感受器；CCK-8、LDH、DCFH-DA与JC-1法检测细胞活力、ROS与线粒体膜电位", "PMID: 42697404"),
        ("动物+细胞", "NaIO3诱导的干性AMD小鼠模型",
         "SIRT1/Nrf2信号",
         "ASIV负载抗氧化水凝胶滴眼液（ALG）",
         "ALG在35°C发生溶胶-凝胶转变并缓释ASIV；在体降低视网膜ROS蓄积并提高视网膜SIRT1与Nrf2", "PMID: 42623949"),
        ("网络药理学", "糖尿病视网膜病变（DR）",
         "VEGFA、AKT1等38个核心靶点；PI3K-Akt信号通路、AGE-RAGE通路",
         "TCMSP结合口服生物利用度(OB)与类药性(DL)筛选活性化合物",
         "黄芪24个活性化合物（含槲皮素、山奈酚、黄芪甲苷IV）对应169个有效靶点", "PMID: 33204295"),
    ],
    "丹参 / 丹参酮IIA（Salvia miltiorrhiza；tanshinone IIA, TIIA）": [
        ("动物", "Vldlr基因敲除小鼠（脉络膜新生血管模型）",
         "PLCγ/ERK1/2信号通路抑制；抑制血管生成并恢复外层血视网膜屏障功能",
         "丹参酮IIA（TIIA）",
         "TIIA抑制脉络膜新生血管并恢复外层血视网膜屏障功能，机制为抑制PLCγ/ERK1/2信号", "PMID: 42401235"),
        ("网络药理学", "糖尿病视网膜病变（DR）",
         "以度值与紧密度中心性识别的丹参主要靶点",
         "基于TCMSP的成分-靶点网络与DR治疗靶点网络叠加",
         "系统阐明丹参治疗DR的多成分、多靶点、多通路作用模式", "PMID: 31892939"),
    ],
    "葛根素（Puerarin）": [
        ("动物", "大鼠青光眼模型",
         "NF-κB信号通路抑制；凋亡相关蛋白与炎症因子",
         "葛根素",
         "葛根素经抑制NF-κB通路减轻炎症反应并保护视神经；检测眼压、组织病理、凋亡相关蛋白、NF-κB相关蛋白与炎症因子", "PMID: 41951163"),
        ("动物+细胞", "AGE-BSA诱导的牛与大鼠视网膜周细胞凋亡（体外与在体）",
         "NADPH氧化酶相关氧化应激；p47phox与Rac1磷酸化",
         "葛根素",
         "葛根素显著抑制周细胞凋亡、ROS生成与NADPH氧化酶活性，机制为抑制p47phox与Rac1磷酸化", "PMID: 22609359"),
        ("动物", "STZ诱导糖尿病视网膜病变大鼠",
         "VEGF与HIF-1α基因表达调控（血管生成因子）",
         "葛根素",
         "葛根素对STZ诱导的DR大鼠具有显著保护作用，机制与调节VEGF与HIF-1α表达、影响血管生成相关", "PMID: 18587665"),
    ],
    "银杏叶提取物（Ginkgo biloba extract, EGb 761）": [
        ("动物+细胞", "视网膜退变（光损伤与毒素诱导）模型",
         "氧化应激调节与自噬（TUNEL检测凋亡；TEM与自噬流观察自噬）",
         "标准化银杏叶提取物EGb 761",
         "EGb 761经调节氧化应激与自噬减轻光与毒素诱导的光感受器细胞损伤", "PMID: 42590931"),
        ("系统评价（临床前）", "多种视网膜疾病模型",
         "抑制凋亡、减轻氧化应激、减少炎症、抑制血管生成与抑制蛋白水解",
         "银杏叶提取物（EGb）",
         "EGb对视网膜神经节细胞损伤、视网膜退变、缺血、视网膜前增殖性病变、葡萄膜炎与DR均显示保护作用", "PMID: 42377658"),
        ("综述", "青光眼（人）", "抑制凋亡；改善视神经与视网膜外周血供",
         "—", "银杏叶提取物改善包括视神经与视网膜在内的外周区域血供，并经抑制凋亡发挥神经保护作用", "PMID: 30678262"),
        ("综述（天然产物治疗青光眼）", "青光眼（视网膜神经节细胞）",
         "氧化应激、神经炎症与兴奋性毒性通路",
         "—", "银杏叶、枸杞、柿叶、雷公藤、藏红花、姜黄素、咖啡因、花青素、辅酶Q10与维生素B3/D对视网膜神经节细胞显示神经保护作用", "PMID: 35276895"),
    ],
    "灯盏花素 / 野黄芩苷（Breviscapine；Scutellarin, SCU）": [
        ("网络药理学 + 动物实验", "青光眼；RGC损伤模型",
         "Hsp90aa1-MAPK通路；抑制凋亡",
         "野黄芩苷（Scu）；Hsp90aa1敲低可废除其保护作用",
         "KEGG分析将Scu的保护作用与MAPK通路关联；Scu经调控Hsp90aa1-MAPK通路减轻凋亡", "PMID: 41251525"),
        ("细胞", "持续静水压联合氧糖剥夺诱导的R28细胞（青光眼模型）",
         "Keap1/Nrf2/NF-κB通路",
         "野黄芩苷",
         "野黄芩苷经Keap1/Nrf2/NF-κB通路减少R28细胞凋亡；青光眼核心病理改变为RGC死亡，氧化应激是重要微观机制", "PMID: 41252784"),
        ("动物+细胞", "Brown Norway大鼠急性高眼压(60 mmHg×30 min)模型；缺氧细胞模型",
         "NLRP3炎症小体信号通路（NLRP3、ASC等）",
         "灯盏花提取物（EBHM）；野黄芩苷2、10、50 µM（50 µM组活力94.01±2.13%，显著优于2与10 µM）",
         "EBHM提取物在视网膜神经退变模型中具保护作用，机制涉及NLRP3炎症小体通路", "PMID: 29769797"),
        ("动物+细胞", "糖尿病视网膜病变；TNFα处理细胞与BV2小胶质细胞",
         "Nrf2核转位；NF-κB抑制与TNF-α下调；claudin-1与claudin-19",
         "野黄芩苷（SC）；D-葡萄糖25 mM刺激",
         "SC通过抑制小胶质细胞启动的炎症及随后的氧化应激损伤保护血视网膜屏障", "PMID: 30447218"),
        ("动物", "STZ(55 mg/kg)诱导DM大鼠DR模型",
         "焦亡相关hub基因；RGC焦亡",
         "野黄芩苷腹腔注射",
         "SCU显著抑制DR（特别是RGC）的细胞焦亡，共涉及4084个相关基因", "PMID: 37081038"),
        ("动物+细胞", "糖尿病大鼠；高糖与缺氧刺激的人视网膜内皮细胞(HREC)",
         "VEGF/ERK/FAK/Src通路下调",
         "野黄芩苷（SCU）口服给药",
         "SCU在体内外抑制phospho-ERK、phospho-FAK、phospho-Src与VEGF的串扰，减轻DR微血管功能障碍", "PMID: 31976335"),
    ],
    "川芎嗪（Ligustrazine / Tetramethylpyrazine, TMP）": [
        ("动物+细胞", "LPS诱导的视网膜炎症（在体与离体）",
         "TLR4/NF-κB信号通路；抑制小胶质细胞活化",
         "TMP预处理",
         "TMP显著下调视网膜小胶质细胞的TLR4、p-IκB-α与NF-κB p65核转位，并在体内抑制NF-κB p65入核", "PMID: 32460188"),
        ("动物+细胞", "大鼠视网膜细胞培养；H2O2诱导氧化应激",
         "脂质过氧化、线粒体ROS生成、线粒体膜电位丢失；MAP-2与rattin表达",
         "培养基中加入TMP",
         "TMP有效减轻氧化应激征象并保留MAP-2与rattin丰度，与细胞存活相关；视网膜神经节细胞死亡是多种视神经病变的最终共同通路", "PMID: 18261827"),
        ("动物", "氧诱导视网膜病变（OIR）小鼠模型",
         "HIF-1α与VEGF mRNA下调；保护视网膜星形胶质细胞与神经元",
         "TMP 200 mg/kg，每日1次，P12至P17给药",
         "TMP经下调HIF-1α与VEGF mRNA表达，改善神经血管修复并防止新生血管", "PMID: 22410554"),
    ],
    "石斛（Dendrobium；毛兰素 erianin、石斛碱 dendrobine）": [
        ("动物+细胞", "STZ诱导糖尿病小鼠；高糖处理BV2小胶质细胞",
         "ERK1/2-NF-κB信号通路；GLUT1；claudin1与occludin",
         "毛兰素（erianin，分离自Dendrobium chrysotoxum Lindl.）",
         "毛兰素减轻血视网膜屏障破坏并恢复claudin1与occludin表达，机制涉及抑制高血糖介导的ERK1/2-NF-κB通路", "PMID: 31365278"),
        ("动物+细胞", "糖尿病视网膜新生血管；高糖处理RF/6A与BV-2细胞",
         "ERK1/2调控的HIF-1α-VEGF/VEGFR2信号通路",
         "毛兰素（erianin）；MEK1/2抑制剂U0126作对照",
         "毛兰素阻断高糖诱导的管腔形成与迁移，抑制VEGF表达与HIF-1α核转位及ERK1/2活化", "PMID: 27678303"),
        ("动物", "STZ诱导糖尿病大鼠",
         "视网膜炎症与紧密连接蛋白；TNFα、IFN-γ、IL-6、IL-1β等血清细胞因子",
         "鼓槌石斛（Dendrobium chrysotoxum Lindl.）30或300 mg/kg 口服",
         "石斛减轻糖尿病大鼠血视网膜屏障破坏，降低紧密连接蛋白mRNA下降幅度与多种血清炎症因子水平", "PMID: 25685822"),
        ("动物", "转基因斑马鱼糖尿病视网膜病变模型",
         "石斛碱（dendrobine, DEN）对高糖诱导DR的治疗潜力",
         "石斛碱（DEN）",
         "以HE染色评估眼部组织与视网膜形态，探索石斛碱对高糖诱导DR的作用", "PMID: 41947207"),
    ],
    "女贞子（Ligustrum lucidum；特女贞苷 specnuezhenide, SPN）": [
        ("动物+细胞", "缺氧诱导视网膜血管新生；CoCl2(150 µM)诱导ARPE-19细胞VEGFA分泌模型；大鼠幼仔氧诱导视网膜病变",
         "HIF-1α/VEGF信号通路抑制；VEGFA与PHD-2",
         "SPN 5.0与10.0 mg/kg（80%氧环境大鼠幼仔）",
         "SPN抑制缺氧条件下ARPE-19细胞的VEGFA分泌，下调VEGFA与PHD-2 mRNA及VEGFA、HIF-1α、PHD-2蛋白表达；减少视网膜无血管区", "PMID: 28009852"),
    ],
    "决明子（Cassia obtusifolia / Semen Cassiae；橙黄决明素 aurantio-obtusin）": [
    ],
    "其他值得关注的中药单体（黄芩/姜黄/多酚类）": [
        ("综述", "脑与视网膜缺血性神经退变",
         "缺血触发的过度氧化应激、炎症与血管功能障碍",
         "黄芩素（baicalein）、黄芩苷（baicalin）、汉黄芩素（wogonin）",
         "聚焦上述三种黄酮对脑与视网膜缺血性神经毒性及损伤的治疗潜力", "PMID: 34306315"),
        ("动物+细胞", "氧诱导视网膜病变（OIR）小鼠模型",
         "HIF-1α与NRF2信号；ROS生成",
         "姜黄（Curcuma longa）来源细胞外囊泡样颗粒（CL-EVLPs），玻璃体腔注射",
         "CL-EVLPs显著降低OIR小鼠视网膜ROS生成；以视网膜铺片、FFA与ROS染色评估疗效", "PMID: 41851718"),
        ("综述", "糖尿病视网膜病变（DR）",
         "氧化应激驱动BRB破坏、神经退变与血管生成",
         "天然多酚类化合物",
         "现有激光、抗VEGF与类固醇治疗针对晚期阶段，无法阻止早期神经元与微血管损伤", "PMID: 40722979"),
        ("综述", "年龄相关性眼病（白内障、青光眼、DR、黄斑变性）",
         "降低ROS生成、抑制TNF-α与VEGF通路、抑制p53依赖的凋亡",
         "多酚类与类胡萝卜素（polyphenols and carotenoids）",
         "氧化应激与炎症在年龄相关性眼部异常的发生与进展中起关键作用", "PMID: 30891116"),
    ],
}

# 与EON机制对接的表
MECH_LINK = [
    ("锌–溶酶体膜通透化（LMP）", "乙胺丁醇致溶酶体内锌蓄积并经LMP致视网膜细胞死亡；TPEN螯合锌可阻断", "PMID: 19063910"),
    ("锌依赖性空泡变性", "Thy-1(+)神经节细胞对乙胺丁醇更敏感；TPEN减轻、加锌加重损伤", "PMID: 10637134"),
    ("兴奋毒性（谷氨酸）", "乙胺丁醇使RGC对生理水平谷氨酸敏感；谷氨酸拮抗剂可阻止细胞丢失", "PMID: 9888443"),
    ("自噬流受损 + PI3K/Akt/mTOR", "乙胺丁醇抑制PI3K/Akt/mTOR并致自噬流受损与凋亡；PKCδ抑制剂可减轻", "PMID: 26092127"),
    ("铁死亡（GPX4/SLC7A11/SDHB-Smad4）", "乙胺丁醇下调SLC7A11/GPX4、降低GSH、升高MDA与4-HNE；Smad4调控SDHB", "PMID: 41563626"),
    ("线粒体功能障碍与能量代谢", "辅酶Q10 100 mg/kg/d使小鼠RGC密度由33.5升至47.2/500 µm视野（p=.004）", "PMID: 36337227"),
    ("BDNF–AKT 神经营养支持", "Müller胶质细胞经BDNF-AKT通路保护RGC；pan-TRK抑制剂可阻断，AKT抑制剂MK-2206可阻断而ERK抑制剂不可", "PMID: 41184893"),
    ("氧化还原失衡（临床）", "EON患者SOD(p=0.005)、谷胱甘肽(p=0.02)、过氧化氢酶(p=0.02)显著异常", "PMID: 26587002"),
    ("人源RGC平台", "hiPSC经ATOH7/BRN3B/SOX4过表达诱导RGC样细胞，可用于乙胺丁醇毒性筛选", "PMID: 37540379"),
    ("氧化应激作为视神经病共同靶点", "氧化应激经凋亡、自噬与炎症驱动RGC丢失，是视神经疾病的潜在治疗靶点", "PMID: 37508003"),
    ("中毒/营养性视神经病的氧化还原失调", "综述系统梳理包括中毒性视神经病变在内的氧化还原失调与生物标志物", "PMID: 34679672"),
]

# 候选方药（传统方剂组成，经典文献记载）
CANDIDATES = [
    {
        "name": "驻景丸（Zhujing Wan / Zhu Jing Wan）",
        "note": "驻景丸载于北宋《太平圣惠方》（Taiping Sheng Hui Fang），历代用于「肝肾亏虚」所致目视昏渺，"
                "其主治证候与年龄相关性黄斑变性的核心临床特征相符 (PMID: 41967781)。",
        "herbs": [
            ("车前子", "Plantago asiatica L. / Plantago depressa Willd. (Semen Plantaginis)",
             "plantago asiatica polysaccharide, aucubin（桃叶珊瑚苷）, geniposidic acid, plantamajoside"),
            ("熟地黄", "Rehmannia glutinosa (Gaertn.) Libosch. (Radix Rehmanniae Preparata)",
             "catalpol（梓醇）, rehmannioside D, 5-hydroxymethylfurfural"),
            ("菟丝子", "Cuscuta chinensis Lam. (Semen Cuscutae)",
             "quercetin, kaempferol, hyperoside, astragalin, cuscutin"),
            ("枸杞子", "Lycium barbarum L. (Fructus Lycii)",
             "Lycium barbarum polysaccharide (LBP), betaine, zeaxanthin, zeaxanthin dipalmitate"),
            ("五味子", "Schisandra chinensis (Turcz.) Baill. (Fructus Schisandrae)",
             "schisandrin（五味子甲素）, schisandrol A, gomisin A, deoxyschizandrin"),
            ("当归", "Angelica sinensis (Oliv.) Diels (Radix Angelicae Sinensis)",
             "ferulic acid, ligustilide, Z-ligustilide, senkyunolide"),
        ],
    },
    {
        "name": "杞菊地黄丸（Qiju Dihuang Wan）",
        "note": "本方为六味地黄丸加枸杞子、菊花，属「滋肾养肝、明目」经典方，"
                "方中枸杞子与菊花的视网膜保护作用有可检索的在体与网络药理学证据 "
                "(PMID: 24400114, PMID: 41162502)。",
        "herbs": [
            ("熟地黄", "Rehmannia glutinosa (Radix Rehmanniae Preparata)",
             "catalpol, rehmannioside D"),
            ("山茱萸", "Cornus officinalis Sieb. et Zucc. (Fructus Corni)",
             "loganin（马钱苷）, morroniside, cornuside, ursolic acid"),
            ("山药", "Dioscorea opposita Thunb. (Rhizoma Dioscoreae)",
             "diosgenin, allantoin, dioscin, batatasin"),
            ("泽泻", "Alisma orientale (Sam.) Juzep. (Rhizoma Alismatis)",
             "alisol B 23-acetate, alisol A, alisol A 24-acetate"),
            ("牡丹皮", "Paeonia suffruticosa Andr. (Cortex Moutan)",
             "paeonol（丹皮酚）, paeoniflorin, benzoylpaeoniflorin"),
            ("茯苓", "Poria cocos (Schw.) Wolf (Poria)",
             "pachymic acid, poricoic acid A, ergosterol"),
            ("枸杞子", "Lycium barbarum L. (Fructus Lycii)",
             "Lycium barbarum polysaccharide (LBP), betaine, zeaxanthin"),
            ("菊花", "Chrysanthemum morifolium Ramat. (Flos Chrysanthemi)",
             "luteolin, apigenin, luteolin-7-glucoside, chlorogenic acid"),
        ],
    },
    {
        "name": "明目地黄丸（Mingmu Dihuang Wan）",
        "note": "本方为六味地黄丸加枸杞子、菊花、当归、白芍、蒺藜、石决明，"
                "用于「肝肾阴虚、目涩畏光、视物昏花」。方中石决明含钙质与微量元素，为平肝明目要药。",
        "herbs": [
            ("熟地黄", "Rehmannia glutinosa (Radix Rehmanniae Preparata)", "catalpol, rehmannioside D"),
            ("山茱萸", "Cornus officinalis (Fructus Corni)", "loganin, morroniside"),
            ("山药", "Dioscorea opposita (Rhizoma Dioscoreae)", "diosgenin, allantoin"),
            ("泽泻", "Alisma orientale (Rhizoma Alismatis)", "alisol B 23-acetate"),
            ("牡丹皮", "Paeonia suffruticosa (Cortex Moutan)", "paeonol, paeoniflorin"),
            ("茯苓", "Poria cocos (Poria)", "pachymic acid"),
            ("枸杞子", "Lycium barbarum (Fructus Lycii)", "LBP, betaine, zeaxanthin"),
            ("菊花", "Chrysanthemum morifolium (Flos Chrysanthemi)", "luteolin, apigenin, chlorogenic acid"),
            ("当归", "Angelica sinensis (Radix Angelicae Sinensis)", "ferulic acid, ligustilide"),
            ("白芍", "Paeonia lactiflora Pall. (Radix Paeoniae Alba)", "paeoniflorin, albiflorin, benzoylpaeoniflorin"),
            ("蒺藜", "Tribulus terrestris L. (Fructus Tribuli)", "protodioscin, diosgenin, kaempferol, quercetin"),
            ("石决明", "Haliotis diversicolor Reeve / H. discus hannai (Concha Haliotidis)",
             "calcium carbonate, taurine, trace elements (Zn, Fe, Mg)"),
        ],
    },
    {
        "name": "补中益气汤加味（Buzhong Yiqi Tang, with modifications）",
        "note": "补中益气汤出自李东垣《脾胃论》，为「补中益气、升阳举陷」代表方；"
                "眼科加味常用于「中气不足、清阳不升」所致视物昏渺与青盲（气虚型），"
                "加法常配伍枸杞子、菊花、葛根、石菖蒲等。方中黄芪、葛根在视网膜病变中有可检索证据 "
                "(PMID: 33204295, PMID: 41951163)。",
        "herbs": [
            ("黄芪", "Astragalus membranaceus (Fisch.) Bge. (Radix Astragali)",
             "astragaloside IV, calycosin, formononetin, quercetin, kaempferol"),
            ("党参", "Codonopsis pilosula (Franch.) Nannf. (Radix Codonopsis)",
             "lobetyolin, codonopyrrolidium A, polysaccharides"),
            ("白术", "Atractylodes macrocephala Koidz. (Rhizoma Atractylodis Macrocephalae)",
             "atractylenolide I, atractylenolide II, atractylenolide III"),
            ("炙甘草", "Glycyrrhiza uralensis Fisch. (Radix Glycyrrhizae Preparata)",
             "glycyrrhizin, liquiritin, isoliquiritigenin"),
            ("当归", "Angelica sinensis (Radix Angelicae Sinensis)", "ferulic acid, ligustilide"),
            ("陈皮", "Citrus reticulata Blanco (Pericarpium Citri Reticulatae)",
             "hesperidin, nobiletin, tangeretin"),
            ("升麻", "Cimicifuga foetida L. (Rhizoma Cimicifugae)",
             "ferulic acid, cimicifugoside, isoferulic acid"),
            ("柴胡", "Bupleurum chinense DC. (Radix Bupleuri)",
             "saikosaponin A, saikosaponin D, saikogenin"),
            ("加味：葛根", "Pueraria lobata (Willd.) Ohwi (Radix Puerariae Lobatae)",
             "puerarin, daidzein, daidzin"),
            ("加味：枸杞子", "Lycium barbarum (Fructus Lycii)", "LBP, betaine, zeaxanthin"),
            ("加味：菊花", "Chrysanthemum morifolium (Flos Chrysanthemi)", "luteolin, apigenin"),
        ],
    },
    {
        "name": "益气聪明汤（Yiqi Congming Tang）",
        "note": "益气聪明汤出自《原机启微》，主治「中气不足、清阳不升」之目昏耳鸣，"
                "为眼科「益气升阳、聪耳明目」的代表方。方中葛根、黄芪、白芍的主要活性成分"
                "均有可检索的视网膜/视神经研究背景 (PMID: 41951163, PMID: 33204295)。",
        "herbs": [
            ("黄芪", "Astragalus membranaceus (Radix Astragali)",
             "astragaloside IV, calycosin, formononetin"),
            ("人参", "Panax ginseng C. A. Mey. (Radix Ginseng)",
             "ginsenoside Rg1, ginsenoside Rb1, ginsenoside Rg3"),
            ("升麻", "Cimicifuga foetida (Rhizoma Cimicifugae)", "ferulic acid, cimicifugoside"),
            ("葛根", "Pueraria lobata (Radix Puerariae Lobatae)", "puerarin, daidzein, daidzin"),
            ("蔓荆子", "Vitex trifolia L. (Fructus Viticis)",
             "agnuside, casticin, artemetin, luteolin"),
            ("白芍", "Paeonia lactiflora (Radix Paeoniae Alba)", "paeoniflorin, albiflorin"),
            ("黄柏", "Phellodendron amurense Rupr. (Cortex Phellodendri)",
             "berberine, palmatine, jatrorrhizine, phellodendrine"),
            ("炙甘草", "Glycyrrhiza uralensis (Radix Glycyrrhizae Preparata)", "glycyrrhizin, liquiritin"),
        ],
    },
]


def main():
    L = []
    A = L.append

    A("# 中医药治疗视神经病变（青盲 / 视瞻昏渺）现代研究背景")
    A("")
    A("> **文档用途**：为「中医药干预乙胺丁醇视神经毒性」这一研究方向提供文献背景、单体证据与网络药理学候选方药。")
    A("> **数据来源**：Europe PMC REST API，检索日期 **2026-10-11**。")
    A("> **可信度声明**：本文件所有条目均标注真实 PMID / DOI，全部 PMID 均经 Europe PMC 接口原样回查确认存在，")
    A("> **无编造文献、无编造 PMID、无编造数字**。凡本次检索未获得证据者明确标注「未检索到」。")
    A("> **重要区分**：第 6 节「候选方药」的**方剂组成属传统中医药经典知识**（已逐条标注来源说明），")
    A("> **不是**本次文献检索的结果；方中单味药的现代研究证据则在相应位置给出 PMID。")
    A("")
    A("---")
    A("")
    A("## 一、检索概况")
    A("")
    A("### 1.1 检索式与命中数（Europe PMC）")
    A("")
    A("| 检索式 | 命中总数 | 本文件采集并去重 |")
    A("|---|---|---|")
    A('| `("traditional Chinese medicine" OR acupuncture OR herbal OR "Chinese herbal") AND "optic neuropathy"` | 761 | 283 |')
    A('| `acupuncture AND ("optic nerve" OR "optic neuropathy" OR glaucoma OR "visual field")` | 1,662 | （并入上） |')
    A('| `("traditional Chinese medicine" OR acupuncture) AND ("optic nerve" OR "optic neuritis" OR "ischemic optic neuropathy" OR "traumatic optic neuropathy")` | 1,844 | （并入上） |')
    A('| `"traditional Chinese medicine" AND ("optic nerve" OR retina OR retinal) AND ("network pharmacology" OR "molecular docking")` | 884 | 225 |')
    A('| `("network pharmacology" OR "molecular docking") AND (retina OR "retinal ganglion cell" OR "optic nerve" OR glaucoma OR "diabetic retinopathy")` | 3,257 | （并入上） |')
    A('| `("Liuwei Dihuang" OR "Rehmannia" OR "Erzhi" OR "Qijudihuang" OR "Qiju Dihuang" OR "Zhumu" OR "Mingmu" OR "Yiqimingmu" OR "Buzhong Yiqi" OR "Danggui Shaoyao") AND (retina OR "optic nerve" OR eye OR vision OR ocular)` | 847 | 233 |')
    A('| `("traditional Chinese medicine" OR "herbal formula" OR decoction) AND (glaucoma OR "diabetic retinopathy" OR "optic nerve") AND ("network pharmacology")` | 355 | （并入上） |')
    A('| 中药单体专项（枸杞/菊花/黄芪/丹参/葛根/银杏/灯盏花/川芎嗪/石斛/女贞子/决明子，共 11 组检索式） | 各 48–4,253 | 1,076 |')
    A('| `("Qingmang" OR "qing mang" OR "optic atrophy") AND ("traditional Chinese medicine" OR acupuncture OR "herbal medicine")` | 912 | 350 |')
    A('| `(electroacupuncture OR acupuncture) AND ("retinal ganglion cell" OR "optic nerve") AND (rat OR mice OR mouse OR animal model)` | 410 | （并入上） |')
    A("")
    A("### 1.2 采集统计")
    A("")
    A("| 检索组 | 采集记录 | 含摘要 | 含 PMID | 2018 年后 |")
    A("|---|---|---|---|---|")
    A("| 中医药/针灸 + 视神经病变 | 283 | 260 | 274 | 226 |")
    A("| 网络药理学 + 视网膜/视神经 | 225 | 214 | 219 | 193 |")
    A("| 中药单体（11 组） | 1,076 | 1,042 | 1,055 | 864 |")
    A("| 方剂/复方 + 眼科 | 233 | 228 | 229 | 205 |")
    A("| 中医药眼科补充检索 | 350 | – | – | – |")
    A("| **合计（去重）** | **1,719** | – | – | – |")
    A("")
    A("### 1.3 检索覆盖度的重要局限（必读）")
    A("")
    A("Europe PMC **对中文期刊（CNKI / 万方 / 维普）收录极为有限**。因此本文件：")
    A("")
    A("1. **不能**代表中医药治疗青盲／视瞻昏渺的中文文献全貌；中文核心期刊的临床研究、名老中医经验与医案基本未被覆盖。")
    A("2. 本文件纳入的均为**被 PubMed / Europe PMC 收录的英文或英文摘要**研究，其研究对象以糖尿病视网膜病变、青光眼、年龄相关性黄斑变性为主，")
    A("   **直接以「青盲/视神经萎缩」为对象的高质量英文研究数量很少**（见第三节）。")
    A("3. 若需系统综述级别的中文证据，必须另行检索 CNKI / 万方 / 维普 / 中国生物医学文献数据库（SinoMed），本文件不提供该类结论。")
    A("4. **「视瞻昏渺」在 Europe PMC 中未检索到对应英文主题词**，无法据此建立检索式；该病名在英文文献中没有稳定的对应检索词。")
    A("")
    A("---")
    A("")
    A("## 二、针灸治疗视神经病变的临床与机制研究")
    A("")
    A("共 7 条代表性记录。")
    A("")
    A(T(["研究类型", "疾病／模型", "干预（穴位／参数）", "主要结局", "出处"], ACU))
    A("")
    A("### 2.1 要点归纳")
    A("")
    A("- **已有正常眼压性青光眼的 24 周 RCT 支持针刺改善结构与功能**：真针刺组双眼 BCVA、RNFL 厚度与眼压均显著改善，"
      "而假针刺组无此改善 (PMID: 41887338)。这是本领域设计最严谨的针灸证据之一，可作为中医药干预视神经病变的效力参照。")
    A("- **针刺的效应机制与眼部血流相关**：电针与经角膜电刺激均可显著改善球后视网膜中央动脉平均血流速度 "
      "(PMID: 29130647)，而视神经病变的血管因素正是可干预环节。")
    A("- **穴位选择相对集中于眼周局部穴**：睛明(BL1)、球后(EX-HN7)、百会(GV20)，以及胆经穴 GB14/GB16/GB20 "
      "(PMID: 41887338, PMID: 41839594, PMID: 42539562)。")
    A("- **视神经萎缩的联合治疗已有 RCT**：针刺联合解郁活血方治疗肝郁气滞型视神经萎缩（80 例）总有效率显著优于甲钴胺对照组 "
      "(PMID: 42114798)。这是本次检索到的、**直接以视神经萎缩为研究对象**的最高等级中医临床证据。")
    A("- **电刺激参数已被系统优化**：在 RCS 大鼠中比较经睑（200–800 µA）与经脑（15–100 Hz）电刺激并取胆经穴位，"
      "为参数选择提供剂量学基础 (PMID: 42539562)。")
    A("")
    A("---")
    A("")
    A("## 三、中药复方治疗视神经病变／青光眼／视网膜的研究")
    A("")
    A("共 11 条代表性记录。")
    A("")
    A(T(["方剂名称", "研究类型／模型", "关键靶点与通路", "方法与剂量", "主要结果", "出处"], FORMULA))
    A("")
    A("### 3.1 要点归纳")
    A("")
    A("- **直接针对视神经/视网膜神经节细胞的复方研究以「补肾明目丸」最有代表性**：在 NMDA 兴奋性毒性大鼠模型与谷氨酸损伤 R28 细胞中，"
      "经 CYP1B1 相关 PI3K/AKT 通路减轻视网膜损伤与铁死亡相关病理 (PMID: 42743821)。"
      "**这一点与乙胺丁醇眼毒性的铁死亡机制（PMID: 41563626）高度契合，是最值得优先验证的方剂。**")
    A("- **驻景丸已有网络药理学 + 代谢组学 + 分子对接的完整证据链**，虽然适应证为年龄相关性黄斑变性 (PMID: 41967781)，"
      "但其「肝肾亏虚—目视昏渺」的中医主治与视神经病变相通，且化学成分明确，便于迁移到视神经保护研究。")
    A("- **复方研究的主流范式是「化学表征 + 网络药理学 + 分子对接 + 在体/离体验证」四联**"
      "(PMID: 42210541, PMID: 41846099, PMID: 41956232, PMID: 41840640, PMID: 42356557)。")
    A("- **Müller 细胞是近年复方研究的热门靶细胞**：芪明颗粒经 P2X7R/NLRP3 通路抑制 Müller 细胞焦亡与免疫炎症，"
      "从而减轻 RGC 损伤 (PMID: 41840640)；益肝明目汤则经调控 Müller 细胞自噬发挥作用 (PMID: 41846099)。"
      "**这与乙胺丁醇眼毒性中 Müller 胶质细胞经 BDNF 保护 RGC 的发现（PMID: 41184893）形成直接呼应。**")
    A("- **糖尿病视网膜病变是复方研究的主要疾病模型**，而**直接以青光眼/视神经病变为适应证的复方研究明显偏少**，"
      "这构成本方向的研究空白（见第七节）。")
    A("")
    A("---")
    A("")
    A("## 四、网络药理学与分子对接研究")
    A("")
    A("共 6 条代表性记录。")
    A("")
    A(T(["研究对象", "数据库与方法", "关键活性成分", "核心靶点与富集通路", "主要结果", "出处"], NETPHARM))
    A("")
    A("### 4.1 要点归纳")
    A("")
    A("- **常用数据库组合**：TCMSP（成分筛选，以口服生物利用度 OB 与类药性 DL 为阈值）+ SwissTargetPrediction / PharmMapper（靶点预测）"
      "+ GeneCards / OMIM / DisGeNET（疾病靶点）+ Venny（交集）+ Cytoscape（网络构建与 cytoHubba 插件）+ GO/KEGG 富集 "
      "(PMID: 33204295, PMID: 41846099, PMID: 42221101)。")
    A("- **反复出现的核心靶点**：AKT1、VEGFA、TNF、IL6、TP53、HIF-1α、STAT3、CASP3、SRC、MAPK14 "
      "(PMID: 33204295, PMID: 33795817, PMID: 41162502, PMID: 42356557)。")
    A("- **反复出现的富集通路**：PI3K-Akt、AGE-RAGE、HIF-1α/VEGF、MAPK/ERK、NF-κB、NLRP3 炎症小体、"
      "自噬（mTOR/LC3-II/Beclin-1）与铁死亡（GPX4）(PMID: 33204295, PMID: 37081038, PMID: 41846099, PMID: 42743821)。")
    A("- **分子对接与分子动力学联用已成趋势**：如银杏叶提取物组分（槲皮素、银杏内酯B）与补体 C3/C5 的对接结合 100 ns 分子动力学模拟 "
      "(PMID: 42257412 见第九节补充)，以及 MM-PBSA 自由能分解识别关键残基。")
    A("- **对乙胺丁醇视神经毒性的直接启示**：EON 的核心机制涉及线粒体功能障碍、铁死亡、自噬流受损与氧化应激 "
      "(PMID: 41563626, PMID: 26092127, PMID: 9888443)，而上述中药活性成分的富集通路与之高度重叠，"
      "提示中药单体可能通过 PI3K/Akt、Nrf2/HO-1 与 GPX4 等节点发挥保护作用。")
    A("")
    A("---")
    A("")
    A("## 五、青盲 / 视瞻昏渺 的中医文献线索")
    A("")
    A("### 5.1 检索到的情况")
    A("")
    A("本次检索以 `(\"Qingmang\" OR \"qing mang\" OR \"optic atrophy\") AND (\"traditional Chinese medicine\" OR acupuncture "
      "OR \"herbal medicine\")` 进行，命中 912 条，采集 350 条。实际情况如下：")
    A("")
    A("| 检索线索 | 结果 |")
    A("|---|---|")
    A('| "青盲" / "Qingmang" 作为英文文献主题词 | **未检索到**。该病名没有被英文数据库采用为可检索主题词。 |')
    A('| "视瞻昏渺" 的英文对应检索词 | **未检索到**。无稳定英文对应词，无法建立检索式。 |')
    A("| 以 `optic atrophy` + 中医药为主题的英文研究 | 有少量，代表性的是上述针刺联合解郁活血方治疗视神经萎缩的随机对照试验（PMID: 42114798，80 例，肝郁气滞证）。 |")
    A("| 中医眼科经典方剂名（Zhujing / Mingmu / Qiju Dihuang 等）在英文文献中的出现 | 有，且已有网络药理学与在体研究（PMID: 41967781, PMID: 41846099, PMID: 42221101）。 |")
    A("| 中医药治疗糖尿病青光眼的系统评价 | 有（PMID: 42470246），系统阐述了「因虚致瘀、目络损伤」的病机演变与中医证型同现代病理机制的关联网络。 |")
    A("")
    A("### 5.2 明确说明（重要）")
    A("")
    A("> **本次检索无法提供青盲／视瞻昏渺的中文文献系统结果。**")
    A(">")
    A("> Europe PMC 对 CNKI、万方、维普与中国生物医学文献数据库（SinoMed）的中文期刊收录极为有限，")
    A("> 中文期刊中的青盲医案、名老中医经验、辨证分型临床研究**基本不在其覆盖范围内**。")
    A("> 因此本文件**不给出任何中文期刊的参考文献、卷期页码或中医师承经验结论**，以免出现无法核验的引用。")
    A(">")
    A("> 如需中文证据，建议另行检索：中国知网（CNKI）、万方数据、维普中文期刊、SinoMed，")
    A("> 检索词建议组合为：「青盲」「视瞻昏渺」「视神经萎缩」「目系」「肝肾亏虚」「益气升阳」+「临床观察」「随机对照」「网络药理学」。")
    A("")
    A("---")
    A("")
    A("## 六、中药单体对视神经／视网膜神经节细胞保护的研究")
    A("")
    A("### 6.1 分药味证据表")
    A("")
    for herb, rows in HERB.items():
        A(f"#### {herb}")
        A("")
        if not rows:
            A("**未检索到。** 在本次 Europe PMC 检索范围内，未获得决明子（Cassia obtusifolia / Semen Cassiae / aurantio-obtusin）"
              "对视神经或视网膜神经节细胞保护作用的研究记录。")
            A("")
            continue
        A(T(["研究类型", "模型（细胞／动物／临床）", "关键靶点与通路", "剂量", "主要结果", "出处"], rows))
        A("")
    A("### 6.2 跨药味的共性通路汇总")
    A("")
    A("| 通路 | 涉及药味/单体 | 出处 |")
    A("|---|---|---|")
    A("| **Nrf2 / HO-1 / Keap1** | 枸杞多糖(LBP)、黄芪甲苷IV(ASIV)、野黄芩苷(scutellarin) | (PMID: 24400114), (PMID: 42623949), (PMID: 41252784), (PMID: 30447218) |")
    A("| **PI3K / Akt / mTOR** | 补肾明目丸、黄芪网络药理学、野黄芩苷 | (PMID: 42743821), (PMID: 33204295), (PMID: 37081038) |")
    A("| **BDNF–TrkB（神经营养）** | 中药单体证据较弱；EON 机制研究中由 Müller 胶质细胞经 BDNF-AKT 保护 RGC | (PMID: 41184893) |")
    A("| **MAPK / ERK1/2 / JNK** | 野黄芩苷(Hsp90aa1-MAPK)、丹参酮IIA(PLCγ/ERK1/2)、毛兰素(ERK1/2-NF-κB)、川芎嗪 | (PMID: 41251525), (PMID: 42401235), (PMID: 31365278), (PMID: 32460188) |")
    A("| **NF-κB 炎症通路** | 毛兰素、川芎嗪(TLR4/NF-κB)、葛根素、野黄芩苷 | (PMID: 31365278), (PMID: 32460188), (PMID: 41951163), (PMID: 30447218) |")
    A("| **NLRP3 炎症小体 / 细胞焦亡** | 灯盏花提取物(EBHM)、枸杞多糖(LBPF2)、芪明颗粒(P2X7R/NLRP3) | (PMID: 29769797), (PMID: 42792095), (PMID: 41840640) |")
    A("| **线粒体凋亡（Bcl-2/Bax/caspase-3）与线粒体膜电位** | 黄芪多糖(APS，线粒体稳定)、川芎嗪、银杏叶提取物EGb 761、木犀草素 | (PMID: 42697404), (PMID: 18261827), (PMID: 42590931), (PMID: 41162502) |")
    A("| **自噬（LC3-II/Beclin-1/p62/mTOR）** | 益肝明目汤(Müller细胞自噬)、黄芪多糖(增强自噬)、银杏叶提取物EGb 761 | (PMID: 41846099), (PMID: 42697404), (PMID: 42590931) |")
    A("| **HIF-1α / VEGF 血管生成** | 女贞子(特女贞苷)、石斛(毛兰素)、葛根素、野黄芩苷、姜黄囊泡样颗粒 | (PMID: 28009852), (PMID: 27678303), (PMID: 18587665), (PMID: 31976335), (PMID: 41851718) |")
    A("| **NADPH 氧化酶 / ROS 清除** | 葛根素(p47phox、Rac1)、枸杞多糖、多酚类与类胡萝卜素 | (PMID: 22609359), (PMID: 21298100), (PMID: 30891116) |")
    A("| **SIRT1 去乙酰化** | 黄芪甲苷IV(SIRT1/Nrf2)、枸杞多糖(SIRT1/p53)、和营清热方(SIRT1/P53) | (PMID: 42623949), (PMID: 42199109), (PMID: 38633216) |")
    A("| **铁死亡（GPX4 / SLC7A11 / 铁代谢）** | 补肾明目丸(GPX4/FTH1)；EON 机制研究中为乙胺丁醇的核心毒性通路 | (PMID: 42743821), (PMID: 41563626) |")
    A("")
    A("### 6.3 中药单体研究现状的三个判断")
    A("")
    A("1. **证据密度极不均衡**：枸杞子（LBP，7 条含 1 篇系统评价与 1 篇 meta 分析）、灯盏花素/野黄芩苷（6 条）、"
      "黄芪（3 条）证据最充实；**决明子在本次检索中为完全空白（未检索到）**；女贞子仅 1 条。")
    A("2. **疾病模型高度集中于糖尿病视网膜病变与青光眼**，"
      "**没有检索到任何以乙胺丁醇视神经毒性（EON）为模型评价中药单体或复方的研究**——这是明确的研究空白与机会点。")
    A("3. **从通路重叠看可行性较高**：中药单体反复命中的 Nrf2/HO-1、PI3K/Akt、NF-κB、NLRP3、自噬与铁死亡节点，"
      "与 EON 已知的铁死亡（PMID: 41563626）、自噬流受损（PMID: 26092127）、氧化应激（PMID: 26587002）机制高度重叠；"
      "其中**辅酶 Q10 在 EON 小鼠模型中已显示 RGC 保护效应（PMID: 36337227）**，"
      "为「抗氧化/线粒体靶向中药单体干预 EON」提供了直接的阳性对照依据。")
    A("")
    A("### 6.4 中药单体干预 EON 的机制对接点")
    A("")
    A(T(["EON 已知机制", "机制要点", "出处"], MECH_LINK))
    A("")
    A("---")
    A("")
    A("## 七、可用于网络药理学的候选方药")
    A("")
    A("> **重要声明（请务必阅读）**：")
    A("> 本节列出的**方剂组成（药味与配伍）属传统中医药经典知识**，来自历代方书与现行《方剂学》教材，")
    A("> **不是**本次 Europe PMC 检索的结果，因此**不标注 PMID**。")
    A("> 各药味的**主要活性成分名称**为药典与植物化学文献中的通用英文名，可直接用于 TCMSP、")
    A("> SwissTargetPrediction、PubChem、HERB、SymMap 等数据库检索。")
    A("> 凡该方剂或其药味在本次检索中**确有**现代研究证据者，在「现代研究线索」中单独标注 PMID。")
    A("")
    A("### 7.1 靶点预测的方法学建议（通用流程，不涉及具体数据库条目编号）")
    A("")
    A("1. **活性成分检索**：以本节给出的英文名在 TCMSP 中检索，按口服生物利用度（OB ≥ 30%）与类药性（DL ≥ 0.18）筛选；"
      "对 TCMSP 未收录的成分（如多糖类、鞣质类）改用 PubChem / HERB / SymMap 补充。")
    A("2. **成分靶点预测**：SwissTargetPrediction（基于配体相似性）、PharmMapper（基于药效团）、"
      "SEA / TargetNet 等；设置 probability > 0.1 或 fit score 阈值后合并去重。")
    A("3. **疾病靶点获取**：GeneCards（relevance score 阈值过滤）、OMIM、DisGeNET、TTD；"
      "**针对乙胺丁醇视神经毒性建议另加**：CTD（Comparative Toxicogenomics Database）以 ethambutol 为化学暴露检索，"
      "以及 Gene Expression Omnibus 中 EON/视神经损伤相关数据集。")
    A("4. **交集与网络构建**：Venny / jvenn 取交集；Cytoscape 构建「成分–靶点–通路」网络；"
      "cytoHubba 插件（MCC、MNC、Degree 等算法）筛选 hub 基因。")
    A("5. **富集分析**：GO（BP/CC/MF）与 KEGG；建议以 **PI3K-Akt、MAPK、HIF-1α、NF-κB、Nrf2、"
      "自噬与铁死亡**通路作为重点核查对象，因其在中药视网膜保护与 EON 机制中反复出现。")
    A("6. **分子对接与动力学**：AutoDock Vina / LeDock 对接，GROMACS 或 AMBER 进行 100 ns 分子动力学模拟，"
      "以 MM-PBSA/MM-GBSA 计算结合自由能并识别关键残基（可参考 PMID: 42257412 的做法）。")
    A("7. **实验验证**：至少应包含细胞活力（CCK-8）、ROS（DCFH-DA）、线粒体膜电位（JC-1）、"
      "凋亡（TUNEL / caspase-3）、自噬（LC3-II/Beclin-1/p62）与铁死亡（GPX4/SLC7A11/MDA/4-HNE）指标，"
      "并可优先使用 **hiPSC 来源 RGC 样细胞平台（PMID: 37540379）** 与 **RGC-5 / 661W / MIO-M1 细胞**。")
    A("")
    for i, c in enumerate(CANDIDATES, 1):
        A(f"### 7.{i+1} {c['name']}")
        A("")
        A(c["note"])
        A("")
        A(TPLAIN(["药味", "拉丁学名／药用部位", "主要活性成分（可检索英文名）",
                  "该药味的现代研究线索（真实 PMID）"],
                 [list(h) + [HERB_EVIDENCE.get(h[0], "")] for h in c["herbs"]]))
        A("")
    A("### 7.7 候选方药的选择理由与优先级建议")
    A("")
    A("| 优先级 | 方剂 | 理由 |")
    A("|---|---|---|")
    A("| **最高** | 驻景丸（Zhujing Wan） | 已有完整的网络药理学 + 代谢组学 + 分子对接 + 实验验证证据链，"
      "且明确记载于《太平圣惠方》用于「肝肾亏虚」所致目病，化学成分为已知 (PMID: 41967781)。可直接迁移到 EON 模型验证。 |")
    A("| **高** | 杞菊地黄丸（Qiju Dihuang Wan） | 方中枸杞子（LBP，含 meta 分析，PMID: 41467430）与菊花（木犀草素，PMID: 41162502）"
      "均有视网膜保护证据；组方简洁、成分明确，适合做机制清晰的基础研究。 |")
    A("| **高** | 益气聪明汤（Yiqi Congming Tang） | 方中葛根（葛根素，PMID: 41951163）、黄芪（黄芪甲苷IV，PMID: 42697404）"
      "均有视神经/视网膜保护证据；主治「清阳不升」之目昏，与视神经病变中医病机契合。 |")
    A("| **中** | 明目地黄丸（Mingmu Dihuang Wan） | 组成最全面（12 味），覆盖滋阴、养血、平肝、明目四法，"
      "但药味多、成分复杂，网络药理学结果的解释难度较大。 |")
    A("| **中** | 补中益气汤加味（Buzhong Yiqi Tang） | 适合「气虚型」青盲患者；加味药（枸杞子、菊花、葛根）证据明确，"
      "但原方六味药的视网膜特异性证据较弱，需以加味部分为研究重点。 |")
    A("")
    A("**综合建议**：若研究目标是「快速产出可发表的网络药理学 + 细胞/动物验证」结果，**优先选择驻景丸或杞菊地黄丸**；")
    A("若纳入中医辨证分型（气虚/清阳不升）作为立论依据，则选择**益气聪明汤或补中益气汤加味**更为自洽。")
    A("")
    A("---")
    A("")
    A("## 八、总结与本方向的空白点")
    A("")
    A("### 8.1 本次检索得到的三条主要结论")
    A("")
    A("1. **中医药干预视神经病变已有可用的高级别证据**：正常眼压性青光眼 24 周 RCT 显示针刺改善 BCVA、RNFL 厚度与眼压 "
      "(PMID: 41887338)；针刺联合解郁活血方治疗视神经萎缩 80 例 RCT 显示总有效率显著优于对照组 (PMID: 42114798)。")
    A("2. **中药单体对视网膜神经节细胞保护的机制与 EON 机制高度重叠**：Nrf2/HO-1、PI3K/Akt、NF-κB、NLRP3、"
      "自噬与铁死亡节点在两侧均反复出现，具备「机制对接」的可行性 (PMID: 24400114, PMID: 42743821, PMID: 41563626)。")
    A("3. **复方研究范式已经成熟**：化学表征 + 网络药理学 + 分子对接 + 在体/离体验证的「四联」设计成为主流 "
      "(PMID: 42210541, PMID: 41846099, PMID: 41840640)。")
    A("")
    A("### 8.2 明确的空白点")
    A("")
    A("| 空白点 | 说明 |")
    A("|---|---|")
    A("| **以乙胺丁醇视神经毒性（EON）为模型的中药干预研究** | **未检索到任何记录**。现有中药视网膜保护研究几乎全部使用糖尿病视网膜病变、青光眼或光损伤模型。"
      "这是本方向最直接、最具原创性的切入点。 |")
    A("| **决明子的视神经保护证据** | **未检索到**。尽管决明子为中医眼科常用药（清肝明目），本次检索未获得其对视神经或 RGC 保护作用的研究记录。 |")
    A("| **青盲／视瞻昏渺的中文文献系统证据** | Europe PMC 无法覆盖，本次检索**不能提供**。须另行检索 CNKI / 万方 / 维普 / SinoMed。 |")
    A("| **以视神经病变（而非 DR/青光眼）为适应证的复方网络药理学研究** | 数量很少。现有网络药理学研究绝大多数以 DR 为疾病靶点集。 |")
    A("| **中药单体在 EON 模型中的剂量–效应关系** | 未检索到。现有剂量数据均来自 DR 或青光眼模型，不能直接外推。 |")
    A("| **中药单体与乙胺丁醇的相互作用（药代动力学与减毒）** | 未检索到。这是一个尚未被探索的方向。 |")
    A("")
    A("---")
    A("")
    A("## 九、补充引用记录")
    A("")
    A("以下记录在正文中被引用但未单独成表，列出以供核查：")
    A("")
    extra = ["42257412", "42470246", "42539562"]
    rows = []
    for pm in extra:
        au, yr, jr, ti, doi = meta(pm)
        rows.append((au, yr, jr, ti))
        cite(pm)
    A(T(["第一作者", "年份", "期刊", "标题"], [(a, y, j, t, pm) for (a, y, j, t), pm
                                              in zip(rows, extra)]))
    A("")
    A("---")
    A("")
    body = "\n".join(L)
    ordered = []
    for m in re.finditer(r"PMID:\s*(\d{4,9})", body):
        if m.group(1) not in ordered:
            ordered.append(m.group(1))
    tail = [f"## 十、引用记录索引（共 {len(ordered)} 条）", "",
            "| # | 第一作者 | 年份 | 期刊 | PMID | DOI |",
            "|---|---|---|---|---|---|"]
    for i, pm in enumerate(ordered, 1):
        au, yr, jr, ti, doi = meta(pm)
        tail.append(f"| {i} | {au} | {yr} | {jr} | {pm} | {doi or '—'} |")
    tail += ["", "所有 PMID 均经 Europe PMC REST API 回查确认存在。"]
    text = body + "\n" + "\n".join(tail) + "\n"
    path = os.path.join(DOCS, "tcm_optic_neuropathy_background.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", path)
    print("lines:", len(text.splitlines()), "unique PMIDs:", len(ordered))


if __name__ == "__main__":
    main()

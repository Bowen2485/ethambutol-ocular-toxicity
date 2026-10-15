# -*- coding: utf-8 -*-
"""Append the MD-environment round to PROGRESS.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "PROGRESS.md"
t = P.read_text(encoding="utf-8")

ADD = """
---

## 八、全原子分子动力学：环境打通与首轮运行（2026-10-14 追加）

### 8.1 为什么换到 WSL

Windows 侧无法运行 OpenMM：`openmm-8.6.1` 与 `8.2.0` 的 win_amd64 wheel 都出现
**平台插件加载失败**（Windows 错误码 126）。用 ctypes 能加载同一批 DLL，但 OpenMM 自己的
加载器拒绝，且试遍 `OpenMM.libs/lib/`、`lib/plugins/`、`OPENMM_PLUGIN_DIR` 均无效。
**这是 wheel 打包问题，非配置问题。**

WSL（Ubuntu 24.04 + conda-forge）下 `['Reference', 'CPU', 'CUDA']` 三平台全部可用。

### 8.2 打通的七个障碍

| # | 障碍 | 根因 | 解决 |
|---|---|---|---|
| 1 | Windows wheel 插件加载失败 | 打包问题 | 改用 WSL + conda-forge |
| 2 | 以为构建名无 `cuda` 即 CPU 版 | **构建名不可作判据** | 以平台列表 + 建 Context 为准 |
| 3 | `n_rotatable_bonds` 不存在 | 猜 API | 改用 RDKit `Lipinski.NumRotatableBonds` |
| 4 | 配体坐标放大 10 倍 | conformer 是 **pint Quantity**，无 `value_in_unit`；SDF 坐标是埃 | 读 `.magnitude` + `.units`，显式 ÷10 |
| 5 | 配体模板未注册 | `molecules=` 属 `create_system` 而非 `__init__` | `gen.add_molecules([mol])` |
| 6 | `addSolvent` 报"未识别残基 JNI" | **JNI 是受体自带非标准残基**，非对接配体；且配体须在加溶剂之后插入 | `clean_receptors.py` + 调整顺序 |
| 7 | GAFF 报"无工具包可分配电荷" | **conda 把 antechamber 真品放 `bin/`，包装脚本在 `bin/wrapped_progs/` 遮蔽它** | PATH 前置 `bin/`，设 `AMBERHOME` |

**坑 2、6、7 的错误信息都会误导方向**，已详细记录在 `docs/MD环境踩坑记录_实测.md`。

### 8.3 新增文件

| 文件 | 用途 |
|---|---|
| `src/run_md_allatom.py` | 全原子 MD 主流程（PDBFixer → 加溶剂 → 插配体 → GAFF → 平衡 → 生产），**含四阶段断点续跑** |
| `src/analyse_md.py` | 按四判据出稳定性结论（配体 RMSD、受体 RMSD、接触存活率、回转半径） |
| `src/clean_receptors.py` | 剥离非模板化残基、保留指定辅因子 → `receptors_clean/` |
| `src/probe_all_apis.py` | **52 项穷举自检**，用真实输入验证每个 API 并打印真实签名 |
| `src/ligand_openmm.py` | 备用：不依赖 OpenFF 的配体参数化（Gasteiger + 手工项） |
| `run_in_wsl.sh` | 长任务用 `nohup` 在 WSL 内启动，**独立于编辑会话** |
| `docs/MD环境踩坑记录_实测.md` | 上表的详细版，含正确代码片段 |
| `docs/WSL配置与MD运行教程.md` | A–G 七级教程 |

诊断类脚本（31 个）已归档至 `src/diagnostics/`。

### 8.4 靶点规模实测（决定时间预算）

| 靶点 | 溶剂化后原子数 | 1 ns 预计 |
|---|---|---|
| **NFE2L2** (2FLU) | **45,545** | 约 1 小时 ✅ |
| BCL2 (5JSN) | 130,615 | 3–5 小时 |
| MFN2 (6JFM) | 389,131 | 10–15 小时 |
| TNF (5MU8) | 未测（54,511 蛋白原子，多聚体） | 更长 |

实测速度：**约 28 ns/day**（CUDA + mixed precision，含启动开销的下限）。

### 8.5 首轮运行

NFE2L2，1 ns。日志 `wsl_md_run.txt` 显示体系构建 → 最小化 → NVT 平衡全部成功，
checkpoint 机制生效。**结论待运行完成后回填。**

### 8.6 会话稳定性问题与应对

编辑会话崩溃三次，杀掉三个长任务（MD 两次、MR 一次）。

**对策**：所有长任务改用 `nohup` 在 WSL 内启动，日志写到 Windows 侧供直接读取。
MD 已加断点续跑（`minimise → nvt → npt → production`）。

### 8.7 MR 补全面临的网络障碍

WSL 提示"检测到 localhost 代理配置，但未镜像到 WSL"。

- **MD 不需要联网**，不受影响
- **MR 需要**：7 个暴露的结局扫描未缓存（含 BMI 阳性对照），需对 FinnGen 做 HTTP 范围请求
- 缓存现状：工具变量 **10/10 全部已缓存**；结局扫描已有 4,825 个（覆盖 eGFR、胱抑素 C、血清肌酐）

**三条退路**（见 `docs/期刊推荐与投稿信_重定位版.md` 之外的说明）：
① WSL 改用 `networkingMode=mirrored` + `autoProxy=true`；② 在 Windows 侧反复重启续跑；
③ **接受 3 个暴露并修改方法学表述**（结论不变，零额外耗时）。

### 8.8 HMOX1 血红素的未决问题

用户要求保留血红素。实测 `1N45_clean.pdb` 含 **2 个 HEM 残基、2 个铁原子**（晶体学二聚体，
仅一个为真实活性中心），且**无 CONECT 记录**，键级需靠感知。

已提取 `receptors_clean/1N45/HEM.pdb`。参数化方案未定，**成功与否尚未验证**。
"""

if "## 八、全原子分子动力学" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print(f"PROGRESS.md updated: {len(t):,} chars")
else:
    print("PROGRESS.md already contains the MD round")

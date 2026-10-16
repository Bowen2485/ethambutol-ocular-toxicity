# MD 生产段：搁置记录（2026-10-17）

> **结论先行**：MD 生产段**已搁置**，原因见第一节。搁置**不影响当前稿件**——
> §3.9b 的表述与现有 `results/md_allatom_stability_pbc.csv` 仍然自洽。
> 但本次尝试**意外抢救出 HMOX1 的 0.48 ns 生产段**（第三节），若要用它，
> 必须连带改写 §3.9b 的解读段，因此列为待作者决策，**未擅自改稿**。

---

## 一、为什么搁置

作者决定（2026-10-17）：**MD 运行会导致机器过热重启**，此前已发生一次，
曾中断多靶点运行。因此不再继续跑 GPU 生产段。

搁置时进程状态：WSL 已关闭、GPU 0%、温度 58 °C，无残留进程。

---

## 二、一个必须记录的设计事实：**续跑不可能**

`addSolvent` 的溶剂放置**不可复现**，因此每次重建体系原子数都不同：

| 时间 | 体系原子数 | 结果 |
|---|---|---|
| 10-09 / 10-14 首轮 | 78,429 | 停在 NVT+早期 NPT（0.23 ns） |
| 10-16 22:04 尝试 | 79,056 | 粒子数不符 → 丢弃 checkpoint，从 minimise 重跑 |
| 10-17 00:12 尝试 | 79,113 | 再次丢弃 checkpoint，从 minimise 重跑 |

`src/run_md_allatom.py` 自身已写明这一点：

> L466-470：*"A checkpoint can only be loaded into a system with the same particle count.
> addSolvent is not deterministic - two builds of the same BCL2 receptor gave …
> OpenMMException 'wrong number of particles', which aborted the whole target"*

运行日志亦原样记录（`logs/wsl_md_hmox1.txt`）：

```
[00:12:40] HMOX1: the checkpoint was built on 79056 atoms but this system has 79113,
           because solvent placement is not reproducible; discarding the checkpoint
           and running from the start
```

**后果**：checkpoint 守卫（本意是防止拿错体系的 checkpoint 污染模拟）使"断点续跑"
在现有实现下**永远无法生效**。每一次启动都必须从 minimise 重来，且必须
**一口气跑完** minimise → NVT(0.1 ns) → NPT(0.4 ns) → production(N ns)，
中途被打断就只剩该次尝试已写出的那一段轨迹。

这也解释了 HMOX1/MFN2 为何长期停在"0 生产帧"：它们不是跑得慢，而是**每次都被打断**。

---

## 三、本次抢救出来的东西（重要）

00:12–00:22 那次尝试**跑进了生产段**才被杀掉：

```
[00:13:37] HMOX1: checkpoint written after nvt
[00:13:37] HMOX1: NPT equilibration 400 ps
[00:17:37] HMOX1: checkpoint written after npt
[00:17:37] HMOX1: production 1.0 ns (500000 steps)      ← 已进入生产段
```

`md_allatom/HMOX1/md.log` 末行到 **step 495,000 = 990 ps**（累计 0.5 ns 平衡 + **0.49 ns 生产**），
轨迹 `traj_20261017-001249.dcd`（90 MB，98 帧，**未截断到不可读**）。

对这条轨迹重做 PBC 成像分析后（`analyse_md_pbc.py`，2026-10-17 于 WSL 运行）：

| 靶点 | 轨迹 | 帧数 | 总时长 | 配体 RMSD | 受体 RMSD | 接触数 | 最小距离 | 判定 |
|---|---|---|---|---|---|---|---|---|
| NFE2L2 | traj.dcd | 150 | 1.50 ns | 5.62 Å | 1.18 Å | 292→312 | 2.18 Å | 保持 |
| **HMOX1** | **traj_20261017-001249.dcd** | **98** | **0.98 ns** | **5.13 Å** | **1.44 Å** | **456→562** | **1.86 Å** | **保持** |
| MFN2 | traj_20261014-205604.dcd | 13 | 0.13 ns | 3.32 Å | 1.34 Å | 329→272 | 1.77 Å | 保持 |

即 **HMOX1 由"0.23 ns 平衡段、0 生产帧"变为"0.98 ns，其中约 0.48 ns 为非限制性生产段"**，
是原定"补跑生产段"目标的**部分达成**（目标 1.0 ns，实得约 0.48 ns）。

输出位置（**仅在 WSL，尚未回拷到工作副本**）：
`/home/bowen/ethambutol/results/md_allatom_stability_pbc.csv`

### 若要把这段抢救结果写进稿件，必须连带改的地方

现行稿件 §3.9b 的 HMOX1 行与解读文字是按**旧轨迹**（0.23 ns 平衡段）写的，
换成新轨迹后**不只是换数字**：

| 数值 | 稿件现值（旧轨迹） | 新轨迹 |
|---|---|---|
| 分析时长 | 0.23 ns（NVT + 早期 NPT） | 0.98 ns（含约 0.48 ns 生产段） |
| 配体 RMSD | 2.85 Å | **5.13 Å** |
| 受体 backbone RMSD | 1.28 Å | 1.44 Å |
| 接触数 | 601 → 670 | 456 → 562 |
| 最小配体–蛋白距离 | 1.76 Å | 1.86 Å |

其中**配体 RMSD 2.85 → 5.13 Å 会直接推翻稿件现有的解读句**：

> "…the one quantity that does differ is the ligand RMSD, and it differs in an informative
> direction: it is largest on NFE2L2 (5.62 Å) … and **smallest on HMOX1 (2.85 Å), where the
> pocket is a deep cavity**."

新值下 HMOX1（5.13 Å）不再是最小，该句必须重写。
另外 §3.9b 的**另两张表**（RMSF／极性接触、结合口袋残基）由
`analyse_md_extra.py`、`analyse_md_contacts.py`、`check_md_pocket.py` 等脚本产出，
**本次未重跑**，若采用新轨迹也需一并重算。

### 一个工具一致性陷阱

`src/write_md_pbc_v2.py` 是**生成器**（生成 `analyse_md_pbc.py`），不是分析器本身。
用它生成的分析器产出的 CSV 列只有 `ns_analysed`，**没有**现行
`results/md_allatom_stability_pbc.csv` 里的
`equilibration_frames / production_frames / ns_production / ns_trajectory_total / trajectory_phase`
五个列。也就是说**现行稿件的表来自比 `write_md_pbc_v2.py` 更新的脚本**，
重跑前须先确认用的是哪一版，否则会悄悄丢掉"生产帧/平衡帧"的计数。

---

## 四、各靶点现状（搁置时）

| 靶点 | state.json | 原子数 | 轨迹文件（WSL） | 目录大小 |
|---|---|---|---|---|
| NFE2L2 | `production` / 1.5 ns | 45,545 | `traj.dcd`（79 MB） | 93 MB |
| HMOX1 | `npt` / 0.5 ns | 79,113 | `traj_20261017-001249.dcd`（90 MB，98 帧） | 168 MB |
| MFN2 | `nvt` / 0.1 ns | 387,227 | `traj_20261014-205604.dcd`（58 MB，13 帧） | 174 MB |
| BCL2 | 无 checkpoint | 130,656 | 无（曾溶剂化但未产出轨迹） | 21 MB |
| TNF | 无 checkpoint | — | 无（从未启动） | 8.8 MB |

实测吞吐：45k 原子约 235 ns/day；79k 原子约 **157 ns/day**（本次 0.49 ns / 4.5 min）。
据此，MFN2（387k 原子，约为 HMOX1 的 4.9 倍）跑满 0.5 ns 平衡 + 1 ns 生产约需 **1 小时左右**
（注：`PROGRESS.md` §8.4 表里"MFN2 1 ns 需 10–15 小时"的旧估计与本实测不符，应以实测为准）。

---

## 五、若日后要续跑，怎么做

```bash
# 1) 启动（一次只跑一个靶点；必须在同一个 WSL 会话内跑完，中途被切断则本次作废）
wsl -d Ubuntu -- bash -c 'bash /mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox/run_production_segments.sh MFN2'

# 2) 看进度
wsl -d Ubuntu -- bash /home/bowen/ethambutol/check_md.sh

# 3) 跑完后的分析（CPU，不动 GPU）
wsl -d Ubuntu -- bash -c 'cd /home/bowen/ethambutol && /home/bowen/miniconda3/envs/md/bin/python src/analyse_md_pbc.py'
```

注意事项：
- **必须用托管后台作业承载**（`run_in_background`），不要用 `Start-Process` 脱离进程：
  2026-10-16 22:04 的脱离式启动在命令结束后即被回收，WSL 随之关闭，运行在 22:05:52 死掉。
- 跑之前确认 `~/ethambutol/results/md_allatom_stability_pbc.csv` 用的分析脚本版本
  （见第三节"工具一致性陷阱"）。
- 散热是硬约束：单次尝试若需 >30 分钟，应评估是否分次、或先解决散热。

---

## 六、对当前稿件的结论

**§3.9b 不改。** 现行表述（只有 NFE2L2 跑满 1 ns 生产段；HMOX1 0.23 ns、MFN2 0.13 ns
取自平衡阶段；三位点"一致但只是提示性而非结论性"）与其引用的
`results/md_allatom_stability_pbc.csv` 完全自洽，且已如实披露。本次抢救出的
0.48 ns 生产段**未采用**（理由见第三节）。

**已修正的一处独立缺陷（2026-10-17）。** 稿件 Methods §2.6b 原文写
*"Pose stability was judged on four quantities, all measured during production"*，
而 §3.9b 自己说明 HMOX1、MFN2 两处**没有任何生产帧**——方法句与结果自相矛盾。
现改为：

> *"Pose stability was judged on four quantities, measured over the analysed window of
> each trajectory — the unrestrained production segment where a run reached one, and
> otherwise the equilibration phases actually completed, labelled per target in
> Section 3.9b: …"*

同段末的 "every production metric" 相应改为 "every metric of a production window"。
改后 `src/final_audit.py` **71 项**、`src/audit_crosslanguage.py` **35 项**、
`src/verify_latex.py` **34 项**全部通过。

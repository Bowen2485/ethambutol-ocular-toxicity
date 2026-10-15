# MD 环境踩坑记录（WSL）

> 记录时间：2026-10-14
> 目的：这轮在 WSL 里配置 MD 时踩了七个坑，其中三个极易复发且错误信息会误导人。
> 本文只记录**经过实测确认**的结论，不写推测。

---

## 环境事实（已实测）

| 项目 | 值 |
|---|---|
| WSL | Ubuntu 24.04.3 LTS，kernel 6.6.87.2-microsoft-standard-WSL2 |
| GPU | NVIDIA GeForce RTX 5070 Ti Laptop，12,227 MiB，驱动 617.42 |
| conda | 用户原有的 `~/miniconda3`（非 miniforge3） |
| MD 环境 | `~/miniconda3/envs/md`，Python 3.12.15 |
| OpenMM | 8.6.1.dev-b399af4（conda-forge 构建 `py312hdfcc665_0`） |
| 平台 | `['Reference', 'CPU', 'CUDA']` ✅ |
| 相关包 | openff-toolkit 0.19.0、openmmforcefields 0.16.0、rdkit 2026.03.1、mdtraj 1.11.2 |
| 实测速度 | 约 28 ns/day（45,000 原子体系，CUDA + mixed precision，含启动开销的下限） |

---

## 坑 1：conda-forge 的 OpenMM 构建名不含 `cuda`，但**确实带 CUDA**

**错误认知**：看到构建名 `py312hdfcc665_0` 里没有 `cuda`，就以为装成了纯 CPU 版，打算重装。

**事实**：这个构建**注册了可用的 CUDA 平台**，`CUDA context built OK on platform: CUDA`。

**教训**：**构建字符串无法用来判断是否支持 CUDA。唯一可靠的判据是平台列表本身**：

```bash
~/miniconda3/envs/md/bin/python -c "
import openmm
print([openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])"
# 看到 'CUDA' 才算数
```

而且**列平台还不够**——要真正建立 Context 才算通过（脚本第 4 步就是干这个的）。

---

## 坑 2（最隐蔽）：`wrapped_progs` 遮蔽 antechamber，导致 GAFF 报出误导性错误

**症状**：

```
ValueError: No registered toolkits can provide the capability
            "assign_partial_charges" for args "()" and kwargs "{'molecule': ...}"
```

这个错误会让人以为是 **OpenFF 与 openmmforcefields 版本不兼容**（注册表查询确实也抛了 `AttributeError: 'ToolkitRegistry' object has no attribute 'list_available_toolkits_for_capability'`）。

**真实原因**：conda 的 AmberTools 把可执行文件放在 `envs/md/bin/`，同时又放了一份**包装脚本**在 `envs/md/bin/wrapped_progs/`。`shutil.which('antechamber')` 找到的是包装脚本 → 路径判定为"不可用" → OpenFF 认为没有电荷后端 → 报出上面那句与真实原因无关的错误。

**修复**（`run_md_allatom.py` 的 `configure_ambertools()` 已自动做这件事）：

```bash
export PATH="$HOME/miniconda3/envs/md/bin:$PATH"    # 注意：不是 wrapped_progs
export AMBERHOME="$HOME/miniconda3/envs/md"
```

**验证**：

```bash
which antechamber   # 应为 .../envs/md/bin/antechamber
```

修复后，`gaff-2.11`、`gaff-2.2.20`、`openff-2.1.0`、`openff-2.2.0` **全部可用**。

---

## 坑 3：openff-toolkit 0.19 的 conformer 是 **pint Quantity**，不是 OpenMM Quantity

**症状**：

```
AttributeError: Neither Quantity object nor its magnitude (...) has attribute 'value_in_unit'
```

**原因**：`mol.conformers[0]` 返回 pint `Quantity`，它**没有 `value_in_unit()` 方法**——那是 OpenMM 单位系统的方法。pint 用 `.magnitude` 与 `.units`。

**实测确认**：

```
mol.conformers[0] type -- Quantity, has value_in_unit=False,
                          has magnitude=True, units=<Unit('angstrom')>
```

**正确写法**：

```python
conf = mol.conformers[0]
mag = conf.magnitude                    # numpy 数组
uname = str(conf.units)                 # 'angstrom'
coords_nm = np.asarray(mag) / 10.0 if 'angstrom' in uname.lower() else np.asarray(mag)
```

**注意**：PubChem 的 SDF 坐标是**埃**，必须 ÷10 转纳米。乙胺丁醇转换后跨度应为 **1.09–1.15 nm**（若看到 11 左右说明漏了转换）。

---

## 坑 4：`np.asarray()` 作用于 OpenMM `Vec3` 列表会生成 object 数组

**症状**：

```
TypeError: unsupported operand type(s) for +: 'float' and 'Quantity'
   lig_pos = ... + np.asarray(pos_rec).mean(axis=0)
```

**原因**：`np.asarray()` 对 Vec3 列表生成的是 **object 数组**，元素内含 Quantity，所以算术类型不匹配。

**正确写法**（`positions_to_array()` 已封装）：

```python
def positions_to_array(positions):
    out = np.empty((len(positions), 3), dtype=float)
    for i, p in enumerate(positions):
        try:
            v = p.value_in_unit(unit.nanometer)     # 带单位的 Vec3
            out[i] = (v.x, v.y, v.z)
        except AttributeError:
            try:
                out[i] = (float(p.x), float(p.y), float(p.z))
            except AttributeError:
                out[i] = (float(p[0]), float(p[1]), float(p[2]))
    return out
```

---

## 坑 5：`addSolvent` 必须在**配体加入之前**调用

**症状**：

```
ValueError: No template found for residue 6955 (JNI) ...
Did not recognize residue JNI; did you forget to call .add_molecules() to add it?
```

**两个独立的坑叠在一起**：

1. **顺序问题**：`Modeller.addSolvent` 内部会构建体系。若拓扑里已有配体，而它用的 `ForceField` 看不到配体模板，就会失败。`gen.add_molecules()` 帮不上忙，因为 `addSolvent` **不走 SystemGenerator**。

   **正确顺序**：
   ```python
   modeller = app.Modeller(rec_top, rec_pos)      # 只有蛋白
   gen.add_molecules([mol])                       # 注册配体参数
   modeller.addSolvent(gen.forcefield, ...)       # ← 此时无配体，可成功
   modeller.add(lig_top, lig_pos)                 # ← 再插入配体
   ```

2. **`JNI` 不是配体**：错误信息里的 `JNI` 是**受体文件自带的非标准残基**（TNF 结构 5MU8 里有 1794 个原子），不是对接的乙胺丁醇。**这句错误信息会把人引向错误方向**——我因此误判过一轮。

   **处理**：用 `src/clean_receptors.py` 剥离非标准残基后再跑。

---

## 坑 6：受体文件普遍含非模板化残基

实测各受体文件（`src/probe_nonstandard_residues.py`）：

| 受体 | 非标准内容 | 处理 |
|---|---|---|
| 5MU8 (TNF) | `JNI` × 1794 原子 | 剥离（剩 54,511 蛋白原子，**体系过大**） |
| 9TMV | `UNK` × 3306 原子 | 剥离 |
| 9KC4 (SDHB) | `FAD`/`HEM`/`SF4`/`F3S`/`FES` | **功能辅因子，需单独参数化** |
| 1N45 (HMOX1) | `HEM` × 86 原子 | **血红素需保留并参数化** |
| 7UX2 | `GTP`/`GDP` | 剥离或参数化 |
| 6JFM (MFN2) | `ACT`×8、`CA`×3 | 剥离 |
| **2FLU (NFE2L2)、5JSN (BCL2)** | **无** | 干净 |

**只剥离添加剂、保留辅因子的脚本**：`src/clean_receptors.py`，产物在 `receptors_clean/`。

---

## 坑 7：体系规模差异极大，选错靶点会浪费大量时间

同样是"一个 hub 靶点"，溶剂化后的规模差 8 倍：

| 靶点 | 溶剂化后原子数 | 1 ns 预计耗时 |
|---|---|---|
| **NFE2L2** (2FLU) | **45,545** | **约 1 小时** ✅ 首选 |
| BCL2 (5JSN) | 130,615 | 3–5 小时 |
| MFN2 (6JFM) | 389,131 | 10–15 小时 ❌ |
| TNF (5MU8) | 未测（54,511 蛋白原子，多聚体） | 更长，12 GB 显存可能不足 |

**教训**：跑之前先看溶剂化后的原子数（脚本会打印），别直接按"靶点数"估时间。

---

## 附：一次性自检脚本

`src/probe_all_apis.py` —— **穷举验证 MD 流程用到的每个 API**，用真实输入、不 mock，逐项报通过/失败并打印真实签名。

这次它一次暴露了全部剩余问题（52 项检查）。**新增或修改 MD 代码后应先跑它**：

```bash
~/miniconda3/envs/md/bin/python ~/ethambutol/src/probe_all_apis.py 2>&1 \
  | tee "/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox/wsl_feedback.txt"
```

---

## 附：长任务要独立于编辑会话

编辑会话崩溃三次，杀掉了三个长任务（MD 两次、MR 一次）。

**根因**：会话启动的后台任务随会话存活。

**解决**：用 `nohup` 在 WSL 里直接跑，与编辑器无关：

```bash
bash ~/ethambutol/run_in_wsl.sh md      # 或 mr / both
bash ~/ethambutol/run_in_wsl.sh status  # 查进度
```

MD 已加**四阶段断点续跑**（`minimise → nvt → npt → production`，各写一次 checkpoint），中断后重启会自动从上次完成的阶段继续。

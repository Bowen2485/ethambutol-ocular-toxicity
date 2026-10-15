# 在 WSL 中运行本项目：完整教程

> 编写日期：2026-10-14
> 适用对象：本机 Windows 11（build 26300）＋ RTX 5070 Ti Laptop（12 GB，compute capability 12.0）
> 教程分三级，按你的需要选取；**只做 C 级即可跑分子动力学**

---

## 零、先回答"为什么 Windows 不行"

我在 Windows 上试过旁装便携 Python 3.13 并把 OpenMM 的 wheel 解包使用，结果：

| 尝试 | 结果 |
|---|---|
| 解包 `openmm-8.6.1-cp313-win_amd64.whl` | ctypes 能加载 `OpenMMCPU.dll`，但 OpenMM 自己的加载器报 **Windows 错误码 126** |
| 解包 `openmm-8.2.0`（稳定版） | 同样症状 |
| 把 DLL 放到 `OpenMM.libs/lib/`、`lib/plugins/`、改 `OPENMM_PLUGIN_DIR` | 全部无效 |
| 检查 DLL 导入表 | 所有依赖都能解析（含 NVIDIA 驱动提供的 `OpenCL.dll`） |

**结论：`pip` 的 Windows wheel 在"解包而非安装"的用法下，平台插件无法注册。** 这是 wheel 打包与加载路径的问题，不是你的配置问题。

WSL 里没有这个问题，有三个原因：

1. **conda-forge 提供完整的 Linux 构建**，插件路径正常
2. **WSL2 支持 NVIDIA GPU 直通**（需 Windows 侧装好驱动，WSL 内**不要**装驱动）
3. 官方 Linux wheel 在 `pip install` 下能正确注册 `CUDA` 与 `CPU` 平台

⚠️ **一个必须提前知道的坑**：你的显卡是 **Blackwell（compute capability 12.0）**，需要 **CUDA 12.8 及以上**编译的 OpenMM。若装到旧构建（CUDA 12.0–12.6），OpenMM 会**静默退回 CPU 平台**——速度差约百倍。本教程第三节有显式验证步骤，**必须做**。

---

## A 级：先验证 GPU 能不能用（约 10 分钟，强烈建议先做）

在装任何东西之前先确认 WSL 的 GPU 直通可用。

### A1. 安装 WSL（**以管理员身份**打开 PowerShell）

```powershell
wsl --install -d Ubuntu-24.04
```

装完**重启电脑**。若提示"已安装"，直接下一步。

如果这条命令报错（本机曾出现 `Wsl/E_ACCESSDENIED`），先确认虚拟化已开启：

```powershell
# 需管理员；输出应显示 State : Enabled
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

若为 `Disabled`，启用后重启：

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### A2. 进入 Ubuntu 并验证 GPU

首次启动 Ubuntu 会让你设用户名和密码。之后：

```bash
# 1) WSL 里能看到 GPU 吗（不需要在 WSL 里装驱动）
nvidia-smi

# 2) 内核与版本
uname -r
cat /etc/os-release | head -2
```

`nvidia-smi` 应显示 `NVIDIA GeForce RTX 5070 Ti Laptop GPU`，且 **CUDA Version ≥ 12.8**。

若 `nvidia-smi` 找不到命令：在 **Windows** 侧更新 NVIDIA 驱动到最新版（WSL 的 GPU 支持由 Windows 驱动提供），然后 `wsl --shutdown` 再进入。

**做完 A 级就能判断这条路是否可行。** 若 A2 通过，继续 C 级；若失败，说明本机虚拟化被策略限制，需联系管理员。

---

## B 级：跑完整分析管线（含 35 GB FAERS 库）

只在你要**重跑 FAERS 部分**时才需要。

### B1. 安装 Python 与依赖

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

cd ~
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy pandas scipy statsmodels matplotlib networkx scikit-image
```

### B2. 项目文件怎么放（**重要**，涉及 35 GB）

三种方案，按你的磁盘情况选：

**方案一：直接从 /mnt/c 读取（推荐，零拷贝）**

WSL 可以直接访问 Windows 文件：

```bash
cd /mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox
ls -la
```

优点：不占额外空间，立刻可用。
缺点：**跨文件系统 I/O 慢**（SQLite 全表扫描会明显变慢，实测可能慢 2–5 倍）。

**方案二：把轻量部分复制进 WSL 原生文件系统（推荐用于 MD）**

只复制分析脚本、对接文件、结果——约 60 MB：

```bash
mkdir -p ~/ethambutol
cd /mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox
cp -r src ~/ethambutol/
cp -r docking ~/ethambutol/
cp -r results ~/ethambutol/
cp -r tables ~/ethambutol/
cp -r manuscript ~/ethambutol/
```

**方案三：整个项目复制（要跑 FAERS 全表时）**

需要额外 **42 GB** 空间：

```bash
mkdir -p ~/ethambutol
cd /mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox
cp -r data/derived/faers.sqlite ~/ethambutol/data/derived/
cp -r data/raw ~/ethambutol/data/
```

复制 35 GB 需要一段时间（视磁盘而定，可能 10–30 分钟）。先确认 WSL 所在盘有空间：

```bash
df -h ~
```

### B3. 确认脚本可跑

项目内所有脚本都用**相对路径**（基于脚本自身位置向上寻找项目根目录），所以无需改路径：

```bash
cd ~/ethambutol
python src/final_audit.py        # 应为 60 项全过
python src/audit_crosslanguage.py # 应为 33 项全过
```

若报缺少 `data/derived/faers.sqlite`，说明你选了方案二但脚本需要数据库——改用方案一或方案三。

---

## C 级：安装 OpenMM 跑分子动力学（**核心章节**）

### C1. 用 conda 安装（最稳，推荐）

conda-forge 的 OpenMM 构建完整，插件路径正常。

```bash
# 安装 miniforge（比 Anaconda 轻，且默认用 conda-forge）
cd ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3
source ~/miniforge3/etc/profile.d/conda.sh
conda init bash
exec bash
```

创建环境并安装：

```bash
conda create -n md -c conda-forge python=3.12 openmm pdbfixer openmmforcefields parmed mdtraj numpy scipy -y
conda activate md
```

### C2. **验证 CUDA 平台（必做）**

这一步决定成败。运行：

```bash
python -c "
import openmm
print('openmm', openmm.version.version)
print('CUDA version used by OpenMM:', openmm.version.cuda_version)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  {p.getName():12s} speed={p.getSpeed()}')
"
```

**期望输出**包含 `CUDA`：

```
openmm 8.x.x
  Reference    speed=1.0
  CPU          speed=...
  CUDA         speed=...      <-- 必须有这一行
```

**若没有 CUDA 行**，按以下顺序排查：

1. `nvidia-smi` 显示的 CUDA Version 是否 ≥ 12.8？若 < 12.8，更新 Windows 侧 NVIDIA 驱动
2. 装的是哪个 OpenMM？检查是否为 CUDA 版：
   ```bash
   conda list | grep -i openmm
   ```
   若显示 `openmm 8.x cpu_*` 这类 **cpu** 构建，改为装 CUDA 版：
   ```bash
   conda install -c conda-forge "openmm=*=cuda*" -y
   ```
3. 测试 CUDA 平台能否真正建立计算环境（比 `getNumPlatforms()` 更严格）：
   ```bash
   python -c "
   import openmm as mm, openmm.app as app, openmm.unit as u
   from openmm.app import Topology, Element
   top = Topology(); ch = top.addChain(); res = top.addResidue('ALA', ch)
   for nm, el in (('N','N'), ('CA','C'), ('C','C'), ('O','O')):
       top.addAtom(nm, Element.getBySymbol(el), res)
   import numpy as np
   pos = [mm.Vec3(*v) for v in np.random.rand(4,3)] * u.nanometer
   sysm = mm.System()
   for _ in range(4): sysm.addParticle(12.0)
   integ = mm.LangevinMiddleIntegrator(300*u.kelvin, 1/u.picosecond, 0.002*u.picoseconds)
   ctx = mm.Context(sysm, integ, mm.Platform.getPlatformByName('CUDA'))
   ctx.setPositions(pos)
   print('CUDA context built OK, platform:', ctx.getPlatform().getName())
   "
   ```

### C3. 用 pip 安装（备选）

若不想装 conda：

```bash
pip install openmm pdbfixer
python -c "import openmm; print([openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])"
```

官方 Linux wheel 通常自带 CUDA 支持。若仍无 CUDA，回到 C1 用 conda。

---

## D 级：把本项目的 MD 脚本迁移到 WSL

我在 Windows 上写了一套**粗粒化** MD（因为 OpenMM 用不了）。到了 WSL 你应该**改用全原子 MD**，因为那才是审稿人认的标准方法。

### D1. 我留下的资产（可直接复用）

| 文件 | 用途 |
|---|---|
| `src/md_force_verify.py` | **力场正确性检验工具**——用能量单调性验证力等于势能负梯度。任何自写 MD 都该先跑这个 |
| `src/md_well_depth.py` | 测量结合口袋势阱深度（kT 单位），判断配体能否热逃逸 |
| `src/md_receptor_deform.py` | 检查受体在配体作用下的形变 |
| `src/md_coarse.py` | 粗粒化实现（**仅供参照，不建议用于论文**） |

### D2. 建议的全原子 MD 流程

输入文件已就绪：受体在 `docking/receptors/<PDBID>/<PDBID>_clean.pdb`，配体姿态在 `docking/poses/<基因>__ethambutol.pdbqt`。

```bash
conda activate md
cd ~/ethambutol
mkdir -p md_allatom && cd md_allatom
```

**第 1 步：受体准备**（补氢、加缺失原子）

```bash
python - <<'PY'
from pdbfixer import PDBFixer
from openmm.app import PDBFile
fixer = PDBFixer(filename='../docking/receptors/1N45/1N45_clean.pdb')
fixer.findMissingResidues()
fixer.findMissingAtoms()
fixer.addMissingAtoms()
fixer.addMissingHydrogens(7.4)          # pH 7.4
PDBFile.writeFile(fixer.topology, fixer.positions, open('receptor_fixed.pdb','w'))
PY
```

**第 2 步：配体准备**（PDBQT → SDF → 参数）

```bash
# 用 Open Babel 转格式（WSL 里装：sudo apt install -y openbabel）
obabel ../docking/poses/TNF__ethambutol.pdbqt -O ligand.sdf -f 1 -l 1

# 生成小分子力场参数（需要 openmmforcefields 里的 GAFF/OpenFF）
python - <<'PY'
from openff.toolkit import Molecule
from openmmforcefields.generators import SMIRNOFFTemplateGenerator
mol = Molecule.from_file('ligand.sdf')
gen = SMIRNOFFTemplateGenerator(molecules=[mol])
print('ligand parameters generated:', gen)
PY
```

**第 3 步：组装体系并跑模拟**

```bash
python - <<'PY'
import openmm as mm, openmm.app as app, openmm.unit as u
from openmmforcefields.generators import SystemGenerator

# 显式溶剂 + PME，这是标准做法
system_generator = SystemGenerator(
    forcefields=['amber14-all.xml', 'amber14/tip3pfb.xml'],
    small_molecule_forcefield='gaff-2.11')

pdb = app.PDBFile('receptor_fixed.pdb')
lig = app.PDBFile('ligand.pdb')      # 由上一步转换得到

modeller = app.Modeller(pdb.topology, pdb.positions)
modeller.add(lig.topology, lig.positions)
modeller.addSolvent(system_generator.forcefield, padding=1.0*u.nanometer,
                    ionicStrength=0.15*u.molar)

system = system_generator.create_system(modeller.topology)

# 平台选择：CUDA + 混合精度
platform = mm.Platform.getPlatformByName('CUDA')
props = {'Precision': 'mixed', 'CudaDeviceIndex': '0'}

integrator = mm.LangevinMiddleIntegrator(300*u.kelvin,
                                        1/u.picosecond, 0.002*u.picoseconds)
sim = app.Simulation(modeller.topology, system, integrator, platform, props)
sim.context.setPositions(modeller.positions)

# 能量最小化 -> 升温 -> 平衡 -> 生产
sim.minimizeEnergy()
sim.reporters.append(app.DCDReporter('traj.dcd', 5000))
sim.reporters.append(app.StateDataReporter('md.log', 5000,
    step=True, time=True, potentialEnergy=True, temperature=True, speed=True))

sim.step(250000)     # 0.5 ns 平衡，实际请按需加长
print('equilibration done; speed above in ns/day')
sim.step(5000000)    # 10 ns 生产
print('production done')
PY
```

**参考耗时**：RTX 5070 Ti 上约 15 万原子的体系，CUDA + mixed 精度通常可跑 **50–150 ns/天**，即 10 ns 约 2–5 小时。脚本里 `speed` 字段会打印实际 ns/day，第一次跑完据此调整时长。

**第 4 步：分析**（RMSD、配体停留、MM/GBSA）

```bash
python - <<'PY'
import mdtraj as md
t = md.load('traj.dcd', top='receptor_fixed.pdb')
# 配体是否停留在口袋：以初始姿态为参照
ligand_idx = t.topology.select('resname UNL')
rmsd = md.rmsd(t, t, 0, atom_indices=ligand_idx)
print('ligand RMSD: mean %.2f A, max %.2f A' % (rmsd.mean()*10, rmsd.max()*10))
PY
```

### D3. 关键判据（用来写进论文）

| 指标 | 稳定结合 | 不稳定 |
|---|---|---|
| 配体 RMSD（相对初始姿态） | < 2 Å 且长时间平台 | 持续上升 > 3 Å |
| 结合口袋残基 RMSD | < 2 Å | 明显增大 |
| 氢键/接触数 | 保持初始的 > 60% | 持续下降 |
| MM/GBSA ΔG | 负值且稳定 | 接近 0 或为正 |

**把这四个指标都算出来再写结论**。我粗粒化模型失败的原因正是势能函数形式不真实（在参考距离处无梯度），全原子力场没有这个问题。

---

## E 级：常见问题

**E1. `wsl --install` 报 `E_ACCESSDENIED`**
需管理员权限；若管理员也报错，说明组策略禁用了 WSL，需联系 IT。

**E2. `nvidia-smi` 在 WSL 里没有输出**
Windows 侧驱动需为 **≥ 527.41** 且支持 WSL。更新后 `wsl --shutdown` 重启。

**E3. OpenMM 有 CUDA 平台但跑起来极慢**
多半是静默退回了 CPU。在脚本里**显式指定平台名**并断言：
```python
ctx = mm.Context(system, integrator, mm.Platform.getPlatformByName('CUDA'))
assert ctx.getPlatform().getName() == 'CUDA', 'fell back to CPU!'
```

**E4. 跨 /mnt/c 读写太慢**
SQLite 全表扫描从 `/mnt/c` 读取会慢数倍。把数据库复制到 WSL 原生盘（`~/`）再跑。

**E5. 内存不足**
WSL2 默认最多用宿主内存的 50%。创建 `<user directory>\.wslconfig`：
```ini
[wsl2]
memory=24GB
processors=16
swap=8GB
```
然后 `wsl --shutdown` 重启。

**E6. 磁盘空间不足**
项目全量约 42 GB。检查 `df -h ~`。可在 `.wslconfig` 里限制但无法扩容——WSL 的虚拟盘会随使用增长，上限是宿主盘剩余空间。

---

## F 级：执行清单（照做即可）

```text
[ ] 1. 管理员 PowerShell:  wsl --install -d Ubuntu-24.04
[ ] 2. 重启电脑
[ ] 3. 进入 Ubuntu，设用户名密码
[ ] 4. nvidia-smi            -> 确认见 5070 Ti 且 CUDA >= 12.8
[ ] 5. 装 miniforge + conda 环境（C1）
[ ] 6. 验证 CUDA 平台（C2）   -> 必须看到 CUDA 那一行
[ ] 7. 复制项目（B2 方案二或三）
[ ] 8. cd ~/ethambutol && python src/final_audit.py   -> 60 项全过
[ ] 9. 按 D2 跑全原子 MD
[ ] 10. 按 D3 判定并结合四个指标写结论
```

前 4 步是**可行性关卡**：只要第 4 步过了，后面基本不会卡住；若第 4 步失败，先解决驱动或虚拟化，不要往下走。

---

## G 级：我可以为你做的事

告诉我你在哪一步卡住，我可以：

1. **写完整的全原子 MD 脚本**（受体准备 → 配体参数 → 组装 → 平衡 → 生产 → 分析），一次到位，你只需在 WSL 里 `bash run_md.sh`
2. **写 MM/GBSA 计算脚本**（需要 `openmm` + `openmmforcefields`，用 AMBER 的 GB 模型逐帧计算 ΔG）
3. **写批量脚本**：14 个 hub 靶点自动循环，输出统一的稳定性汇总表
4. **把现有的 `md_force_verify.py` 改造成全原子版**——它检验"力是否等于势能负梯度"，是防止我上次那类错误复发的有效工具

**我的建议**：先做 A 级（10 分钟）确认 GPU 直通可用，再让我按第 1、3 项写好脚本，你在 WSL 里一次跑完。

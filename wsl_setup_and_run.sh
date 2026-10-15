#!/usr/bin/env bash
# =============================================================================
# WSL setup and run script for the ethambutol MD work.   (v2)
#
# Run inside WSL (Ubuntu), from the project root:
#     cd /mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox
#     bash wsl_setup_and_run.sh
#
# v2 fixes, after the first run failed:
#   * the interpreter is addressed by absolute path instead of relying on
#     `conda activate`, which did not take effect and left the Python checks
#     running under the base environment (they reported "No module named openmm")
#   * an existing conda installation is detected and reused rather than a second
#     one being installed alongside it
#   * the OpenMM build string is inspected, because conda-forge also ships
#     CPU-only builds and those would silently run roughly 100x slower
# =============================================================================
set -uo pipefail

# Resolve the project from this script's own location.  Using $PWD was wrong: the
# script may be invoked from elsewhere (for example /mnt/c/... rather than the copy
# under $HOME), and the later `cd "$PROJECT"` would then operate on the wrong tree.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT="${PROJECT:-$SCRIPT_DIR}"
ENV_NAME="${ENV_NAME:-md}"
NS="${NS:-10}"
TARGETS="${TARGETS:-TNF HMOX1 MFN2 NFE2L2 BCL2}"
CUDA_MAJOR_NEEDED=12
CUDA_MINOR_NEEDED=8

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[warning] %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m[fail] %s\033[0m\n' "$*" >&2; exit 1; }

# --------------------------------------------------------------------- step 0
say "Step 0: environment facts"
echo "  user    : $(whoami)"
echo "  kernel  : $(uname -r)"
echo "  distro  : $(. /etc/os-release && echo "$PRETTY_NAME")"
echo "  project : $PROJECT"
[ -f "$PROJECT/src/run_md_allatom.py" ] || \
  die "src/run_md_allatom.py not found under $PROJECT - run this from the project root"

# --------------------------------------------------------------------- step 1
say "Step 1: GPU visibility"
command -v nvidia-smi >/dev/null 2>&1 || die "nvidia-smi not found.
  The GPU comes from the *Windows* driver; do not install one inside WSL.
  Update the Windows NVIDIA driver, then:  wsl --shutdown   (from Windows)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
# the driver's CUDA version appears in the nvidia-smi banner, not in --query-gpu
CUDA_VER=$(nvidia-smi 2>/dev/null | sed -n 's/.*CUDA Version: *\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -1)
echo "  driver CUDA version: ${CUDA_VER:-not reported}"
if [ -n "${CUDA_VER:-}" ]; then
  MAJ=${CUDA_VER%%.*}; MIN=${CUDA_VER##*.}
  if [ "$MAJ" -lt "$CUDA_MAJOR_NEEDED" ] || \
     { [ "$MAJ" -eq "$CUDA_MAJOR_NEEDED" ] && [ "$MIN" -lt "$CUDA_MINOR_NEEDED" ]; }; then
    warn "CUDA $CUDA_VER is older than ${CUDA_MAJOR_NEEDED}.${CUDA_MINOR_NEEDED}.
  An RTX 50-series card needs CUDA 12.8+ for OpenMM's CUDA platform.
  Update the Windows NVIDIA driver, then re-run."
  fi
fi

# --------------------------------------------------------------------- step 2
say "Step 2: locate conda"
CONDA_BASE=""
for cand in "$HOME/miniforge3" "$HOME/miniconda3" "$HOME/anaconda3" /opt/conda; do
  if [ -x "$cand/bin/conda" ]; then CONDA_BASE="$cand"; break; fi
done
if [ -z "$CONDA_BASE" ] && command -v conda >/dev/null 2>&1; then
  CONDA_BASE=$(conda info --base 2>/dev/null || true)
fi
if [ -z "$CONDA_BASE" ] || [ ! -x "$CONDA_BASE/bin/conda" ]; then
  echo "  no conda found; installing miniforge into \$HOME/miniforge3 ..."
  URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
  if command -v wget >/dev/null 2>&1; then wget -q "$URL" -O /tmp/mf.sh
  else curl -fsSL "$URL" -o /tmp/mf.sh; fi
  bash /tmp/mf.sh -b -p "$HOME/miniforge3" || die "miniforge install failed"
  CONDA_BASE="$HOME/miniforge3"
fi
echo "  using conda at: $CONDA_BASE"
"$CONDA_BASE/bin/conda" --version || die "conda is not runnable"

# --------------------------------------------------------------------- step 3
say "Step 3: create the '$ENV_NAME' environment"
ENV_PREFIX="$CONDA_BASE/envs/$ENV_NAME"
if [ -x "$ENV_PREFIX/bin/python" ]; then
  echo "  environment already exists at $ENV_PREFIX"
else
  "$CONDA_BASE/bin/conda" create -y -p "$ENV_PREFIX" -c conda-forge \
    python=3.12 openmm pdbfixer openmmforcefields openff-toolkit \
    parmed mdtraj numpy scipy pandas || die "conda create failed"
fi
PY="$ENV_PREFIX/bin/python"
[ -x "$PY" ] || die "interpreter not found at $PY"

# Everything below calls "$PY" directly.  Relying on `conda activate` is what broke
# the first attempt: the activation did not persist and the checks ran under base,
# reporting "No module named openmm" even though the environment was fine.
echo "  interpreter: $PY"
"$PY" -c "import sys; print('  python     :', sys.version.split()[0])"
"$PY" -c "import openmm; print('  openmm     :', openmm.version.version)" \
  || die "openmm is not importable from $PY"

say "Step 3b: OpenMM build variant"
BUILD=$("$CONDA_BASE/bin/conda" list -p "$ENV_PREFIX" openmm 2>/dev/null | awk '/^openmm/{print $3}')
echo "  build string: ${BUILD:-unknown}"
# Informational only.  The build string is NOT a reliable guide: conda-forge's
# openmm 8.6.1 py312hdfcc665_0 carries no "cuda" in its name yet registers a working
# CUDA platform, so the platform list from Python (next step) is the only trustworthy
# test.  An earlier version of this script treated a missing "cuda" in the build
# string as a problem and would have reinstalled the package needlessly.
echo "  (not a reliable indicator - step 4 tests the platform directly)"

# --------------------------------------------------------------------- step 4
say "Step 4: verify a CUDA context can actually be built"
"$PY" - <<'PY' || exit 1
import sys
import openmm as mm
print(f"  openmm {mm.version.version}")
try:
    print(f"  CUDA runtime the build expects: {mm.version.cuda_version}")
except Exception:
    print("  this build does not report a CUDA version")
names = [mm.Platform.getPlatform(i).getName()
         for i in range(mm.Platform.getNumPlatforms())]
print(f"  platforms: {names}")

if "CUDA" not in names:
    print("""
  The CUDA platform is not registered.  Checks, in order:
    1. driver CUDA >= 12.8?          nvidia-smi
    2. is this a CPU-only build?     see the build string printed in step 3b
       fix:  conda install -p <env> -c conda-forge 'openmm=*=cuda*' -y
    3. after changing the build:     conda clean -a   then reinstall
""")
    sys.exit(1)

# listing a platform is weaker than using it, so build a real context
import numpy as np
import openmm.unit as u
sysm = mm.System()
for _ in range(1000):
    sysm.addParticle(12.0)
sysm.setDefaultPeriodicBoxVectors(mm.Vec3(4,0,0), mm.Vec3(0,4,0), mm.Vec3(0,0,4))
nb = mm.NonbondedForce()
nb.setNonbondedMethod(mm.NonbondedForce.CutoffPeriodic)
nb.setCutoffDistance(1.0)
for _ in range(1000):
    nb.addParticle(0.0, 0.3, 0.05)
sysm.addForce(nb)
integ = mm.LangevinMiddleIntegrator(300*u.kelvin, 1/u.picosecond, 0.002*u.picoseconds)
ctx = mm.Context(sysm, integ, mm.Platform.getPlatformByName("CUDA"))
ctx.setPositions([mm.Vec3(*v) for v in np.random.rand(1000,3)] * u.nanometer)
ctx.getState(getEnergy=True)
print(f"  CUDA context built OK on platform: {ctx.getPlatform().getName()}")
PY
STATUS=$?
[ $STATUS -eq 0 ] || die "the CUDA platform is not usable - see the guidance above"

# --------------------------------------------------------------------- step 5
say "Step 5: project checks"
cd "$PROJECT" || die "cannot enter $PROJECT"
[ -f docking/results.csv ] || die "docking/results.csv not found"
[ -f docking/ligands/ethambutol/pubchem_3d.sdf ] || die "ligand SDF not found"
echo "  docking rows : $(($(wc -l < docking/results.csv) - 1))"
echo "  receptor dirs: $(ls docking/receptors 2>/dev/null | wc -l)"
if [ -f data/derived/faers.sqlite ]; then
  echo "  FAERS db     : present"
else
  echo "  FAERS db     : absent (fine for MD; needed only to re-run the pharmacovigilance parts)"
fi

# --------------------------------------------------------------------- step 6
if [ -z "${TARGETS// /}" ] || [ "${NS}" = "0" ]; then
  say "Step 6: MD skipped (TARGETS empty or NS=0)"
else
  say "Step 6: all-atom MD for: $TARGETS   (${NS} ns each)"
  "$PY" src/run_md_allatom.py --targets $TARGETS --ns "$NS" \
    || die "MD run failed - inspect md_allatom/<GENE>/ for logs"

  # ------------------------------------------------------------------- step 7
  say "Step 7: analysis"
  "$PY" src/analyse_md.py || warn "analysis failed; trajectories are still there"
fi

say "Done"
cat <<'EOF'
Next:
  * results/md_allatom_stability.csv  per-target verdicts
  * md_allatom/<GENE>/traj.dcd        trajectories
  Report every target including unstable ones, plus production length,
  the platform used, and the ns/day achieved.
EOF

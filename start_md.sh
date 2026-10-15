#!/usr/bin/env bash
# =============================================================================
# Start molecular dynamics for ONE target.
#
# Why one target at a time
#     A three-target job takes about two and a half hours, and the run dies whenever
#     the WSL session ends - which has now happened three times, twice losing work.
#     One target fits in 30 to 60 minutes, and a target that finishes is written to
#     disk and cannot be lost by a later failure.  Run this repeatedly, once per
#     target, keeping the terminal open while it runs.
#
# Usage
#     bash ~/ethambutol/start_md.sh HMOX1
#     bash ~/ethambutol/start_md.sh BCL2
#     NS=2 bash ~/ethambutol/start_md.sh MFN2      # longer production
# =============================================================================
set -uo pipefail

WIN="/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox"
PROJ="$HOME/ethambutol"
ENV_DIR="$HOME/miniconda3/envs/md"
PY="$ENV_DIR/bin/python"
NS="${NS:-1}"
GENE="${1:-}"

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
die() { printf '\033[1;31m[fail] %s\033[0m\n' "$*" >&2; exit 1; }

[ -n "$GENE" ] || die "usage: bash start_md.sh <GENE>   e.g. HMOX1"
[ -d "$PROJ" ] || die "project not found at $PROJ"
[ -x "$PY" ] || die "interpreter not found at $PY"

say "Target $GENE, ${NS} ns of production"

# stop anything already running so two jobs cannot compete for the GPU
if pgrep -f "run_md_allatom" > /dev/null 2>&1; then
  echo "  a run is already active; stopping it first"
  pkill -f run_md_allatom || true
  sleep 3
fi

# AmberTools: the real executables are in bin/, and bin/wrapped_progs shadows them
export PATH="$ENV_DIR/bin:$PATH"
export AMBERHOME="$ENV_DIR"
command -v antechamber > /dev/null || die "antechamber not on PATH"

# latest scripts, including the checkpoint particle-count guard
cp "$WIN/src/run_md_allatom.py" "$PROJ/src/" 2>/dev/null || true
cp "$WIN/src/analyse_md.py" "$PROJ/src/" 2>/dev/null || true
cp "$WIN/src/probe_ligand_escape.py" "$PROJ/src/" 2>/dev/null || true
rm -rf "$PROJ/src/__pycache__"
[ -d "$PROJ/receptors_clean" ] || cp -r "$WIN/receptors_clean" "$PROJ/" \
  || die "could not copy receptors_clean"

LOG="$WIN/wsl_md_${GENE,,}.txt"
say "Starting; log: $LOG"
echo "  keep this terminal open until it prints 'production finished'"
echo "  progress is also visible in md_allatom/$GENE/md.log"
echo

cd "$PROJ"
setsid nohup env TARGETS="$GENE" NS="$NS" PATH="$PATH" AMBERHOME="$AMBERHOME" \
  bash wsl_setup_and_run.sh > "$LOG" 2>&1 < /dev/null &
echo "  pid $!"
echo
echo "Check on it with:"
echo "    bash $PROJ/check_md.sh"
echo "When it finishes, analyse it with:"
echo "    $PY $PROJ/src/analyse_md.py"
echo "    $PY $PROJ/src/probe_ligand_escape.py"

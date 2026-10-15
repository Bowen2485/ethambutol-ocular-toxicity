#!/usr/bin/env bash
# =============================================================================
# Run the long jobs inside WSL, independent of the editor session.
#
# Why this exists
#     Long runs were started from the editing session three times and were killed
#     each time the session ended.  Both jobs below only need the WSL side: the MD
#     uses the GPU, and the Mendelian randomisation is pure pandas/numpy plus a
#     bundled BGZF reader, with no GPU and no live API calls once the cache is copied.
#     Starting them here with nohup means they survive.
#
# Usage
#     bash run_in_wsl.sh md        # MD for the small clean target (resumable)
#     bash run_in_wsl.sh mr        # complete the MR panel
#     bash run_in_wsl.sh both
#     bash run_in_wsl.sh status    # what is running, and how far along
#
# Everything writes a log into the Windows-side project directory, so the results can
# be read without copying them back manually.
# =============================================================================
set -uo pipefail

WIN="/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox"
PROJ="$HOME/ethambutol"
PY="$HOME/miniconda3/envs/md/bin/python"
ENV_DIR="$HOME/miniconda3/envs/md"
STAGE="$PROJ"
LOGDIR="$WIN"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[warn] %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m[fail] %s\033[0m\n' "$*" >&2; exit 1; }

[ -d "$PROJ" ] || die "project not found at $PROJ"
[ -x "$PY" ] || die "interpreter not found at $PY"

# --------------------------------------------------------------------- status
if [ "${1:-}" = "status" ]; then
  say "Running processes"
  pgrep -af "run_md_allatom|mr_final" || echo "  none"
  for f in "$LOGDIR/wsl_md_run.txt" "$LOGDIR/wsl_mr_run.txt"; do
    if [ -f "$f" ]; then
      echo
      echo "--- $(basename "$f") (last 6 lines) ---"
      tail -6 "$f"
    fi
  done
  echo
  echo "--- MD progress ---"
  for d in "$PROJ"/md_allatom/*/; do
    [ -d "$d" ] || continue
    n=$(basename "$d")
    st="no checkpoint"
    [ -f "$d/state.json" ] && st=$(python3 -c "
import json,sys
try:
    j=json.load(open('$d/state.json'))
    print(f\"stage={j.get('last_stage')} ns_done={j.get('ns_completed')}\")
except Exception as e:
    print('unreadable')
")
    echo "  $n: $st"
  done
  exit 0
fi

WHICH="${1:-both}"

# =========================================================== shared preparation
if [ "$WHICH" = "md" ] || [ "$WHICH" = "both" ]; then
  say "Preparing the MD run"
  # the cleaned receptors are needed here; they live on the Windows side
  if [ ! -d "$PROJ/receptors_clean" ]; then
    echo "  copying receptors_clean from the Windows side"
    cp -r "$WIN/receptors_clean" "$PROJ/" || die "copy failed"
  fi
  # refresh the scripts so the latest fixes are used
  cp "$WIN/src/"*.py "$PROJ/src/" 2>/dev/null || true
  rm -rf "$PROJ/src/__pycache__"
  # GAFF needs the AmberTools executables on PATH, and a wrapper directory shadows
  # them unless the real bin/ comes first
  export PATH="$ENV_DIR/bin:$PATH"
  export AMBERHOME="$ENV_DIR"
  echo "  PATH starts with : $ENV_DIR/bin"
  echo "  AMBERHOME        : $AMBERHOME"
  echo "  antechamber      : $(command -v antechamber || echo MISSING)"
  [ -n "$(command -v antechamber || true)" ] || die "antechamber not on PATH"

  LOG="$LOGDIR/wsl_md_run.txt"
  say "Starting MD in the background (log: $LOG)"
  echo "  target NFE2L2, 1 ns; resumable from md_allatom/NFE2L2/state.chk"
  cd "$PROJ"
  nohup env TARGETS="NFE2L2" NS="${NS:-1}" PATH="$PATH" AMBERHOME="$AMBERHOME" \
    bash wsl_setup_and_run.sh > "$LOG" 2>&1 &
  echo "  pid $!"
fi

# ================================================== Mendelian randomisation
if [ "$WHICH" = "mr" ] || [ "$WHICH" = "both" ]; then
  say "Preparing the MR run"
  # the scripts need data/derived and the regional scan cache; the 35 GB database is
  # not needed for this, only the small CSVs and the cached windows
  if [ ! -d "$PROJ/data/derived" ]; then
    echo "  copying data/derived (about 30 MB excluding the database)"
    mkdir -p "$PROJ/data/derived"
    rsync -a --exclude 'faers.sqlite*' "$WIN/data/derived/" "$PROJ/data/derived/" \
      || cp "$WIN/data/derived/"*.csv "$WIN/data/derived/"*.json \
            "$PROJ/data/derived/" 2>/dev/null || true
  fi
  if [ ! -d "$PROJ/data/raw/opengwas" ]; then
    echo "  copying the OpenGWAS scan cache; this is the slow part, about 2.8 GB"
    mkdir -p "$PROJ/data/raw"
    rsync -a --info=progress2 "$WIN/data/raw/opengwas" "$PROJ/data/raw/" \
      || die "cache copy failed; the MR run would need to re-fetch everything"
  fi
  if [ ! -d "$PROJ/data/raw/finngen" ]; then
    mkdir -p "$PROJ/data/raw"
    cp -r "$WIN/data/raw/finngen" "$PROJ/data/raw/" 2>/dev/null || true
  fi
  echo "  cached OpenGWAS windows it can reuse: $(ls "$PROJ/data/raw/opengwas"/mr_*.tsv 2>/dev/null | wc -l)"

  # pandas and numpy are the only requirements and both are already in the md env
  LOG="$LOGDIR/wsl_mr_run.txt"
  say "Starting MR in the background (log: $LOG)"
  echo "  completing the panel from the cached instrument files"
  cd "$PROJ"
  nohup env PATH="$PATH" "$PY" src/mr_final.py > "$LOG" 2>&1 &
  echo "  pid $!"
fi

say "Both jobs started"
cat <<EOF
Check progress at any time with:
    bash $PROJ/run_in_wsl.sh status
or read the tails of
    $LOGDIR/wsl_md_run.txt
    $LOGDIR/wsl_mr_run.txt
EOF

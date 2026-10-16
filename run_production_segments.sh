#!/usr/bin/env bash
# =============================================================================
# Run the missing production segments, one target at a time, in one WSL session.
#
# Why this exists
#     run_md_allatom.py writes state.json only when a stage finishes, and WSL shuts
#     the VM down about a minute after the last session exits.  start_md.sh returns as
#     soon as it has nohup'd the real run, so nothing holds the VM open and the run
#     dies with it.  This driver stays in the foreground for the whole job, which is
#     what keeps the VM alive, and it starts the next target only after the previous
#     one has actually written its production state.
#
#     Both remaining targets are resumable: HMOX1 and MFN2 have their nvt stage on
#     disk, so each restarts at npt rather than from the beginning.
#
# Usage (from inside WSL, or from Windows via wsl -d Ubuntu -- bash ...)
#     bash run_production_segments.sh HMOX1 MFN2
#     NS=2 bash run_production_segments.sh HMOX1
# =============================================================================
set -uo pipefail

PROJ="${PROJ:-$HOME/ethambutol}"
WIN="/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox"
NS="${NS:-1}"

# state.json counts the equilibration segments too: nvt 0.1 + npt 0.4 + production NS.
TARGET_TOTAL=$(awk -v ns="$NS" 'BEGIN{printf "%.2f", 0.5 + ns - 0.1}')

stamp() { date '+%F %T'; }
say()   { printf '\n%s==> %s%s\n' "$(tput bold 2>/dev/null || true)" "$*" "$(tput sgr0 2>/dev/null || true)"; }

[ -d "$PROJ" ] || { echo "project not found at $PROJ"; exit 1; }
[ -x "$HOME/miniconda3/envs/md/bin/python" ] || { echo "md env python not found"; exit 1; }

TARGETS=("$@")
[ ${#TARGETS[@]} -gt 0 ] || TARGETS=(HMOX1 MFN2)

say "Production segments to run: ${TARGETS[*]}   (${NS} ns each)"
echo "  completion threshold: ns_completed >= $TARGET_TOTAL in md_allatom/<gene>/state.json"

wait_target() {
  local gene="$1" st ns i
  # 40 h of 30 s polls; MFN2 is 387k atoms and the slowest in the panel.
  for ((i = 0; i < 4800; i++)); do
    sleep 30
    st=$(cat "$PROJ/md_allatom/$gene/state.json" 2>/dev/null || echo '')
    ns=$(sed -n 's/.*"ns_completed": *\([0-9.]*\).*/\1/p' <<<"$st")

    if [[ "$st" == *'"last_stage": "production"'* ]] && \
       awk -v a="${ns:-0}" -v b="$TARGET_TOTAL" 'BEGIN{exit !(a >= b)}'; then
      echo "$(stamp) $gene PRODUCTION COMPLETE (${ns} ns)"
      return 0
    fi

    # report roughly every 10 minutes so the log is readable
    if (( i % 20 == 0 )); then
      echo "$(stamp) $gene state: ${st:-<none>}"
      if ! pgrep -f run_md_allatom >/dev/null 2>&1; then
        echo "$(stamp) $gene: no run_md_allatom process alive - stopping the wait"
        return 1
      fi
    fi
  done
  echo "$(stamp) $gene: timed out after 40 h"
  return 1
}

for g in "${TARGETS[@]}"; do
  say "$(stamp) starting $g"
  bash "$PROJ/start_md.sh" "$g" 2>&1 | sed 's/^/    /'
  wait_target "$g"
done

say "ALL REQUESTED TARGETS FINISHED  $(stamp)"
for g in "${TARGETS[@]}"; do
  echo "  $g: $(cat "$PROJ/md_allatom/$g/state.json" 2>/dev/null || echo '<no state>')"
done
echo
echo "Next: analyse, then rebuild the manuscript table"
echo "    $HOME/miniconda3/envs/md/bin/python $PROJ/src/analyse_md.py"
echo "    $HOME/miniconda3/envs/md/bin/python $PROJ/src/write_md_pbc_v2.py"

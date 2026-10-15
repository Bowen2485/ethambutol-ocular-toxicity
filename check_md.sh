#!/usr/bin/env bash
# =============================================================================
# Check the molecular-dynamics run, and say plainly whether to wait or restart.
#
# Why a script rather than a one-liner
#     Stage progress is written only when a stage finishes, so the main log can be
#     silent for over an hour while NPT equilibration and production run back to back.
#     That silence has been misread as a dead process, so this checks the things that
#     actually move: the integrator log, which OpenMM writes every 10 ps, and the
#     trajectory file, which grows continuously.  It then prints one verdict.
#
# Usage
#     bash ~/ethambutol/check_md.sh
#     bash ~/ethambutol/check_md.sh --analyse    # also run the analysis when finished
# =============================================================================
set -uo pipefail

PROJ="$HOME/ethambutol"
WIN="/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox"
PY="$HOME/miniconda3/envs/md/bin/python"
BOLD=$'\033[1;36m'; OK=$'\033[1;32m'; WARN=$'\033[1;33m'; BAD=$'\033[1;31m'; OFF=$'\033[0m'

say() { printf '\n%s==> %s%s\n' "$BOLD" "$*" "$OFF"; }

say "Time"
date '+  now: %Y-%m-%d %H:%M:%S'

say "Is a run alive?"
if pgrep -af "run_md_allatom|wsl_setup" > /tmp/_md_procs 2>/dev/null; then
  sed 's/^/  /' /tmp/_md_procs
  ALIVE=yes
else
  echo "  no matching process"
  ALIVE=no
fi

say "Stage log, main log and checkpoints"
if [ -f "$WIN/wsl_md_more.txt" ]; then
  echo "  main log last written: $(date -r "$WIN/wsl_md_more.txt" '+%H:%M:%S')"
  echo "  last three stage lines:"
  grep -aE "checkpoint|equilibration|production|finished|ns/day" "$WIN/wsl_md_more.txt" \
    | tail -3 | sed 's/^/    /'
fi
for d in "$PROJ"/md_allatom/*/; do
  [ -d "$d" ] || continue
  g=$(basename "$d")
  st="no checkpoint"
  [ -f "$d/state.json" ] && st=$(tr -d '\n' < "$d/state.json")
  traj=$(ls -1 "$d"/traj*.dcd 2>/dev/null | tail -1)
  if [ -n "$traj" ]; then
    tsize=$(du -h "$traj" | cut -f1)
    ttime=$(date -r "$traj" '+%H:%M:%S')
    trajinfo="$tsize, last written $ttime"
  else
    trajinfo="none"
  fi
  printf '  %-8s %s\n           trajectory: %s\n' "$g" "$st" "$trajinfo"
done

say "Integrator progress (written every 10 ps; this is what actually moves)"
FOUND=0
for d in "$PROJ"/md_allatom/*/; do
  [ -f "$d/md.log" ] || continue
  g=$(basename "$d")
  when=$(date -r "$d/md.log" '+%H:%M:%S')
  age=$(( ( $(date +%s) - $(date -r "$d/md.log" +%s) ) / 60 ))
  echo "  $g  md.log last written $when  (${age} min ago)"
  tail -2 "$d/md.log" | sed 's/^/      /'
  FOUND=1
done
[ "$FOUND" = 1 ] || echo "  no md.log yet"

# ------------------------------------------------------------------- verdict
say "VERDICT"
NEWEST_LOG=""
for d in "$PROJ"/md_allatom/*/; do
  [ -f "$d/md.log" ] || continue
  t=$(date -r "$d/md.log" +%s)
  if [ -z "$NEWEST_LOG" ] || [ "$t" -gt "$NEWEST_LOG" ]; then NEWEST_LOG="$t"; fi
done
AGE_MIN=-1
[ -n "$NEWEST_LOG" ] && AGE_MIN=$(( ( $(date +%s) - NEWEST_LOG ) / 60 ))

if [ "$ALIVE" = yes ] && [ "$AGE_MIN" -ge 0 ] && [ "$AGE_MIN" -le 10 ]; then
  printf '%s  RUNNING.%s md.log was written %s min ago, so the integrator is advancing.\n' \
    "$OK" "$OFF" "$AGE_MIN"
  echo "  Leave this terminal open. Do not close it - WSL shuts the VM down about a"
  echo "  minute after the last session exits, which kills the run."
elif [ "$ALIVE" = yes ]; then
  printf '%s  PROCESS EXISTS BUT THE INTEGRATOR IS STALLED.%s md.log is %s min old.\n' \
    "$WARN" "$OFF" "$AGE_MIN"
  echo "  That is not normal - a 400 ps NPT stage on a 79,000-atom system takes about"
  echo "  25 minutes. Kill it and restart the target on its own:"
  echo "      pkill -f run_md_allatom"
  echo "      bash $PROJ/start_md.sh HMOX1"
else
  printf '%s  NOT RUNNING.%s\n' "$BAD" "$OFF"
  if grep -qa "production finished" "$WIN/wsl_md_more.txt" 2>/dev/null; then
    echo "  Some targets did finish. Recover them with:"
    echo "      bash $PROJ/recover_md.sh"
  else
    echo "  No target completed in this attempt. Start one target at a time:"
    echo "      bash $PROJ/start_md.sh HMOX1"
  fi
fi

if [ "${1:-}" = "--analyse" ]; then
  say "Running the analysis"
  cd "$PROJ"
  "$PY" src/analyse_md.py 2>&1 | tail -25
  "$PY" src/probe_ligand_escape.py 2>&1 | tail -25
fi

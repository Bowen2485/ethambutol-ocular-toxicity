#!/usr/bin/env bash
# =============================================================================
# Run the remaining MD targets so the dissociation result is not based on one system.
#
# Why more targets
#     NFE2L2 gave a clear result: the docked ethambutol left the site at 0.56 ns and
#     diffused to about 22 A from any protein atom, never returning to the original
#     pose.  One target cannot support a general statement, and a reviewer will ask
#     whether NFE2L2 is simply an unlucky case.  Three more are therefore run, chosen
#     to span the docking-score range so the conclusion does not depend on picking the
#     weakest hits.
#
#     TNF       -5.50 kcal/mol, the best score in the panel (large system, ~56k atoms)
#     HMOX1     -5.09, mid range, and the only target with a retained cofactor
#     BCL2      -4.95, mid range, clean receptor
#     (NFE2L2 -5.01 is already done)
#
# Estimated time from the measured 231-237 ns/day on a 45k-atom system, scaled by
# atom count: TNF ~40-60 min, HMOX1 ~10-15 min, BCL2 ~20-30 min.
#
# Usage
#     bash run_more_md.sh            # all three, 1 ns each
#     bash run_more_md.sh TNF        # a single target
#     NS=2 bash run_more_md.sh       # longer production
# =============================================================================
set -uo pipefail

WIN="/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox"
PROJ="$HOME/ethambutol"
ENV_DIR="$HOME/miniconda3/envs/md"
PY="$ENV_DIR/bin/python"
NS="${NS:-1}"
TARGETS="${*:-TNF HMOX1 BCL2}"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m[fail] %s\033[0m\n' "$*" >&2; exit 1; }

[ -d "$PROJ" ] || die "project not found at $PROJ"
[ -x "$PY" ] || die "interpreter not found at $PY"

say "Targets: $TARGETS   (${NS} ns each)"

# GAFF needs the AmberTools executables; the wrapper directory shadows the real ones
export PATH="$ENV_DIR/bin:$PATH"
export AMBERHOME="$ENV_DIR"
command -v antechamber >/dev/null || die "antechamber not on PATH"

# refresh the scripts with the latest fixes
cp "$WIN/src/"*.py "$PROJ/src/" 2>/dev/null || true
rm -rf "$PROJ/src/__pycache__"
# the cleaned receptors, which are what removed the untemplatable residues
if [ ! -d "$PROJ/receptors_clean" ]; then
  cp -r "$WIN/receptors_clean" "$PROJ/" || die "could not copy receptors_clean"
fi

say "HMOX1 note"
echo "  The cleaned receptor for 1N45 is PROTEIN ONLY: its two HEM residues were"
echo "  extracted separately into receptors_clean/1N45/HEM.pdb when the receptor was"
echo "  cleaned.  So HMOX1 will run, but as the apoprotein.  Heme is both the substrate"
echo "  and the catalytic centre of a heme oxygenase, so a simulation without it does not"
echo "  describe the active site, and the manuscript has to say so.  Parameterising the"
echo "  heme (iron centre, no CONECT records) is not implemented.  BCL2 and MFN2 are"
echo "  unaffected."

mkdir -p "$WIN/logs"
LOG="$WIN/logs/wsl_md_more.txt"
say "Starting in the background; log: $LOG"
echo "  production per target: $NS ns"
cd "$PROJ"
nohup env TARGETS="$TARGETS" NS="$NS" PATH="$PATH" AMBERHOME="$AMBERHOME" \
  bash wsl_setup_and_run.sh > "$LOG" 2>&1 &
echo "  pid $!"

cat <<EOF

Watch progress with:
    tail -f "$LOG"
or, for the per-target integration log:
    tail -f "$PROJ"/md_allatom/*/md.log

When it finishes, analyse everything at once:
    $PY "$PROJ/src/analyse_md.py"
    $PY "$PROJ/src/probe_ligand_escape.py"
EOF

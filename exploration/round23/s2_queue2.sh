#!/bin/bash
# Round 23 S2 queue part 2: runs the 6 remaining S2 jobs detached.
# Usage: setsid nohup bash s2_queue2.sh > s2_queue2.log 2>&1 < /dev/null &
# Lockfile guard: only one instance.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
LOCK=$R23/s2_queue2.lock
exec 9>"$LOCK"
flock -n 9 || { echo "[s2_queue2] another instance holds the lock, exiting"; exit 0; }

HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp|openroad"
foreign_heavies() { ps -eo args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "round23" | grep -v "r23_spn" | grep -v "s2_queue" | wc -l; }
log() { echo "$(date -u +%FT%TZ) $1" >> $R23/progress.log; echo "$(date -u +%FT%TZ) $1"; }

CANDS="r23_spn_mix4r_hs_rh_nw r23_spn_mix4r_mols8b_nw r23_spn_mix4r_pbrnd14_nw r23_spn_mix4r_sb1_nw r23_spn_mix4r_sb2_nw r23_spn_mix4r_sb3_nw"

run_one() {
  c=$1
  # skip if a complete verdict already exists
  if grep -qE "^KILL|^PASS" $R23/s2_$c.log 2>/dev/null; then
    log "S2_SKIP $c (verdict already in log)"
    return
  fi
  # wait for own earlier launches (max 2 concurrent incl. any still-running round23 diffprof)
  while [ "$(ps -eo args | grep -E 'diffprof_r23' | grep -v grep | wc -l)" -ge 2 ]; do
    sleep 60
  done
  while [ "$(foreign_heavies)" -ge 2 ]; do
    log "[polite] $(foreign_heavies) foreign heavies, sleeping 60s"
    sleep 60
  done
  KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  log "S2_LAUNCH $c"
  $FB/build/diffprof_$c $KEY 22 $KILL_REP > $R23/s2_$c.log 2>&1
  v=$(grep -E '^KILL|^PASS' $R23/s2_$c.log 2>/dev/null | tail -1 | head -c 120)
  log "S2_DONE $c $v"
}

log "=== S2 queue part 2: 6 candidates (hs_rh, mols8b, pbrnd14, sb1-3) ==="
for c in $CANDS; do
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
log "=== S2 queue part 2 complete ==="

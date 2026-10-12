#!/bin/bash
# Batch-59 S0 sweep: bundle + run_synth.py for every keep in
# all_keeps.jsonl (z-order), ranks [START..END] (args, defaults 0..64).
# Bundler output RECORDED to disk (b57 lesson: the report run found no
# recorded bit-exact output). run_synth.py ONLY for S0 measurement.
# Strict bar <19.2u (frontier t6_b57_8). Resumable: ranks with a RESULT
# line already in s0_all.log are skipped.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration/new_constructions/batch59 || exit 1
START=${1:-0}
END=${2:-64}
LOG=s0_all.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: ranks $START..$END deadline=$deadline" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll_s0.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: S0 sweep ranks $START..$END" >> "$LOG"
cd /home/hatch/workspace/mix/exploration || exit 1
for r in $(seq "$START" "$END"); do
  name="t6_b59_$r"
  if grep -q "RESULT name=$name " new_constructions/batch59/s0_all.log 2>/dev/null; then
    echo "$(date -u +%FT%TZ) rank $r ($name): RESULT present, skipping" >> new_constructions/batch59/s0_all.log
    continue
  fi
  echo "$(date -u +%FT%TZ) rank $r: bundling $name" >> new_constructions/batch59/s0_all.log
  python3 new_constructions/batch57/gen_b57_bundle.py \
      new_constructions/batch59/all_keeps.jsonl "$r" "$name" \
      > "new_constructions/batch59/bundle_$name.log" 2>&1
  brc=$?
  echo "rank $r bundle exit=$brc" >> new_constructions/batch59/s0_all.log
  if [ "$brc" -ne 0 ]; then
    echo "rank $r BUNDLE-FAIL, see bundle_$name.log" >> new_constructions/batch59/s0_all.log
    continue
  fi
  python3 run_synth.py "fast_battery/candidates/$name/rtl.v" "$name" \
      "new_constructions/batch59/s0_$name" >> new_constructions/batch59/s0_all.log 2>&1
  echo "rank $r ($name) run_synth exit=$?" >> new_constructions/batch59/s0_all.log
done
echo "$(date -u +%FT%TZ) S0 sweep ranks $START..$END COMPLETE" >> new_constructions/batch59/s0_all.log

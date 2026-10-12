#!/bin/bash
# Batch-62 S0 sweep: bundle + run_synth.py for every keep in
# pilot_keeps.jsonl (z-order), ranks [START..END] (args, defaults 0..N-1).
# Bundler output RECORDED to disk. run_synth.py ONLY for S0 measurement
# (pinned yosys). Strict bar <18.6u (frontier t6_b59_47). XCHECK clean
# required. Resumable: ranks with a RESULT line already in s0_all.log
# are skipped. Cleared-flag backoff pattern. Launched under setsid.
cd /home/hatch/workspace/mix/exploration/new_constructions/batch62 || exit 1
NKEEPS=$(grep -c . pilot_keeps.jsonl 2>/dev/null || echo 0)
START=${1:-0}
END=${2:-$((NKEEPS-1))}
LOG=s0_all.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: ranks $START..$END nkeeps=$NKEEPS deadline=$deadline" >> "$LOG"
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
  name="t6_b62_$r"
  if grep -q "RESULT name=$name " new_constructions/batch62/s0_all.log 2>/dev/null; then
    echo "$(date -u +%FT%TZ) rank $r ($name): RESULT present, skipping" >> new_constructions/batch62/s0_all.log
    continue
  fi
  echo "$(date -u +%FT%TZ) rank $r: bundling $name" >> new_constructions/batch62/s0_all.log
  python3 new_constructions/batch62/gen_b62_bundle.py \
      new_constructions/batch62/pilot_keeps.jsonl "$r" "$name" \
      > "new_constructions/batch62/bundle_$name.log" 2>&1
  brc=$?
  echo "rank $r bundle exit=$brc" >> new_constructions/batch62/s0_all.log
  if [ "$brc" -ne 0 ]; then
    echo "rank $r BUNDLE-FAIL, see bundle_$name.log" >> new_constructions/batch62/s0_all.log
    continue
  fi
  python3 run_synth.py "fast_battery/candidates/$name/rtl.v" "$name" \
      "new_constructions/batch62/s0_$name" >> new_constructions/batch62/s0_all.log 2>&1
  echo "rank $r ($name) run_synth exit=$?" >> new_constructions/batch62/s0_all.log
  date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-s0 rank $r done" > new_constructions/batch62/heartbeat.txt
done
echo "$(date -u +%FT%TZ) S0 sweep ranks $START..$END COMPLETE" >> new_constructions/batch62/s0_all.log

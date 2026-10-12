#!/bin/bash
# Batch-59 PILOT: muxD5f-local (perturbation search around the t6_b57_8
# winner schedule) with fisher-matched triage. 80 draws, seed 0xB592.
# Pre-registered rules (DESIGN.md):
#   - pre-pilot 7/12 KEEP (minz=2.3) -> basin thesis CONFIRMED;
#     pilot runs to get the full keep set;
#   - >=1 keep -> bit-exact bundle (gen_b57_bundle.py verbatim, output
#     recorded to disk) -> S0 (run_synth.py ONLY, strict <19.2u) ->
#     cost-eligible keeps escalate in z-order (pre-pilot + pilot keeps
#     combined) -> staged battery S1->S4 -> Q1 (sac_z5=0 mandatory);
#   - 0/80 -> AXIS-KILL -> escalate to deferred mux3f.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration/new_constructions/batch59 || exit 1
LOG=pilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll_pilot.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 backoff_poll_pilot.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: pilot 80 draws seed 0xB592" >> "$LOG"
rm -f pilot_keeps.jsonl
python3 t6_b59_screen.py muxD5flocal 80 0xB592 pilot_keeps.jsonl >> "$LOG" 2>&1
rc=$?
nkeeps=0
[ -f pilot_keeps.jsonl ] && nkeeps=$(wc -l < pilot_keeps.jsonl)
echo "pilot exit=$rc keeps=$nkeeps" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"

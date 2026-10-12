#!/bin/bash
# Batch-29 S0 sweep: bundle pilot keeps in (n_reject, z)-order, then
# run_synth.py (authorized path, pinned yosys 0.69, ref mul64 103.5u).
# Escalation bars (recorded):
#   SPEED: delay strictly < 18.6u (t6_b59_47) -> speed-challenger path.
#   SIZE:  keep Pareto-nondominated vs Frontier S on (delay,cells,area)
#          with delay <= 20.1u (t6_b33b) -> size-challenger path.
#   else: S0-doomed, no battery.
set -u
B29=/home/hatch/workspace/mix/exploration/hybrid/batch29
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
cd "$B29"

# Backoff gate (cleared-flag pattern: single gate, no post-loop re-check).
cleared=0
for i in $(seq 1 720); do
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  sleep 60
done
if [ "$cleared" -eq 0 ]; then echo "BACKOFF-FAIL: load never cleared in 12h" >&2; exit 9; fi

export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
: > s0_sweep.log
: > s0_summary.txt

# Rank keeps by (n_reject, z).
python3 - "$B29/pilot_keeps.jsonl" <<'EOF' > "$B29/keep_ranks.txt"
import json, sys
entries = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
entries = [e for e in entries if e.get("form")=="muxD5f" and e.get("base")=="hyb28_mu5_324"]
entries.sort(key=lambda e: (e.get("n_reject",99), e["z"]))
for r, e in enumerate(entries):
    print(r, e["z"], e.get("n_reject"), e.get("n_perturb"))
EOF
n=$(wc -l < keep_ranks.txt)
echo "S0 sweep: $n keeps to bundle+synthesize (z-order)" | tee -a s0_sweep.log

while read -r rank z nrej m; do
  name=$(printf "hyb29_mu5_%03d" "$rank")
  echo "=== S0 $name (rank $rank, z=$z, n_reject=$nrej, m=$m) $(date -u +%FT%TZ) ===" | tee -a s0_sweep.log
  nice -n 19 python3 "$B29/gen_b29_bundle.py" "$B29/pilot_keeps.jsonl" "$rank" "$name" > "bundle_$name.log" 2>&1
  brc=$?
  if [ $brc -ne 0 ]; then echo "BUNDLE-FAIL $name rc=$brc" | tee -a s0_sweep.log; continue; fi
  tail -2 "bundle_$name.log" >> s0_sweep.log
  workdir="$B29/s0_work_$name"
  mkdir -p "$workdir"
  nice -n 19 python3 "$EXP/run_synth.py" "$FB/candidates/$name/rtl.v" "$name" "$workdir" > "s0_$name.log" 2>&1
  src=$?
  res=$(grep "^RESULT" "s0_$name.log" | tail -1)
  echo "rc=$src $res" | tee -a s0_sweep.log
  echo "$name rank=$rank z=$z $res" >> s0_summary.txt
done < keep_ranks.txt

echo "=== S0 SWEEP COMPLETE $(date -u +%FT%TZ) ===" | tee -a s0_sweep.log
cat s0_summary.txt >> s0_sweep.log

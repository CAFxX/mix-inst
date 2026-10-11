#!/bin/bash
# Wave-13 S-box cost sweep: per-stage S0 for all 7 pool S-boxes (pure + pre-whitened).
# Kill bar: stage <3.3u (6-stage beats 20.1u) or <3.96u (5-stage).
W13=/home/hatch/workspace/mix/exploration/adder_lat/wave13
cd "$W13" || exit 1
: > sbox_cost/sweep_results.txt
for box in BOYAR19_GF4INV ULBC_s1 JIA25_12GE_R1 LU21_SKINNY ORTHROS_S0 PRINCE_S0 THF_BLINK_S0; do
  W13_BOX="$box" python3 gen_stage_bundle.py >/dev/null 2>&1 || { echo "GENFAIL $box" >> sbox_cost/sweep_results.txt; continue; }
  top="w13s_$(echo "$box" | tr 'A-Z' 'a-z')"
  # parse: first 'crit=' on the ^RESULT line is the DUT delay; ref_crit= comes later
  # (a greedy '.*crit=' pattern matches ref_crit=103.5 -- the REF multiplier value)
  r1=$(python3 ../../run_synth.py "sbox_cost/$box/stage_pure.v" "${top}_pure" "sbox_cost/$box/work_pure" 2>/dev/null | grep '^RESULT' | grep -o 'crit=[0-9.]*' | head -1 | cut -d= -f2)
  r2=$(python3 ../../run_synth.py "sbox_cost/$box/bundle/rtl.v" "$top" "sbox_cost/$box/work_pre" 2>/dev/null | grep '^RESULT' | grep -o 'crit=[0-9.]*' | head -1 | cut -d= -f2)
  echo "$box pure=${r1:-FAIL} pre=${r2:-FAIL}" >> sbox_cost/sweep_results.txt
  echo "[$box] pure=$r1 pre=$r2"
done
echo "SWEEP DONE $(date -u +%FT%TZ)"

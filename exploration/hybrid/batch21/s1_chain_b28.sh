#!/bin/bash
FB=~/workspace/mix/exploration/fast_battery
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
for c in hyb28_mu5_266a hyb28_mu5_266b hyb28_mu5_282; do
  mkdir -p "$FB/results/$c"
  echo "=== S1 $c started $(date -u +%FT%TZ) ==="
  python3 "$FB/src/s1_screen.py" "$c" "$FB/results/$c" > "$FB/results/$c/s1.out" 2>&1
  echo "S1 $c rc=$? verdict: $(python3 -c "import json;print(json.load(open(\"$FB/results/$c/s1_result.json\"))[\"verdict\"])" 2>/dev/null || echo NORESULT)"
done
echo "S1 CHAIN DONE"

#!/bin/bash
FB=~/workspace/mix/exploration/fast_battery
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
for c in hyb28_mu5_304a hyb28_mu5_304b hyb28_mu5_323 hyb28_mu5_324 hyb28_mu5_325 hyb28_mu5_326 hyb28_mu5_328 hyb28_mu5_339 hyb28_mu5_351 hyb28_mu5_443 hyb28_mu5_471 hyb28_mu5_480 hyb28_mu5_568 hyb28_mu5_570 hyb28_mu5_621; do
  mkdir -p "$FB/results/$c"
  echo "=== S1 $c started $(date -u +%FT%TZ) ==="
  python3 "$FB/src/s1_screen.py" "$c" "$FB/results/$c" > "$FB/results/$c/s1.out" 2>&1
  echo "S1 $c rc=$? verdict: $(python3 -c "import json;print(json.load(open(\"$FB/results/$c/s1_result.json\"))[\"verdict\"])" 2>/dev/null || echo NORESULT)"
done
echo "S1 RESERVE CHAIN DONE"

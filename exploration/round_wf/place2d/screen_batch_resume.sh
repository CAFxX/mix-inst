#!/bin/bash
# Resume of screen_batch.sh: first 2 candidates done (both S2-KILL).
# Remaining 3: aff_a17_b17 (xcheck done, S2 never ran), aff_a49_b49, aff_a09_b25.
cd /home/hatch/workspace/mix/exploration/round_wf
for c in wf2d_aff_a17_b17 wf2d_aff_a49_b49 wf2d_aff_a09_b25; do
  echo "=== $c ==="
  python3 validation/run_s2_screen.py $c
  echo "rc=$? for $c"
done
echo "ALL DONE"

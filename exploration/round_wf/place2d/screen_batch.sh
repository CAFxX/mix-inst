#!/bin/bash
# Sequential S2 screens for 2D-phase finalists, ordered by S (diffusion safety).
# Each run_s2_screen.py backs off on >=2 foreign heavies. Designed to run detached.
cd /home/hatch/workspace/mix/exploration/round_wf
for c in wf2d_rnd_S392 wf2d_rnd_S374 wf2d_aff_a17_b17 wf2d_aff_a49_b49 wf2d_aff_a09_b25; do
  echo "=== $c ==="
  python3 validation/run_s2_screen.py $c
  echo "rc=$? for $c"
done
echo "ALL DONE"

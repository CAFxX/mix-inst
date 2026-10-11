#!/bin/bash
# Full routed P&R A/B: winner vs 64x64 multiplier, identical flow/corner/utilization.
# Winner: 1700 cells -> DIE=300 (25.5% util). Multiplier: 9639 cells -> DIE=670 (~25% util).
set -e
source ~/tools/sky130-env.sh
export PDK_TLEF=/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
export PDK_LEF_SC_HD=/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
cd ~/workspace/mix/exploration/pnr
run_one() { # TOP SYNTH WD DIE
  export TOP=$1 SYNTH=$2 WD=$3 DIE=$4
  mkdir -p $WD
  ~/tools/sky130bin/openroad -no_splash -exit flow_full.tcl > $WD/flow.log 2>&1
  echo "done $1 -> $WD"
}
run_one r3_xorlin_qm ../results/r3/pnr_qm/synth.v wd_mixer_full 300
run_one mul64_64 synth_mul64_64.v wd_mul_full 670

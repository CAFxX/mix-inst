#!/bin/bash
# S5 driver: runs stages for one design, skipping completed checkpoints.
# Usage: run_s5.sh <r22c|mult>
# Resumable: re-running picks up after the last completed stage.
# FAILS HARD if a stage finishes without producing its checkpoint
# (openroad exits 0 even on Tcl errors — never trust rc alone).
set -u
source ~/tools/sky130-env.sh
export YOSYS=/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys
FLOWDIR=~/workspace/mix/exploration/s5_r22c/flow
S5ROOT=~/workspace/mix/exploration/s5_r22c
D=$1
case $D in
  r22c) TOP=r22c_spn_mix4r_lp_nw; RTL=~/workspace/your_files/mix_rtl_pareto/mix_r22c_spn_mix4r_lp_nw.v ;;
  mult) TOP=mul64; RTL=~/workspace/mix/synth/mul64.v ;;
  *) echo "usage: $0 <r22c|mult>"; exit 1 ;;
esac
WORK=$S5ROOT/$D
mkdir -p "$WORK/reports" "$S5ROOT/logs"
export TOP RTL WORK FLOWDIR
log=$S5ROOT/logs/${D}.log

fail() { echo "[$(date -u +%FT%TZ)] $D: FATAL: $1" | tee -a "$log"; echo "$D:FAILED:$1:$(date -u +%FT%TZ)" >> "$S5ROOT/FLOW_STATE.md"; exit 1; }

# Stage 0: yosys -> sky130 structural netlist (+ equivalence sim check)
if [ ! -s "$WORK/ysynth.v" ]; then
  echo "[$(date -u +%FT%TZ)] $D stage s0_ysynth: START" | tee -a "$log"
  sed -e "s|\${RTL}|$RTL|g" -e "s|\${TOP}|$TOP|g" -e "s|\${WORK}|$WORK|g" -e "s|\${PDK_LIB}|$PDK_LIB|g" \
    "$FLOWDIR/s0_ysynth.ys.tmpl" > "$WORK/s0_ysynth.ys"
  "$YOSYS" -s "$WORK/s0_ysynth.ys" >> "$log" 2>&1
  [ -s "$WORK/ysynth.v" ] || fail "s0_ysynth produced no netlist"
  # equivalence gate: mapped netlist must match validated RTL (design-specific)
  bash "$FLOWDIR/equiv_${D}.sh" >> "$log" 2>&1 || fail "equivalence check failed for $D"
  echo "[$(date -u +%FT%TZ)] $D stage s0_ysynth: DONE" | tee -a "$log"
  echo "$D:s0_ysynth:$(date -u +%FT%TZ):ok" >> "$S5ROOT/FLOW_STATE.md"
else echo "[$(date -u +%FT%TZ)] $D stage s0_ysynth: SKIP" | tee -a "$log"; fi

or_stage() { # $1=name $2=tcl $3=checkpoint
  if [ -s "$3" ]; then echo "[$(date -u +%FT%TZ)] $D stage $1: SKIP" | tee -a "$log"; return 0; fi
  echo "[$(date -u +%FT%TZ)] $D stage $1: START" | tee -a "$log"
  openroad -no_splash "$FLOWDIR/$2" >> "$log" 2>&1
  [ -s "$3" ] || fail "stage $1 finished without checkpoint $3"
  echo "[$(date -u +%FT%TZ)] $D stage $1: DONE" | tee -a "$log"
  echo "$D:$1:$(date -u +%FT%TZ):ok" >> "$S5ROOT/FLOW_STATE.md"
}

or_stage s1_link   s1_link.tcl     "$WORK/linked.ok"
or_stage s2_floor  s2_floorplan.tcl "$WORK/floorplan.def"
or_stage s3_place  s3_place.tcl    "$WORK/placed.def"
or_stage s4_route  s4_route.tcl    "$WORK/routed.def"
or_stage s5_report s5_reports.tcl  "$WORK/reports/timing_max.rpt"
echo "[$(date -u +%FT%TZ)] $D: ALL STAGES COMPLETE" | tee -a "$log"

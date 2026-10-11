#!/bin/bash
# Round 10 bit-exactness: C<->model 10k vectors, RTL<->model 300 vectors.
set -u
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r10_feist6_rot0211_nw r10_feist6_rot0313_nw r10_feist6_rot0317_nw r10_feist6_rot0411_nw r10_feist6_rot0307_nw r10_feist6_rot0511_nw r10_feist6_rot311 r10_feist5_s1_lin2_nw r10_feist5_s1_2sbox_nw r10_feist5_rot311 r10_feist6_rot311_ksalt_nw r10_feist6_rot311_ksrot_nw r10_feist6_altrot311_713_nw"
PROG=$EXP/round10/xcheck_progress.log
: > "$PROG"
check_one() {
  C=$1
  # C build + xcheck 10k
  gcc -O2 -o $FB/build/xc_$C $FB/src/s2_diffprof.c $FB/candidates/$C/impl.c -lm 2>$EXP/round10/xcheck/build_$C.err || { echo "BUILD-FAIL $C" >> "$PROG"; return 1; }
  python3 $FB/src/xcheck.py $C $FB/build/xc_$C 10000 $EXP/round10/xcheck/$C.txt >$EXP/round10/xcheck/$C.log 2>&1 || { echo "XCHECK-FAIL $C" >> "$PROG"; return 1; }
  echo "XCHECK-PASS $C" >> "$PROG"
  # RTL check 300 vectors
  python3 $EXP/check_rtl.py round10.models.r10.$C $FB/candidates/$C/rtl.v $C $EXP/round10/rtlcheck/$C 300 >$EXP/round10/rtlcheck/$C.log 2>&1 || { echo "RTLCHECK-FAIL $C" >> "$PROG"; return 1; }
  echo "RTLCHECK-PASS $C" >> "$PROG"
}
export -f check_one
export EXP FB PROG
echo "$CANDS" | tr ' ' '\n' | xargs -P 2 -I{} bash -c 'check_one {}'
echo DONE >> "$PROG"

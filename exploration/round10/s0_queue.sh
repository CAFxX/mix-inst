#!/bin/bash
# Round 10 S0 synthesis queue: authorized run_synth.py path, max 2 lanes.
EXP=/home/hatch/workspace/mix/exploration
CANDS="r10_feist6_rot0211_nw r10_feist6_rot0313_nw r10_feist6_rot0317_nw r10_feist6_rot0411_nw r10_feist6_rot0307_nw r10_feist6_rot0511_nw r10_feist6_rot311 r10_feist5_s1_lin2_nw r10_feist5_s1_2sbox_nw r10_feist5_rot311 r10_feist6_rot311_ksalt_nw r10_feist6_rot311_ksrot_nw r10_feist6_altrot311_713_nw"
synth_one() {
  C=$1
  mkdir -p "$EXP/round10/s0/$C"
  echo "START $C $(date -u +%FT%TZ)"
  python3 "$EXP/run_synth.py" "$EXP/fast_battery/candidates/$C/rtl.v" "$C" "$EXP/round10/s0/$C" > "$EXP/round10/s0/$C/synth.log" 2>&1
  RC=$?
  if [ $RC -eq 0 ]; then
    grep '^RESULT' "$EXP/round10/s0/$C/synth.log"
    echo "SYNTH-PASS $C"
  else
    echo "SYNTH-FAIL $C rc=$RC"
    tail -30 "$EXP/round10/s0/$C/synth.log"
  fi
  echo "END $C $(date -u +%FT%TZ)"
}
export -f synth_one
export EXP
echo "$CANDS" | tr ' ' '\n' | xargs -P 2 -I{} bash -c 'synth_one {}'
echo QUEUE-DONE

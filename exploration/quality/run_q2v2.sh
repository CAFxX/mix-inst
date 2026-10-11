#!/bin/bash
# Q2 v2 runner: 6 seq x 8 red = 48 cells/candidate, max 2 concurrent.
# Old seq1 x {low8,low16,low32,high32,xor32} logs already exist as
# q2_<name>_s1_<red>.log (migrated) — skipped here.
# New: s1 x {lemire1e9p7,mod1e9p7,mod1000} + s8/s256/s4k/s64k/s4g x all 8.
cd ~/workspace/mix/exploration/quality
PR=~/tools/practrand/PractRand/RNG_test
KEY=123456789ABCDEF0
NBYTES=1073741824
CANDS="r7_feist8_s1_1sbox r7_feist8_r311 r7_feist8_spn_nw r7_feist8_r517 r6_feist8_spn r7_feist8_rksimple r7_feist8_rkcheap r7_feist8_gift"
SEQS="s1 s8 s256 s4k s64k s4g"
REDS="low8 low16 low32 high32 xor32 lemire1e9p7 mod1e9p7 mod1000"

prmode() {
    case "$1" in
        low8|low16|mod1000) echo "stdin" ;;
        *) echo "stdin32" ;;
    esac
}

run_one() {
    local c=$1 s=$2 r=$3
    local log="q2_${c}_${s}_${r}.log"
    if [ -f "$log" ] && { grep -q "no anomalies" "$log" || grep -q "FAIL.*!!!!" "$log"; }; then
        echo "SKIP $c/$s/$r (already done)"
        return 0
    fi
    local m; m=$(prmode $r)
    echo "START $c/$s/$r [$m] $(date +%H:%M:%S)"
    ./qgen_$c $KEY $NBYTES $s $r 2>"$log.generr" | $PR $m > "$log" 2>&1
    echo "DONE $c/$s/$r rc=$? $(date +%H:%M:%S)"
}

for c in $CANDS; do
  for s in $SEQS; do
    for r in $REDS; do
      # skip the 5 already-done s1 cells
      if [ "$s" = "s1" ]; then
        case "$r" in low8|low16|low32|high32|xor32) continue;; esac
      fi
      while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
      run_one $c $s $r &
    done
  done
done
wait
echo ALL_Q2V2_DONE

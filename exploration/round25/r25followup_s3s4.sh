#!/bin/bash
# Item 1 (c)+(d): S3 PractRand 1GB std+strided, then S4 SmallCrush, for
# r25_spn_pba19_sb_rasC2_5_nw. Polite: waits while >=2 foreign heavies run.
# Logs: round25/s0_r25_top4_rasC2_5/{s3.log,s3b.log,s4.log}
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
TU=$HOME/tools/testu01/install
C=r25_spn_pba19_sb_rasC2_5_nw
OUT=$EXP/round25/s0_r25_top4_rasC2_5
HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp"
foreign_heavies() { ps -eo args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "r25followup_s3s4" | grep -v "$C" | wc -l; }
polite_wait() { while [ "$(foreign_heavies)" -ge 2 ]; do echo "[polite] $(foreign_heavies) foreign heavies, sleeping 60s"; sleep 60; done; }

KEY1=0x123456789abcdef0
KEY2=0x0
GOLDEN_OUT=0x40acac99160bc28d

polite_wait
echo "=== S3 standard (KEY1) ==="
bash $FB/src/s3_practrand.sh "$C" "$FB/build/gen_$C" "$OUT" "$KEY1" 1 > $OUT/s3.log 2>&1
S3A=$?
echo "S3 standard exit: $S3A"
[ $S3A -ne 0 ] && { echo "S3-FAIL standard"; exit 2; }

polite_wait
echo "=== S3 strided (KEY2) ==="
mkdir -p $OUT/strided
bash $FB/src/s3_practrand.sh "${C}_strided" "$FB/build/gen_$C" "$OUT/strided" "$KEY2" 0x9E3779B97F4A7C15 > $OUT/s3b.log 2>&1
S3B=$?
echo "S3 strided exit: $S3B"
[ $S3B -ne 0 ] && { echo "S3-FAIL strided"; exit 2; }

polite_wait
echo "=== S4 SmallCrush ==="
gcc -O2 -o $FB/build/sc_$C $FB/src/s4_smallcrush.c $FB/candidates/$C/impl.c \
  -DGOLDEN_OUT="$GOLDEN_OUT" -I"$TU/include" -L"$TU/lib" \
  -ltestu01 -lprobdist -lmylib -lm || { echo "S4-FAIL build"; exit 1; }
export LD_LIBRARY_PATH="$TU/lib:${LD_LIBRARY_PATH:-}"
$FB/build/sc_$C "$KEY1" > $OUT/s4.log 2>&1
S4X=$?
echo "S4 binary exit: $S4X"
[ $S4X -ne 0 ] && { echo "S4-FAIL run"; exit 2; }
if grep -q "gave a p-value outside" $OUT/s4.log; then echo "S4-FAIL p-value"; exit 2; fi
grep -q "All tests were passed" $OUT/s4.log || { echo "S4-FAIL no pass confirmation"; exit 2; }
echo "S4-PASS"
echo "ALL DONE: S3 std + strided + S4 PASS"

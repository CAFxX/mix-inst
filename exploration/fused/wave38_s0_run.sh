#!/bin/bash
# Wave-38 stratified S0 runner (track 8, inc 13): wait for load backoff to
# clear, then run run_synth.py sequentially on the 8 stratified-sample
# bundles (global yosys flock inside run_synth.py serializes anyway).
# Detached; survives supervisor death. Per-keep logs in wave38_s0/<name>.log;
# summary appended to wave38_s0.log. Bar: crit strictly < 19.8u MEASURED.
set -u
cd /home/hatch/workspace/mix/exploration/fused || exit 1
LOG=wave38_s0.log
mkdir -p wave38_s0
echo "[wave38-s0] started $(date -u +%FT%TZ) pid=$$" >> "$LOG"
for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "[wave38-s0] backoff CLEAR after ${i} polls $(date -u +%FT%TZ)" >> "$LOG"
    break
  fi
  if [ "$i" = 720 ]; then
    echo "[wave38-s0] LOUD: backoff never cleared in 12h; exiting" >> "$LOG"
    exit 1
  fi
  sleep 60
done
FB=/home/hatch/workspace/mix/exploration/fast_battery/candidates
for name in w38_t039 w38_t064 w38_t004 w38_t027 w38_t116 w38_t049 w38_t090 w38_t104; do
  if grep -q "^RESULT name=${name} " wave38_s0/${name}.log 2>/dev/null; then
    echo "[wave38-s0] skip ${name} (RESULT already recorded)" >> "$LOG"
    continue
  fi
  echo "[wave38-s0] S0 ${name} start $(date -u +%FT%TZ)" >> "$LOG"
  nice -n 10 python3 /home/hatch/workspace/mix/exploration/run_synth.py \
    "$FB/${name}/rtl.v" "$name" "wave38_s0/${name}" \
    > "wave38_s0/${name}.log" 2>&1
  rc=$?
  res=$(grep "^RESULT " "wave38_s0/${name}.log" || echo "NO-RESULT rc=${rc}")
  xc=$(grep -c "^XCHECK:" "wave38_s0/${name}.log" || true)
  echo "[wave38-s0] S0 ${name} done rc=${rc} xcheck_lines=${xc}: ${res}" >> "$LOG"
done
echo "[wave38-s0] ALL DONE $(date -u +%FT%TZ)" >> "$LOG"
touch wave38_S0_DONE.txt

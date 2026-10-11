#!/bin/bash
# Batch-49 Q4-LUT mining launcher: backoff-gated, checkpointed, resumable.
# - Polls load-shed backoff until clear (never piles onto a saturated box).
# - anneal_q4_fast.py checkpoints every completed start to
#   mine_q4_fast.starts.jsonl and skips checkpointed starts on resume,
#   so a silent death can no longer lose completed starts.
# - Deterministic: seed per start is 0xB492+k; resume reproduces identically.
set -u
D=~/workspace/mix/exploration/new_constructions/batch49
cd "$D"
LOG=mine_q4_fast.log
n=0
while ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; do
  n=$((n+1))
  [ $((n % 5)) -eq 1 ] && echo "[$(date -u +%FT%TZ)] [b49-mine] backoff blocked, waiting 60s" >> "$LOG"
  sleep 60
done
echo "[$(date -u +%FT%TZ)] [b49-mine] backoff clear, starting 12-start mining" >> "$LOG"
exec python3 anneal_q4_fast.py 12 >> "$LOG" 2>&1

#!/bin/bash
# hetstage2 gate4 launcher — cleared-flag single-gate backoff wrapper.
# Polls load-shed.sh backoff every 60s (<=12h); the cleared flag is the
# single source of truth (AGENTS.md lesson 2026-10-11: never re-check
# after the loop). On clear, runs gate4.py detached (setsid + nice-19).
cd ~/workspace/mix/exploration/sbox_screen/hetstage2 || exit 1
cleared=0
i=0
while [ $i -lt 720 ]; do
  i=$((i + 1))
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1); rc=$?
  echo "$(date -u +%FT%TZ) poll $i rc=$rc: $out" >> backoff_poll_gate4.out
  if [ $((i % 10)) -eq 0 ]; then
    date -u +%FT%TZ > gate4_heartbeat.txt
    ~/workspace/system/bin/workreg.py heartbeat --id track2-hetstage2 \
      2>/dev/null || true
  fi
  if [ $rc -eq 0 ]; then cleared=1; break; fi
  sleep 60
done
if [ $cleared -eq 0 ]; then
  echo "$(date -u +%FT%TZ) BACKOFF-FAIL: load never cleared in 12h" >> backoff_poll_gate4.out
  exit 1
fi
echo "$(date -u +%FT%TZ) BACKOFF CLEAR after $i polls; launching gate4" >> backoff_poll_gate4.out
date -u +%FT%TZ > gate4_heartbeat.txt
setsid nice -n 19 python3 gate4.py >> gate4.log 2>&1 < /dev/null &
echo "gate4 pid $!"
date -u +%FT%TZ > gate4_heartbeat.txt

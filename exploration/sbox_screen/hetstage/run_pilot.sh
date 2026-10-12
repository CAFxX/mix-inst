#!/bin/bash
# hetstage pilot launcher — cleared-flag single-gate backoff wrapper.
# Polls load-shed.sh backoff every 60s (<=12h); the cleared flag is the
# single source of truth (AGENTS.md lesson 2026-10-11: never re-check
# after the loop). On clear, runs the 120-draw pilot detached.
cd ~/workspace/mix/exploration/sbox_screen/hetstage || exit 1
cleared=0
i=0
while [ $i -lt 720 ]; do
  i=$((i + 1))
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1); rc=$?
  echo "$(date -u +%FT%TZ) poll $i rc=$rc: $out" >> backoff_poll_pilot.out
  if [ $((i % 10)) -eq 0 ]; then
    date -u +%FT%TZ > heartbeat.txt
  fi
  if [ $rc -eq 0 ]; then cleared=1; break; fi
  sleep 60
done
if [ $cleared -eq 0 ]; then
  echo "$(date -u +%FT%TZ) BACKOFF-FAIL: load never cleared in 12h" >> backoff_poll_pilot.out
  exit 1
fi
echo "$(date -u +%FT%TZ) BACKOFF CLEAR after $i polls; launching pilot" >> backoff_poll_pilot.out
date -u +%FT%TZ > heartbeat.txt
setsid nice -n 19 python3 t8_hetstage_screen.py hetstage 0xB802 pilot_keeps.jsonl >> pilot.log 2>&1 < /dev/null &
echo "pilot pid $!"
date -u +%FT%TZ > heartbeat.txt

#!/bin/bash
# hetstage2 pilot launcher — cleared-flag single-gate backoff wrapper.
# Polls load-shed.sh backoff every 60s (<=12h); the cleared flag is the
# single source of truth (AGENTS.md lesson 2026-10-11: never re-check
# after the loop). On clear, runs the 36-draw pilot detached (setsid +
# nice-19 so it outlives the launching session; AGENTS.md 2026-10-11).
# Registers workreg entry track2-hetstage2 before launch.
cd ~/workspace/mix/exploration/sbox_screen/hetstage2 || exit 1
cleared=0
i=0
while [ $i -lt 720 ]; do
  i=$((i + 1))
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1); rc=$?
  echo "$(date -u +%FT%TZ) poll $i rc=$rc: $out" >> backoff_poll_pilot.out
  if [ $((i % 10)) -eq 0 ]; then
    date -u +%FT%TZ > heartbeat.txt
    ~/workspace/system/bin/workreg.py heartbeat --id track2-hetstage2 \
      2>/dev/null || true
  fi
  if [ $rc -eq 0 ]; then cleared=1; break; fi
  sleep 60
done
if [ $cleared -eq 0 ]; then
  echo "$(date -u +%FT%TZ) BACKOFF-FAIL: load never cleared in 12h" >> backoff_poll_pilot.out
  exit 1
fi
echo "$(date -u +%FT%TZ) BACKOFF CLEAR after $i polls; launching pilot" >> backoff_poll_pilot.out
~/workspace/system/bin/workreg.py register --id track2-hetstage2 \
  --description "track-2 hetstage2 lane: dense GF-mul pool + [CIRC2,MUXD x4], inner-DIFF-SEQ primary triage (seed 0xB803, 36 draws)" \
  --kind subagent 2>&1 | tee -a backoff_poll_pilot.out
date -u +%FT%TZ > heartbeat.txt
setsid nice -n 19 python3 t8_hetstage2_screen.py hetstage2 0xB803 pilot_keeps.jsonl >> pilot.log 2>&1 < /dev/null &
echo "pilot pid $!"
date -u +%FT%TZ > heartbeat.txt

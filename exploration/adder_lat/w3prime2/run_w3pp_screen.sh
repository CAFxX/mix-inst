#!/bin/bash
# W3'' screen launcher: backoff-gated (cleared-flag pattern), resumable.
# Run via: setsid agentwork-launch.sh --nice 19 --tag track3/w3pp-screen --
#          adder_lat/w3prime2/run_w3pp_screen.sh >> screen.log 2>&1 < /dev/null &
cd /home/hatch/workspace/mix/exploration/adder_lat/w3prime2 || exit 1

cleared=0
for i in $(seq 1 1440); do  # <=12h backoff polling
    out=$(/home/hatch/workspace/system/bin/load-shed.sh backoff 2>&1)
    echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll.out
    if [ $? -eq 0 ]; then
        cleared=1
        break
    fi
    sleep 30
done
if [ "$cleared" -eq 0 ]; then
    echo "BACKOFF-FAIL: load never cleared in 12h" >&2
    exit 1
fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- starting W3'' screen" | tee -a screen.log
exec nice -n 19 python3 screen_w3pp.py >> screen.log 2>&1

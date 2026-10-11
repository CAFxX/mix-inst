#!/bin/bash
# Escalation runner for hyb28_mu5_324 (S1 CAL_PASS): wait for backoff clear,
# run S0 via run_synth.py; if crit < 19.8 and XCHECK clean, run battery from stage 2.
LOG=~/workspace/mix/exploration/hybrid/batch21/escalation_324.log
CAND=hyb28_mu5_324
echo "escalation runner started $(date -u +%FT%TZ) polling backoff every 60s" >> "$LOG"
for i in $(seq 1 180); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "backoff CLEAR at $(date -u +%FT%TZ) after $i polls; running S0" >> "$LOG"
    ~/workspace/system/bin/agentwork-launch.sh --nice 10 --tag track5/b28-s0-324 -- python3 ~/workspace/mix/exploration/run_synth.py ~/workspace/mix/exploration/fast_battery/candidates/$CAND/rtl.v $CAND ~/workspace/mix/exploration/hybrid/batch21/s0_b28_mu5_324 >> ~/workspace/mix/exploration/hybrid/batch21/s0_b28_mu5_324.log 2>&1
    cat ~/workspace/mix/exploration/hybrid/batch21/s0_b28_mu5_324.log >> "$LOG"
    CRIT=$(grep -oP 'RESULT name='$CAND' cells=\d+ area=\d+ crit=\K[0-9.]+' ~/workspace/mix/exploration/hybrid/batch21/s0_b28_mu5_324.log | tail -1)
    echo "S0 crit=$CRIT" >> "$LOG"
    if [ -n "$CRIT" ] && python3 -c "exit(0 if float('$CRIT') < 19.8 else 1)"; then
      if grep -q "XCHECK: analyze.py == analyze2.py" ~/workspace/mix/exploration/hybrid/batch21/s0_b28_mu5_324.log; then
        echo "cost-eligible + XCHECK clean; launching battery S2->S4" >> "$LOG"
        cd ~/workspace/mix/exploration/fast_battery && ~/workspace/system/bin/agentwork-launch.sh --nice 10 --tag track5/b28-battery324 -- bash run_fast_battery.sh $CAND 2 >> ~/workspace/mix/exploration/hybrid/batch21/battery_b28_324.log 2>&1
        echo "battery exited rc=$? at $(date -u +%FT%TZ)" >> "$LOG"
      else
        echo "XCHECK NOT clean; battery NOT launched" >> "$LOG"
      fi
    else
      echo "cost-INELIGIBLE (crit>=19.8 or missing); battery NOT launched" >> "$LOG"
    fi
    exit 0
  fi
  sleep 60
done
echo "escalation runner TIMEOUT after 180 polls at $(date -u +%FT%TZ)" >> "$LOG"
exit 1

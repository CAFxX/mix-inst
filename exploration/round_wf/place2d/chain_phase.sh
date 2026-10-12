#!/bin/bash
# Wire-friendly 2D track: phased pipeline (detached, setsid/nohup).
# Phase 0: wait for S2 resume driver (PID 1887) to finish the 3 aff candidates.
# Phase A: full battery S0->S4 + Q1 for every S2-PASS candidate.
# Phase B: build + S2-screen the next W2d=384 affine cluster (5 more).
# Phase C: build + S2-screen hill-climb high-S tours (S=404/448/452).
# Polite: S2 screens carry their own gate (run_s2_screen.py); batteries wait
# for <2 foreign heavies before starting.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
WF=$EXP/round_wf
FB=$EXP/fast_battery
LOGD=$WF/validation/logs
CHAINLOG=$LOGD/chain_phase.log

log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a $CHAINLOG; }

polite_wait() {
  # wait until fewer than 2 foreign heavy binaries are running
  while true; do
    n=$(ps aux | grep -E "yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp" | grep -v "run_s2_screen\|chain_phase" | wc -l)
    if [ "$n" -lt 2 ]; then break; fi
    log "[polite] $n foreign heavies, sleeping 120s"
    sleep 120
  done
}

log "=== chain_phase start ==="

# Phase 0: wait for resume driver
log "Phase 0: waiting for S2 resume driver PID 1887"
while kill -0 1887 2>/dev/null; do sleep 60; done
log "Phase 0: resume driver done"

# Phase A: batteries for S2-PASS candidates
mkdir -p $WF/validation/q1
for c in wf2d_aff_a17_b17 wf2d_aff_a49_b49 wf2d_aff_a09_b25; do
  if ! grep -q "VERDICT: S2-PASS" $LOGD/s2_$c.log 2>/dev/null; then
    log "Phase A: $c no S2-PASS, skipping battery"
    continue
  fi
  log "Phase A: battery $c"
  polite_wait
  rm -rf $FB/candidates/$c
  cp -r $WF/validation/candidates/$c $FB/candidates/$c
  bash $FB/run_fast_battery.sh $c > $LOGD/battery_$c.log 2>&1
  log "Phase A: battery rc=$? for $c"
  log "Phase A: Q1 $c"
  python3 $EXP/round13/q1_sacbic.py $c $WF/validation/q1 > $LOGD/q1_$c.log 2>&1
  log "Phase A: Q1 rc=$? : $(python3 -c "
import json
d=json.load(open('$WF/validation/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f'%(d['sac_z5'],d['bic_maxcorr']))" 2>/dev/null)"
done

# Phase B: next W2d=384 affine cluster (S2-first pivot)
log "Phase B: building 5 more W2d=384 aff candidates"
python3 - "$WF" << 'PYEOF'
import json, sys
WF = sys.argv[1]
pairs = [(17,63),(49,63),(57,9),(9,47),(57,47)]
for a,b in pairs:
    name = "wf2d_aff_a%02d_b%02d" % (a,b)
    P = [(a*i+b) % 64 for i in range(64)]
    open("/tmp/P_%s.json" % name, "w").write(json.dumps(P))
    print(name, flush=True)
PYEOF
for ab in "a17_b63" "a49_b63" "a57_b09" "a09_b47" "a57_b47"; do
  c="wf2d_aff_$ab"
  if [ ! -d $WF/validation/candidates/$c ]; then
    python3 $WF/validation/gen_from_P.py $c /tmp/P_$c.json >> $CHAINLOG 2>&1
    log "Phase B: built $c"
  fi
  log "Phase B: S2 screen $c"
  python3 $WF/validation/run_s2_screen.py $c >> $CHAINLOG 2>&1
  log "Phase B: S2 rc=$? for $c"
done

# Phase C: hill-climb high-S tours (S2-first pivot)
log "Phase C: building hill-climb high-S tours"
python3 - "$WF" << 'PYEOF'
import json, sys
WF = sys.argv[1]
d = json.load(open(WF + "/place2d/improve_S374.json"))
# pick one tour each at S=404, 448, 452 (unscreened; S=374/392 already killed)
want = {}
for e in d:
    if e['S'] in (404, 448, 452) and e['S'] not in want:
        want[e['S']] = e['tour']
for S, tour in sorted(want.items()):
    name = "wf2d_hc_S%d" % S
    P = [0]*64
    for k in range(64):
        P[tour[k]] = tour[(k+1) % 64]
    assert sorted(P) == list(range(64))
    open("/tmp/P_%s.json" % name, "w").write(json.dumps(P))
    print(name, "S=%d" % S, flush=True)
PYEOF
for S in 404 448 452; do
  c="wf2d_hc_S$S"
  if [ ! -d $WF/validation/candidates/$c ]; then
    python3 $WF/validation/gen_from_P.py $c /tmp/P_$c.json >> $CHAINLOG 2>&1
    log "Phase C: built $c"
  fi
  log "Phase C: S2 screen $c"
  python3 $WF/validation/run_s2_screen.py $c >> $CHAINLOG 2>&1
  log "Phase C: S2 rc=$? for $c"
done

log "=== chain_phase ALL DONE ==="

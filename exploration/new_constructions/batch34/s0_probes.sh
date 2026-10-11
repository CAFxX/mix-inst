#!/bin/bash
# Batch-34 S0 cost probes: per-stage delay for dense stage forms.
# Usage: run under agentwork-launch.sh --nice 19 --tag track6/b34-s0
NC=/home/hatch/workspace/mix/exploration/new_constructions
B34=$NC/batch34
RS=/home/hatch/workspace/mix/exploration/run_synth.py
# INFRA 2026-10-11: /tmp is 100% full box-wide -> ABC temp script fails.
# Point TMPDIR at the batch34 tmp dir (verified working).
export TMPDIR="$B34/tmp"
mkdir -p "$TMPDIR" "$B34/s0_probes"
for t in stg_and1 stg_a3 stg_d2a3 stg_aoi stg_add16; do
  if [ ! -f "$B34/s0_probes/$t/s0_result.json" ]; then
    echo "$(date -u +%FT%TZ) S0 start $t" | tee -a "$B34/s0_probes.log"
    nice -n 19 python3 "$RS" "$B34/probes.v" "$t" "$B34/s0_probes/$t" >> "$B34/s0_probes.log" 2>&1
    echo "$(date -u +%FT%TZ) S0 done $t rc=$?" | tee -a "$B34/s0_probes.log"
  else
    echo "SKIP $t (already done)"
  fi
done
echo "$(date -u +%FT%TZ) ALL S0 PROBES DONE" | tee -a "$B34/s0_probes.log"

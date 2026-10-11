#!/bin/bash
# Batch-35 S0 cost probes: per-stage delay for shift-AND stage forms.
# Positive control stg_and1 must read ~3.3u (else toolchain/result untrusted).
B35=/home/hatch/workspace/mix/exploration/new_constructions/batch35
RS=/home/hatch/workspace/mix/exploration/run_synth.py
export TMPDIR="$B35/tmp"
mkdir -p "$TMPDIR" "$B35/s0_probes"
for t in stg_and1 stg_shand stg_shand_nm; do
  if [ ! -f "$B35/s0_probes/$t/s0_result.json" ]; then
    echo "$(date -u +%FT%TZ) S0 start $t" | tee -a "$B35/s0_probes.log"
    nice -n 19 python3 "$RS" "$B35/probes.v" "$t" "$B35/s0_probes/$t" >> "$B35/s0_probes.log" 2>&1
    echo "$(date -u +%FT%TZ) S0 done $t rc=$?" | tee -a "$B35/s0_probes.log"
  else
    echo "SKIP $t (already done)"
  fi
done
echo "$(date -u +%FT%TZ) ALL S0 PROBES DONE" | tee -a "$B35/s0_probes.log"

#!/bin/bash
# Batch-35 S0 per-stage probe RERUN (incarnation VII, 2026-10-11).
# The 02:05-02:36 serial runs produced NO RESULT lines (RuntimeErrors from the
# ref-ABC outage window + untrustworthy rc=0 interleaving). This rerun uses
# the DUT-only path (synth_one: identical Yosys flow, pinned toolchain,
# analyze.py==analyze2.py XCHECK, skips the mul64 reference) into FRESH dirs,
# serial order: positive control stg_and1 first (~3.3u expected), then
# stg_shand, then stg_shand_nm. Every RESULT line is evidence; absence = fail.
B35=/home/hatch/workspace/mix/exploration/new_constructions/batch35
OUT=/home/hatch/workspace/mix/exploration/new_constructions/batch37/s0_rerun2.log
mkdir -p "$B35/s0_probes_v2"
{
echo "$(date -u +%FT%TZ) S0-RERUN2 start"
for t in stg_and1 stg_shand stg_shand_nm; do
  echo "$(date -u +%FT%TZ) S0-RERUN2 start $t"
  nice -n 19 python3 "$B35/s0_dut_probe.py" "$B35/probes.v" "$t" "$B35/s0_probes_v2/$t"
  echo "$(date -u +%FT%TZ) S0-RERUN2 done $t rc=$?"
done
echo "$(date -u +%FT%TZ) S0-RERUN2 ALL DONE"
} 2>&1 | tee "$OUT"

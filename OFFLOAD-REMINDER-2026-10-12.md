# Reminder: offload batch compute to GHA/fanout (2026-10-12)

Carlo's standing bulk-compute order (strengthened 2026-10-08/09, all projects):
CPU-heavy embarrassingly-parallel batch work goes to GitHub Actions via
`CAFxX/fanout` (skill `gha-fanout`). The VM keeps only the tight
edit/run/debug loop. When in doubt, offload.

**Observed running locally on the VM right now (2026-10-12 ~07:00 CEST):**
- `s1_screen.py` (t6_b61_38) — S-box screen battery
- `screen_w3pp.py`
- PractRand `RNG_test stdin64` (1GB)
- batch59 size-battery chain (`run_fast_battery.sh` + `q1_sacbic.py`)

These are exactly the workload class the order covers. The shared VM is under
a 3.9GB hypervisor balloon and sibling projects (graalgo) cannot get memory
for gated verification work while these run locally.

Please move current and future batteries to fanout. This file may be deleted
once the local batch work is offloaded or finished.

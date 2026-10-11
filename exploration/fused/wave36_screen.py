#!/usr/bin/env python3
"""Wave-36: V-series two-lane re-screen with the RECALIBRATED triage.

Rationale (re-test trigger, not a blind re-run): wave-34's 0/100 used the
MISCALIBRATED marg proxy (bars -10.37/-7.1 that REJECTED both S1-clean
frontiers b33c/al_and6a -- wave-35 finding, ledger row "wave-35 S-box
co-design"). A 0/100 under a proxy that kills known-good designs is not
evidence against the construction. Re-screening with the recalibrated
proxy (PB -11.0 / RD -9.0, +RND64 scenario) and the harder exact-DIFF
triage (lin_diff, SEQ + RND64, bar <10) from wave35_lib.

Variants (from fused/wave34_probe.py, AND-only cross-lane throughout):
  V2   indep+cross, 3 stages: xn = x^(xa&xb)^(xc&yd) ; yn = y^(ye&yf)^(xg&yh)
  V3   V1 4-stage:             xn = x^(xa&yb)         ; yn = y^(yd&xe)
  V2x4 V2 structure, 4 stages (new: V2's diffusion + V3's depth)

Controls: wave-35 committed pair (b33c z=3.34 KEEP / wave-34 V0 z=739994 KILL)
-- run fused/wave35_controls.py before trusting results (already VERIFIED).

Cost notes: V3 ~2.5u/stage x4 ~= 10u; V2 ~3.5u/stage x3 ~= 10.5-14u --
both cost-eligible (< 19.8u) if quality passes. KEEPs escalate via the
b33 playbook (bundle + bit-exact + S0 + S1...).

Usage: wave36_screen.py <VARIANT> <N_TRY> [SEED]
Logs per-try JSONL to wave36_<VARIANT>_diag.jsonl (wave-35 lesson).
"""
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from wave35_lib import _marg_proxy, seq_exact_diff, rnd64_exact_diff
from wave34_probe import make_stages, make_mix

VARIANT = sys.argv[1]            # V2 | V3 | V2x4
N_TRY = int(sys.argv[2])
SEED = int(sys.argv[3], 0) if len(sys.argv) > 3 else {"V2": 0x362, "V3": 0x363, "V2x4": 0x364}[VARIANT]
OUTP = f"wave36_{VARIANT}_diag"

NSTAGES = {"V2": 3, "V3": 4, "V2x4": 4}[VARIANT]
BASE = {"V2": "V2", "V3": "V3", "V2x4": "V2"}[VARIANT]


def main():
    rng = random.Random(SEED)
    t0 = time.time()
    n_keep = n_marg = 0
    seq_zs = []
    with open(f"{OUTP}.jsonl", "w") as jf:
        for tried in range(1, N_TRY + 1):
            stages = make_stages(BASE, NSTAGES, rng)
            mix_fn = make_mix(BASE, stages)
            rec = {"try": tried, "stages": stages}
            ok_m, worst = _marg_proxy(mix_fn)
            rec["marg_ok"] = bool(ok_m)
            rec["marg_margin"] = worst[0]
            rec["marg_desc"] = worst[1]
            z = zr = None
            keep = False
            if ok_m:
                n_marg += 1
                z, _ = seq_exact_diff(mix_fn)
                rec["z"] = z
                seq_zs.append(z)
                if z < 10.0:
                    zr, _ = rnd64_exact_diff(mix_fn)
                    rec["zr"] = zr
                    keep = zr < 10.0
                    n_keep += keep
            status = ("KEEP" if keep else
                      ("SEQ-KILL" if (z is not None and z >= 10.0) else
                       ("RND64-KILL" if (zr is not None and zr >= 10.0) else "MARG-KILL")))
            rec["status"] = status
            jf.write(json.dumps(rec) + "\n")
            jf.flush()
            zs = f" z={z:.1f}" if z is not None else ""
            zrs = f" zr={zr:.1f}" if zr is not None else ""
            print(f"[{VARIANT}] TRY {tried}: marg={worst[0]:+.1f}{zs}{zrs} "
                  f"{status} ({time.time()-t0:.0f}s)", flush=True)
    seq_zs.sort()
    n = len(seq_zs)
    print(f"DONE [{VARIANT}]: {N_TRY} tries, marg-pass {n_marg}/{N_TRY}, KEEP {n_keep}",
          flush=True)
    if seq_zs:
        print(f"  seq-z dist: min={seq_zs[0]:.1f} med={seq_zs[n//2]:.1f} "
              f"max={seq_zs[-1]:.1f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()

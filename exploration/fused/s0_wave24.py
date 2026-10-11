#!/usr/bin/env python3
"""S0 runner for wave-24 survivors: synth DUT via run_synth.synth_one."""
import os, sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from run_synth import synth_one
EXP = "/home/hatch/workspace/mix/exploration"
CAND = os.path.join(EXP, "fast_battery", "candidates")
WORK = os.path.join(EXP, "fused", "s0_work")
NAMES = sys.argv[1:] or ["fz24_o", "fz24_p"]
def main():
    for name in NAMES:
        src = os.path.join(CAND, name, "rtl.v")
        wd = os.path.join(WORK, name)
        t0 = time.time()
        try:
            r = synth_one(src, name, os.path.join(wd, "_dut"))
            dt = time.time() - t0
            print(f"RESULT name={name} cells={r['cells']} area={r['area']:.0f} "
                  f"crit={r['crit']:.1f}u synth_time={dt:.0f}s", flush=True)
        except Exception as e:
            print(f"RESULT name={name} FAILED: {str(e)[:300]}", flush=True)
if __name__ == "__main__":
    main()

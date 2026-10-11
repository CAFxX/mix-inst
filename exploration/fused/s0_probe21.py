#!/usr/bin/env python3
"""Light S0 probe runner for wave-21: synth DUT only (no mul64 ref).

Reuses run_synth.synth_one (pinned Yosys 0.69, dual-analyzer cross-check).
Usage: python3 s0_probe21.py [workdir_suffix]
Prints one RESULT line per probe. Work goes under fused/s0_work/wl21_<name>/.
"""
import os, sys, time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from run_synth import synth_one

EXP = "/home/hatch/workspace/mix/exploration"
RTL = os.path.join(EXP, "fused", "wave21_rtl")
WORK = os.path.join(EXP, "fused", "s0_work")

def main():
    names = sorted(f[:-2] for f in os.listdir(RTL) if f.endswith(".v"))
    for name in names:
        src = os.path.join(RTL, name + ".v")
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

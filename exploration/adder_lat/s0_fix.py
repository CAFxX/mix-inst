#!/usr/bin/env python3
"""S0 re-run for the 120-schedule and6 search (2026-10-10).

Fixes the crit-parse bug in resume_search_and6.py: its regex
re.search(r"crit=([\\d.]+)", stdout) matched the FIRST 'crit=' token in
run_synth.py output, which is the mul64 REFERENCE line (ref_crit=103.5),
not the DUT's crit. Every 'S0 ... crit=103.5u' line in search_and6_120.log
is therefore the reference, not a measurement.

This script:
  1. Reads all 42 KEEP lines (i=0..57 original run + i=58..119 resume run)
     from search_and6_120.log.
  2. Builds RTL via gen_waveP.build for any tag missing from
     fast_battery/candidates/.
  3. Synthesizes the mul64 reference ONCE (cached) and each DUT, parsing
     the DUT line (DUT <top> ... crit=<v>) explicitly.
  4. Appends real results to search_and6_120_s0fix.log.
"""
import os
import re
import subprocess
import sys

AD = "/home/hatch/workspace/mix/exploration/adder_lat"
EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, AD)
sys.path.insert(0, EXP)
from gen_waveP import build
import run_synth

LOG = os.path.join(AD, "search_and6_120.log")
FIXLOG = os.path.join(AD, "search_and6_120_s0fix.log")
WORK = "/tmp/s0fix"


def parse_dut_crit(stdout):
    m = re.search(r"^DUT\s+\S+.*?crit=([\d.]+)", stdout, re.M)
    assert m, "no DUT crit line in run_synth output"
    return float(m.group(1))


def main():
    keeps = []
    with open(LOG) as f:
        for line in f:
            m = re.match(r"z=\s*([\d.]+)\s+KEEP\s+(as6_200_\d+)\s+(\[.*\])", line)
            if m:
                keeps.append((float(m.group(1)), m.group(2), eval(m.group(3))))
    os.makedirs(WORK, exist_ok=True)
    ref = run_synth.synth_one(run_synth.REF_V, "mul64", os.path.join(WORK, "_ref"))
    print(f"REF mul64: crit={ref['crit']:.1f} (cached, reused for all DUTs)", flush=True)

    with open(FIXLOG, "a") as fl:
        fl.write(f"# S0 fix run: {len(keeps)} candidates, ref crit={ref['crit']:.1f}\n")
        fl.flush()
        for z, tag, sched in keeps:
            try:
                st = [("and", a, b, c) for (a, b, c) in sched]
                cdir = os.path.join(EXP, "fast_battery/candidates", tag)
                rtl = os.path.join(cdir, "rtl.v")
                if not os.path.exists(rtl):
                    build(tag, st, f"and6 sched search {tag} z={z:.1f}", "SKINNY")
                wd = os.path.join(WORK, "_" + tag)
                r = subprocess.run(
                    [sys.executable, "-c",
                     "import sys,os; sys.path.insert(0,'" + EXP + "'); "
                     "import run_synth; "
                     "d=run_synth.synth_one(sys.argv[1],sys.argv[2],sys.argv[3]); "
                     "print('DUT '+sys.argv[2]+' crit=%.1f area=%.0f cells=%d' % (d['crit'],d['area'],d['cells']))",
                     rtl, tag, wd],
                    capture_output=True, text=True, timeout=900)
                m = re.search(r"^DUT\s+\S+\s+crit=([\d.]+)\s+area=([\d.]+)\s+cells=(\d+)", r.stdout, re.M)
                assert m, f"parse fail for {tag}:\nstdout={r.stdout[-1500:]}\nstderr={r.stderr[-1500:]}"
                crit, area, cells = float(m.group(1)), float(m.group(2)), int(m.group(3))
                line = (f"S0FIX {tag}: crit={crit:.1f}u z={z:.1f} cells={cells} "
                        f"delay_ratio={crit/ref['crit']:.3f} sched={sched}")
                print(line, flush=True)
                fl.write(line + "\n")
                fl.flush()
            except Exception as e:
                err = f"S0FIX {tag}: ERROR {e}"
                print(err, flush=True)
                fl.write(err + "\n")
                fl.flush()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Item 3 S0 runner: run_synth.py + check_rtl equiv for rasC2_0 / rasC1_2.
Usage: s0_item3.py <candidate>   (candidate short name: rasC2_0 | rasC1_2)
Writes round25/s0_r25_top4_<short>/{s0.log,s0_result.json}.
Polite: waits while >=2 yosys processes run (foreign or own).
Resumable: skips if s0_result.json already has a verdict."""
import json
import os
import re
import subprocess
import sys
import time

EXP = "/home/hatch/workspace/mix/exploration"
FB = EXP + "/fast_battery"
SHORT2CAND = {
    "rasC2_0": "r25_spn_pba19_sb_rasC2_0_nw",
    "rasC1_2": "r25_spn_pba19_sb_rasC1_2_nw",
}
BAR = 0.9


def yosys_count():
    r = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True)
    return sum(1 for l in r.stdout.splitlines()
               if "yosys" in l and "grep" not in l)


def main():
    short = sys.argv[1]
    cand = SHORT2CAND[short]
    outdir = os.path.join(EXP, "round25", f"s0_r25_top4_{short}")
    os.makedirs(outdir, exist_ok=True)
    res_path = os.path.join(outdir, "s0_result.json")
    if os.path.exists(res_path):
        d = json.load(open(res_path))
        if d.get("verdict") in ("PASS", "FAIL"):
            print(f"[S0 {cand}] already {d['verdict']}, skipping")
            return 0
    log = open(os.path.join(outdir, "s0.log"), "a")
    rtl = os.path.join(FB, "candidates", cand, "rtl.v")

    while yosys_count() >= 2:
        print("[S0 polite] >=2 yosys running, sleeping 60s", flush=True)
        time.sleep(60)

    t0 = time.time()
    r = subprocess.run(
        [sys.executable, os.path.join(EXP, "run_synth.py"), rtl, cand,
         os.path.join(outdir, "_synth")],
        capture_output=True, text=True)
    t_dut = time.time() - t0
    log.write(r.stdout + r.stderr)
    m = re.search(r"RESULT name=\S+ cells=(\d+) area=([\d.]+) crit=([\d.]+) "
                  r"delay_ratio=([\d.]+)", r.stdout)
    if not m:
        log.write("S0 INFRA FAIL: no RESULT line\n")
        print(f"[S0 {cand}] INFRA FAIL")
        return 1
    cells, area, crit, ratio = (int(m.group(1)), float(m.group(2)),
                               float(m.group(3)), float(m.group(4)))
    verdict = "PASS" if ratio <= BAR else "FAIL"

    # equiv check (iverilog, 1000 vectors vs numpy model)
    t1 = time.time()
    r2 = subprocess.run(
        [sys.executable, os.path.join(EXP, "check_rtl.py"),
         f"round25.models.r25.{cand}", rtl, cand, outdir, "1000"],
        capture_output=True, text=True)
    t_equiv = time.time() - t1
    log.write(r2.stdout + r2.stderr)
    equiv_ok = ("RTLCHECK" in r2.stdout and "PASS" in r2.stdout
                and r2.returncode == 0)
    if not equiv_ok:
        verdict = "FAIL"
    out = {
        "candidate": cand, "verdict": verdict,
        "delay_u": crit, "cells": cells, "area": area,
        "delay_ratio_vs_mult": ratio, "ratio_bar": BAR,
        "equiv_check": {"ok": bool(equiv_ok), "detail": "n=1000",
                        "nvecs": 1000},
        "flow": "yosys 0.69+ abc -genlib mini.genlib, explicit no-dretime script (see README)",
        "time_dut_s": round(t_dut, 1), "time_equiv_s": round(t_equiv, 1),
    }
    json.dump(out, open(res_path, "w"), indent=1)
    line = (f"[S0 {cand}] delay={crit:.1f}u cells={cells} x_mult={ratio:.3f} "
            f"(bar {BAR}) equiv={'ok' if equiv_ok else 'FAIL'} -> {verdict}")
    log.write(line + "\n")
    print(line, flush=True)
    print(f"S0 EXIT: {0 if verdict == 'PASS' else 2}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())

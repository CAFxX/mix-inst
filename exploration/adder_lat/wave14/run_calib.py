#!/usr/bin/env python3
"""Wave-14 calibration: S0 (run_synth.py, pinned Yosys 0.69, XCHECK) for each
word-level primitive in calib.v. Parses the RESULT line's FIRST crit= (the DUT,
not ref_crit — cf. the 2026-10-10 22:55 vacuous-sweep lesson)."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_SYNTH = "/home/hatch/workspace/mix/exploration/run_synth.py"
CALIB_V = os.path.join(HERE, "calib.v")
WORK = os.path.join(HERE, "work")

TOPS = [
    "w_add64", "w_add32x2", "w_add16x4",
    "w_add3", "w_add4",
    "w_mul16", "w_mul32", "w_mulc64", "w_gf64",
]


def synth(top):
    wd = os.path.join(WORK, f"calib_{top}")
    # 2026-10-11: the yosys->abc pipe STALLS (0-CPU hang, never clears) when the
    # ABC temp path is long: ABC echoes "abc 01> source <tmpdir>/abc.script",
    # and for echo lines >60 cols on non-TTY stdin ABC emits "\r"+overflow
    # only, dropping the "source " keyword -- yosys's read_until_abc_done then
    # never sets seen_source_cmd and loops in read() forever AFTER abc
    # successfully finishes (track-6 root cause, strace byte-level proof).
    # run_synth.py now forces TMPDIR=/tmp for the yosys invocation, so the
    # retry below is a backstop, not the fix; fail loudly if both attempts fail.
    last = None
    for attempt in (1, 2):
        try:
            r = subprocess.run([sys.executable, RUN_SYNTH, CALIB_V, top, wd],
                               capture_output=True, text=True, timeout=1800)
            last = r
            if r.returncode == 0:
                break
            print(f"{top}: attempt {attempt} run_synth rc={r.returncode} "
                  f"-- retrying", flush=True)
        except subprocess.TimeoutExpired:
            print(f"{top}: attempt {attempt} timed out after 1800s -- retrying",
                  flush=True)
    r = last
    out = r.stdout + r.stderr
    if r.returncode != 0:
        raise RuntimeError(f"run_synth failed for {top}:\n{out[-3000:]}")
    mline = re.search(r"^RESULT.*$", out, re.M)
    assert mline, f"no RESULT line for {top}:\n{out[-2000:]}"
    line = mline.group(0)
    crit = float(re.search(r"crit=([0-9.]+)", line).group(1))  # first crit= = DUT
    cells = int(re.search(r"cells=(\d+)", line).group(1))
    area = float(re.search(r"area=([0-9.]+)", line).group(1))
    refcrit = float(re.search(r"ref_crit=([0-9.]+)", line).group(1))
    return {"crit": crit, "cells": cells, "area": area, "ref_crit": refcrit}


def main():
    os.makedirs(WORK, exist_ok=True)
    # 2026-10-11: /tmp (512M tmpfs) is 100% full of sibling scratch (graalgo);
    # Yosys ABC temp dirs die there. Redirect ours under the workspace.
    os.environ["TMPDIR"] = os.path.join(WORK, "tmp")
    os.makedirs(os.environ["TMPDIR"], exist_ok=True)
    res = {}
    for top in TOPS:
        d = synth(top)
        res[top] = d
        print(f"{top:12s} crit={d['crit']:.1f}u cells={d['cells']} "
              f"area={d['area']:.0f} (ref mul64 {d['ref_crit']:.1f}u)", flush=True)
    with open(os.path.join(WORK, "calib.json"), "w") as f:
        json.dump(res, f, indent=1)
    a64 = res["w_add64"]["crit"]
    print(f"\nADD64 north star: {a64:.1f}u; adder-like bar (~1.5x): {1.5*a64:.1f}u; "
          f"frontier bar: 19.8u")
    # CSA-inference verdict
    d3 = res["w_add3"]["crit"] - a64
    d4 = res["w_add4"]["crit"] - a64
    print(f"CSA probe: add3-add64={d3:+.1f}u, add4-add64={d4:+.1f}u "
          f"(~+2u/op => CSA fused; ~+{a64:.0f}u/op => chained CPA)")


if __name__ == "__main__":
    main()

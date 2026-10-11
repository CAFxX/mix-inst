#!/usr/bin/env python3
"""RTL-vs-model check via yosys 'sim' (no iverilog on this box).

Usage: rtl_sim_check.py <candir> <top> [nvec=64]
Builds a yosys script that reads the RTL, then for each (val,key) vector
sets inputs and reads 'out', comparing against the numpy model.
"""
import importlib.util
import os
import subprocess
import sys

import numpy as np

YOSYS = "/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys"


def main():
    candir, top = sys.argv[1], sys.argv[2]
    nvec = int(sys.argv[3]) if len(sys.argv) > 4 else 64
    rtl = os.path.join(candir, "rtl.v")
    spec = importlib.util.spec_from_file_location("m", os.path.join(candir, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    rng = np.random.default_rng(0xBEEF)
    V = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    E = m.mix_np(V, K)

    cmds = [f"read_verilog {rtl}", f"hierarchy -check -top {top}", "prep"]
    for i in range(nvec):
        cmds.append(f"sim -set val {int(V[i])} -set key {int(K[i])}")
        cmds.append(f"sim -get out")
    cmds.append("sim -reset")
    r = subprocess.run([YOSYS, "-p", "; ".join(cmds)], capture_output=True,
                       text=True, timeout=600)
    got = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("Value out:"):
            got.append(int(line.split(":", 1)[1].strip(), 0))
    assert len(got) == nvec, f"got {len(got)}/{nvec} values:\n{r.stdout[-2000:]}"
    bad = [(i, int(E[i]), got[i]) for i in range(nvec) if int(E[i]) != got[i]]
    if bad:
        print(f"RTLCHECK FAIL: {len(bad)}/{nvec} mismatches, first: {bad[0]}")
        sys.exit(1)
    print(f"RTLCHECK PASS ({nvec}/{nvec} vectors, top={top})")


if __name__ == "__main__":
    main()

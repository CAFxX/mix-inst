#!/usr/bin/env python3
"""Round 23 fast xcheck: identical to fast_battery/src/xcheck.py in vectors and
verdict logic, but evaluates the Python model VECTORIZED (mix_np on the full
array) instead of one scalar mix() call per vector. ~100x faster; the C side
(--hash binary) and the comparison are unchanged.

Usage: xcheck_fast.py <candidate> <binary> <nvecs> <out_vecfile>
Exits 0 iff all vectors match.
"""
import importlib.util
import random
import subprocess
import sys

import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery"


def load_model_np(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix_np


def main():
    cand, binary, nvecs, vecfile = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    mix_np = load_model_np(cand)
    rng = random.Random(0xC0FFEE)  # identical vectors to xcheck.py
    vecs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(nvecs)]
    with open(vecfile, "w") as f:
        for v, k in vecs:
            f.write("%016x %016x\n" % (v, k))
    r = subprocess.run([binary, "--hash", vecfile], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"XCHECK {cand}: C --hash failed rc={r.returncode}\n{r.stderr[-1000:]}")
        return 1
    V = np.array([v for v, _ in vecs], dtype=np.uint64)
    K = np.array([k for _, k in vecs], dtype=np.uint64)
    PY = np.asarray(mix_np(V, K), dtype=np.uint64)
    bad = 0
    lines = r.stdout.splitlines()
    if len(lines) != nvecs:
        print(f"XCHECK {cand}: FAIL C emitted {len(lines)} lines, expected {nvecs}")
        return 1
    for i, ((v, k), line) in enumerate(zip(vecs, lines)):
        parts = line.split()
        if len(parts) != 3:
            bad += 1
            continue
        cv, ck, ch = (int(p, 16) for p in parts)
        if cv != v or ck != k or ch != int(PY[i]):
            bad += 1
            if bad <= 3:
                print(f"  mismatch v={v:016x} k={k:016x} C={ch:016x} py={int(PY[i]):016x}")
    if bad:
        print(f"XCHECK {cand}: FAIL {bad}/{nvecs} mismatches")
        return 1
    print(f"XCHECK {cand}: PASS {nvecs}/{nvecs} C==Python")
    return 0


if __name__ == "__main__":
    sys.exit(main())

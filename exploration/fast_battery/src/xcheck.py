#!/usr/bin/env python3
"""Cross-check: C impl (--hash mode) vs Python model on N random (v,k) vectors.
Usage: xcheck.py <candidate> <binary> <nvecs> <out_vecfile>
Exits 0 iff all vectors match. This gates every C-based stage (S2/S3/S4):
a mismatch means the C port is wrong, not the candidate.
"""
import importlib.util
import random
import subprocess
import sys

FB = "/home/hatch/workspace/mix/exploration/fast_battery"

def load_model(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix

def main():
    cand, binary, nvecs, vecfile = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    mix = load_model(cand)
    rng = random.Random(0xC0FFEE)
    vecs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(nvecs)]
    with open(vecfile, "w") as f:
        for v, k in vecs:
            f.write("%016x %016x\n" % (v, k))
    r = subprocess.run([binary, "--hash", vecfile], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"XCHECK {cand}: C --hash failed rc={r.returncode}\n{r.stderr[-1000:]}")
        return 1
    bad = 0
    for (v, k), line in zip(vecs, r.stdout.splitlines()):
        parts = line.split()
        if len(parts) != 3:
            bad += 1
            continue
        cv, ck, ch = (int(p, 16) for p in parts)
        if cv != v or ck != k or ch != (mix(v, k) & ((1 << 64) - 1)):
            bad += 1
            if bad <= 3:
                print(f"  mismatch v={v:016x} k={k:016x} C={ch:016x} py={mix(v,k):016x}")
    if bad:
        print(f"XCHECK {cand}: FAIL {bad}/{nvecs} mismatches")
        return 1
    print(f"XCHECK {cand}: PASS {nvecs}/{nvecs} C==Python")
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Bit-exact check wave-24: model.py mix() vs compiled impl.c mix_hash(). 200 vectors."""
import os, subprocess, sys, tempfile, random

EXP = "/home/hatch/workspace/mix/exploration"
CAND = os.path.join(EXP, "fast_battery", "candidates")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from gen_fused24 import SPECS

HARNESS = r"""
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
uint64_t mix_hash(uint64_t v, uint64_t k);
int main(void) {
    uint64_t v, k;
    while (scanf("%" SCNx64 " %" SCNx64, &v, &k) == 2)
        printf("%016" PRIx64 "\n", mix_hash(v, k));
    return 0;
}
"""

def main():
    rng = random.Random(0xF224)
    vecs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(200)]
    ok_all = True
    for name, stages, desc in [s for s in SPECS]:
        d = os.path.join(CAND, name)
        sys.path.insert(0, d)
        for mod in list(sys.modules):
            if mod == "model":
                del sys.modules[mod]
        import model
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "t.c")
            exe = os.path.join(td, "t")
            open(src, "w").write(open(os.path.join(d, "impl.c")).read() + HARNESS)
            r = subprocess.run(["cc", "-O2", "-o", exe, src],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(f"BITEXACT name={name} COMPILE-FAIL {r.stderr[:200]}")
                ok_all = False
                continue
            inp = "".join(f"{v:016x} {k:016x}\n" for v, k in vecs)
            r = subprocess.run([exe], input=inp, capture_output=True, text=True)
            got = r.stdout.strip().split("\n")
            n_ok = sum(1 for (v, k), g in zip(vecs, got)
                       if model.mix(v, k) == int(g, 16))
            print(f"BITEXACT name={name} {n_ok}/200", flush=True)
            if n_ok != 200:
                ok_all = False
        sys.path.remove(d)
    print("ALL-OK" if ok_all else "FAILURES-PRESENT")

if __name__ == "__main__":
    main()

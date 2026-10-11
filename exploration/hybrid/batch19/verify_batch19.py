#!/usr/bin/env python3
"""Verify batch-19 bundles: compile impl.c, compare mix_hash vs model.py
on 200 random vectors. Bit-exactness is the gate before S0."""
import os
import random
import subprocess
import sys

CANDS_DIR = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
TMP = "/tmp/b19_verify"


def main():
    names = sys.argv[1:]
    random.seed(20261010)
    vecs = [(random.getrandbits(64), random.getrandbits(64)) for _ in range(200)]
    os.makedirs(TMP, exist_ok=True)
    inp = "\n".join(f"{v:#018x} {k:#018x}" for v, k in vecs) + "\n"

    ok_all = True
    for name in names:
        d = os.path.join(CANDS_DIR, name)
        harness = os.path.join(TMP, f"{name}_harness.c")
        with open(harness, "w") as f:
            f.write(
                '#include <stdio.h>\n#include <stdint.h>\n'
                'uint64_t mix_hash(uint64_t val, uint64_t key);\n'
                'int main(void){unsigned long long v,k;\n'
                'while(scanf("%llx %llx",&v,&k)==2)\n'
                'printf("%016llx\\n",(unsigned long long)mix_hash(v,k));\n'
                'return 0;}\n')
        exe = os.path.join(TMP, name)
        r = subprocess.run(["cc", "-O2", "-o", exe, harness,
                            os.path.join(d, "impl.c")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: COMPILE FAIL\n{r.stderr[-500:]}")
            ok_all = False
            continue
        r = subprocess.run([exe], input=inp, capture_output=True, text=True,
                           timeout=60)
        c_out = r.stdout.strip().split("\n")

        if "model" in sys.modules:
            del sys.modules["model"]
        sys.path.insert(0, d)
        mod = importlib.import_module("model")
        sys.path.pop(0)
        py_out = [f"{mod.mix_hash(v, k):016x}" for v, k in vecs]
        del sys.modules["model"]

        mism = sum(1 for a, b in zip(c_out, py_out) if a != b)
        if mism == 0 and len(c_out) == 200:
            print(f"{name}: bit-exact 200/200 OK")
        else:
            print(f"{name}: MISMATCH {mism}/200 (got {len(c_out)} lines)")
            ok_all = False
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()

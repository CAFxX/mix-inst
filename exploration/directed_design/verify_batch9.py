#!/usr/bin/env python3
"""Batch-9 bit-exactness verification: model.py vs impl.c on 214 vectors,
then RTL vs model via check_rtl.py on 52 vectors (iverilog).

Usage: verify_batch9.py
Exit 0 iff all 6 candidates pass both gates.
"""
import importlib.util
import os
import subprocess
import sys

DD = "/home/hatch/workspace/mix/exploration/directed_design"
FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
NAMES = ["dd9_scsc_linall_a", "dd9_scsc_linall_k", "dd9_scsc_nolin_a",
         "dd9_sccs_nolin_a", "dd9_cssc_nolin_a", "dd9_scsc_nolin_b"]
NVEC_MODEL_C = 214
NVEC_RTL = 52

HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
uint64_t mix_hash(uint64_t v, uint64_t k);
int main(void) {
    unsigned long long v, k;
    while (scanf("%llx %llx", &v, &k) == 2)
        printf("%016llx\n", (unsigned long long)mix_hash((uint64_t)v, (uint64_t)k));
    return 0;
}
'''


def load_model(name):
    p = os.path.join(FB, "candidates", name, "model.py")
    spec = importlib.util.spec_from_file_location("model_" + name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    import numpy as np
    rng = np.random.default_rng(0xD6D6)
    V = rng.integers(0, 2**64, size=NVEC_MODEL_C, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=NVEC_MODEL_C, dtype=np.uint64)

    workdir = "/tmp/b9_verify"
    os.makedirs(workdir, exist_ok=True)
    open(os.path.join(workdir, "harness.c"), "w").write(HARNESS)

    all_ok = True
    for name in NAMES:
        # --- model vs C ---
        m = load_model(name)
        E = [m.mix(int(V[i]), int(K[i])) for i in range(NVEC_MODEL_C)]
        impl = os.path.join(workdir, f"impl_{name}.c")
        src = open(f"/tmp/b9_{name}/impl.c").read()
        open(impl, "w").write(src)
        exe = os.path.join(workdir, f"harness_{name}")
        r = subprocess.run(["gcc", "-O2", "-o", exe, impl,
                            os.path.join(workdir, "harness.c")],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"{name}: C COMPILE FAILED\n{r.stderr[-1500:]}")
            all_ok = False
            continue
        vec_in = "\n".join(f"{int(V[i]):016x} {int(K[i]):016x}" for i in range(NVEC_MODEL_C))
        r = subprocess.run([exe], input=vec_in, capture_output=True, text=True, timeout=120)
        got = r.stdout.strip().split()
        if len(got) != NVEC_MODEL_C:
            print(f"{name}: C harness produced {len(got)} outputs, want {NVEC_MODEL_C}")
            all_ok = False
            continue
        bad = [i for i in range(NVEC_MODEL_C) if int(got[i], 16) != E[i]]
        if bad:
            print(f"{name}: model vs C MISMATCH on {len(bad)}/{NVEC_MODEL_C} (first bad idx {bad[0]})")
            all_ok = False
        else:
            print(f"{name}: model vs C {NVEC_MODEL_C}/{NVEC_MODEL_C} OK")

        # --- RTL vs model (iverilog) ---
        rtl = os.path.join(DD, "candidates", name + ".v")
        wdir = os.path.join(workdir, f"rtl_{name}")
        r = subprocess.run(
            ["nice", "-n", "10", sys.executable, os.path.join(EXP, "check_rtl.py"),
             f"fast_battery.candidates.{name}.model.mix_np", rtl, name, wdir, str(NVEC_RTL)],
            capture_output=True, text=True, timeout=600, cwd=EXP)
        tail = (r.stdout + r.stderr).strip().splitlines()
        tail = tail[-1] if tail else "(no output)"
        if r.returncode != 0:
            print(f"{name}: RTL check FAILED: {tail}")
            all_ok = False
        else:
            print(f"{name}: RTL vs model {NVEC_RTL}/{NVEC_RTL} ({tail})")

    print("VERIFY " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

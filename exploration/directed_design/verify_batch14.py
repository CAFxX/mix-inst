#!/usr/bin/env python3
"""Batch-14 bit-exactness verification:
  1. screen-numpy (d10_screen.mix_np_spec on batch14_specs.json) vs
     mk_model model.py mix_np on 900 random (v,k) — the D10 XCHECK;
  2. model.py vs impl.c on 214 vectors;
  3. RTL vs model via check_rtl.py on 52 vectors (iverilog).

Usage: verify_batch14.py [name ...]   (default: all 4)
Exit 0 iff all candidates pass all three gates.
Workdir is inside directed_design/ (reboot-safe, unlike /tmp).
"""
import importlib.util
import json
import os
import subprocess
import sys

DD = "/home/hatch/workspace/mix/exploration/directed_design"
FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
ALL = ["dd14_ax1_shr2_shr5", "dd14_ax1_shl2_shr6",
       "dd14_ax2_ssss_midori_1943", "dd14_ax2_ssss_midori_r13_shr6"]
NAMES = sys.argv[1:] or ALL
NVEC_XCHECK = 900
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
    sys.path.insert(0, DD)
    import d10_screen
    specs = {s["name"]: s for s in
             json.load(open(os.path.join(DD, "specs", "batch14_specs.json")))}

    workdir = os.path.join(DD, "work_batch14", "verify")
    os.makedirs(workdir, exist_ok=True)
    open(os.path.join(workdir, "harness.c"), "w").write(HARNESS)

    all_ok = True
    for name in NAMES:
        m = load_model(name)
        spec = specs[name]

        # --- 1. screen-numpy vs artifact model (the D10 XCHECK) ---
        rng = np.random.default_rng(0xD11D14)
        Vx = rng.integers(0, 2**64, size=NVEC_XCHECK, dtype=np.uint64)
        Kx = rng.integers(0, 2**64, size=NVEC_XCHECK, dtype=np.uint64)
        E = m.mix_np(Vx, Kx)
        # note: mix_np_spec takes a scalar key; model.mix_np takes vector K.
        # compare elementwise with the same per-vector keys via scalar calls.
        bad = 0
        for i in range(NVEC_XCHECK):
            sv = int(d10_screen.mix_np_spec(
                np.array([Vx[i]]), int(Kx[i]), spec)[0])
            if sv != int(E[i]):
                bad += 1
                if bad <= 3:
                    print(f"{name}: XCHECK mismatch i={i}: "
                          f"screen={sv:016x} model={E[i]:016x}")
        if bad:
            print(f"{name}: screen vs model MISMATCH {bad}/{NVEC_XCHECK}")
            all_ok = False
        else:
            print(f"{name}: screen vs model {NVEC_XCHECK}/{NVEC_XCHECK} OK")

        # --- 2. model vs C ---
        rng = np.random.default_rng(0xD10D)
        V = rng.integers(0, 2**64, size=NVEC_MODEL_C, dtype=np.uint64)
        K = rng.integers(0, 2**64, size=NVEC_MODEL_C, dtype=np.uint64)
        E = [m.mix(int(V[i]), int(K[i])) for i in range(NVEC_MODEL_C)]
        impl = os.path.join(DD, "work_batch14", f"impl_{name}", "impl.c")
        if not os.path.exists(impl):
            print(f"{name}: MISSING {impl}")
            all_ok = False
            continue
        exe = os.path.join(workdir, f"harness_{name}")
        r = subprocess.run(["gcc", "-O2", "-o", exe, impl,
                            os.path.join(workdir, "harness.c")],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"{name}: C COMPILE FAILED\n{r.stderr[-1500:]}")
            all_ok = False
            continue
        vec_in = "\n".join(f"{int(V[i]):016x} {int(K[i]):016x}"
                           for i in range(NVEC_MODEL_C))
        r = subprocess.run([exe], input=vec_in, capture_output=True,
                           text=True, timeout=120)
        got = r.stdout.strip().split()
        if len(got) != NVEC_MODEL_C:
            print(f"{name}: C harness produced {len(got)} outputs, "
                  f"want {NVEC_MODEL_C}")
            all_ok = False
            continue
        bad = [i for i in range(NVEC_MODEL_C) if int(got[i], 16) != E[i]]
        if bad:
            print(f"{name}: model vs C MISMATCH on {len(bad)}/{NVEC_MODEL_C} "
                  f"(first bad idx {bad[0]})")
            all_ok = False
        else:
            print(f"{name}: model vs C {NVEC_MODEL_C}/{NVEC_MODEL_C} OK")

        # --- 3. RTL vs model (iverilog) ---
        rtl = os.path.join(DD, "candidates", name + ".v")
        wdir = os.path.join(workdir, f"rtl_{name}")
        env = dict(os.environ)
        env["PATH"] = os.path.expanduser("~/tools/ivl-env/bin") + ":" + env.get("PATH", "")
        r = subprocess.run(
            ["nice", "-n", "10", sys.executable, os.path.join(EXP, "check_rtl.py"),
             f"fast_battery.candidates.{name}.model.mix_np", rtl, name, wdir, str(NVEC_RTL)],
            capture_output=True, text=True, timeout=600, cwd=EXP, env=env)
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

#!/usr/bin/env python3
"""Wave-1 triage: (1) C-vs-Python bit-exactness, (2) avalanche, (3) mini differential scan.
Cheap pre-screen before official S0/S1/S2. Single-threaded, polite.
Usage: triage.py <cand> [cand ...]
"""
import importlib.util, json, math, os, subprocess, sys
import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
TMP = "/home/hatch/workspace/tmp"
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def load_model(cand):
    p = os.path.join(FB, cand, "model.py")
    spec = importlib.util.spec_from_file_location("tm_" + cand, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def xcheck_c(cand, n=2000):
    """Compile impl.c with a vector harness; compare vs Python model."""
    cdir = os.path.join(FB, cand)
    harness = os.path.join(TMP, f"xch_{cand}.c")
    exe = os.path.join(TMP, f"xch_{cand}")
    with open(harness, "w") as f:
        f.write('#include <stdio.h>\n#include <stdint.h>\n#include <inttypes.h>\n'
                'uint64_t mix_hash(uint64_t v, uint64_t k);\n'
                'int main(int argc, char**argv){uint64_t v,k;\n'
                ' while(scanf("%" SCNx64 " %" SCNx64, &v, &k)==2)\n'
                '  printf("%016" PRIx64 "\\n", mix_hash(v,k));\n'
                ' return 0;}\n')
    r = subprocess.run(["gcc", "-O2", "-o", exe, harness, os.path.join(cdir, "impl.c")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return f"C-COMPILE-FAIL: {r.stderr[-500:]}"
    rng = np.random.default_rng(1234)
    vs = rng.integers(0, 2**64, n, dtype=np.uint64)
    ks = rng.integers(0, 2**64, n, dtype=np.uint64)
    inp = "\n".join(f"{int(v):x} {int(k):x}" for v, k in zip(vs, ks))
    r = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return f"C-RUN-FAIL: {r.stderr[-500:]}"
    lines = r.stdout.strip().split("\n")
    if len(lines) != n:
        return f"C-LINE-COUNT {len(lines)} != {n}"
    m = load_model(cand)
    for i, (v, k) in enumerate(zip(vs, ks)):
        py = m.mix(int(v), int(k))
        c = int(lines[i], 16)
        if py != c:
            return f"MISMATCH vec {i}: py={py:#x} c={c:#x}"
    return "OK"

def avalanche(m, n=20000, seed=7):
    """Flip each input bit; measure output flip probs. Returns (maxdev, meandev)."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, n, dtype=np.uint64)
    k = np.uint64(0x123456789ABCDEF0)
    base = m.mix_np(xs, k)
    devs = []
    for b in range(64):
        out = m.mix_np(xs ^ (np.uint64(1) << np.uint64(b)), k)
        d = out ^ base
        # count ones per bit position
        cnt = np.unpackbits(d.view(np.uint8)).reshape(n, 64).sum(axis=0)
        # bit order within unpackbits: MSB first per byte; just take max dev over all 64
        p = cnt / n
        devs.append(np.abs(p - 0.5).max())
    return float(np.max(devs)), float(np.mean(devs))

def mini_diff(m, n=2**18, seed=99):
    """N pairs, 12 weight-1 deltas; report max |z| of per-output-bit bias."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, n, dtype=np.uint64)
    k = np.uint64(0x123456789ABCDEF0)
    base = m.mix_np(xs, k)
    zmax = 0.0
    for b in [0, 1, 5, 13, 31, 32, 33, 47, 55, 60, 61, 63]:
        out = m.mix_np(xs ^ (np.uint64(1) << np.uint64(b)), k)
        d = (out ^ base).astype(np.uint64)
        for ob in range(64):
            ones = int(((d >> np.uint64(ob)) & np.uint64(1)).sum())
            z = abs(ones - n / 2) / math.sqrt(n / 4)
            if z > zmax:
                zmax = z
    return zmax

def main():
    for cand in sys.argv[1:]:
        try:
            xc = xcheck_c(cand)
        except Exception as e:
            xc = f"XCHECK-EXC {e}"
        line = f"{cand}: xcheck={xc}"
        if xc == "OK":
            try:
                m = load_model(cand)
                t0 = __import__("time").time()
                amax, amean = avalanche(m)
                zd = mini_diff(m)
                dt = __import__("time").time() - t0
                verdict = "TRIAGE-PASS" if (amax < 0.06 and zd < 9.0) else "TRIAGE-KILL"
                line += f" aval_maxdev={amax:.4f} aval_meandev={amean:.5f} minidiff_zmax={zd:.1f} -> {verdict} ({dt:.0f}s)"
            except Exception as e:
                line += f" TRIAGE-EXC {e}"
        print(line, flush=True)

if __name__ == "__main__":
    main()

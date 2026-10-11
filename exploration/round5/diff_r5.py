"""Round 5, T5: differential-first profiler (M9-style).

For each candidate, over all 64 weight-1 input deltas at N=2^16 random pairs:
  - max |z| of per-output-bit flip probability (null ~4.5)
  - low-8-bit truncated chi2 on the worst delta (null 255 +/- 23)
Also profiles the h_xorspn3 baseline for comparison.
"""
import math
import os
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round5/models")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round4/models")
from r5 import CANDIDATES  # noqa: E402
from r4_hybrid import mix_h_xorspn3_np  # noqa: E402

KEY = np.uint64(0x123456789ABCDEF0)
N = 1 << 18  # sequential inputs, M9's distribution


def profile(fn):
    worst_z = 0.0
    worst = None
    X = np.arange(N, dtype=np.uint64)  # sequential, like M9
    K = np.full(N, KEY, dtype=np.uint64)
    for d in range(64):
        Y = X ^ (np.uint64(1) << np.uint64(d))
        D = np.asarray(fn(X, K), dtype=np.uint64) ^ np.asarray(fn(Y, K),
                                                              dtype=np.uint64)
        n = float(N)
        denom = math.sqrt(n / 4.0)
        for b in range(64):
            c = int((((D >> np.uint64(b)) & np.uint64(1))).sum())
            z = abs((c - n / 2.0) / denom)
            if z > worst_z:
                worst_z = z
                worst = (d, b)
    return worst_z, worst


def low8_chi2(fn, delta):
    """Truncated differential: chi2 of low-8-bit output differences at delta."""
    X = np.arange(N, dtype=np.uint64)
    Y = X ^ (np.uint64(1) << np.uint64(delta))
    K = np.full(N, KEY, dtype=np.uint64)
    D = np.asarray(fn(X, K), dtype=np.uint64) ^ np.asarray(fn(Y, K),
                                                          dtype=np.uint64)
    lo = (D & np.uint64(0xFF)).astype(np.int64)
    counts = np.bincount(lo, minlength=256).astype(float)
    exp = N / 256.0
    return float((((counts - exp) ** 2) / exp).sum())


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "results"), exist_ok=True)
    import sys
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    specs = [("h_xorspn3_baseline", mix_h_xorspn3_np)] +             [(n, f) for n, f, _, _ in CANDIDATES if only is None or n in only]
    print(f"{'name':22s} {'max|z|':>8s} {'worst(d,b)':>12s} {'low8chi2':>10s}  flag")
    for name, fn in specs:
        mz, w = profile(fn)
        c2 = low8_chi2(fn, w[0])
        flag = "DIFF-FLAG" if (mz > 10 or c2 > 400) else "ok"
        print(f"{name:22s} {mz:8.1f} {str(w):>12s} {c2:10.1f}  {flag}",
              flush=True)

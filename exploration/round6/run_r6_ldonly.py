"""Round 6 LIN/DIFF-only sweep (fast exploration)."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
from r6 import CANDIDATES_R6
from screen_lindiff import screen_lindiff
from screen_cal import KEYS, N
import numpy as np

K = np.uint64

for name, fn, desc in CANDIDATES_R6:
    t0 = time.time()
    try:
        S_seq = {}
        for key in KEYS:
            V = np.arange(N, dtype=np.uint64)
            S = np.asarray(fn(V, np.full(N, K(key), dtype=np.uint64)),
                           dtype=np.uint64)
            S_seq[("SEQ", key)] = S
        r = screen_lindiff(S_seq, name, verbose=False)
        dt = time.time() - t0
        verdict = r["verdict"]
        lin_D = max(r["lin_D"].values()) if r["lin_D"] else 0
        diff_w = max(w for w, _ in r["diff_worst"].values()) if r["diff_worst"] else 0
        print(f"{verdict:8s} {name:22s} linD<={lin_D:4d} diffW={diff_w:8.0f} {dt:5.1f}s | {desc}", flush=True)
    except Exception as e:
        print(f"ERROR    {name:22s} {e}", flush=True)

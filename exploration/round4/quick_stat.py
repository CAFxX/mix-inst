"""Quick preliminary statistical check (fast, not calibrated)."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round4/models")
import numpy as np
from r4_blink import mix_blink3_np, mix_blink4_np, mix_midori3_np

def quick_check(fn, name, n=1<<16, key=0x123456789ABCDEF0):
    """Single scenario: sequential inputs, check per-bit z-scores."""
    V = np.arange(n, dtype=np.uint64)
    K = np.full(n, np.uint64(key), dtype=np.uint64)
    S = np.asarray(fn(V, K), dtype=np.uint64)
    # per-bit bias z-score
    maxz = 0
    for b in range(64):
        ones = np.sum((S >> np.uint64(b)) & np.uint64(1))
        # z = (ones - n/2) / sqrt(n/4)
        z = (ones - n/2) / np.sqrt(n/4)
        maxz = max(maxz, abs(z))
    print(f"[{name}] n={n}: max|z|={maxz:.1f} {'WEAK' if maxz > 6 else 'ok'}", flush=True)
    return maxz

for fn, name in [(mix_blink3_np, "blink3"), (mix_blink4_np, "blink4"), (mix_midori3_np, "midori3")]:
    quick_check(fn, name)

"""Debug avalanche bias: find worst (input-bit, output-bit) pairs."""
import numpy as np, sys
sys.path.insert(0, "/home/hatch/workspace/mix")
from tests_part1 import mix64_np, murmur_np, U64

rng = np.random.default_rng(11)
T = 4096
V = rng.integers(0, 2**64, size=T, dtype=np.uint64)
K = rng.integers(0, 2**64, size=T, dtype=np.uint64)
bit = np.arange(64, dtype=np.uint64)

for name, fn in (("MIX64", mix64_np), ("murmur", murmur_np)):
    base = fn(V, K)
    Pall = np.empty((128, 64))
    for i in range(64):
        F = fn(V ^ (U64(1) << U64(i)), K)
        Pall[i] = (((base ^ F)[:, None] >> bit) & U64(1)).mean(axis=0)
        F = fn(V, K ^ (U64(1) << U64(i)))
        Pall[64 + i] = (((base ^ F)[:, None] >> bit) & U64(1)).mean(axis=0)
    dev = np.abs(Pall - 0.5)
    print(f"=== {name} ===")
    print("row means (avg over out bits) for val-bit flips 0..63:")
    print(np.array2string(Pall[:64].mean(axis=1), precision=3, max_line_width=200))
    print("row means for key-bit flips:")
    print(np.array2string(Pall[64:].mean(axis=1), precision=3, max_line_width=200))
    print("col means (avg over in bits) for out bits 0..63:")
    print(np.array2string(Pall.mean(axis=0), precision=3, max_line_width=200))
    idx = np.dstack(np.unravel_index(np.argsort(dev.ravel())[-8:], (128, 64)))[0]
    print("worst 8 (inbit[0-63=val,64-127=key], outbit, p):")
    for a, b in idx:
        src = "val" if a < 64 else "key"
        print(f"  {src} bit {a%64:2d} -> out bit {b:2d}: p={Pall[a,b]:.4f}")

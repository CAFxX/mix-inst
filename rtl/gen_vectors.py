"""Generate golden vectors: val, key, expected = mix_spn_scalar(val,key,12)."""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spn import mix_spn_scalar

rng = random.Random(0xBEEF)
N = 3000
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectors.hex"), "w") as f:
    for _ in range(N):
        v = rng.getrandbits(64)
        k = rng.getrandbits(64)
        e = mix_spn_scalar(v, k, 12)
        f.write(f"{v:016x} {k:016x} {e:016x}\n")
    # edge cases
    for v, k in [(0, 0), (0xFFFFFFFFFFFFFFFF, 0), (0, 0xFFFFFFFFFFFFFFFF),
                 (0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF),
                 (1, 0), (0, 1), (0x8000000000000000, 0x8000000000000000)]:
        f.write(f"{v:016x} {k:016x} {mix_spn_scalar(v, k, 12):016x}\n")
print(f"{N + 7} vectors written")

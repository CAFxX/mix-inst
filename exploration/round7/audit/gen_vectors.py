"""Generate (val, key, expected) vectors for the r7_feist8_s1_1sbox RTL review.
Writes vectors.hex: one line per vector, 'val_hex key_hex expected_hex'.
"""
import os, sys, random
import numpy as np

sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
from r7 import r7_feist8_s1_1sbox  # noqa: E402

AUDIT = os.path.expanduser("~/workspace/mix/exploration/round7/audit")
M64 = (1 << 64) - 1

def model(val, key):
    # scalar wrapper around the numpy model (avoid uint64 overflow warnings)
    return int(r7_feist8_s1_1sbox(np.uint64(val), np.uint64(key)))

vecs = []
# --- edge cases ---
edge = [
    (0x0000000000000000, 0x0000000000000000),
    (0x0000000000000000, 0xFFFFFFFFFFFFFFFF),
    (0xFFFFFFFFFFFFFFFF, 0x0000000000000000),
    (0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF),
    (0x0000000000000001, 0x0000000000000000),
    (0x8000000000000000, 0x0000000000000000),
    (0x0000000100000000, 0x0000000000000000),
    (0x0000000000000001, 0xFFFFFFFFFFFFFFFF),
    (0x0123456789ABCDEF, 0xFEDCBA9876543210),
    (0xAAAAAAAAAAAAAAAA, 0x5555555555555555),
    (0x5555555555555555, 0xAAAAAAAAAAAAAAAA),
]
# single-bit val with key=0 (all 64 positions), single-bit key with val=0
for b in range(64):
    edge.append((1 << b, 0))
    edge.append((0, 1 << b))
for v, k in edge:
    vecs.append((v, k))

# --- random vectors ---
rng = random.Random(0xC0FFEE)
N_RAND = 2000
for _ in range(N_RAND):
    vecs.append((rng.getrandbits(64), rng.getrandbits(64)))

with open(os.path.join(AUDIT, "vectors.hex"), "w") as f:
    for v, k in vecs:
        e = model(v, k)
        f.write(f"{v:016x} {k:016x} {e:016x}\n")
print(f"wrote {len(vecs)} vectors")

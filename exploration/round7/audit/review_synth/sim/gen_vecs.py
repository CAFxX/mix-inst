"""Generate test vectors + expected outputs for mapped-netlist sim check."""
import sys, os
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round7/models")
import random
import numpy as np
from r7 import r7_feist8_s1_1sbox

random.seed(0xC0FFEE)
vecs = []
# edge cases first
vecs.append((0x0000000000000000, 0x0000000000000000))  # val=0, key=0
vecs.append((0x0000000000000000, 0x123456789ABCDEF0))  # val=0
vecs.append((0xFEDCBA9876543210, 0x0000000000000000))  # key=0
vecs.append((0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF))  # all ones
vecs.append((0x0000000000000001, 0x0000000000000000))  # val=1, key=0
vecs.append((0x8000000000000000, 0x8000000000000000))  # msb only
# random bulk
N_RAND = 2048
for _ in range(N_RAND):
    vecs.append((random.getrandbits(64), random.getrandbits(64)))

outdir = "/home/hatch/workspace/mix/exploration/round7/audit/review_synth/sim"
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "vectors.hex"), "w") as fv, \
     open(os.path.join(outdir, "expected.hex"), "w") as fe:
    for v, k in vecs:
        e = int(r7_feist8_s1_1sbox(np.uint64(v), np.uint64(k)))
        assert 0 <= e < 2**64
        fv.write(f"{v:016x}{k:016x}\n")
        fe.write(f"{e:016x}\n")
print(f"wrote {len(vecs)} vectors ({N_RAND} random + {len(vecs)-N_RAND} edge)")

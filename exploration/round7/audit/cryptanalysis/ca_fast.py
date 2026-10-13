"""Fast empirical checks: C vs Python bit-exactness, birthday collision sanity."""
import sys, os, ctypes, subprocess
import numpy as np
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
from r7 import r7_feist8_s1_1sbox

print("== C impl vs Python model bit-exactness ==")
subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", "/tmp/mixc.so",
    os.path.expanduser("~/workspace/mix/exploration/fast_battery/candidates/r7_feist8_s1_1sbox/impl.c")],
    check=True)
lib = ctypes.CDLL("/tmp/mixc.so")
lib.mix_hash.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
lib.mix_hash.restype = ctypes.c_uint64
rng = np.random.default_rng(42)
N = 3000
v = rng.integers(0, 1 << 64, N, dtype=np.uint64)
k = rng.integers(0, 1 << 64, N, dtype=np.uint64)
py = r7_feist8_s1_1sbox(v, k)
mism = sum(1 for i in range(N) if lib.mix_hash(int(v[i]), int(k[i])) != int(py[i]))
print(f"  {N} random vectors: {mism} mismatches -> {'BIT-EXACT' if mism==0 else 'MISMATCH!'}")
# structured vectors incl. 0
v2 = np.array([0, 1, (1<<64)-1, 0x8000000000000000, 0x0000000100000000], dtype=np.uint64)
k2 = np.array([0, 0, (1<<64)-1, 0x5555555555555555, 0xAAAAAAAAAAAAAAAA], dtype=np.uint64)
py2 = r7_feist8_s1_1sbox(v2, k2)
mism2 = sum(1 for i in range(len(v2)) if lib.mix_hash(int(v2[i]), int(k2[i])) != int(py2[i]))
print(f"  {len(v2)} structured vectors: {mism2} mismatches")

print()
print("== birthday collision sanity (2^24 random vals, fixed key) ==")
N = 1 << 24
kfix = np.uint64(0x123456789ABCDEF0)
vv = rng.integers(0, 1 << 64, N, dtype=np.uint64)
kk = np.full(N, kfix)
h = r7_feist8_s1_1sbox(vv, kk)
u, c = np.unique(h, return_counts=True)
ncoll = int(np.sum(c - 1))
expected = N * (N - 1) / 2 / 2**64
print(f"  collisions: {ncoll} (birthday expectation ~{expected:.4f})")
# also sequential inputs (like M9)
vv2 = np.arange(N, dtype=np.uint64)
h2 = r7_feist8_s1_1sbox(vv2, kk)
u2, c2 = np.unique(h2, return_counts=True)
print(f"  sequential 2^24: collisions = {int(np.sum(c2-1))}")

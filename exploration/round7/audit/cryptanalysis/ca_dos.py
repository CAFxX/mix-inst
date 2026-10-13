"""Empirical validation: model vs C, trail probability measurement, birthday sanity."""
import sys, os, math, ctypes, subprocess
import numpy as np
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/audit/cryptanalysis"))
from ca_trails import beam_search, recover_trail, lin32
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
from r7 import r7_feist8_s1_1sbox

print("== (1) C impl vs Python model bit-exactness ==")
subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", "/tmp/mixc.so",
    os.path.expanduser("~/workspace/mix/exploration/fast_battery/candidates/r7_feist8_s1_1sbox/impl.c")],
    check=True)
lib = ctypes.CDLL("/tmp/mixc.so")
lib.mix_hash.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
lib.mix_hash.restype = ctypes.c_uint64
rng = np.random.default_rng(42)
N = 2000
v = rng.integers(0, 1 << 64, N, dtype=np.uint64)
k = rng.integers(0, 1 << 64, N, dtype=np.uint64)
py = r7_feist8_s1_1sbox(v, k)
mism = 0
for i in range(N):
    if lib.mix_hash(int(v[i]), int(k[i])) != int(py[i]):
        mism += 1
print(f"  {N} random vectors: {mism} mismatches -> {'BIT-EXACT' if mism==0 else 'MISMATCH!'}")

print()
print("== (2) best-trail recovery + empirical probability ==")
states, history = beam_search(nrounds=8, beam=4000, keep_history=True)
best = max(states.items(), key=lambda z: z[1][0])
(dL8, dR8), (lp, prev, ei, nact) = best
trail = recover_trail(history, (dL8, dR8))
(dL0, dR0) = trail[0]
din = (dL0 << 32) | dR0
dout = (dL8 << 32) | dR8
pred_log2 = lp / math.log(2)
print(f"  best 8-round trail: P_pred = 2^{pred_log2:.2f}, active S-boxes = {nact}")
print(f"  input diff  = 0x{din:016x}, output diff = 0x{dout:016x}")
print(f"  round-by-round state diffs:")
for r, (a, b) in enumerate(trail):
    print(f"    r{r}: (0x{a:08x}, 0x{b:08x})")

# empirical: fixed key, random v
kfix = np.uint64(0x123456789ABCDEF0)
N = 1 << 20
vv = rng.integers(0, 1 << 64, N, dtype=np.uint64)
kk = np.full(N, kfix)
h1 = r7_feist8_s1_1sbox(vv, kk)
h2 = r7_feist8_s1_1sbox(vv ^ np.uint64(din), kk)
hits = int(np.sum((h1 ^ h2) == np.uint64(dout)))
print(f"  empirical over 2^20 pairs (key fixed): {hits} hits -> P_emp = 2^{math.log2(hits/N) if hits else float('-inf'):.2f} (pred 2^{pred_log2:.2f})")

# best zero-output trail
zc = [(s, v) for s, v in states.items() if s == (0, 0)]
if zc:
    (dLz, dRz), (lpz, pvz, eiz, nactz) = zc[0]
    trailz = recover_trail(history, (0, 0))
    dinz = (trailz[0][0] << 32) | trailz[0][1]
    print(f"  best ZERO-output trail: P = 2^{lpz/math.log(2):.2f}, active={nactz}, input diff=0x{dinz:016x}")
    # would-be collision search cost
    print(f"  collision search via this trail needs ~2^{-lpz/math.log(2):.1f} pairs vs birthday 2^32")
else:
    print("  no zero-output trail in beam: best zero-output P < beam cutoff (<< 2^-64)")

print()
print("== (3) birthday collision sanity (2^24 random vals, fixed key) ==")
N = 1 << 24
vv = rng.integers(0, 1 << 64, N, dtype=np.uint64)
kk = np.full(N, kfix)
h = r7_feist8_s1_1sbox(vv, kk)
u, c = np.unique(h, return_counts=True)
ncoll = int(np.sum(c - 1))
expected = N * (N - 1) / 2 / 2**64
print(f"  collisions: {ncoll} (expected ~{expected:.3f} for a random 64-bit function)")

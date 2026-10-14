"""Follow-up: (a) fixed Lemire binning for X=2^32; (b) top-bit balance under
high-only-varying inputs, SPN-10 vs baselines, larger N."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spn import mix_spn_np, U64
from tests_part1 import splitmix_np, murmur_np
from tests_part3 import lemire_high64, chi2_z, monobit_z

R = 10


def lemire_binned_z(S, X):
    Y = lemire_high64(S, X)
    if X <= 2048:
        return chi2_z(np.bincount(Y.astype(np.int64), minlength=X))[0]
    s = max(0, X.bit_length() - 11)
    nbins = min(2048, 1 << max(1, (X - 1).bit_length() - s))
    return chi2_z(np.bincount(((Y >> U64(s))).astype(np.int64), minlength=nbins))[0]


def seq(fn, key, I, j, N):
    K = np.full(N, U64(key), dtype=np.uint64)
    V = U64(I) + U64(j) * np.arange(N, dtype=np.uint64)
    return fn(V, K)


print("--- (a) Lemire X=2^32 with fixed binning (SPN-10) ---")
for cname, key, I, j in [
    ("key=0,I=0,j=1", 0, 0, 1),
    ("key=0123,I=fedc,j=2^32", 0x0123456789ABCDEF, 0xFEDCBA9876543210, 0x100000000),
    ("key=rnd", 0x243F6A8885A308D3, 0x452821E638D01377, 0xB5297A4D68EFEED),
]:
    S = seq(lambda V, K: mix_spn_np(V, K, rounds=R), key, I, j, 1 << 18)
    print(f"  {cname}: z={lemire_binned_z(S, 2**32):+.2f}")

print("--- (b) top-bit (lemire X=2) balance, high-only-varying inputs ---")
for name, fn in (("SPN-10", lambda V, K: mix_spn_np(V, K, rounds=R)),
                 ("splitmix", splitmix_np), ("murmur", murmur_np)):
    for cname, key, I, j, N in [
        ("k=0123,I=fedc,j=2^32", 0x0123456789ABCDEF, 0xFEDCBA9876543210, 0x100000000, 1 << 21),
        ("k=0,I=0,j=2^32", 0, 0, 0x100000000, 1 << 20),
        ("k=gold,I=0,j=2^32", 0x9E3779B97F4A7C15, 0, 0x100000000, 1 << 20),
        ("k=dead,I=mid,j=2^33", 0xDEADBEEFCAFEBABE, 0x123456789ABCDEF0, 0x200000000, 1 << 20),
    ]:
        S = seq(fn, key, I, j, N)
        z = monobit_z((S >> U64(63)) & U64(1))
        flag = "  <-- FLAG" if abs(z) >= 4 else ""
        print(f"  {name:9s} {cname}: top-bit monobit z={z:+.2f}{flag}")

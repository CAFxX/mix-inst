"""Re-run screen reduction cells at N=2^24 on SEQ and PTR-j8 (peer-review remediation, stats C3).
Chunked hashing (~134MB S array + small temporaries). Uses screen_lib's exact
cell statistics; lemire-2^32 uses a searchsorted binning mathematically
identical to the library's digitize path (avoids the object-array blowup)."""
import sys, time, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/mix/exploration')
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/models')
from spn4_xorlin_1137 import mix_spn4_xorlin_1137_np
from screen_lib import mask_z, mask32_z, lemire_z, lemire_np, lemire_preimg, chi2_z_exact, W64

N = 1 << 24
CH = 1 << 22
KEYS = [0x123456789ABCDEF0, 0x0]

def hash_full(scen, key):
    S = np.empty(N, dtype=np.uint64)
    for off in range(0, N, CH):
        I = scen(off, CH)
        S[off:off+CH] = mix_spn4_xorlin_1137_np(I, np.uint64(key))
        del I
    return S

def scen_seq(off, ch):
    return np.arange(off, off+ch, dtype=np.uint64)

def scen_ptr_j8(off, ch):
    return (np.arange(off, off+ch, dtype=np.uint64) * np.uint64(8))

def lemire_z_2p32(S):
    # identical bins to screen_lib.lemire_z(S, 1<<32): 1024 coarse bins
    X = 1 << 32; B = 1024
    bounds = [(k * X)//B for k in range(B+1)]
    E = np.array([lemire_preimg(bounds[k], bounds[k+1], X) * N / W64 for k in range(B)])
    R = lemire_np(S, X).astype(np.int64)
    idx = np.searchsorted(np.array(bounds[1:-1], dtype=np.int64), R, side='right')
    cnt = np.bincount(idx, minlength=B).astype(float)
    del R, idx
    assert len(cnt) == B and (E > 0).all()
    return chi2_z_exact(cnt, E)

for name, scen in [("SEQ", scen_seq), ("PTR-j8", scen_ptr_j8)]:
    for key in KEYS:
        t0 = time.time()
        S = hash_full(scen, key)
        th = time.time()
        row = [name, f"key={key:#x}"]
        row.append(f"mask8: z={mask_z(S, 8):+.2f}")
        t, zc = mask32_z(S)
        row.append(f"mask32: {t} z={zc:+.2f}")
        row.append(f"lemire10: z={lemire_z(S, 10):+.2f}")
        row.append(f"lemire1000: z={lemire_z(S, 1000):+.2f}")
        row.append(f"lemire2p32: z={lemire_z_2p32(S):+.2f}")
        del S
        print(" | ".join(row) + f"  [hash {th-t0:.0f}s total {time.time()-t0:.0f}s]", flush=True)
print("done", flush=True)

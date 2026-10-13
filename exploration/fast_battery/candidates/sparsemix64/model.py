"""sparsemix64: 4-round heterogeneous SPN, 64 distinct 4-bit S-boxes, sparse inter-round wiring. (Carlo's design)"""
import json, os
import numpy as np
_spec = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spec.json')))
_sboxes = {int(k): v for k, v in _spec['sboxes'].items()}
_wires = {}
for _k, (_sb, _bits) in _spec['wires'].items():
    _r, _n = map(int, _k.split(','))
    _wires[(_r, _n)] = (_sb, _bits)

def _mix64_scalar(x):
    st = {-1: x & 0xFFFFFFFFFFFFFFFF}
    for r in range(4):
        out = 0
        for n in range(16):
            sb, bits = _wires[(r, n)]
            nib = 0
            for b in bits:
                if isinstance(b, list):
                    bit = (st[-1] >> b[1]) & 1
                else:
                    bit = (st[r-1] >> b) & 1
                nib = (nib << 1) | bit
            out |= (_sboxes[sb][nib] << (4*n))
        st[r] = out
    return st[3] & 0xFFFFFFFFFFFFFFFF

# Vectorized: precompute per-round as table lookups on gathered nibbles
# For speed, use scalar loop (S1 needs ~10*2^20 evals; scalar is too slow).
# Instead: implement each round with numpy by gathering bits.

def _gather_nibbles(prev, bit_lists):
    # prev: uint64 array; bit_lists: list of 16x4 bit positions (MSB-first)
    # returns (16, N) array of nibble values
    N = prev.shape[0]
    out = np.zeros((16, N), dtype=np.uint64)
    for n, bits in enumerate(bit_lists):
        nib = np.zeros(N, dtype=np.uint64)
        for b in bits:
            nib = (nib << np.uint64(1)) | ((prev >> np.uint64(b)) & np.uint64(1))
        out[n] = nib
    return out

_bitlists = {}
for _r in range(1, 4):
    _bitlists[_r] = [_wires[(_r, _n)][1] for _n in range(16)]
_sbtabs = {}
for _sb, _tab in _sboxes.items():
    _sbtabs[_sb] = np.array(_tab, dtype=np.uint64)

def mix_np(V, K):
    x = np.atleast_1d(np.asarray(V, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64))
    N = x.shape[0]
    # Round 0: direct nibbles -> sb_0..sb_15
    cur = np.zeros(N, dtype=np.uint64)
    for n in range(16):
        nib = (x >> np.uint64(4*n)) & np.uint64(0xF)
        cur |= (_sbtabs[n][nib] << np.uint64(4*n))
    # Rounds 1-3
    for r in range(1, 4):
        nibs = _gather_nibbles(cur, _bitlists[r])
        nxt = np.zeros(N, dtype=np.uint64)
        for n in range(16):
            sb = _wires[(r, n)][0]
            nxt |= (_sbtabs[sb][nibs[n]] << np.uint64(4*n))
        cur = nxt
    return cur[0] if cur.shape[0] == 1 and np.ndim(V) == 0 and np.ndim(K) == 0 else cur

def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))

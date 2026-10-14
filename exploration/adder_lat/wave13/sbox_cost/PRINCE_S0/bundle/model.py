"""numpy model for PRINCE_S0 stage bundle (bit-exact with triage_wave13.py)."""
import numpy as np

_TAB = np.array([0xb,0xf,0x3,0x2,0xa,0xc,0x9,0x1,0x6,0x7,0x8,0x0,0xe,0x5,0xd,0x4], dtype=np.uint64)
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
_TRANS = np.zeros((16, 16), dtype=np.uint64)
for _a in range(16):
    for _v in range(16):
        _w = np.uint64(0)
        for _b in range(4):
            if (_v >> _b) & 1:
                _w |= np.uint64(1) << np.uint64(16 * _b + _a)
        _TRANS[_a, _v] = _w

def _sbox64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= _TAB[(x >> np.uint64(4*i)) & np.uint64(0xF)] << np.uint64(4*i)
    return y & M64

def _transpose64(x):
    y = np.zeros_like(x)
    for a in range(16):
        y |= _TRANS[a, (x >> np.uint64(4*a)) & np.uint64(0xF)]
    return y

def mix_np(V, K):
    return _transpose64(_sbox64((V ^ K) & M64)) & M64

def mix(v, k):
    return int(mix_np(np.array([np.uint64(v)]), np.array([np.uint64(k)]))[0])

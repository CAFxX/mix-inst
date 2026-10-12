"""hyb11_and6_finalPL: 6-stage al_and6a triplets + final P(37,1)+L(5,13) (control: final layer on frontier design). Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
PA, PB = 37, 1

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _pbox(x):
    y = np.uint64(0)
    y |= ((x >> np.uint64(0)) & np.uint64(1)) << np.uint64(1)
    y |= ((x >> np.uint64(1)) & np.uint64(1)) << np.uint64(38)
    y |= ((x >> np.uint64(2)) & np.uint64(1)) << np.uint64(11)
    y |= ((x >> np.uint64(3)) & np.uint64(1)) << np.uint64(48)
    y |= ((x >> np.uint64(4)) & np.uint64(1)) << np.uint64(21)
    y |= ((x >> np.uint64(5)) & np.uint64(1)) << np.uint64(58)
    y |= ((x >> np.uint64(6)) & np.uint64(1)) << np.uint64(31)
    y |= ((x >> np.uint64(7)) & np.uint64(1)) << np.uint64(4)
    y |= ((x >> np.uint64(8)) & np.uint64(1)) << np.uint64(41)
    y |= ((x >> np.uint64(9)) & np.uint64(1)) << np.uint64(14)
    y |= ((x >> np.uint64(10)) & np.uint64(1)) << np.uint64(51)
    y |= ((x >> np.uint64(11)) & np.uint64(1)) << np.uint64(24)
    y |= ((x >> np.uint64(12)) & np.uint64(1)) << np.uint64(61)
    y |= ((x >> np.uint64(13)) & np.uint64(1)) << np.uint64(34)
    y |= ((x >> np.uint64(14)) & np.uint64(1)) << np.uint64(7)
    y |= ((x >> np.uint64(15)) & np.uint64(1)) << np.uint64(44)
    y |= ((x >> np.uint64(16)) & np.uint64(1)) << np.uint64(17)
    y |= ((x >> np.uint64(17)) & np.uint64(1)) << np.uint64(54)
    y |= ((x >> np.uint64(18)) & np.uint64(1)) << np.uint64(27)
    y |= ((x >> np.uint64(19)) & np.uint64(1)) << np.uint64(0)
    y |= ((x >> np.uint64(20)) & np.uint64(1)) << np.uint64(37)
    y |= ((x >> np.uint64(21)) & np.uint64(1)) << np.uint64(10)
    y |= ((x >> np.uint64(22)) & np.uint64(1)) << np.uint64(47)
    y |= ((x >> np.uint64(23)) & np.uint64(1)) << np.uint64(20)
    y |= ((x >> np.uint64(24)) & np.uint64(1)) << np.uint64(57)
    y |= ((x >> np.uint64(25)) & np.uint64(1)) << np.uint64(30)
    y |= ((x >> np.uint64(26)) & np.uint64(1)) << np.uint64(3)
    y |= ((x >> np.uint64(27)) & np.uint64(1)) << np.uint64(40)
    y |= ((x >> np.uint64(28)) & np.uint64(1)) << np.uint64(13)
    y |= ((x >> np.uint64(29)) & np.uint64(1)) << np.uint64(50)
    y |= ((x >> np.uint64(30)) & np.uint64(1)) << np.uint64(23)
    y |= ((x >> np.uint64(31)) & np.uint64(1)) << np.uint64(60)
    y |= ((x >> np.uint64(32)) & np.uint64(1)) << np.uint64(33)
    y |= ((x >> np.uint64(33)) & np.uint64(1)) << np.uint64(6)
    y |= ((x >> np.uint64(34)) & np.uint64(1)) << np.uint64(43)
    y |= ((x >> np.uint64(35)) & np.uint64(1)) << np.uint64(16)
    y |= ((x >> np.uint64(36)) & np.uint64(1)) << np.uint64(53)
    y |= ((x >> np.uint64(37)) & np.uint64(1)) << np.uint64(26)
    y |= ((x >> np.uint64(38)) & np.uint64(1)) << np.uint64(63)
    y |= ((x >> np.uint64(39)) & np.uint64(1)) << np.uint64(36)
    y |= ((x >> np.uint64(40)) & np.uint64(1)) << np.uint64(9)
    y |= ((x >> np.uint64(41)) & np.uint64(1)) << np.uint64(46)
    y |= ((x >> np.uint64(42)) & np.uint64(1)) << np.uint64(19)
    y |= ((x >> np.uint64(43)) & np.uint64(1)) << np.uint64(56)
    y |= ((x >> np.uint64(44)) & np.uint64(1)) << np.uint64(29)
    y |= ((x >> np.uint64(45)) & np.uint64(1)) << np.uint64(2)
    y |= ((x >> np.uint64(46)) & np.uint64(1)) << np.uint64(39)
    y |= ((x >> np.uint64(47)) & np.uint64(1)) << np.uint64(12)
    y |= ((x >> np.uint64(48)) & np.uint64(1)) << np.uint64(49)
    y |= ((x >> np.uint64(49)) & np.uint64(1)) << np.uint64(22)
    y |= ((x >> np.uint64(50)) & np.uint64(1)) << np.uint64(59)
    y |= ((x >> np.uint64(51)) & np.uint64(1)) << np.uint64(32)
    y |= ((x >> np.uint64(52)) & np.uint64(1)) << np.uint64(5)
    y |= ((x >> np.uint64(53)) & np.uint64(1)) << np.uint64(42)
    y |= ((x >> np.uint64(54)) & np.uint64(1)) << np.uint64(15)
    y |= ((x >> np.uint64(55)) & np.uint64(1)) << np.uint64(52)
    y |= ((x >> np.uint64(56)) & np.uint64(1)) << np.uint64(25)
    y |= ((x >> np.uint64(57)) & np.uint64(1)) << np.uint64(62)
    y |= ((x >> np.uint64(58)) & np.uint64(1)) << np.uint64(35)
    y |= ((x >> np.uint64(59)) & np.uint64(1)) << np.uint64(8)
    y |= ((x >> np.uint64(60)) & np.uint64(1)) << np.uint64(45)
    y |= ((x >> np.uint64(61)) & np.uint64(1)) << np.uint64(18)
    y |= ((x >> np.uint64(62)) & np.uint64(1)) << np.uint64(55)
    y |= ((x >> np.uint64(63)) & np.uint64(1)) << np.uint64(28)
    return y & M64

def _lin(x):
    return (x ^ _rotl(x, 5) ^ _rotl(x, 13)) & M64

def _nl(x, op):
    ra, rb, rc = _rotl(x, 1), _rotl(x, 2), _rotl(x, 13)
    if op == 'and':
        return (x ^ (ra & rb) ^ rc) & M64
    return (x ^ ((~ra) & rb) ^ rc) & M64

def _mix_core(x, k):
    # 6 AND stages (al_and6a triplets)
    ra, rb, rc = _rotl(x, 1), _rotl(x, 2), _rotl(x, 13)
    x = (x ^ (ra & rb) ^ rc) & M64
    ra, rb, rc = _rotl(x, 7), _rotl(x, 19), _rotl(x, 5)
    x = (x ^ (ra & rb) ^ rc) & M64
    ra, rb, rc = _rotl(x, 3), _rotl(x, 11), _rotl(x, 29)
    x = (x ^ (ra & rb) ^ rc) & M64
    ra, rb, rc = _rotl(x, 17), _rotl(x, 31), _rotl(x, 7)
    x = (x ^ (ra & rb) ^ rc) & M64
    ra, rb, rc = _rotl(x, 11), _rotl(x, 23), _rotl(x, 37)
    x = (x ^ (ra & rb) ^ rc) & M64
    ra, rb, rc = _rotl(x, 19), _rotl(x, 41), _rotl(x, 23)
    x = (x ^ (ra & rb) ^ rc) & M64
    x = _lin(_pbox(x))
    return (x ^ _rotl(k, 13)) & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K, K)

def mix(v, k):
    return mix_hash(v, k)

"""Track 6, batch 5: new boolean functions on rotated copies.

Batch 4 verdict: all S0-killed on latency (40-80u). S-box-per-round is too expensive.
The al_ family's ~3u/stage with full 64-bit state mixing is the right cost model.

Batch 5 keeps that structure but uses boolean functions NOT in the al_ track's
opcode list (chi/and/andxor/orand/triand/arx2/feist_chi):
  1. maj     : x ^= maj(ra,rb,rc) ^ rd          (majority: (a&b)|(a&c)|(b&c))
  2. andor   : x ^= (ra&rb) | (rc&rd) ^ re      (AND-OR mix)
  3. majxor  : x ^= maj(ra,rb,rc) ^ (rd&re)     (majority + AND term)
  4. xor3and : x ^= ra ^ rb ^ rc ^ (rd&re&rf)   (XOR + triple-AND)

Each stage: rotate state by schedule, apply function, XOR back. 6/8 stages.
Key: pre-whiten x^=k, per-stage rk folded, post x ^= rotl(k,13).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _maj(a, b, c):
    return ((a & b) | (a & c) | (b & c)) & M64


def cascade(v, k, op, sched):
    x = np.uint64(v) ^ np.uint64(k)
    for i, rots in enumerate(sched):
        r = [_rotl64(x, t) for t in rots]
        if op == "maj":
            # x ^= maj(ra,rb,rc) ^ rd
            x ^= _maj(r[0], r[1], r[2]) ^ r[3]
        elif op == "andor":
            # x ^= (ra&rb) | (rc&rd) ^ re
            x ^= ((r[0] & r[1]) | (r[2] & r[3])) ^ r[4]
        elif op == "majxor":
            # x ^= maj(ra,rb,rc) ^ (rd&re)
            x ^= _maj(r[0], r[1], r[2]) ^ (r[3] & r[4])
        elif op == "xor3and":
            # x ^= ra ^ rb ^ rc ^ (rd&re&rf)
            x ^= r[0] ^ r[1] ^ r[2] ^ (r[3] & r[4] & r[5])
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % len(RC64)]
        x ^= rk
    return (x ^ (np.uint64(k) >> np.uint64(32))) & M64


# rotation schedules: 6-stage and 8-stage
SCHED6 = [(1, 2, 13, 7), (7, 19, 5, 17), (3, 11, 29, 23),
          (17, 31, 7, 11), (11, 23, 37, 5), (19, 41, 23, 13)]
SCHED6_5 = [(1, 2, 13, 7, 29), (7, 19, 5, 17, 3), (3, 11, 29, 23, 41),
            (17, 31, 7, 11, 19), (11, 23, 37, 5, 13), (19, 41, 23, 13, 7)]
SCHED8 = [(1, 2, 13, 7), (7, 19, 5, 17), (3, 11, 29, 23), (13, 5, 17, 31),
          (17, 31, 7, 11), (11, 23, 37, 5), (29, 43, 11, 19), (19, 41, 23, 13)]
SCHED8_5 = [(1, 2, 13, 7, 29), (7, 19, 5, 17, 3), (3, 11, 29, 23, 41),
            (13, 5, 17, 31, 7), (17, 31, 7, 11, 19), (11, 23, 37, 5, 13),
            (29, 43, 11, 19, 23), (19, 41, 23, 13, 7)]
SCHED6_6 = [(1, 2, 13, 7, 29, 37), (7, 19, 5, 17, 3, 11),
            (3, 11, 29, 23, 41, 5), (17, 31, 7, 11, 19, 23),
            (11, 23, 37, 5, 13, 17), (19, 41, 23, 13, 7, 29)]
SCHED8_6 = [(1, 2, 13, 7, 29, 37), (7, 19, 5, 17, 3, 11),
            (3, 11, 29, 23, 41, 5), (13, 5, 17, 31, 7, 19),
            (17, 31, 7, 11, 19, 23), (11, 23, 37, 5, 13, 17),
            (29, 43, 11, 19, 23, 31), (19, 41, 23, 13, 7, 29)]


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_cascade(op, sched, fname):
    # Named wrapper (never a bare lambda): the gen script emits
    # `_mix_scalar` as `return {fn.__name__}(v, k)`, which is only valid
    # Python when __name__ is a real identifier. A lambda's __name__ is
    # '<lambda>' and produced a SyntaxError at S1 load time (2026-10-08).
    def f(v, k):
        return cascade(v, k, op, sched)
    f.__name__ = fname
    return f


CANDIDATES_B5 = {
    "t6_maj6": (_mk_cascade("maj", SCHED6, "cascade_maj6"), "majority cascade, 6 stages"),
    "t6_maj8": (_mk_cascade("maj", SCHED8, "cascade_maj8"), "majority cascade, 8 stages"),
    "t6_andor6": (_mk_cascade("andor", SCHED6_5, "cascade_andor6"), "AND-OR mix, 6 stages"),
    "t6_andor8": (_mk_cascade("andor", SCHED8_5, "cascade_andor8"), "AND-OR mix, 8 stages"),
    "t6_majxor6": (_mk_cascade("majxor", SCHED6_5, "cascade_majxor6"), "majority+AND, 6 stages"),
    "t6_majxor8": (_mk_cascade("majxor", SCHED8_5, "cascade_majxor8"), "majority+AND, 8 stages"),
    "t6_xor3and6": (_mk_cascade("xor3and", SCHED6_6, "cascade_xor3and6"), "XOR+triple-AND, 6 stages"),
    "t6_xor3and8": (_mk_cascade("xor3and", SCHED8_6, "cascade_xor3and8"), "XOR+triple-AND, 8 stages"),
}

MIX_NP_B5 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B5.items()}

# Bind each named wrapper as a module global: the generated _mix_scalar below
# calls `cascade_maj6(v, k)` by name; __name__ alone does not create the global,
# so scalar mix() died with NameError (2026-10-09 fix; source fix lives in
# new_constructions/t6_models_b5.py, copied region).
for _bn, (_bf, _bd) in CANDIDATES_B5.items():
    globals()[_bf.__name__] = _bf
del _bn, _bf, _bd

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B5.items():
        a = fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))
        b = fn(np.uint64(1), np.uint64(0x123456789ABCDEF0))
        assert a != b, name
        print(f"{name}: ok ({desc})")

def _mix_scalar(v, k):
    return cascade_maj6(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B5['t6_maj6'](v, k)

def mix_np(V, K):
    return MIX_NP_B5['t6_maj6'](V, K)

"""w4t bundle w4t_208 -- numpy model, bit-exact with screen w4t_model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [[[45, 49], [13, 12]], [[44, 45], [43, 41]], [[40, 39], [20, 16]]]
PQRS = [2, 11, 32, 41]

def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def mix(val, key):
    V = np.uint64(val); K = np.uint64(key)
    p, q, r, s = PQRS
    x = (V ^ K) & M64
    for ands in STAGES:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = (x ^ rotl(x, p) ^ rotl(x, q) ^ rotl(x, r) ^ rotl(x, s)) & M64
    return int((x ^ rotl(K, 13)) & M64)

def mix_np(V, key):
    V = np.asarray(V, dtype=np.uint64); K = np.uint64(key)
    p, q, r, s = PQRS
    x = (V ^ K) & M64
    for ands in STAGES:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = (x ^ rotl(x, p) ^ rotl(x, q) ^ rotl(x, r) ^ rotl(x, s)) & M64
    return (x ^ rotl(K, 13)) & M64

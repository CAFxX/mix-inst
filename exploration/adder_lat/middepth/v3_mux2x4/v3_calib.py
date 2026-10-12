#!/usr/bin/env python3
"""Avalanche calibration across candidate structures.

Measures mean flipped output bits per weight-1 input delta (64 deltas,
2048 random xs). Fast numpy prefilter: DIFF needs saturated avalanche
(~32 bits, each output bit flipping w.p. ~1/2).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
import v3_model as M  # noqa: E402
import t8_het8_screen as H  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
rotl = H.rotl
mux = H.mux

MU5_324 = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
           ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
           ("MUXD", 46, 51, 43, 44)]
MUXD2 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57)]  # O135 0/200


def muxd_stage(x, s, a, b, d):
    return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64


def lin4(x, a, b, c):
    return (x ^ rotl(x, a) ^ rotl(x, b) ^ rotl(x, c)) & M64


def apply_struct(x, spec):
    for st in spec:
        tag = st[0]
        if tag == "MUX2":
            _, s, p1, p2 = st
            x = M.mux2_layer(x, s, p1, p2)
        elif tag == "MUXD":
            _, s, a, b, d = st
            x = muxd_stage(x, s, a, b, d)
        elif tag == "LIN4":
            _, a, b, c = st
            x = lin4(x, a, b, c)
        else:
            raise AssertionError(tag)
    return x & M64


def avalanche(spec, key, nxs=2048, seed=0x5EED):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=nxs, dtype=np.uint64)
    K = np.uint64(key)
    base = apply_struct((xs ^ K) & M64, spec)
    tot = 0.0
    for j in range(64):
        dj = np.uint64(1) << np.uint64(j)
        out = apply_struct(((xs ^ K) ^ dj) & M64, spec)
        d = out ^ base
        tot += float(np.mean([bin(int(v)).count("1") for v in d]))
    return tot / 64.0


STRUCTS = {
    # name: spec
    "V3-base 4xMUX2": [("MUX2", 0, 7, 29), ("MUX2", 13, 31, 53),
                       ("MUX2", 5, 19, 43), ("MUX2", 11, 23, 47)],
    "MU5-324 5xMUXD (PASS ctrl)": MU5_324,
    "2xMUXD (O135 0/200)": MUXD2,
    "H1 MUX2-LIN4-MUX2-LIN4": [("MUX2", 0, 7, 29), ("LIN4", 7, 23, 41),
                               ("MUX2", 13, 31, 53), ("LIN4", 11, 29, 47)],
    "H2 3xMUX2-LIN4": [("MUX2", 0, 7, 29), ("MUX2", 13, 31, 53),
                       ("MUX2", 5, 19, 43), ("LIN4", 7, 23, 41)],
    "H3 MUX2-LIN4-MUX2-LIN4-MUX2": [("MUX2", 0, 7, 29), ("LIN4", 7, 23, 41),
                                    ("MUX2", 13, 31, 53), ("LIN4", 11, 29, 47),
                                    ("MUX2", 5, 19, 43)],
}

if __name__ == "__main__":
    key = 0x9E3779B97F4A7C15
    for name, spec in STRUCTS.items():
        print(f"{name:32s} avalanche={avalanche(spec, key):.2f} bits", flush=True)

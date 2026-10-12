#!/usr/bin/env python3
"""XCHECK: parse gen_d2.py Verilog assigns, evaluate as Boolean circuit on
random vectors, compare against d2_model.apply / d2_sweep.apply2.
Catches index-direction bugs in the generator without needing iverilog.
"""
import re
import sys

import numpy as np

import d2_model as M
from d2_sweep import apply2

TERM = re.compile(r"([a-z]+\d*)\[(\d+)\]")


def parse_verilog(path):
    assigns = []  # (dst_sig, dst_idx, [(sig, idx)], ops) in order
    for line in open(path):
        line = line.strip()
        m = re.match(r"assign\s+(\w+)\[(\d+)\]\s*=\s*(.*);", line)
        if not m:
            continue
        dst, di, rhs = m.group(1), int(m.group(2)), m.group(3)
        terms = TERM.findall(rhs)
        # rhs is XOR/AND of single-bit terms; determine op structure:
        # top-level split by ^ then by &
        xors = [p.strip() for p in rhs.split("^")]
        expr = []
        for xp in xors:
            ands = [t.strip() for t in xp.split("&")]
            expr.append([TERM.findall(a)[0] for a in ands])
        assigns.append((dst, di, expr))
    return assigns


def eval_verilog(path, x, keys):
    """x: uint64; keys: dict sig->uint64. Returns z uint64."""
    bits = {}
    xb = int(x)
    for i in range(64):
        bits[("x", i)] = (xb >> i) & 1
    for sig, kv in keys.items():
        kv = int(kv)
        for i in range(64):
            bits[(sig, i)] = (kv >> i) & 1
    z = 0
    for dst, di, expr in parse_verilog(path):
        v = 0
        for ands in expr:
            t = 1
            for sig, idx in ands:
                t &= bits[(sig, int(idx))]
            v ^= t
        bits[(dst, di)] = v
        if dst == "z":
            z |= v << di
    return z


def main():
    vpath, form, tapsA, tapsB, rounds = (sys.argv[1], sys.argv[2], sys.argv[3],
                                        sys.argv[4], int(sys.argv[5]))
    tapsA = tuple(int(v) for v in tapsA.split(","))
    tapsB = tuple(int(v) for v in tapsB.split(","))
    rng = np.random.default_rng(0xBE12)
    K = 0x123456789ABCDEF0
    n = 300
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    keys = {}
    for r in range(rounds):
        keys[f"ka{r}"] = np.uint64(K)
        keys[f"kb{r}"] = M.rotl(np.uint64(K), 13)
    bad = 0
    for xv in xs:
        zv = eval_verilog(vpath, xv, keys)
        if form == "1a":
            ref = M.apply(np.uint64(xv), rounds, K, tapsA, tapsB)
        else:
            ref = apply2(np.uint64(xv), rounds, K, tapsA, tapsB)
        if int(zv) != int(ref):
            bad += 1
            if bad < 4:
                print(f"MISMATCH x={xv:#x} verilog={zv:#x} model={ref:#x}")
    print(f"XCHECK {vpath}: {n-bad}/{n} match -> {'PASS' if bad == 0 else 'FAIL'}")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()

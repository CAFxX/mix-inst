#!/usr/bin/env python3
"""Diagnose the best hetstage pilot draws: replay the RNG stream (seed 0xB802)
to reconstruct tries 53 and 78, then run the inner gate + per-key z
breakdown. Read-only; does not modify the pilot artifacts."""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
import t8_hetstage_screen as T
import t8_het8_screen as H
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]


def build_plan():
    plan = []
    a1 = lambda r: T._draw_circ1(r)  # noqa: E731
    a2 = lambda r: T._draw_circ2(r)  # noqa: E731
    plan += [("A", "H1", a1, 7, "CIRC1"), ("A", "H1", a2, 7, "CIRC2"),
             ("A", "H2", a1, 7, "CIRC1"), ("A", "H2", a2, 6, "CIRC2"),
             ("A", "H3", a1, 6, "CIRC1"), ("A", "H3", a2, 7, "CIRC2")]
    pcs = [3, 5, 7]
    pi = [0]

    def b_sparse(r, _pi=pi):
        pc = pcs[_pi[0] % 3]
        _pi[0] += 1
        return T._draw_gfmul(r, pc)

    def b_dense(r):
        return T._draw_gfmul(r, int(r.integers(24, 41)))

    plan += [("B", "H1", b_sparse, 10, "GFM-sp"),
             ("B", "H1", b_dense, 4, "GFM-dense"),
             ("B", "H2", b_sparse, 13, "GFM-sp"),
             ("B", "H3", b_sparse, 13, "GFM-sp")]
    plan += [("C", "H1", T._draw_andor, 14, "ANDOR"),
             ("C", "H2", T._draw_andor, 13, "ANDOR"),
             ("C", "H3", T._draw_andor, 13, "ANDOR")]
    return plan


def per_key_z(stages):
    V = np.arange(N, dtype=np.uint64)
    out = []
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = T.apply_stage(x, st)
        S = ((x ^ T.rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, flp, _ = diff_cell_logps(S, key)
        out.append((key, wz, flp))
    return out


def main():
    rng = np.random.default_rng(0xB802)
    want = {53: None, 78: None}
    n = 0
    meta = {}
    for ttype, tname, hfn, ndraw, label in build_plan():
        for _ in range(ndraw):
            h = hfn(rng)
            stages = T.TEMPLATES[tname](rng, h)
            if n in want:
                want[n] = stages
                meta[n] = (ttype, tname, label)
            n += 1
    for i in (53, 78):
        stages = want[i]
        ttype, tname, label = meta[i]
        print("=== try %d %s/%s %s ===" % (i, ttype, tname, label))
        print("stages:", [T._ser(s) for s in stages])
        inner = T.eval_inner(stages)
        print("INNER lin=%s diff=%s" %
              (inner["lin_verdict"], inner["diff_verdict"]))
        for key, wz, flp in per_key_z(stages):
            print("  key=%#018x worst|z|=%8.1f fisher_logp=%7.1f" %
                  (key, wz, flp))


if __name__ == "__main__":
    main()

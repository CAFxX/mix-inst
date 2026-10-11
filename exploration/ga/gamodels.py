#!/usr/bin/env python3
"""Numpy (vectorized) model decoder for GA genomes.

Imports validated boolean primitives from round20/models/r20.py; implements
the genome pipeline (P-box / XOR-constant / mask genes) identically to the C
and RTL emitters. The three implementations are cross-checked by xcheck
(C-vs-Python, 10k vectors) and S0's mapped-netlist equivalence check.
"""
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/round20/models")
import r20  # noqa: E402

sys.path.insert(0, EXP + "/ga")
from genome import (PERM_TABLES, MASK_PAT, const32, C_PRE64, C_POST64,  # noqa: E402
                    LIN2)

MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _perm_np(x, table, width):
    """Apply bit-permutation table (vectorized over x)."""
    x = np.asarray(x, dtype=np.uint64)
    out = np.zeros_like(x)
    for i, s in enumerate(table):
        out |= ((x >> np.uint64(s)) & np.uint64(1)) << np.uint64(i)
    return out & (MASK64 if width == 64 else MASK32)


def _masknl_np(x, r, pat):
    return (x ^ ((x >> np.uint64(r)) & np.uint64(pat))) & MASK32


# nonlinear primitives (32-bit), by family
def _nl_s1(x):
    return r20._sbox_layer32_np(x, r20.S1)


def _nl_chi(x):
    return r20._chi32_np(x)


def _nl_chi32v(x):
    return r20._chi32v_np(x)


def _nl_chi32w(x):
    return r20._chi32w_np(x)


def _nl_ps(x):
    # parsplit: chi16(R[31:16]) || S1(R[15:0])  (matches gen_r20._ps_block)
    x = x & MASK32
    hi = x >> np.uint64(16)
    chi16 = np.zeros_like(x)
    for i in range(16):
        a0 = (hi >> np.uint64(i)) & np.uint64(1)
        a1 = (hi >> np.uint64((i + 1) % 16)) & np.uint64(1)
        a2 = (hi >> np.uint64((i + 2) % 16)) & np.uint64(1)
        chi16 |= (a0 ^ ((np.uint64(1) - a1) & a2)) << np.uint64(i)
    lo = r20._sbox_layer32_np(x & np.uint64(0xFFFF), r20.S1) & np.uint64(0xFFFF)
    return ((chi16 << np.uint64(16)) | lo) & MASK32


_NL = {
    "s1": _nl_s1, "chi": _nl_chi, "chi32v": _nl_chi32v,
    "chi32w": _nl_chi32w, "ps": _nl_ps,
}

# tag -> (kind, payload). kind: lin2 | notr | fm | keyin
_TAGKIND = {}
for _t, _ab in LIN2.items():
    _fam = {"s1_311": "s1", "s1_713": "s1", "s1_517": "s1",
            "chi_311": "chi", "chi_713": "chi",
            "chi32v_311": "chi32v", "chi32v_517": "chi32v",
            "chi32w_311": "chi32w", "ps_311": "ps"}[_t]
    _TAGKIND[_t] = ("lin2", (_fam, _ab))
for _t in ("s1_notr", "chi_notr", "chi32v_notr", "chi32w_notr", "ps_notr"):
    _fam = _t.split("_")[0]
    _fam = {"s1": "s1", "chi": "chi", "chi32v": "chi32v",
            "chi32w": "chi32w", "ps": "ps"}[_fam]
    _TAGKIND[_t] = ("notr", _fam)
_TAGKIND["chi_keyin_notr"] = ("keyin", None)
_TAGKIND["chi_fm03"] = ("fm", 3)
_TAGKIND["chi_fm07"] = ("fm", 7)
_TAGKIND["chi_fm11"] = ("fm", 11)
_TAGKIND["chi_fm16"] = ("fm", 16)
_TAGKIND["chi_fm311"] = ("fm311", None)


def _parse_mask(mask):
    if mask == "none":
        return None
    r_s, p_s = mask.split("_")
    return int(r_s[1:]), MASK_PAT[p_s]


def decode_np(genome):
    """Return vectorized f(V, K) -> uint64 array for the genome."""
    n = genome["rounds"]
    tags = genome["tags"]
    assert len(tags) == n
    pbox_where = genome.get("pbox_where", "none")
    pbox_perm = genome.get("pbox_perm")
    const_where = genome.get("const_where", "none")
    const_fam = genome.get("const_fam")
    mask_p = _parse_mask(genome.get("mask", "none"))

    p64 = PERM_TABLES[pbox_perm] if pbox_where == "between64" else None
    p32 = PERM_TABLES[pbox_perm] if pbox_where in ("inF32", "replacerot") else None
    replacerot = (pbox_where == "replacerot")

    def F_of(i, R, rk):
        # Returns the full keyed F value (r20 convention: every F bakes ^rk
        # in internally; the Feistel loop then does nR = L ^ F uniformly).
        # i: 0-based round index
        tag = tags[i]
        kind, pay = _TAGKIND[tag]
        a = _perm_np(R, p32, 32) if p32 is not None and pbox_where == "inF32" else R
        if kind == "lin2":
            fam, (la, lb) = pay
            u = _NL[fam](a)
            v = _masknl_np(u, *mask_p) if mask_p else u
            if replacerot:
                lin = (v ^ r20._rotl32_np(v, la) ^ _perm_np(v, p32, 32)) & MASK32
            else:
                lin = r20._lin_ab_np(v, la, lb)
            return (lin ^ rk) & MASK32
        if kind == "notr":
            u = _NL[pay](a)
            v = _masknl_np(u, *mask_p) if mask_p else u
            return (v ^ rk) & MASK32
        if kind == "keyin":
            u = r20._chi32_np((a ^ rk) & MASK32)
            v = _masknl_np(u, *mask_p) if mask_p else u
            return v & MASK32
        if kind == "fm":
            m = pay
            c = r20._chi32_np(a)
            v = _masknl_np(c, *mask_p) if mask_p else c
            y = (v ^ rk) & MASK32
            return (y ^ r20._rotl32_np(y, m)) & MASK32
        if kind == "fm311":
            c = r20._chi32_np(a)
            v = _masknl_np(c, *mask_p) if mask_p else c
            return (r20._rotl32_np(v, 3) ^ r20._rotl32_np(v, 11) ^ rk) & MASK32
        raise ValueError(tag)

    def fn(x, k):
        x = np.asarray(x, dtype=np.uint64)
        k = np.asarray(k, dtype=np.uint64)
        if const_where == "prepost":
            x = (x ^ np.uint64(C_PRE64)) & MASK64
        L = (x >> np.uint64(32)) & MASK32
        R = x & MASK32
        for i in range(1, n + 1):
            Rc = R
            if const_where == "round_F":
                Rc = (R ^ np.uint64(const32(const_fam, i))) & MASK32
            rk = r20._rk32_std_np(k, i)
            t = F_of(i - 1, Rc, rk)
            # r20 convention: F is fully keyed; the loop never re-adds rk.
            nR = (L ^ t) & MASK32
            L, R = R, nR
            if p64 is not None and i < n:
                j = ((L << np.uint64(32)) | R) & MASK64
                j = _perm_np(j, p64, 64)
                L = (j >> np.uint64(32)) & MASK32
                R = j & MASK32
        out = ((R << np.uint64(32)) | L) & MASK64
        if const_where == "prepost":
            out = (out ^ np.uint64(C_POST64)) & MASK64
        return out

    return fn


def bijection_spotcheck(fn, n=2000, seed=0xB1):
    """Fixed-key distinctness check (would fail on a degenerate design)."""
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2 ** 64, size=n, dtype=np.uint64)
    K = np.uint64(0xDEADBEEFCAFEBABE)
    O = fn(V, K)
    assert len(set(O.tolist())) == n, "bijection spot-check FAILED"
    return True

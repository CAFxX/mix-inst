#!/usr/bin/env python3
"""Genome spec for the mix GA: schema, gene pools, validation, operators.

Single source of truth for: tag pool, P-box permutation tables, constant
families, mask patterns, validity rules, crossover/mutation, fingerprinting.
"""
import hashlib
import json
import random

# ---------------------------------------------------------------- pools

GENERAL_TAGS = [
    "s1_311", "s1_713", "s1_517",
    "chi_311", "chi_713",
    "chi32v_311", "chi32v_517",
    "chi32w_311",
    "ps_311",
]
FINAL_TAGS = [
    "s1_notr", "chi_notr", "chi32v_notr", "chi32w_notr",
    "chi_keyin_notr",
    "chi_fm03", "chi_fm07", "chi_fm11", "chi_fm311", "chi_fm16",
    "ps_notr",
]
TAG_POOL = GENERAL_TAGS + FINAL_TAGS

# tags whose F carries a 2-rotation linear lin(x)=x^rotl(x,a)^rotl(x,b)
# (used by the replacerot P-box placement)
LIN2 = {
    "s1_311": (3, 11), "chi_311": (3, 11), "chi32v_311": (3, 11),
    "chi32w_311": (3, 11), "ps_311": (3, 11),
    "s1_713": (7, 13), "chi_713": (7, 13),
    "s1_517": (5, 17), "chi32v_517": (5, 17),
}
# nonlinear family per tag (for the linear-swap mutation)
NL_FAM = {
    "s1_311": "s1", "s1_713": "s1", "s1_517": "s1",
    "chi_311": "chi", "chi_713": "chi",
    "chi32v_311": "chi32v", "chi32v_517": "chi32v",
    "chi32w_311": "chi32w",
    "ps_311": "ps",
}
FAM_TAGS = {}  # (family, (a,b)) -> tag, built below
for _t, _ab in LIN2.items():
    FAM_TAGS[(NL_FAM[_t], _ab)] = _t
LIN_PAIRS = [(3, 11), (7, 13), (5, 17)]

PBOX_WHERE = ["none", "between64", "inF32", "replacerot"]
P64_PERMS = ["bitrev64", "byteswap64", "nibrev64", "interleave64",
             "transpose8x8", "rot64_16", "rot64_32"]
P32_PERMS = ["bitrev32", "byteswap32", "nibrev32", "interleave32",
             "transpose8x4", "rot32_8", "rot32_16"]

CONST_WHERE = ["none", "round_F", "prepost"]
CONST_FAM = ["bit", "byte", "iota"]

MASK_R = [1, 2, 3]
MASK_PAT = {
    "A5": 0xAAAAAAAA,
    "0F": 0x0F0F0F0F,
    "FF": 0x00FF00FF,
    "SP": 0x01010101,
    "H2": 0x0000FFFF,
}
MASK_VALS = ["none"] + [f"r{r}_{p}" for r in MASK_R for p in MASK_PAT]

ROUNDS_CHOICES = [5, 6, 7]

# ------------------------------------------------- permutation tables
# table[i] = source bit index for output bit i.  All are bijections.


def _build_perm_tables():
    T = {}

    def bitrev(w):
        return [w - 1 - i for i in range(w)]

    def byteswap(w):
        nb = w // 8
        t = []
        for i in range(w):
            by, bi = divmod(i, 8)
            t.append((nb - 1 - by) * 8 + bi)
        return t

    def nibrev(w):
        nn = w // 4
        t = []
        for i in range(w):
            ny, ni = divmod(i, 4)
            t.append((nn - 1 - ny) * 4 + ni)
        return t

    def interleave(w):
        h = w // 2
        return [(i // 2) if i % 2 == 0 else (h + i // 2) for i in range(w)]

    def transpose8x8():
        return [j * 8 + i for i in range(8) for j in range(8)]

    def transpose8x4():
        # 8x4 bit-matrix transpose: index i = r*4+c -> c*8+r (a permutation)
        return [(i % 4) * 8 + (i // 4) for i in range(32)]

    def rot(w, k):
        return [(i - k) % w for i in range(w)]

    T["bitrev64"] = bitrev(64)
    T["byteswap64"] = byteswap(64)
    T["nibrev64"] = nibrev(64)
    T["interleave64"] = interleave(64)
    T["transpose8x8"] = transpose8x8()
    T["rot64_16"] = rot(64, 16)
    T["rot64_32"] = rot(64, 32)
    T["bitrev32"] = bitrev(32)
    T["byteswap32"] = byteswap(32)
    T["nibrev32"] = nibrev(32)
    T["interleave32"] = interleave(32)
    T["transpose8x4"] = transpose8x4()
    T["rot32_8"] = rot(32, 8)
    T["rot32_16"] = rot(32, 16)
    return T


PERM_TABLES = _build_perm_tables()
P64_MAP = {n: PERM_TABLES[n] for n in P64_PERMS}
P32_MAP = {n: PERM_TABLES[n] for n in P32_PERMS}

# ------------------------------------------------- constants
# Keccak-f round constants, low 32 bits (standard values)
IOTA32 = [
    0x00000001, 0x00008082, 0x0000808A, 0x80008000, 0x0000808B,
    0x80000001, 0x80008081, 0x00008009, 0x0000008A, 0x00000088,
    0x80008009, 0x8000000A,
]
C_PRE64 = 0x9E3779B97F4A7C15  # golden ratio (nothing-up-my-sleeve)
C_POST64 = 0xBF58476D1CE4E5B9  # splitmix64 gamma (nothing-up-my-sleeve)


def const32(fam, rnd1):
    """32-bit round constant for 1-based round rnd1."""
    if fam == "bit":
        return (1 << ((rnd1 - 1) % 32)) & 0xFFFFFFFF
    if fam == "byte":
        return (rnd1 * 0x01010101) & 0xFFFFFFFF
    if fam == "iota":
        return IOTA32[(rnd1 - 1) % len(IOTA32)]
    raise ValueError(fam)


# ------------------------------------------------- schema / validation

def blank_genome():
    return {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_notr"],
        "pbox_where": "none",
        "pbox_perm": None,
        "const_where": "none",
        "const_fam": None,
        "mask": "none",
    }


def validate(g):
    """Raise ValueError on any invalid genome (fail-closed)."""
    if g["rounds"] not in ROUNDS_CHOICES:
        raise ValueError(f"rounds {g['rounds']}")
    if len(g["tags"]) != g["rounds"]:
        raise ValueError("tags/rounds length mismatch")
    for i, t in enumerate(g["tags"]):
        if t not in TAG_POOL:
            raise ValueError(f"bad tag {t}")
        if t in FINAL_TAGS and i != g["rounds"] - 1:
            raise ValueError(f"final-only tag {t} on round {i+1}")
    if g["pbox_where"] not in PBOX_WHERE:
        raise ValueError(f"pbox_where {g['pbox_where']}")
    if g["pbox_where"] == "none":
        if g["pbox_perm"] is not None:
            raise ValueError("pbox_perm set with where=none")
    elif g["pbox_where"] == "between64":
        if g["pbox_perm"] not in P64_PERMS:
            raise ValueError(f"pbox_perm {g['pbox_perm']} for between64")
    else:
        if g["pbox_perm"] not in P32_PERMS:
            raise ValueError(f"pbox_perm {g['pbox_perm']} for {g['pbox_where']}")
    if g["const_where"] not in CONST_WHERE:
        raise ValueError(f"const_where {g['const_where']}")
    if g["const_where"] == "none":
        if g["const_fam"] is not None:
            raise ValueError("const_fam set with where=none")
    elif g["const_fam"] not in CONST_FAM:
        raise ValueError(f"const_fam {g['const_fam']}")
    if g["mask"] not in MASK_VALS:
        raise ValueError(f"mask {g['mask']}")
    return True


def canonical(g):
    validate(g)
    return json.dumps(g, sort_keys=True)


# ------------------------------------------------- operators

def random_tag(final_round, rng):
    pool = FINAL_TAGS if final_round else GENERAL_TAGS
    return rng.choice(pool)


def random_genome(rng=None):
    r = rng or random
    n = r.choice(ROUNDS_CHOICES)
    g = blank_genome()
    g["rounds"] = n
    g["tags"] = [random_tag(i == n - 1, r) for i in range(n)]
    if r.random() < 0.35:
        g["pbox_where"] = r.choice(PBOX_WHERE[1:])
        g["pbox_perm"] = (r.choice(P64_PERMS) if g["pbox_where"] == "between64"
                          else r.choice(P32_PERMS))
    if r.random() < 0.30:
        g["const_where"] = r.choice(CONST_WHERE[1:])
        g["const_fam"] = r.choice(CONST_FAM)
    if r.random() < 0.25:
        g["mask"] = r.choice(MASK_VALS[1:])
    validate(g)
    return g


def _repair_final_tags(g, rng):
    n = g["rounds"]
    for i in range(n - 1):
        if g["tags"][i] in FINAL_TAGS:
            g["tags"][i] = rng.choice(GENERAL_TAGS)


def crossover(p1, p2, rng=None):
    r = rng or random
    for _ in range(8):
        n1, n2 = p1["rounds"], p2["rounds"]
        c = r.randint(1, min(n1, n2) - 1)
        child = blank_genome()
        child["tags"] = list(p1["tags"][:c]) + list(p2["tags"][c:])
        child["rounds"] = len(child["tags"])
        if child["rounds"] not in ROUNDS_CHOICES:
            continue
        # uniform crossover on scalar genes
        for key in ("pbox_where", "pbox_perm", "const_where", "const_fam", "mask"):
            child[key] = r.choice([p1[key], p2[key]])
        # perm must match where's width; repair if crossed inconsistently
        _fix_pbox_consistency(child, r)
        _repair_final_tags(child, r)
        try:
            validate(child)
            return child
        except ValueError:
            continue
    # fallback: clone + mutate
    return mutate(r.choice([p1, p2]), rng=r)


def _fix_pbox_consistency(g, r=None):
    r = r or random
    w = g["pbox_where"]
    if w == "none":
        g["pbox_perm"] = None
    elif w == "between64":
        if g["pbox_perm"] not in P64_PERMS:
            g["pbox_perm"] = r.choice(P64_PERMS)
    else:
        if g["pbox_perm"] not in P32_PERMS:
            g["pbox_perm"] = r.choice(P32_PERMS)


def _trunc_counterpart(tag):
    """lin <-> notr counterpart for the truncation-toggle mutation."""
    pairs = {
        "s1_311": "s1_notr", "s1_notr": "s1_311",
        "chi_311": "chi_notr", "chi_notr": "chi_311",
        "chi32v_311": "chi32v_notr", "chi32v_notr": "chi32v_311",
        "chi32w_311": "chi32w_notr", "chi32w_notr": "chi32w_311",
        "ps_311": "ps_notr", "ps_notr": "ps_311",
    }
    return pairs.get(tag)


MUT_OPS = [
    ("tag_swap", 0.22),
    ("linear_swap", 0.12),
    ("trunc_toggle", 0.08),
    ("keyin_flip", 0.04),
    ("final_mix", 0.08),
    ("round_count", 0.04),
    ("pbox_where", 0.08),
    ("pbox_perm", 0.07),
    ("const_where", 0.05),
    ("const_fam", 0.03),
    ("mask", 0.09),
]
_MUT_TOTAL = sum(w for _, w in MUT_OPS)


def _pick_op(r):
    x = r.random() * _MUT_TOTAL
    for name, w in MUT_OPS:
        x -= w
        if x <= 0:
            return name
    return MUT_OPS[-1][0]


def mutate(g, rng=None, op=None):
    r = rng or random
    c = json.loads(json.dumps(g))  # deep copy
    n = c["rounds"]
    op = op or _pick_op(r)
    if op == "tag_swap":
        i = r.randrange(n)
        c["tags"][i] = random_tag(i == n - 1, r)
    elif op == "linear_swap":
        i = r.randrange(n)
        t = c["tags"][i]
        if t in NL_FAM:
            fam = NL_FAM[t]
            ab = r.choice([p for p in LIN_PAIRS if (fam, p) in FAM_TAGS])
            c["tags"][i] = FAM_TAGS[(fam, ab)]
    elif op == "trunc_toggle":
        t = c["tags"][n - 1]
        cp = _trunc_counterpart(t)
        if cp is not None:
            c["tags"][n - 1] = cp
    elif op == "keyin_flip":
        t = c["tags"][n - 1]
        if t == "chi_notr":
            c["tags"][n - 1] = "chi_keyin_notr"
        elif t == "chi_keyin_notr":
            c["tags"][n - 1] = "chi_notr"
    elif op == "final_mix":
        c["tags"][n - 1] = r.choice(FINAL_TAGS)
    elif op == "round_count":
        if n == 5:
            dn = +1
        elif n == 7:
            dn = -1
        else:
            dn = r.choice([-1, +1])
        if dn == +1:
            # insert a copy of a random non-final round before the final round
            i = r.randrange(n - 1)
            c["tags"].insert(n - 1, c["tags"][i])
            c["rounds"] = n + 1
        else:
            i = r.randrange(n - 1)
            del c["tags"][i]
            c["rounds"] = n - 1
    elif op == "pbox_where":
        c["pbox_where"] = r.choice(PBOX_WHERE)
        _fix_pbox_consistency(c, r)
    elif op == "pbox_perm":
        if c["pbox_where"] == "between64":
            c["pbox_perm"] = r.choice(P64_PERMS)
        elif c["pbox_where"] != "none":
            c["pbox_perm"] = r.choice(P32_PERMS)
        # (where=none: perm mutation is a no-op by design)
    elif op == "const_where":
        c["const_where"] = r.choice(CONST_WHERE)
        if c["const_where"] != "none" and c["const_fam"] is None:
            c["const_fam"] = r.choice(CONST_FAM)
        if c["const_where"] == "none":
            c["const_fam"] = None
    elif op == "const_fam":
        if c["const_where"] != "none":
            c["const_fam"] = r.choice(CONST_FAM)
    elif op == "mask":
        c["mask"] = r.choice(MASK_VALS)
    else:
        raise ValueError(op)
    _repair_final_tags(c, r)
    validate(c)
    return c


# ------------------------------------------------- fingerprint

def fingerprint(g, model_out_bytes):
    """Dedupe key: canonical genome + model outputs on fixed vectors."""
    h = hashlib.sha256()
    h.update(canonical(g).encode())
    h.update(model_out_bytes)
    return h.hexdigest()

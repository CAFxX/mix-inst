#!/usr/bin/env python3
"""Self-tests for the GA harness. Every test is capable of failing
(capability is demonstrated by the assertions; e.g. a corrupted permutation
table fails test_perm_bijections, a broken decoder fails test_seed_exact).

Run: python3 ga/test_ga.py
"""
import json
import os
import random
import re
import subprocess
import sys

EXP = "/home/hatch/workspace/mix/exploration"
GA = os.path.join(EXP, "ga")
sys.path.insert(0, GA)

import numpy as np

from genome import (PERM_TABLES, P64_PERMS, P32_PERMS, validate, blank_genome,
                    random_genome, crossover, mutate, canonical, const32,
                    IOTA32, MASK_PAT)
from gamodels import decode_np, _perm_np, bijection_spotcheck
import evaluate as EV


def check(name, cond, detail=""):
    status = "ok" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        raise AssertionError(f"test failed: {name} {detail}")


def test_perm_bijections():
    for pname, table in PERM_TABLES.items():
        w = 64 if "64" in pname or "8x8" in pname else 32
        check(f"perm {pname} bijective", sorted(table) == list(range(w)),
              f"w={w}")
    check("p64 set", set(P64_PERMS) <= set(PERM_TABLES))
    check("p32 set", set(P32_PERMS) <= set(PERM_TABLES))


def _perm_ref(x, table, w):
    # independent dumb reference (bit loop in pure python ints)
    out = 0
    for i, s in enumerate(table):
        out |= ((x >> s) & 1) << i
    return out & ((1 << w) - 1)


def test_perm_np_matches_ref():
    rng = random.Random(7)
    for pname, table in PERM_TABLES.items():
        w = 64 if ("64" in pname or "8x8" in pname) else 32
        for _ in range(5):
            xv = rng.getrandbits(w)
            got = int(_perm_np(np.uint64(xv), table, w))
            want = _perm_ref(xv, table, w)
            check(f"perm_np {pname}", got == want, f"{xv:#x}")


def test_const_families():
    check("iota len", len(IOTA32) >= 7)
    check("iota[0]", IOTA32[0] == 0x00000001)
    check("iota[1]", IOTA32[1] == 0x00008082)  # keccak RC1 low32
    check("const bit r1", const32("bit", 1) == 0x00000001)
    check("const bit r33 wraps", const32("bit", 33) == 0x00000001)
    check("const byte r2", const32("byte", 2) == 0x02020202)
    check("const iota r1", const32("iota", 1) == 0x00000001)


def _ref_model(name, src_round):
    import importlib.util
    cands = [p for p in
             __import__("glob").glob(os.path.join(EXP, src_round, "models", "*.py"))]
    spec = importlib.util.spec_from_file_location("refx", cands[0])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, name)


SEED_CASES = [
    ("r20_feist6_alt_notr_chioff13all_nw", "round20",
     ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi32v_notr"]),
    ("r20_feist6_alt_notr_chioff31_nw", "round20",
     ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "chi_notr"]),
    ("r19_feist6_alt_notr_fm07_nw", "round19",
     ["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_fm07"]),
]


def _mkgenome(tags):
    g = blank_genome()
    g["rounds"] = len(tags)
    g["tags"] = list(tags)
    validate(g)
    return g


def test_seed_exact():
    rng = np.random.default_rng(0x5EED)
    V = rng.integers(0, 2 ** 64, size=1024, dtype=np.uint64)
    K = rng.integers(0, 2 ** 64, size=1024, dtype=np.uint64)
    for name, src, tags in SEED_CASES:
        ref = _ref_model(name, src)
        got = decode_np(_mkgenome(tags))(V, K)
        want = ref(V, K)
        check(f"seed exact {name}",
              np.array_equal(np.asarray(got), np.asarray(want)))


def test_seed_bijection():
    for name, src, tags in SEED_CASES:
        fn = decode_np(_mkgenome(tags))
        check(f"bijection {name}", bijection_spotcheck(fn))


def test_operators_fuzz():
    r = random.Random(1234)
    for i in range(500):
        g = random_genome(r)
        validate(g)  # must not raise
        c = crossover(g, random_genome(r), r)
        validate(c)
        m = mutate(g, rng=r)
        validate(m)
    check("operators fuzz 500x", True)


def test_mutate_all_ops():
    r = random.Random(99)
    g = _mkgenome(["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_notr"])
    ops = ["tag_swap", "linear_swap", "trunc_toggle", "keyin_flip",
           "final_mix", "round_count", "pbox_where", "pbox_perm",
           "const_where", "const_fam", "mask"]
    for op in ops:
        m = mutate(g, rng=r, op=op)
        validate(m)
    check("all mutate ops valid", True)
    # trunc_toggle on chi_notr final -> chi_311
    m = mutate(g, rng=r, op="trunc_toggle")
    check("trunc_toggle", m["tags"][-1] == "chi_311", m["tags"][-1])


def test_pareto_utils():
    from ga import dominates, pareto_add
    check("dom basic", dominates((1, 2, 3), (2, 3, 4)))
    check("dom false", not dominates((1, 5, 3), (2, 3, 4)))
    check("dom equal false", not dominates((1, 2, 3), (1, 2, 3)))
    arch = {}
    ok, ev = pareto_add(arch, "a", (37.0, 4357, 12511), {})
    check("add a", ok and not ev)
    ok, ev = pareto_add(arch, "b", (38.0, 5000, 13000), {})
    check("b dominated", not ok and "a" in arch)
    ok, ev = pareto_add(arch, "c", (36.9, 5000, 13000), {})
    check("c enters", ok and "c" in arch)
    ok, ev = pareto_add(arch, "d", (36.0, 4000, 12000), {})
    check("d dominates all", ok and set(arch) == {"d"}, str(set(arch)))


def test_hypothesize():
    g = _mkgenome(["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_notr"])
    # S1 LIN -> guided_linear
    ann = EV.annotate("S1", g, {"lin_rejected": [1, 2], "diff_rejected": [],
                                "pb_rejected": [], "red_rejected": []})
    check("hyp LIN", ann["suggested_fix"] == "guided_linear",
          ann["suggested_fix"])
    # S1 PB -> guided_const (round constants break symmetry)
    ann = EV.annotate("S1", g, {"lin_rejected": [], "diff_rejected": [],
                                "pb_rejected": [1], "red_rejected": []})
    check("hyp PB", ann["suggested_fix"] == "guided_const")
    # S2 spikes on a genome without mid-round truncation -> guided_diffusion
    # (mid-round truncation is not genome-expressible: notr5/drop4 proved it
    #  broken; truncation tags are final-only by design)
    spikes = [(f"0x{i:016x}", 100.0 + i) for i in range(12)]
    ann = EV.annotate("S2", g, {"verdict": "PASS", "max_repeats": 0,
                                "max_z": 500.0, "spikes": spikes})
    check("hyp S2 diffusion", ann["suggested_fix"] == "guided_diffusion",
          ann["hypothesis"][:60])
    # Q1 bic -> guided_finalmix
    ann = EV.annotate("Q1", g, {"sac_z5": 0, "bic_maxcorr": 0.15})
    check("hyp bic", ann["suggested_fix"] == "guided_finalmix")
    check("gene_pattern", len(ann["gene_pattern"]) > 0)


def test_guided_mutate():
    from ga import guided_mutate
    r = random.Random(5)
    g = _mkgenome(["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_notr"])
    ann = {"suggested_fix": "guided_untruncate", "stage": "S2"}
    c = guided_mutate(g, ann, r)
    validate(c)
    check("guided_untruncate restores final linear",
          c["tags"][-1] == "chi_311", c["tags"][-1])
    ann = {"suggested_fix": "guided_const", "stage": "S1"}
    c = guided_mutate(g, ann, r)
    check("guided_const adds round_F",
          c["const_where"] == "round_F" and c["const_fam"] in
          ("bit", "byte", "iota"))
    ann = {"suggested_fix": "guided_finalmix", "stage": "Q1"}
    c = guided_mutate(g, ann, r)
    check("guided_finalmix", c["tags"][-1] in ("chi_fm07", "chi_fm11", "chi_fm311"))


def test_checkpoint_roundtrip():
    import pickle
    import tempfile
    import ga as _ga
    from ga import save_checkpoint, load_checkpoint
    # NEVER write the test checkpoint over the live ga/state/checkpoint.pkl:
    # a 2026-10-03 run of this test clobbered the production checkpoint
    # mid-evolution (recovered from logs + deterministic re-mining).
    orig_state = _ga.STATE
    tmpd = tempfile.mkdtemp(prefix="ga_ckpt_test_")
    try:
        _ga.STATE = tmpd
        r = random.Random(42)
        st = {"rng_state": r.getstate(), "generation": 3,
              "fingerprints": {"abc", "def"}}
        save_checkpoint(st)
        st2 = load_checkpoint()
        r2 = random.Random()
        r2.setstate(st2["rng_state"])
        check("rng state roundtrip",
              r2.random() == random.Random(42).random())
        check("fields", st2["generation"] == 3 and st2["fingerprints"] == {"abc", "def"})
    finally:
        _ga.STATE = orig_state
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)


def test_emit_base_delegates():
    # base genome -> byte-identical to gen_r20 emission path
    import tempfile
    from emit import emit_candidate, is_base
    g = _mkgenome(["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_notr"])
    check("is_base", is_base(g))
    with tempfile.TemporaryDirectory() as td:
        d = emit_candidate("ga_test_base", g, outdir=os.path.join(td, "c"))
        for fn in ("impl.c", "rtl.v", "model.py", "meta.json", "genome.json"):
            check(f"emit {fn}", os.path.exists(os.path.join(d, fn)))
        # C syntax check (fast)
        rc = subprocess.run(["gcc", "-fsyntax-only",
                             os.path.join(d, "impl.c")],
                            capture_output=True).returncode
        check("impl.c syntax", rc == 0)


def test_emit_extended():
    import tempfile
    from emit import emit_candidate, is_base
    g = _mkgenome(["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                   "s1_311", "chi32v_notr"])
    g["pbox_where"] = "between64"
    g["pbox_perm"] = "interleave64"
    g["const_where"] = "round_F"
    g["const_fam"] = "iota"
    g["mask"] = "r2_A5"
    validate(g)
    check("not base", not is_base(g))
    with tempfile.TemporaryDirectory() as td:
        d = emit_candidate("ga_test_ext", g, outdir=os.path.join(td, "c"))
        rc = subprocess.run(["gcc", "-fsyntax-only",
                             os.path.join(d, "impl.c")],
                            capture_output=True).returncode
        check("ext impl.c syntax", rc == 0)
        # model.py loads and matches decode_np
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ga_test_ext_model", os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        rng = np.random.default_rng(11)
        V = rng.integers(0, 2 ** 64, size=64, dtype=np.uint64)
        K = rng.integers(0, 2 ** 64, size=64, dtype=np.uint64)
        check("ext model.py == decode_np",
              np.array_equal(np.asarray(m.mix_np(V, K)),
                             np.asarray(decode_np(g)(V, K))))
        # RTL: all logic inside the always block (AGENTS.md lesson)
        rtl = open(os.path.join(d, "rtl.v")).read()
        check("rtl always block", "always @(*)" in rtl)
        assigns = [ln for ln in rtl.split("\n")
                   if re.match(r"\s*assign\b", ln)]
        check("rtl single module-level assign", len(assigns) == 1, str(assigns))
        check("rtl assign reads only regs",
              assigns[0].strip() == "assign out = {R, L};", assigns[0])


def main():
    test_perm_bijections()
    test_perm_np_matches_ref()
    test_const_families()
    test_seed_exact()
    test_seed_bijection()
    test_operators_fuzz()
    test_mutate_all_ops()
    test_pareto_utils()
    test_hypothesize()
    test_guided_mutate()
    test_checkpoint_roundtrip()
    test_emit_base_delegates()
    test_emit_extended()
    print("\nALL GA SELF-TESTS PASSED")


if __name__ == "__main__":
    main()

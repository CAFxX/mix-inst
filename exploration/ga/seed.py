#!/usr/bin/env python3
"""Seed mining for the GA: archive from all valid solutions (parsed logs, no
re-synthesis), population from the genome-expressible subset (bit-exact
validated), plus Carlo's hand-built cheap-layer seeds.
"""
import glob
import json
import os
import re
import sys

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/ga")
from genome import validate  # noqa: E402
from gamodels import decode_np  # noqa: E402

FB = os.path.join(EXP, "fast_battery")

# candidate -> genome mapping for the population-expressible valid solutions.
# Every entry is bit-exact validated against the checked-in model before use.
GENOME_MAP = {
    "r20_feist6_alt_notr_chioff13all_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi32v_notr"],
        "src": "round20"},
    "r20_feist6_alt_notr_chioff31_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi32w_311", "s1_311", "chi32w_311",
                 "s1_311", "chi_notr"],
        "src": "round20"},
    "r19_feist6_alt_notr_chioff13_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi_notr"],
        "src": "round19"},
    "r20_feist6_alt_notr_keyin_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_keyin_notr"],
        "src": "round20"},
    "r18_feist6_alt_notr_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_notr"],
        "src": "round18"},
    "r19_feist6_alt_notr_fm07_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm07"],
        "src": "round19"},
    "r19_feist6_alt_notr_fm11_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm11"],
        "src": "round19"},
    "r19_feist6_alt_notr_fm311_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm311"],
        "src": "round19"},
    "r19_feist6_alt_notr_fm03_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm03"],
        "src": "round19"},
    "r19_feist6_alt_notr_chioff13_fm03_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi_fm03"],
        "src": "round19"},
    "r20_feist6_alt_notr_fm16_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm16"],
        "src": "round20"},
    "r13_feist6_alt_s1chi_nw": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_311"],
        "src": "round13"},
    "r15_feist6_parsplit_nw": {
        "rounds": 6,
        "tags": ["ps_311"] * 6,
        "src": "round15"},
    "r9_feist6_rot311_nw": {
        "rounds": 6,
        "tags": ["s1_311"] * 6,
        "src": "round9"},
}

# Carlo's hand-built cheap-layer seeds (evaluated through the full pipeline
# like any other novel genome).
HAND_BUILT = {
    "hand_const_iota": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi32v_notr"],
        "pbox_where": "none", "pbox_perm": None,
        "const_where": "round_F", "const_fam": "iota",
        "mask": "none",
    },
    "hand_replacerot": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi32v_notr"],
        "pbox_where": "replacerot", "pbox_perm": "transpose8x4",
        "const_where": "none", "const_fam": None,
        "mask": "none",
    },
    "hand_between64": {
        "rounds": 6,
        "tags": ["s1_311", "chi32w_311", "s1_311", "chi32w_311",
                 "s1_311", "chi_notr"],
        "pbox_where": "between64", "pbox_perm": "interleave64",
        "const_where": "none", "const_fam": None,
        "mask": "none",
    },
    "hand_mask": {
        "rounds": 6,
        "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311",
                 "s1_311", "chi32v_notr"],
        "pbox_where": "none", "pbox_perm": None,
        "const_where": "none", "const_fam": None,
        "mask": "r2_A5",
    },
    "hand_prepost": {
        "rounds": 6,
        "tags": ["s1_311", "chi_311", "s1_311", "chi_311",
                 "s1_311", "chi_fm07"],
        "pbox_where": "none", "pbox_perm": None,
        "const_where": "prepost", "const_fam": "bit",
        "mask": "none",
    },
}

for _hb in HAND_BUILT.values():
    validate(_hb)


def _full_genome(entry):
    g = {
        "rounds": entry["rounds"],
        "tags": list(entry["tags"]),
        "pbox_where": "none", "pbox_perm": None,
        "const_where": "none", "const_fam": None,
        "mask": "none",
    }
    validate(g)
    return g


def mine_s0():
    """Parse S0 (delay, cells, area) from round tables, by column header."""
    out = {}
    for tbl in sorted(glob.glob(os.path.join(EXP, "round*", "ROUND*_TABLE.md"))):
        txt = open(tbl).read()
        # S0 section (most rounds) or Candidates table (round 8)
        m = (re.search(r"## S0.*?(?=\n## |\Z)", txt, re.S)
             or re.search(r"## Candidates.*?(?=\n## |\Z)", txt, re.S))
        if not m:
            continue
        lines = m.group(0).split("\n")
        cols = None
        for ln in lines:
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if re.match(r"^\|[\s\-|:]+\|$", ln.strip()):
                continue
            if cols is None:
                # header row?
                if any("candidat" in c.lower() for c in cells):
                    cols = [c.lower() for c in cells]
                continue
            if cols is None:
                continue
            try:
                i_name = next(i for i, c in enumerate(cols) if "candidat" in c)
                i_d = next(i for i, c in enumerate(cols) if "delay" in c)
                i_c = next(i for i, c in enumerate(cols) if c.strip() == "cells")
                i_a = next(i for i, c in enumerate(cols) if c.strip() == "area")
            except StopIteration:
                continue
            if len(cells) <= max(i_name, i_d, i_c, i_a):
                continue
            name = cells[i_name].strip("* ")
            dm = re.search(r"([\d.]+)\s*u", cells[i_d])
            if not re.fullmatch(r"r\d+_[A-Za-z0-9_]+", name) or not dm:
                continue
            try:
                out[name] = (float(dm.group(1)),
                             int(cells[i_c].replace(",", "").replace("*", "")),
                             int(cells[i_a].replace(",", "").replace("*", "")))
            except ValueError:
                continue
    return out


def q1_record(name):
    """(sac_z5, bic_maxcorr) or None."""
    pats = (glob.glob(os.path.join(EXP, "round*", "q1", f"q1_{name}.json"))
            + glob.glob(os.path.join(EXP, "quality", f"q1_{name}.json")))
    for q in pats:
        try:
            d = json.load(open(q))
            return d.get("sac_z5"), d.get("bic_maxcorr")
        except Exception:
            pass
    return None


def s1_passed(name):
    for p in (glob.glob(os.path.join(EXP, "round*", "s1", name, "s1_result.json"))
              + [os.path.join(FB, "results", name, "s1_result.json")]):
        try:
            d = json.load(open(p))
            if d.get("verdict") == "CAL_PASS":
                return True
        except Exception:
            pass
    return False


def s2_record(name):
    """(passed_bool, max_repeats, max_z) from S2 logs; None if no evidence."""
    cands = (glob.glob(os.path.join(EXP, "round*", f"s2_{name}.log"))
             + [os.path.join(FB, "results", name, "battery.log")]
             + glob.glob(os.path.join(EXP, "round*", f"battery_{name}.log")))
    best = None
    for p in cands:
        try:
            txt = open(p).read()
        except Exception:
            continue
        m = re.findall(r"^(PASS|KILL)[^\n]*max_repeats=(\d+)[^\n]*max\|z\|=([\d.]+)",
                       txt, re.M)
        if m:
            v, rep, z = m[-1]
            best = (v == "PASS", int(rep), float(z))
    return best


def s34_passed(name):
    p = os.path.join(FB, "results", name, "battery.log")
    if not os.path.exists(p):
        return False
    txt = open(p).read()
    if "BATTERY-PASS" in txt:
        return True
    need = ["=== S3 ", "=== S3b ", "=== S4 "]
    for s in need:
        if not re.search(re.escape(s) + r"\[" + re.escape(name) + r"\] rc=0", txt):
            return False
    return True


def mine_archive(s2_zmax=40.0):
    """All S0-S4+Q1 valid solutions: {name: (delay, cells, area, bic, genome)}.

    Validity requires: S0 numbers parsed; S1 CAL_PASS; S2 PASS with
    max_repeats<10 AND max|z|<=zmax (structural rule — excludes the
    notr5/drop4 "fast number, broken design" class); S3/S3b/S4 rc=0;
    Q1 sac_z5==0. No re-synthesis: fitness comes from the logs.
    """
    s0 = mine_s0()
    archive = {}
    for name, (delay, cells, area) in s0.items():
        if not s1_passed(name):
            continue
        s2 = s2_record(name)
        if s2 is None or not s2[0] or s2[1] >= 10 or s2[2] > s2_zmax:
            continue
        if not s34_passed(name):
            continue
        q = q1_record(name)
        if q is None or q[0] != 0:
            continue
        genome = _full_genome(GENOME_MAP[name]) if name in GENOME_MAP else None
        archive[name] = {
            "delay": delay, "cells": cells, "area": area,
            "bic": q[1], "genome": genome,
            "source": "seed-parsed",
        }
    return archive


def load_checked_model(name, src_round):
    """Load a round's checked-in numpy model function by candidate name."""
    import importlib.util
    mod_path = os.path.join(EXP, src_round, "models", f"{src_round}.py")
    # round dirs: round13/models/r13.py etc.
    cands = glob.glob(os.path.join(EXP, src_round, "models", "*.py"))
    if not cands:
        raise FileNotFoundError(src_round)
    spec = importlib.util.spec_from_file_location(f"ref_{src_round}", cands[0])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fn = getattr(m, name, None)
    if fn is None:
        # some rounds name the python function without the r-prefix quirks;
        # try attribute scan
        raise AttributeError(f"{name} not in {cands[0]}")
    return fn


def validate_seed_genomes(nvec=1024, seed=0x5EED):
    """Bit-exact check: decode_np(genome) vs checked-in model, nvec vectors.
    Returns {name: True}; raises on first mismatch (fail-closed)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2 ** 64, size=nvec, dtype=np.uint64)
    K = rng.integers(0, 2 ** 64, size=nvec, dtype=np.uint64)
    ok = {}
    for name, entry in GENOME_MAP.items():
        genome = _full_genome(entry)
        ref = load_checked_model(name, entry["src"])
        got = decode_np(genome)(V, K)
        want = ref(V, K)
        if not np.array_equal(np.asarray(got), np.asarray(want)):
            bad = np.nonzero(np.asarray(got) != np.asarray(want))[0][:3]
            raise AssertionError(
                f"seed genome mismatch for {name} at idx {bad.tolist()}")
        ok[name] = True
    return ok


if __name__ == "__main__":
    a = mine_archive()
    print(f"archive seeds: {len(a)}")
    for n, r in sorted(a.items(), key=lambda kv: kv[1]["delay"]):
        g = "genome" if r["genome"] else "archive-only"
        print(f"  {r['delay']:6.1f}u {r['cells']:6d} {r['area']:7d} "
              f"bic={r['bic']:.4f} [{g}] {n}")
    print("validating seed genomes bit-exact...")
    ok = validate_seed_genomes()
    print(f"  {len(ok)} seed genomes bit-exact OK")

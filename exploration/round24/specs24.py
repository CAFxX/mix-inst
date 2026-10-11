"""Round 24 spec selection: r23 speed-point (19,1) neighborhood sweep.

P1a: b-sweep at a=19 (b in 0..30, b=01 excluded -- r23's config), O34-validated
P1b: a in {21,29,31,33} (untested odd a near 19/27), b=01
P2:  key-schedule round-constant variants (r23 F7 follow-up), (19,1) chassis
P3:  (R,S) rotation pairs for L=x^R^S (VERDICT_SCOPE O45 re-test), (19,1) chassis
P4:  hetero S-boxes hs_aff / hs_alt on the (19,1) chassis (size plays)

Chassis for all: 4r keyed SPN x_{i+1} = L(P(S16(x_i ^ rk_i))), order LPS,
S1, no whitening. rk_i = rotl64(key,13(i+1)) ^ RC(ks,i).

Run: python3 round24/specs24.py
Writes: round24/specs24.json (the frozen spec list).
"""
import json
import os
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
R24 = os.path.join(EXP, "round24")
sys.path.insert(0, os.path.join(R24, "models"))
import r24  # noqa: E402

S1 = r24.S1
P19B01 = r24._P19B01  # (19*i+1)%64 -- r23 speed point


# ---------------- P-box validation (O34 criteria, from specs23) ----------------
def _cycles(pmap):
    seen = [False] * 64
    lens = []
    for i in range(64):
        if not seen[i]:
            j, l = i, 0
            while not seen[j]:
                seen[j] = True
                j = pmap[j]
                l += 1
            lens.append(l)
    return sorted(lens)


def _spread_ok(pmap):
    q = [0] * 64
    for i, d in enumerate(pmap):
        q[d] = i
    for perm in (pmap, q):
        for n in range(16):
            if len({perm[4 * n + b] // 4 for b in range(4)}) != 4:
                return False
    return True


def _pbox_valid(pmap):
    if sorted(pmap) != list(range(64)):
        return False
    if any(pmap[i] == i for i in range(64)):
        return False
    if min(_cycles(pmap)) < 4:
        return False
    return _spread_ok(pmap)


def _affine(a, b):
    return [(a * i + b) % 64 for i in range(64)]


# ---------------- linear rank precheck ----------------
def _rank_of(rots, include_id=True):
    return r24._gf2_rank64(lambda x: r24._lin_rots_np(x, rots, include_id))


def check_linears(specs):
    for s in specs:
        r = _rank_of(s["rots"], s.get("include_id", True))
        s["rank"] = r
        assert r == 64, (s["name"], s["rots"], r)
    print(f"linear rank precheck: {len(specs)} specs all rank 64 OK")


# ---------------- no-retest guard vs round 23 ----------------
def _canon_sbox(s):
    if s.get("sbox_rounds"):
        return ("rounds", json.dumps(s["sbox_rounds"]))
    if s.get("sbox_lanes"):
        return ("lanes", json.dumps(s["sbox_lanes"]))
    return ("hom", json.dumps(s["sbox"]))


def _canon(s):
    return (tuple(s["pbox"]), tuple(s["rots"]), s.get("ks", "golden"),
            s.get("order", "LPS"), s["nrounds"], _canon_sbox(s))


def guard_no_retest(specs):
    r23 = json.load(open(os.path.join(EXP, "round23", "specs23.json")))
    r23_canons = {_canon(s) for s in r23}
    for s in specs:
        assert _canon(s) not in r23_canons, (s["name"], "DUPLICATES an r23 exact config!")
    print(f"no-retest guard: {len(specs)} r24 specs, none matches an r23 exact config OK")


# ---------------- spec assembly ----------------
def build_specs():
    specs = []

    def add(name, desc, nrounds=4, sbox=S1, pbox=P19B01, rots=(3, 11),
            order="LPS", include_id=True, ks="golden", sbox_lanes=None,
            sbox_rounds=None):
        d = {"name": name, "desc": desc, "nrounds": nrounds,
             "sbox": list(sbox), "pbox": list(pbox) if pbox else None,
             "rots": tuple(rots), "order": order,
             "include_id": include_id, "ks": ks}
        if sbox_lanes is not None:
            d["sbox_lanes"] = [list(t) for t in sbox_lanes]
        if sbox_rounds is not None:
            d["sbox_rounds"] = sbox_rounds
        specs.append(d)

    # ---- P1a: b-sweep at a=19 ----
    # Cycle-structure lemma (verified below): for affine P-boxes, all valid
    # (a, b odd) at fixed a are translation-conjugate (b shifts by (a-1)h),
    # hence share one cycle structure. Matched-a 2-vs-4-cycle comparison is
    # impossible; the b-sweep tests the OFFSET (wiring), not cycles.
    print("P1a: cycle structures for a=19, b odd:")
    for b in range(1, 31, 2):
        pm = _affine(19, b)
        print(f"  (19,{b:02d}): cycles={_cycles(pm)} valid={_pbox_valid(pm)}")
    for b in range(0, 31):
        if b == 1:
            continue  # r23's r23_spn_mix4r_pba19b01_nw -- no retest
        pm = _affine(19, b)
        if not _pbox_valid(pm):
            print(f"  P1a: (19,{b:02d}) fails O34 validation -- skipped")
            continue
        cyc = _cycles(pm)
        add(f"r24_spn_mix4r_pba19b{b:02d}_nw",
            f"R24 P1a: 4r SPN, P-box (19,{b:02d}) (cycles {cyc}); "
            f"S1, L=lin(3,11), golden ks.",
            pbox=pm)

    # ---- P1b: untested odd a near 19/27, b=01 ----
    # (21,1) and (33,1) FAIL the O34 spread criterion (single 64-cycle but a
    # nibble's bits don't land in 4 distinct nibbles) -- recorded, not swept.
    # Valid untested set: 29 (1x64), 31 (16x4-cyc), 35 (2x32-cyc).
    for a in (29, 31, 35):
        pm = _affine(a, 1)
        assert _pbox_valid(pm), (a, "O34-invalid!")
        cyc = _cycles(pm)
        add(f"r24_spn_mix4r_pba{a:02d}b01_nw",
            f"R24 P1b: 4r SPN, P-box ({a},01) (cycles {cyc}); "
            f"S1, L=lin(3,11), golden ks.",
            pbox=pm)

    # ---- P2: key-schedule round-constant variants (r23 F7 follow-up) ----
    ks_descs = {
        "rc_smallodd": "RC'[i]=2i+1 (tiny odd constants 1,3,5,7)",
        "rc_gold16": "RC'[i]=(i+1)*0x9E37 (16-bit golden multiples)",
        "rc_rotgolden": "RC'[i]=rotl64(GOLDEN,8(i+1)) (rotated full-entropy)",
        "rc_nibrep": "RC'[i]=(i+1)*0x1111...1111 (repeated-nibble)",
        "rc_gold32": "RC'[i]=(i+1)*0x9E3779B9 (32-bit golden multiples)",
        "rc_altbit": "RC'[i]=0xAAAA.../0x5555... alternating",
    }
    for ks, kdesc in ks_descs.items():
        add(f"r24_spn_mix4r_ks_{ks[3:]}_nw",
            f"R24 P2: 4r SPN, key schedule rk_i=rotl64(key,13(i+1))^RC'[i], "
            f"{kdesc}; P=(19,1), S1, L=lin(3,11).",
            ks=ks)

    # ---- P3: (R,S) rotation pairs (O45 re-test), (19,1) chassis ----
    # r23 P2 tested (3,7),(3,13),(5,11),(7,13),(11,17),(1,7) on the (5,27)
    # chassis -- those exact configs are excluded here by the no-retest guard.
    for a, b in [(3, 17), (5, 13), (5, 17), (7, 11), (7, 17), (11, 13)]:
        add(f"r24_spn_mix4r_l{a:02d}{b:02d}_pb19_nw",
            f"R24 P3: 4r SPN, L=x^rotl(x,{a})^rotl(x,{b}); "
            f"P=(19,1), S1, golden ks.",
            rots=(a, b))

    # ---- P4: hetero S-boxes on the (19,1) chassis ----
    r23specs = {s["name"]: s for s in
                json.load(open(os.path.join(EXP, "round23", "specs23.json")))}
    hs_aff_lanes = r23specs["r23_spn_mix4r_hs_aff_nw"]["sbox_lanes"]
    hs_alt_lanes = r23specs["r23_spn_mix4r_hs_alt_nw"]["sbox_lanes"]
    add("r24_spn_mix4r_hsaff_pb19_nw",
        "R24 P4: 4r SPN, per-lane affine S1 variants (r23 hs_aff tables); "
        "P=(19,1), L=lin(3,11), golden ks.",
        sbox_lanes=hs_aff_lanes)
    add("r24_spn_mix4r_hsalt_pb19_nw",
        "R24 P4: 4r SPN, lanes alternate S1/SB1 (r23 hs_alt tables); "
        "P=(19,1), L=lin(3,11), golden ks.",
        sbox_lanes=hs_alt_lanes)

    # ---- per-layer bijectivity (SPN hard gate) ----
    def _lane_tables(s):
        if s.get("sbox_rounds"):
            sr = s["sbox_rounds"]
            out = []
            for e in sr:
                out += e if isinstance(e[0], (list, tuple)) else [e]
            return out
        if s.get("sbox_lanes"):
            return s["sbox_lanes"]
        return [s["sbox"]]

    for s in specs:
        for t in _lane_tables(s):
            assert r24._is_perm16(t), (s["name"], "sbox lane not a permutation")
        assert r24._is_perm64(s["pbox"]), (s["name"], "pbox not a permutation")
        assert s["ks"] in r24.RK_VARIANTS, (s["name"], "unknown ks")
    print(f"per-layer bijectivity: {len(specs)} specs OK")
    check_linears(specs)
    guard_no_retest(specs)

    # ---- dedupe by model equivalence (pairwise, 300 vectors) ----
    vec_rng = np.random.default_rng(0x2402)
    V = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    K = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    r24._install_specs(specs)
    sigs = {}
    for s in specs:
        fn = getattr(r24, s["name"])
        sigs[s["name"]] = fn(V, K).tobytes()
    seen = {}
    for s in specs:
        dup = [n for n, sg in seen.items() if sg == sigs[s["name"]]]
        assert not dup, (s["name"], "model-duplicate of", dup)
        seen[s["name"]] = sigs[s["name"]]
    print(f"dedupe: {len(specs)} specs pairwise-distinct OK")
    return specs


def main():
    specs = build_specs()
    js = []
    for s in specs:
        e = {"name": s["name"], "desc": s["desc"], "nrounds": s["nrounds"],
             "sbox": s["sbox"], "pbox": s["pbox"], "rots": list(s["rots"]),
             "order": s["order"], "include_id": s["include_id"],
             "ks": s["ks"], "rank": s["rank"]}
        if "sbox_lanes" in s:
            e["sbox_lanes"] = s["sbox_lanes"]
        if "sbox_rounds" in s:
            e["sbox_rounds"] = s["sbox_rounds"]
        js.append(e)
    with open(os.path.join(R24, "specs24.json"), "w") as f:
        json.dump(js, f, indent=1)
    print(f"wrote specs24.json: {len(js)} specs")
    for s in js:
        print(f"  {s['name']}")


if __name__ == "__main__":
    main()

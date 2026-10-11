"""Round 23 spec selection: P-box enumeration, S-box search, linear rank
prechecks, final SPECS assembly. Run: python3 round23/specs23.py
Writes: round23/specs23.json (the frozen spec list).
"""
import json
import os
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
R23 = os.path.join(EXP, "round23")
sys.path.insert(0, os.path.join(R23, "models"))
import r23  # noqa: E402

rng = np.random.default_rng(0x2301)

S1 = r23.S1
O34_P = r23._O34_P  # (5*i+27)%64


# ---------------- P-box validation (O34 criteria) ----------------
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


def select_pboxes(n_affine=12, n_random=2):
    """Enumerate affine (a*i+b)%64, a odd; validate; pick diverse subset."""
    cands = []
    for a in range(1, 64, 2):
        for b in range(64):
            pmap = [(a * i + b) % 64 for i in range(64)]
            if _pbox_valid(pmap):
                c = _cycles(pmap)
                cands.append({"a": a, "b": b, "pmap": pmap,
                              "single": c == [64], "ncyc": len(c)})
    print(f"affine P-boxes passing O34 criteria: {len(cands)}/2048")
    # diversity: prefer varied a, mix single-cycle and multi-cycle, b parity mix
    picked, used_a = [], set()
    # first pass: one per a (round-robin), preferring single-cycle then b-odd
    by_a = {}
    for c in cands:
        by_a.setdefault(c["a"], []).append(c)
    for a in sorted(by_a):
        by_a[a].sort(key=lambda c: (not c["single"], c["b"] % 2 == 0, c["b"]))
    ai = sorted(by_a)
    i = 0
    while len(picked) < n_affine and ai:
        a = ai[i % len(ai)]
        if by_a[a]:
            picked.append(by_a[a].pop(0))
            used_a.add(a)
        else:
            ai.remove(a)
            continue
        i += 1
    # random (non-affine) permutations
    rnd = []
    tries = 0
    while len(rnd) < n_random and tries < 200000:
        tries += 1
        p = rng.permutation(64).tolist()
        if _pbox_valid(p):
            rnd.append({"a": None, "b": None, "pmap": p,
                        "single": _cycles(p) == [64], "ncyc": len(_cycles(p))})
    print(f"random P-boxes: {len(rnd)} found in {tries} tries")
    return picked + rnd


# ---------------- S-box search ----------------
def _sbox_props(s):
    s = list(s)
    m = np.zeros((16, 16), dtype=int)
    for x in range(16):
        for dx in range(16):
            m[dx, s[x] ^ s[x ^ dx]] += 1
    du = int(m[1:, :].max())
    la = 0
    for a in range(16):
        for b in range(16):
            c = 0
            for x in range(16):
                if ((bin(a & x).count("1") + bin(b & s[x]).count("1")) & 1) == 0:
                    c += 1
            la = max(la, abs(c - 8))
    # ANF degree
    deg = 0
    for bit in range(4):
        f = [(s[x] >> bit) & 1 for x in range(16)]
        a = f[:]
        for i in range(4):
            for x in range(16):
                if x & (1 << i):
                    a[x] ^= a[x ^ (1 << i)]
        deg = max(deg, max(bin(x).count("1") for x, v in enumerate(a) if v))
    return du, la, deg


def select_sboxes(n=3):
    """Random 4-bit permutations with DU<=6, |LAT|<=8, degree 3, != S1."""
    picked, seen = [], {tuple(S1)}
    tries = 0
    while len(picked) < n and tries < 400000:
        tries += 1
        s = tuple(rng.permutation(16).tolist())
        if s in seen:
            continue
        seen.add(s)
        du, la, deg = _sbox_props(s)
        if du <= 6 and la <= 8 and deg == 3:
            picked.append({"sbox": list(s), "du": du, "lat": la, "deg": deg})
    print(f"S-boxes: {len(picked)} picked in {tries} tries")
    for p in picked:
        print(f"  {p['sbox']} DU={p['du']} LAT={p['lat']} deg={p['deg']}")
    return picked


# ---------------- linear rank precheck ----------------
def _rank_of(rots, include_id=True):
    return r23._gf2_rank64(lambda x: r23._lin_rots_np(x, rots, include_id))


def check_linears(specs):
    for s in specs:
        r = _rank_of(s["rots"], s.get("include_id", True))
        s["rank"] = r
        assert r == 64, (s["name"], s["rots"], r)
    print(f"linear rank precheck: {len(specs)} specs all rank 64 OK")


# ---------------- spec assembly ----------------
def build_specs():
    specs = []

    def add(name, desc, nrounds=4, sbox=S1, pbox=O34_P, rots=(3, 11),
            order="LPS", include_id=True):
        specs.append({"name": name, "desc": desc, "nrounds": nrounds,
                      "sbox": list(sbox), "pbox": list(pbox) if pbox else None,
                      "rots": tuple(rots), "order": order,
                      "include_id": include_id})

    # P1: 3-round SPN (single most important probe)
    add("r23_spn_mix3r_lp_nw",
        "R23 P1: 3-round keyed SPN x=L(P(S(x^rk))); P=O34, L=lin(3,11), S1. "
        "Round-count cliff probe: each round ~7u -> ~21u if it survives S2.",
        nrounds=3)

    # P2: linear (a,b) sweep at 4r — 2-term (always rank 64) + 3-term no-identity
    lin2 = [(3, 7), (3, 13), (5, 11), (7, 13), (11, 17), (1, 7)]
    for a, b in lin2:
        add(f"r23_spn_mix4r_l{a:02d}{b:02d}_nw",
            f"R23 P2: 4r SPN, L=x^rotl(x,{a})^rotl(x,{b}); S1, P=O34.",
            rots=(a, b))
    lin3 = [(3, 7, 11), (3, 11, 17), (5, 11, 23), (1, 9, 25)]
    for a, b, c in lin3:
        add(f"r23_spn_mix4r_l{a:02d}{b:02d}{c:02d}_nw",
            f"R23 P2: 4r SPN, L=rotl(x,{a})^rotl(x,{b})^rotl(x,{c}) "
            f"(no-identity 3-term, r21 3rot_ns form); S1, P=O34.",
            rots=(a, b, c), include_id=False)

    # P3: P-box sweep
    pboxes = select_pboxes(12, 2)
    for i, pb in enumerate(pboxes, 1):
        tag = (f"a{pb['a']:02d}b{pb['b']:02d}" if pb["a"] is not None
               else f"rnd{i:02d}")
        cyc = "1x64" if pb["single"] else f"{pb['ncyc']}cyc"
        add(f"r23_spn_mix4r_pb{tag}_nw",
            f"R23 P3: 4r SPN, P-box {tag} ({cyc}, validated O34 criteria); "
            f"S1, L=lin(3,11).",
            pbox=pb["pmap"])

    # P4: S-box variants
    sboxes = select_sboxes(3)
    for i, sb in enumerate(sboxes, 1):
        add(f"r23_spn_mix4r_sb{i}_nw",
            f"R23 P4: 4r SPN, S-box sb{i}={sb['sbox']} "
            f"(DU={sb['du']} LAT={sb['lat']} deg={sb['deg']}); P=O34, L=lin(3,11).",
            sbox=sb["sbox"])

    # P5: order flip
    add("r23_spn_mix4r_pl_nw",
        "R23 P5: 4r SPN with P(L(S)) order (vs baseline L(P(S))); "
        "S1, P=O34, L=lin(3,11).",
        order="PLS")

    # per-layer bijectivity proof for every spec (SPN hard gate)
    for s in specs:
        assert r23._is_perm16(s["sbox"]), (s["name"], "sbox not a permutation")
        assert s["pbox"] is None or r23._is_perm64(s["pbox"]), (s["name"], "pbox")
    check_linears(specs)

    # dedupe by model equivalence (pairwise, 300 vectors)
    vec_rng = np.random.default_rng(0x2302)
    V = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    K = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    sigs = {}
    for s in specs:
        out = r23._spn(V, K, s["nrounds"], s["sbox"], s["pbox"], s["rots"],
                       s["order"], s["include_id"])
        sigs[s["name"]] = out.tobytes()
    seen = {}
    for s in specs:
        dup = [n for n, sg in seen.items() if sg == sigs[s["name"]]]
        assert not dup, (s["name"], "model-duplicate of", dup)
        seen[s["name"]] = sigs[s["name"]]
    print(f"dedupe: {len(specs)} specs pairwise-distinct OK")
    return specs


def main():
    specs = build_specs()
    # freeze (tuples -> lists for JSON)
    js = []
    for s in specs:
        js.append({"name": s["name"], "desc": s["desc"], "nrounds": s["nrounds"],
                   "sbox": s["sbox"], "pbox": s["pbox"], "rots": list(s["rots"]),
                   "order": s["order"], "include_id": s["include_id"],
                   "rank": s["rank"]})
    with open(os.path.join(R23, "specs23.json"), "w") as f:
        json.dump(js, f, indent=1)
    print(f"wrote specs23.json: {len(js)} specs")
    for s in js:
        print(f"  {s['name']}")


if __name__ == "__main__":
    main()

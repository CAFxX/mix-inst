"""Round 23 specs P6/P8/P9: heterogeneous S-boxes, MOLS(8) P-boxes, key-schedule probe.

Appends to specs23.json (existing 29 specs frozen). Run:
    python3 round23/specs23_p689.py
Writes: appended specs23.json + round23/specs_p689.json (the new ones).
"""
import json
import os
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
R23 = os.path.join(EXP, "round23")
sys.path.insert(0, os.path.join(R23, "models"))
sys.path.insert(0, R23)
import r23  # noqa: E402
import specs23  # noqa: E402

S1 = specs23.S1
O34_P = specs23.O34_P
SB1 = [5, 6, 3, 1, 12, 2, 4, 7, 10, 11, 13, 9, 8, 0, 14, 15]


def _is_perm16(t):
    return sorted(t) == list(range(16))


def _aff_xor_variant(sbox, c_in, c_out):
    """Affine-equivalent S-box: S'(x) = S(x^c_in)^c_out. Preserves DU/LAT/deg."""
    return [sbox[x ^ c_in] ^ c_out for x in range(16)]


def build_p6():
    """Heterogeneous S-boxes (all 4r, P=O34, L=lin(3,11), order LPS)."""
    specs = []

    def add(name, desc, **kw):
        s = {"name": name, "desc": desc, "nrounds": 4,
             "sbox": list(S1), "pbox": list(O34_P), "rots": (3, 11),
             "order": "LPS", "include_id": True, "ks": "golden"}
        s.update(kw)
        # bijectivity gate: every lane table in every round is a permutation
        if s.get("sbox_rounds"):
            assert len(s["sbox_rounds"]) == 4
            for r, e in enumerate(s["sbox_rounds"]):
                tabs = e if isinstance(e[0], (list, tuple)) else [e]
                for t in tabs:
                    assert _is_perm16(t), (name, "round", r, "not a permutation")
        if s.get("sbox_lanes"):
            assert len(s["sbox_lanes"]) == 16
            for n, t in enumerate(s["sbox_lanes"]):
                assert _is_perm16(t), (name, "lane", n, "not a permutation")
        specs.append(s)

    # P6a: alternate S1/SB1 by lane
    lanes_alt = [list(S1) if i % 2 == 0 else list(SB1) for i in range(16)]
    add("r23_spn_mix4r_hs_alt_nw",
        "R23 P6a: 4r SPN, heterogeneous S-box lanes alternate S1/SB1 "
        "(even lanes S1 DU4, odd lanes SB1 DU6); P=O34, L=lin(3,11). "
        "Delay expectation capped (max-depth); tests S2 margins.",
        sbox_lanes=lanes_alt)

    # P6b: 16 affine-equivalent S1 variants (XOR-constant translations)
    lanes_aff = [_aff_xor_variant(S1, n, (n * 7) % 16) for n in range(16)]
    for t in lanes_aff:
        assert _is_perm16(t)
        du, la, deg = specs23._sbox_props(t)
        assert (du, la, deg) == (4, 8, 3), (du, la, deg)
    add("r23_spn_mix4r_hs_aff_nw",
        "R23 P6b: 4r SPN, per-lane affine-equivalent S1 variants "
        "S_n(x)=S1(x^n)^(7n%16) (all DU4/LAT8/deg3 by affine equivalence); "
        "P=O34, L=lin(3,11).",
        sbox_lanes=lanes_aff)

    # P6c: split by round halves (rounds 0-1 S1, rounds 2-3 SB1)
    add("r23_spn_mix4r_hs_rh_nw",
        "R23 P6c: 4r SPN, S-box split by round halves (rounds 0-1 S1, "
        "rounds 2-3 SB1); P=O34, L=lin(3,11).",
        sbox_rounds=[list(S1), list(S1), list(SB1), list(SB1)])

    return specs


def _gf8_mul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        a <<= 1
        if a & 8:
            a ^= 0xB
        b >>= 1
    return p & 7


def build_p8():
    """MOLS(8)-derived P-boxes via OA(64,4,8,2) column pairs (validated O34)."""
    specs = []
    # selected unique valid P-boxes (tag, pmap) from the OA search
    sel = json.load(open("/tmp/hettest/mols8_sel.json"))
    # pick 3 structurally diverse: (L1,J), (J,I), and another (L1,J) variant
    picks = []
    for e in sel:
        t = tuple(e["tag"])
        if t[2:4] == ("L1", "J") and len([p for p in picks if p[0][2:4] == ("L1", "J")]) < 2:
            picks.append((t, e["pmap"]))
        elif t[2:4] == ("J", "I") and not any(p[0][2:4] == ("J", "I") for p in picks):
            picks.append((t, e["pmap"]))
        if len(picks) == 3:
            break
    assert len(picks) == 3, f"only {len(picks)} picks"
    for i, (tag, pmap) in enumerate(picks, 1):
        assert specs23._pbox_valid(pmap), tag
        specs.append({
            "name": f"r23_spn_mix4r_mols8{chr(96+i)}_nw",
            "desc": f"R23 P8: 4r SPN, MOLS(8)-derived P-box mols8{chr(96+i)} "
                    f"OA cols {tag[2]},{tag[3]} base(a={tag[0]},b={tag[1]}) "
                    f"off=({tag[4]},{tag[5]}) (O34-validated); S1, L=lin(3,11).",
            "nrounds": 4, "sbox": list(S1), "pbox": list(pmap),
            "rots": (3, 11), "order": "LPS", "include_id": True,
            "ks": "golden",
        })
    return specs


def build_p9():
    """Key-schedule probe: no round constant (cost-model null hypothesis)."""
    return [{
        "name": "r23_spn_mix4r_ks0_nw",
        "desc": "R23 P9: 4r SPN, key schedule rk_i=rotl64(key,13*(i+1)) "
        "(no GOLDEN round constant); S1, P=O34, L=lin(3,11). Null probe: "
        "ABC folds XOR-with-const into XNOR2, expect ~0 delay delta; "
        "key-side/data-side wall balanced per critpath.",
        "nrounds": 4, "sbox": list(S1), "pbox": list(O34_P),
        "rots": (3, 11), "order": "LPS", "include_id": True,
        "ks": "norot_const",
    }]


def main():
    new_specs = build_p6() + build_p8() + build_p9()
    print(f"new specs: {len(new_specs)}")
    for s in new_specs:
        print(f"  {s['name']}")

    # linear rank check (all use (3,11) which is rank 64, but verify)
    for s in new_specs:
        r = r23._gf2_rank64(
            lambda x, _s=s: r23._lin_rots_np(x, tuple(_s["rots"]), _s["include_id"]))
        assert r == 64, (s["name"], r)
        s["rank"] = r
    print("linear rank 64 OK for all")

    # dedupe vs existing + among new (model equivalence, 300 vectors)
    existing = json.load(open(os.path.join(R23, "specs23.json")))
    vec_rng = np.random.default_rng(0x2302)
    V = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    K = vec_rng.integers(0, 2**64, size=300, dtype=np.uint64)
    r23._install_specs(existing)  # ensure installed for comparison
    sigs = {}
    for s in existing:
        fn = getattr(r23, s["name"])
        sigs[s["name"]] = fn(V, K).tobytes()
    r23._install_specs(new_specs)
    for s in new_specs:
        fn = getattr(r23, s["name"])
        sg = fn(V, K).tobytes()
        dup = [n for n, g in sigs.items() if g == sg]
        assert not dup, (s["name"], "model-duplicate of", dup)
        sigs[s["name"]] = sg
        # empirical bijectivity 5k x 2 keys
        V5 = np.random.default_rng(0x2303).integers(0, 2**64, size=5000,
                                                    dtype=np.uint64)
        for kk in (np.uint64(0x123456789ABCDEF0), np.uint64(0)):
            O = fn(V5, np.uint64(kk))
            assert len(set(O.tolist())) == 5000, (s["name"], "collision!")
    print(f"dedupe + bijectivity OK ({len(new_specs)} new)")

    # append to frozen specs23.json
    js = []
    for s in new_specs:
        e = {"name": s["name"], "desc": s["desc"], "nrounds": s["nrounds"],
             "sbox": s["sbox"], "pbox": s["pbox"], "rots": list(s["rots"]),
             "order": s["order"], "include_id": s["include_id"],
             "rank": s["rank"], "ks": s["ks"]}
        if s.get("sbox_lanes"):
            e["sbox_lanes"] = [list(t) for t in s["sbox_lanes"]]
        if s.get("sbox_rounds"):
            e["sbox_rounds"] = [
                [list(t) for t in r] if isinstance(r[0], (list, tuple))
                else list(r) for r in s["sbox_rounds"]]
        js.append(e)
    with open(os.path.join(R23, "specs_p689.json"), "w") as f:
        json.dump(js, f, indent=1)
    all_specs = existing + js
    with open(os.path.join(R23, "specs23.json"), "w") as f:
        json.dump(all_specs, f, indent=1)
    print(f"specs23.json: {len(existing)} + {len(js)} = {len(all_specs)} specs")
    print("names:", [s["name"] for s in new_specs])


if __name__ == "__main__":
    main()

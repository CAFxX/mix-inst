#!/usr/bin/env python3
"""Round 23 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in specs23.json (frozen by specs23.py).

Bit-exactness: numpy model round25/models/r25.py is the reference; generated
C/RTL verified via xcheck (C vs Python, 10k) and check_rtl (RTL vs Python, 300).

RTL policy (inherited from gen_r22): direct boolean assigns inside ONE always
@(*) block (no Verilog functions); all round logic as blocking assigns inside
the block; module-level `assign out` tap only.
"""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R23 = os.path.join(EXP, "round25")
sys.path.insert(0, os.path.join(R23, "models"))
import numpy as np  # noqa: E402
import r25  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")


# ---------------- Quine-McCluskey (4 vars), from gen_r22 ----------------
def _qm_primes(minterms):
    cubes = [(0, m) for m in sorted(minterms)]
    primes = set()
    while True:
        used = [False] * len(cubes)
        nxt = []
        seen = set()
        for i in range(len(cubes)):
            for j in range(i + 1, len(cubes)):
                m1, b1 = cubes[i]
                m2, b2 = cubes[j]
                if m1 != m2:
                    continue
                d = (b1 ^ b2) & ~m1 & 0xF
                if d and (d & (d - 1)) == 0:
                    nc = (m1 | d, (b1 & ~d) & 0xF)
                    if nc not in seen:
                        seen.add(nc)
                        nxt.append(nc)
                    used[i] = used[j] = True
        for i, c in enumerate(cubes):
            if not used[i]:
                primes.add(c)
        if not nxt:
            break
        cubes = nxt
    return primes


def _qm_cover(minterms, primes):
    uncovered = set(minterms)
    chosen = []
    primes = list(primes)
    while uncovered:
        def covers(p):
            m, b = p
            return [v for v in uncovered if (v & ~m) == (b & ~m)]
        best = max(primes, key=lambda p: len(covers(p)))
        cov = covers(best)
        assert cov, "prime cover failed"
        chosen.append(best)
        uncovered -= set(cov)
    return chosen


_dnf_cache = {}


def dnf_for_sbox_bit(sbox, bit):
    key = (tuple(sbox), bit)
    if key not in _dnf_cache:
        mt = [v for v in range(16) if (sbox[v] >> bit) & 1]
        if not mt:
            cubes = []
        elif len(mt) == 16:
            cubes = [(0xF, 0)]
        else:
            cubes = _qm_cover(mt, _qm_primes(mt))
        _dnf_cache[key] = cubes
    return _dnf_cache[key]


# ---------------- heterogeneous S-box resolution ----------------
def resolve_sboxes(spec):
    """Normalize spec S-box config to sboxes[r][lane] = 16-list (nrounds x 16).

    Spec fields: "sbox" (16-list, homogeneous default), "sbox_lanes"
    (16x16-list, per-lane for all rounds), "sbox_rounds" (list of nrounds,
    each a 16-list or 16x16-list). Every lane table must be a 4-bit
    permutation (checked at spec build); the S-layer is then bijective.
    """
    nr = spec["nrounds"]

    def as_lanes(e):
        if isinstance(e[0], (list, tuple)):
            assert len(e) == 16, "per-lane sbox needs 16 tables"
            return [list(t) for t in e]
        return [list(e)] * 16

    if spec.get("sbox_rounds"):
        sr = spec["sbox_rounds"]
        assert len(sr) == nr, "sbox_rounds length must equal nrounds"
        return [as_lanes(e) for e in sr]
    if spec.get("sbox_lanes"):
        return [as_lanes(spec["sbox_lanes"]) for _ in range(nr)]
    sb = spec["sbox"]
    if sb and isinstance(sb[0], (list, tuple)):
        return [as_lanes(sb) for _ in range(nr)]
    return [[list(sb)] * 16 for _ in range(nr)]


def _sboxes_homogeneous(sboxes):
    t0 = sboxes[0][0]
    return all(lane == t0 for rnd in sboxes for lane in rnd)


# ---------------- C emission ----------------
def build_c(spec):
    name, desc = spec["name"], spec["desc"]
    sbox, pbox = spec["sbox"], spec["pbox"]
    rots, include_id = spec["rots"], spec["include_id"]
    order, nrounds = spec["order"], spec["nrounds"]
    sboxes = resolve_sboxes(spec)
    het = not _sboxes_homogeneous(sboxes)
    # key schedule variant
    ks = spec.get("ks", "golden")
    if ks == "golden":
        rc = ", ".join(f"0x{((i + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF:016X}ULL" for i in range(4))
        rk_c = f"""static uint64_t rk64(uint64_t k, int i) {{ /* i 0-based; ks=golden */
    static const uint64_t RC[4] = {{{rc}}};
    unsigned r = (13u * (unsigned)(i + 1)) & 63u;
    return rotl64(k, r) ^ RC[i];
}}"""
    elif ks == "norot_const":
        rk_c = """static uint64_t rk64(uint64_t k, int i) { /* i 0-based; P9: no round const */
    unsigned r = (13u * (unsigned)(i + 1)) & 63u;
    return rotl64(k, r);
}"""
    elif ks in r25.RK_VARIANTS:
        rc = ", ".join(f"0x{r25.RK_VARIANTS[ks][i]:016X}ULL" for i in range(4))
        rk_c = f"""static uint64_t rk64(uint64_t k, int i) {{ /* i 0-based; ks={ks} */
    static const uint64_t RC[4] = {{{rc}}};
    unsigned r = (13u * (unsigned)(i + 1)) & 63u;
    return rotl64(k, r) ^ RC[i];
}}"""
    else:
        raise ValueError(ks)
    if het:
        sb = ("{" + ",".join(
            "{" + ",".join("{" + ",".join(str(v) for v in lane) + "}"
                           for lane in rnd) + "}"
            for rnd in sboxes) + "}")
        sboxt_decl = (f"static const uint8_t SBOXT[{nrounds}][16][16] = {sb};")
        sbox_fn = """static uint64_t sbox64(uint64_t x, int r) {
    uint64_t res = 0;
    for (int i = 0; i < 16; i++)
        res |= (uint64_t)SBOXT[r][i][(x >> (4*i)) & 0xFu] << (4*i);
    return res;
}"""
        sbox_call = "sbox64(x ^ rk64(key, i), i)"
    else:
        sb = "{" + ",".join(str(v) for v in sbox) + "}"
        sboxt_decl = f"static const uint8_t SBOXT[16] = {sb};"
        sbox_fn = """static uint64_t sbox64(uint64_t x) {
    uint64_t r = 0;
    for (int i = 0; i < 16; i++)
        r |= (uint64_t)SBOXT[(x >> (4*i)) & 0xFu] << (4*i);
    return r;
}"""
        sbox_call = "sbox64(x ^ rk64(key, i))"
    # linear function
    if include_id:
        terms = ["x"] + [f"rotl64(x, {r})" for r in rots]
    else:
        terms = [f"rotl64(x, {r})" for r in rots]
    lin_expr = " ^ ".join(terms)
    # pbox wiring
    pb_lines = "\n".join(
        f"        y |= ((x >> {i}) & 1u) << {d};" for i, d in enumerate(pbox))
    if order == "LPS":
        rnd = "x = lin_spec(pbox64(t));"
    else:
        rnd = "x = pbox64(lin_spec(t));"
    return f"""/* {name}: {desc}
 * GENERATED by round25/gen_r25.py -- do not edit by hand.
 * Bit-exact vs Python model round25/models/r25.py ({name}). */
#include <stdint.h>

{sboxt_decl}

static uint64_t rotl64(uint64_t x, unsigned r) {{
    r &= 63u;
    return r ? (x << r) | (x >> (64u - r)) : x;
}}
{rk_c}
{sbox_fn}
static uint64_t pbox64(uint64_t x) {{
    uint64_t y = 0;
{pb_lines}
    return y;
}}
static uint64_t lin_spec(uint64_t x) {{
    return {lin_expr};
}}
uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint64_t x = val;
    for (int i = 0; i < {nrounds}; i++) {{
        uint64_t t = {sbox_call};
        {rnd}
    }}
    return x;
}}
"""


# ---------------- Verilog emission ----------------
def _v_sbox16_stmts(sbox, inp, outp, lane_tables=None):
    """Emit S-box DNF assigns. sbox: 16-list (all lanes) or lane_tables:
    list of 16 16-lists (lane n uses lane_tables[n])."""
    lines = []
    for n in range(16):
        tab = lane_tables[n] if lane_tables is not None else sbox
        for bit in range(4):
            cubes = dnf_for_sbox_bit(tab, bit)
            if not cubes:
                lines.append(f"        {outp}[{4*n+bit}] = 1'b0;")
                continue
            terms = []
            for m, b in cubes:
                lits = []
                for k in range(4):
                    if not ((m >> k) & 1):
                        lits.append(f"{'' if (b >> k) & 1 else '~'}{inp}[{4*n+k}]")
                terms.append("(" + " & ".join(lits) + ")" if lits else "1'b1")
            lines.append(f"        {outp}[{4*n+bit}] = " + " | ".join(terms) + ";")
    return lines


def _v_pbox_stmts(pmap, inp, outp):
    return [f"        {outp}[{d}] = {inp}[{i}];" for i, d in enumerate(pmap)]


def _v_rotl_concat(inp, r):
    if r == 0:
        return inp
    return f"{{{inp}[{63-r}:0], {inp}[63:{64-r}]}}"


def _v_lin_stmts(rots, include_id, inp, outp):
    terms = ([inp] if include_id else []) + [_v_rotl_concat(inp, r) for r in rots]
    return [f"        {outp} = " + " ^ ".join(terms) + ";"]


V_HDR = """// {name}: {desc}
// GENERATED by round25/gen_r25.py -- do not edit by hand.
// Bit-exact vs Python model round25/models/r25.py ({name}).
// Direct boolean assigns inside one always @(*) block (no functions).
module {name}(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);

reg [63:0] x, t, s, p;
reg [63:0] rkv;
always @(*) begin
"""


def _v_roundkey_stmts(i, ks="golden"):
    r = (13 * (i + 1)) % 64
    if ks == "golden":
        rc = f"{((i + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF:016X}"
        return [f"        rkv = ((key << {r}) | (key >> {64-r})) ^ 64'h{rc};  // ks=golden"]
    elif ks == "norot_const":
        return [f"        rkv = ((key << {r}) | (key >> {64-r}));"]
    elif ks in r25.RK_VARIANTS:
        rc = f"{r25.RK_VARIANTS[ks][i]:016X}"
        return [f"        rkv = ((key << {r}) | (key >> {64-r})) ^ 64'h{rc};  // ks={ks}"]
    else:
        raise ValueError(ks)


def build_verilog(spec):
    name, desc = spec["name"], spec["desc"]
    sboxes = resolve_sboxes(spec)
    ks = spec.get("ks", "golden")
    L = [V_HDR.format(name=name, desc=desc)]
    L.append("    x = val;")
    for i in range(spec["nrounds"]):
        L += _v_roundkey_stmts(i, ks)
        L.append("    t = x ^ rkv;")
        L += _v_sbox16_stmts(None, "t", "s", lane_tables=sboxes[i])
        if spec["order"] == "LPS":
            L += _v_pbox_stmts(spec["pbox"], "s", "p")
            L += _v_lin_stmts(spec["rots"], spec["include_id"], "p", "x")
        else:
            L += _v_lin_stmts(spec["rots"], spec["include_id"], "s", "p")
            L += _v_pbox_stmts(spec["pbox"], "p", "x")
    L.append("end\n")
    L.append("assign out = x;\n")
    L.append("endmodule\n")
    return "\n".join(L)


def build_model_py(spec):
    name = spec["name"]
    return ('"""Python model wrapper for %s (fast_battery candidate interface)."""\n'
            'import sys, json\nimport numpy as np\n'
            'sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round25/models")\n'
            'sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round25")\n'
            'import r25\n'
            '_all = json.load(open("/home/hatch/workspace/mix/exploration/round25/specs25.json"))\n'
            '_spec = next(s for s in _all if s["name"] == "%s")\n'
            '_spec["rots"] = tuple(_spec["rots"])\n'
            'r25._install_specs([_spec])\n'
            'from r25 import %s as _np\n\n'
            'def mix(v, k):\n    return int(_np(np.uint64(v), np.uint64(k)))\n\n'
            'mix_np = _np\n' % (name, name, name))


# ---------------- self-tests ----------------
def _selftest_all(specs):
    # 1. numpy baseline == r22c
    r25._selftest_r23()
    # 2. per-spec: numpy model vs direct reimplementation sanity (bijectivity)
    rng = np.random.default_rng(0x2303)
    V = rng.integers(0, 2**64, size=5000, dtype=np.uint64)
    K0 = np.uint64(0x123456789ABCDEF0)
    K1 = np.uint64(0)
    r25._install_specs(specs)
    for s in specs:
        fn = getattr(r25, s["name"])
        for kk in (K0, K1):
            O = fn(V, np.uint64(kk))
            assert len(set(O.tolist())) == len(V), (s["name"], "collision!")
    print(f"bijectivity: {len(specs)} specs x 2 keys x 5k samples collision-free OK")
    # 3. DNF emission valid for every spec's sbox tables (all rounds/lanes)
    import re
    for s in specs:
        sboxes = resolve_sboxes(s)
        seen = set()
        for rnd in sboxes:
            for lane_tab in rnd:
                t = tuple(lane_tab)
                if t in seen:
                    continue
                seen.add(t)
                stmts = _v_sbox16_stmts(None, "R", "u",
                                       lane_tables=[lane_tab] * 16)
                assert len(stmts) == 64
                for n in range(16):
                    for bit in range(4):
                        stmt = stmts[n * 4 + bit]
                        m = re.match(r"\s*u\[(\d+)\] = (.*);", stmt)
                        assert m and int(m.group(1)) == 4 * n + bit
                        expr = m.group(2)
                        for v in range(16):
                            env = {f"R[{4*n+k}]": (v >> k) & 1 for k in range(4)}
                            py = expr
                            for var, val in sorted(env.items(), key=lambda kv: -len(kv[0])):
                                py = py.replace("~" + var, f"(1-{val})").replace(var, str(val))
                            py = py.replace("&", " and ").replace("|", " or ")
                            got = eval(py)  # noqa: S307 - test-only
                            want = (lane_tab[v] >> bit) & 1
                            assert bool(got) == bool(want), (s["name"], n, bit, v)
    print(f"DNF emission: {len(specs)} specs x distinct tables x 64 bits OK")
    # 4. Verilog lin/pbox emission vs numpy for every spec
    for s in specs:
        # pbox wiring map
        got = {}
        for st in _v_pbox_stmts(s["pbox"], "s", "p"):
            m = re.match(r"\s*p\[(\d+)\] = s\[(\d+)\];", st)
            assert m
            got[int(m.group(2))] = int(m.group(1))
        assert [got[i] for i in range(64)] == s["pbox"], (s["name"], "pbox emission")
        # lin: emulate concatenation form in python
        xv = 0x5CDB5A824B383A06

        def rotl(v, r):
            return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v
        terms = ([xv] if s["include_id"] else []) + [rotl(xv, r) for r in s["rots"]]
        want = 0
        for t in terms:
            want ^= t
        stmts = _v_lin_stmts(s["rots"], s["include_id"], "p", "x")
        assert len(stmts) == 1 and stmts[0].count("{") == stmts[0].count("}"), s["name"]
        gotv = int(r25._lin_rots_np(np.uint64(xv), tuple(s["rots"]), s["include_id"]))
        assert gotv == want, (s["name"], "lin emission")
    print(f"lin/pbox emission: {len(specs)} specs OK")


def main():
    specs = json.load(open(os.path.join(R23, "specs25.json")))
    _selftest_all(specs)
    for s in specs:
        name = s["name"]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(build_c(s))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(build_verilog(s))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(build_model_py(s))
        fn = getattr(r25, name)
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k),
                            "out": hex(int(fn(np.uint64(v), np.uint64(k))))})
        meta = {"name": name, "description": s["desc"], "composition": s["desc"],
                "rtl_top": name,
                "screen_keys": ["0x123456789abcdef0", "0x0"],
                "practrand_keys": ["0x123456789abcdef0", "0x0"],
                "goldens": goldens}
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print("generated", name)
    print("gen_r23 complete")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Artifact emitter for GA genomes -> fast_battery/candidates/<name>/.

Emits impl.c, rtl.v, model.py, meta.json, genome.json.

Two paths:
- BASE genomes (no P-box/XOR-const/mask genes active, all tags in gen_r20's
  C_F_EXPR): delegates byte-identically to round20/gen_r20.py.
- EXTENDED genomes: custom emitter implementing the exact pipeline of
  gamodels.decode_np in C and Verilog. Cross-checked by xcheck (C-vs-Python,
  10k vectors) and S0's mapped-netlist equivalence check.

Pipeline (identical in numpy/C/RTL):
  x = val ^ C_PRE64                                   [const prepost]
  (L,R) = split(x)
  for i in 1..n:
    Rc = R ^ C32(fam,i)                               [const round_F]
    a  = P32(Rc)                                      [pbox inF32]
    (t, keyin) = F_pipeline(tag, a, rk)               # below
    nR = L ^ t            if keyin-tag (rk baked into t)
         L ^ t ^ rk       otherwise
    (L,R) = (R, nR)
    if pbox between64 and i<n: (L,R) = split64(P64(join64(L,R)))
  out = join64(R,L) ^ C_POST64                        [const prepost]

F_pipeline(tag, a, rk), with optional mask m(x)=x^((x>>r)&PAT) on the
nonlinear output and optional replacerot linear:
  lin2(fam,(la,lb)): u=NL(a); v=mask(u); t = v^rotl(v,la)^P32(v)  [replacerot]
                                              or v^rotl(v,la)^rotl(v,lb)
                     F = t ^ rk
  notr(fam):         u=NL(a); v=mask(u); t = v; F = t ^ rk
  keyin:             u=chi32(a^rk); v=mask(u); t = v            (rk baked)
  fm_m:              c=chi32(a); v=mask(c); y=v^rk; t = y^rotl(y,m)
  fm311:             c=chi32(a); v=mask(c); t = rotl(c,3)^rotl(c,11)^rk
"""
import json
import os
import re
import sys

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/round20")
sys.path.insert(0, EXP + "/ga")
import gen_r20 as G  # noqa: E402
from genome import (PERM_TABLES, P64_PERMS, P32_PERMS, const32,  # noqa: E402
                    C_PRE64, C_POST64, MASK_PAT, TAG_POOL)
from gamodels import _TAGKIND, _NL  # noqa: E402  (tag dispatch, checked)

FB = os.path.join(EXP, "fast_battery", "candidates")

BASE_TAGS = set(G.C_F_EXPR.keys())


def is_base(genome):
    # BASE path delegates byte-identically to round20/gen_r20.py, whose
    # C_MAIN_TMPL hardcodes 6 rounds. Non-6-round genomes MUST go through the
    # custom emitter (round-parameterized); routing a 7-rounder through BASE
    # emits a 6-round main loop and fails xcheck 10000/10000 (seed_rnd16,
    # 2026-10-03).
    return (genome.get("rounds") == 6
            and genome.get("pbox_where", "none") == "none"
            and genome.get("const_where", "none") == "none"
            and genome.get("mask", "none") == "none"
            and all(t in BASE_TAGS for t in genome["tags"]))


def genome_desc(genome):
    parts = [f"{genome['rounds']}r Feistel",
             "F=[" + ",".join(genome["tags"]) + "]"]
    if genome.get("pbox_where", "none") != "none":
        parts.append(f"pbox:{genome['pbox_where']}/{genome['pbox_perm']}")
    if genome.get("const_where", "none") != "none":
        parts.append(f"const:{genome['const_where']}/{genome.get('const_fam')}")
    if genome.get("mask", "none") != "none":
        parts.append(f"mask:{genome['mask']}")
    parts.append("no whitening")
    return "GA " + " ".join(parts)


# ------------------------------------------------------------ C

def _c_pbox_fns(perm_names):
    """Bit-loop P-box functions (obviously correct; xcheck-gated)."""
    out = []
    for name in sorted(set(perm_names)):
        table = PERM_TABLES[name]
        w = 64 if "64" in name else 32
        T = "uint64_t" if w == 64 else "uint32_t"
        lines = [f"static {T} pbox_{name}({T} x) {{",
                 f"    {T} r = 0;"]
        for i, s in enumerate(table):
            lines.append(f"    r |= (({T})((x >> {s}) & 1u)) << {i};")
        lines.append("    return r;\n}")
        out.append("\n".join(lines))
    return "\n".join(out)


_C_NL = {
    "s1": "sbox32({x}, S1T)",
    "chi": "chi32({x})",
    "chi32v": "chi32v({x})",
    "chi32w": "chi32w({x})",
    "ps": "((chi16(({x}) >> 16) << 16) | sbox16(({x}) & 0xFFFFu, S1T))",
}

_C_FM_EXPR = {
    "chi_fm03": 3, "chi_fm07": 7, "chi_fm11": 11, "chi_fm16": 16,
}


def _c_F_lines(tag, genome, src):
    """C lines computing t (pre-key F value); sets keyin=True if rk baked in."""
    kind, pay = _TAGKIND[tag]
    mask = genome.get("mask", "none")
    replacerot = genome.get("pbox_where") == "replacerot"
    p32 = genome.get("pbox_perm")
    L = []
    keyin = False
    if kind == "lin2":
        fam, (la, lb) = pay
        L.append(f"        u = {_C_NL[fam].format(x=src)};")
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"        u = u ^ ((u >> {r}) & 0x{pat:08X}u);")
        if replacerot:
            L.append(f"        p = pbox_{p32}(u);")
            L.append(f"        t = u ^ rotl32(u, {la}) ^ p;")
        else:
            L.append(f"        t = u ^ rotl32(u, {la}) ^ rotl32(u, {lb});")
    elif kind == "notr":
        L.append(f"        u = {_C_NL[pay].format(x=src)};")
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"        u = u ^ ((u >> {r}) & 0x{pat:08X}u);")
        L.append("        t = u;")
    elif kind == "keyin":
        L.append(f"        u = chi32(({src}) ^ rk);")
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"        u = u ^ ((u >> {r}) & 0x{pat:08X}u);")
        L.append("        t = u;")
        keyin = True
    elif kind == "fm":
        m = pay
        L.append(f"        u = chi32({src});")
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"        u = u ^ ((u >> {r}) & 0x{pat:08X}u);")
        L.append("        t = u ^ rk;")
        L.append(f"        t = t ^ rotl32(t, {m});")
        keyin = True
    elif kind == "fm311":
        L.append(f"        u = chi32({src});")
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"        u = u ^ ((u >> {r}) & 0x{pat:08X}u);")
        L.append("        t = rotl32(u, 3) ^ rotl32(u, 11) ^ rk;")
        keyin = True
    else:
        raise ValueError(tag)
    return L, keyin


def _parse_mask_c(mask):
    r_s, p_s = mask.split("_")
    return int(r_s[1:]), MASK_PAT[p_s]


def gen_impl_custom(name, genome, desc):
    n = genome["rounds"]
    pbox_where = genome.get("pbox_where", "none")
    const_where = genome.get("const_where", "none")
    const_fam = genome.get("const_fam")

    perms = set()
    if pbox_where == "between64":
        perms.add(genome["pbox_perm"])
    elif pbox_where in ("inF32", "replacerot"):
        perms.add(genome["pbox_perm"])

    body = G.C_COMMON.format(name=name, desc=desc)
    body += _c_pbox_fns(perms)
    body += ("static uint32_t masknl_c(uint32_t x, int r, uint32_t mp) { "
             "return x ^ ((x >> r) & mp); }\n\n")
    body += f"uint64_t mix_hash(uint64_t val, uint64_t key) {{\n"
    if const_where == "prepost":
        body += f"    val ^= 0x{C_PRE64:016X}ULL;\n"
    body += ("    uint32_t L = (uint32_t)(val >> 32);\n"
             "    uint32_t R = (uint32_t)val;\n"
             "    uint32_t t, u, m, p, fx, Rc, rk;\n"
             f"    for (int i = 1; i <= {n}; i++) {{\n")
    if const_where == "round_F":
        # per-round literal constants
        consts = ", ".join(f"0x{const32(const_fam, i):08X}u" for i in range(1, n + 1))
        body += (f"        static const uint32_t RC[{n}] = {{{consts}}};\n"
                 "        Rc = R ^ RC[i - 1];\n")
    else:
        body += "        Rc = R;\n"
    body += "        rk = RK32(key, i);\n"
    if pbox_where == "inF32":
        body += f"        fx = pbox_{genome['pbox_perm']}(Rc);\n"
        src = "fx"
    else:
        src = "Rc"
    # per-round if-chain
    keyin_rounds = []
    for ri, tag in enumerate(genome["tags"], start=1):
        kw = "if" if ri == 1 else "else if"
        lines, keyin = _c_F_lines(tag, genome, src)
        if keyin:
            keyin_rounds.append(ri)
        body += f"        {kw} (i == {ri}) {{\n" + "\n".join(lines) + "\n        }\n"
    if keyin_rounds:
        cond = " || ".join(f"i == {ri}" for ri in keyin_rounds)
        body += (f"        uint32_t nR = ({cond}) ? (L ^ t) : (L ^ t ^ rk);\n")
    else:
        body += "        uint32_t nR = L ^ t ^ rk;\n"
    body += ("        L = R; R = nR;\n")
    if pbox_where == "between64":
        body += (f"        if (i < {n}) {{\n"
                 f"            uint64_t j64 = ((uint64_t)L << 32) | R;\n"
                 f"            j64 = pbox_{genome['pbox_perm']}(j64);\n"
                 "            L = (uint32_t)(j64 >> 32); R = (uint32_t)j64;\n"
                 "        }\n")
    body += "    }\n"
    body += "    uint64_t out = ((uint64_t)R << 32) | L;\n"
    if const_where == "prepost":
        body += f"    out ^= 0x{C_POST64:016X}ULL;\n"
    body += "    return out;\n}\n"
    return body


# ------------------------------------------------------------ RTL

def _v_pbox_assigns(dst, src, perm_name):
    table = PERM_TABLES[perm_name]
    return "\n".join(
        f"            {dst}[{i}] = {src}[{s}];" for i, s in enumerate(table))


def _ps_block_local():
    """parsplit t = chi16(R[31:16]) || S1(R[15:0]), chi offsets (1,2).

    Local port of gen_r20._ps_block: that function calls chi16_assigns,
    which is NOT defined in gen_r20's namespace (latent bug — round 20 never
    emitted ps tags so it never fired; the GA hit it on seed_rnd17,
    2026-10-03). Offsets/semantics match gamodels._nl_ps and gen_r19.
    Writes t[..] so _v_nonlin's t[ -> dst[ retarget keeps working.
    """
    lines = []
    for i in range(16):
        lines.append(
            f"            t[{16 + i}] = R[{16 + i}] ^ "
            f"(~R[{16 + (i + 1) % 16}] & R[{16 + (i + 2) % 16}]);")
    lines.append(G.sbox_dnf_assigns(G.S1, "t", "R", 4,
                                   dst_base=0, src_base=0))
    return "\n".join(lines)


def _v_nonlin(dst, fam, src):
    if fam == "s1":
        return G.sbox_dnf_assigns(G.S1, dst, src, 8)
    if fam == "chi":
        return G.chi32_assigns(dst, src)
    if fam == "chi32v":
        return G.chi32v_assigns(dst, src)
    if fam == "chi32w":
        return G.chi32w_assigns(dst, src)
    if fam == "ps":
        # _ps_block writes t[..]; retarget to dst
        return re.sub(r"\bt\[", dst + "[", _ps_block_local())
    raise ValueError(fam)


def _v_F_lines(tag, genome, src):
    """Verilog lines computing t (pre-key); returns (lines, keyin)."""
    kind, pay = _TAGKIND[tag]
    mask = genome.get("mask", "none")
    replacerot = genome.get("pbox_where") == "replacerot"
    p32 = genome.get("pbox_perm")
    L = []
    keyin = False

    def maybe_mask(dst="u"):
        if mask != "none":
            r, pat = _parse_mask_c(mask)
            L.append(f"            {dst} = {dst} ^ (({dst} >> {r}) & 32'h{pat:08X});")

    if kind == "lin2":
        fam, (la, lb) = pay
        L.append(_v_nonlin("u", fam, src))
        maybe_mask("u")  # mask applies in place on u
        if replacerot:
            L.append(_v_pbox_assigns("p", "u", p32))
            L.append(f"            t = u ^ {{u[{31 - la}:0], u[31:{32 - la}]}} ^ p;")
        else:
            L.append(f"            t = u ^ {{u[{31 - la}:0], u[31:{32 - la}]}}"
                     f" ^ {{u[{31 - lb}:0], u[31:{32 - lb}]}};")
    elif kind == "notr":
        L.append(_v_nonlin("u", pay, src))
        maybe_mask("u")
        L.append("            t = u;")
    elif kind == "keyin":
        L.append(f"            u = {src} ^ rk32;")
        L.append(G.chi32_assigns("t", "u"))
        maybe_mask("t")
        keyin = True
    elif kind == "fm":
        m = pay
        L.append(G.chi32_assigns("u", src))
        maybe_mask("u")
        L.append("            t = u ^ rk32;")
        L.append(f"            t = t ^ {{t[{31 - m}:0], t[31:{32 - m}]}};")
        keyin = True
    elif kind == "fm311":
        L.append(G.chi32_assigns("u", src))
        maybe_mask("u")
        L.append("            t = {u[28:0], u[31:29]} ^ {u[20:0], u[31:21]} ^ rk32;")
        keyin = True
    else:
        raise ValueError(tag)
    return "\n".join(L), keyin


def gen_rtl_custom(name, genome, desc):
    n = genome["rounds"]
    pbox_where = genome.get("pbox_where", "none")
    const_where = genome.get("const_where", "none")
    const_fam = genome.get("const_fam")

    hdr = G.V_HDR.format(name=name, desc=desc)
    decl = """
reg [31:0] L, R;
reg [31:0] Lt, Rt;
reg [31:0] t, u, m, p, fx, Rc;
reg [31:0] rk32;
reg [63:0] rkv;
reg [63:0] pq, npq;
integer i, r;
"""
    body = []
    body.append("always @(*) begin")
    if const_where == "prepost":
        pre_hi = (C_PRE64 >> 32) & 0xFFFFFFFF
        pre_lo = C_PRE64 & 0xFFFFFFFF
        body.append(f"    L = val[63:32] ^ 32'h{pre_hi:08X};")
        body.append(f"    R = val[31:0] ^ 32'h{pre_lo:08X};")
    else:
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")
    body.append(f"    for (i = 0; i < {n}; i = i + 1) begin")
    body.append("        " + G.V_RK_STD.replace("\n", "\n        "))
    if const_where == "round_F":
        sel = " else ".join(
            f"if (i == {ri - 1}) Rc = R ^ 32'h{const32(const_fam, ri):08X};"
            for ri in range(1, n + 1))
        body.append(f"        {sel}")
    else:
        body.append("        Rc = R;")
    if pbox_where == "inF32":
        for ln in _v_pbox_assigns("fx", "Rc", genome["pbox_perm"]).split("\n"):
            body.append(ln)
        src = "fx"
    else:
        src = "Rc"
    keyin_rounds = []
    for ri, tag in enumerate(genome["tags"]):
        kw = "if" if ri == 0 else "else if"
        lines, keyin = _v_F_lines(tag, genome, src)
        if keyin:
            keyin_rounds.append(ri)
        body.append(f"        {kw} (i == {ri}) begin")
        for ln in lines.split("\n"):
            body.append(ln)
        body.append("        end")
    body.append("        Lt = R;")
    if keyin_rounds:
        cond = " || ".join(f"i == {ri}" for ri in keyin_rounds)
        body.append(f"        if ({cond}) Rt = L ^ t;")
        body.append("        else Rt = L ^ t ^ rk32;")
    else:
        body.append("        Rt = L ^ t ^ rk32;")
    body.append("        L = Lt;")
    body.append("        R = Rt;")
    if pbox_where == "between64":
        body.append(f"        if (i < {n - 1}) begin")
        body.append("            pq = {L, R};")
        for ln in _v_pbox_assigns("npq", "pq", genome["pbox_perm"]).split("\n"):
            body.append(ln)
        body.append("            L = npq[63:32];")
        body.append("            R = npq[31:0];")
        body.append("        end")
    body.append("    end")
    body.append("end")
    body.append("")
    if const_where == "prepost":
        post = C_POST64
        body.append(f"assign out = ({{R, L}} ^ 64'h{post:016X});")
    else:
        body.append("assign out = {R, L};")
    body.append("")
    body.append("endmodule")
    return hdr + decl + "\n".join(body) + "\n"


# ------------------------------------------------------------ model.py / meta.json

MODEL_PY = '''"""Python model wrapper for {name} (GA candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys, os, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/ga")
from gamodels import decode_np
_gpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genome.json")
_genome = json.load(open(_gpath))
_np_fn = decode_np(_genome)

def mix(v, k):
    return int(_np_fn(np.uint64(v), np.uint64(k)))

mix_np = _np_fn
'''

META_JSON = """{{
 "name": "{name}",
 "description": "{desc}",
 "composition": "{desc}",
 "rtl_top": "{name}",
 "screen_keys": [
  "0x123456789abcdef0",
  "0x0"
 ],
 "practrand_keys": [
  "0x123456789abcdef0",
  "0x0"
 ],
 "goldens": [
  {{
   "val": "0x0",
   "key": "0x123456789abcdef0",
   "out": "{golden0}"
  }},
  {{
   "val": "0x123456789abcdef0",
   "key": "0x0",
   "out": "{golden1}"
  }}
 ]
}}"""


def emit_candidate(name, genome, outdir=None):
    """Write impl.c, rtl.v, model.py, meta.json, genome.json. Returns dir."""
    from genome import validate
    validate(genome)
    d = outdir or os.path.join(FB, name)
    os.makedirs(d, exist_ok=True)
    desc = genome_desc(genome)
    if is_base(genome):
        impl = G.gen_impl(name, genome["tags"], desc)
        rtl = G.gen_rtl(name, genome["tags"], desc)
    else:
        impl = gen_impl_custom(name, genome, desc)
        rtl = gen_rtl_custom(name, genome, desc)
    with open(os.path.join(d, "impl.c"), "w") as f:
        f.write(impl)
    with open(os.path.join(d, "rtl.v"), "w") as f:
        f.write(rtl)
    with open(os.path.join(d, "genome.json"), "w") as f:
        json.dump(genome, f, indent=1, sort_keys=True)
    with open(os.path.join(d, "model.py"), "w") as f:
        f.write(MODEL_PY.format(name=name))
    # goldens from the numpy decoder (single source of truth)
    sys.path.insert(0, os.path.join(EXP, "ga"))
    from gamodels import decode_np, bijection_spotcheck
    fn = decode_np(genome)
    bijection_spotcheck(fn)  # fail-closed: degenerate designs die here
    import numpy as _np
    g0 = f"0x{int(fn(_np.uint64(0), _np.uint64(0x123456789ABCDEF0))):016x}"
    g1 = f"0x{int(fn(_np.uint64(0x123456789ABCDEF0), _np.uint64(0))):016x}"
    with open(os.path.join(d, "meta.json"), "w") as f:
        f.write(META_JSON.format(name=name, desc=desc, golden0=g0, golden1=g1))
    return d

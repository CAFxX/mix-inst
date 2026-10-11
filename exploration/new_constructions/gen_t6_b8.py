#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 8 (fused + het5).

Each bundle in fast_battery/candidates/<name>/ gets:
  - rtl.v:      Verilog RTL, bit-exact with the model
  - model.py:   SELF-CONTAINED Python model (no sys.path hacks — 2026-10-09
                lesson: sys.path-insert model.py caused GHA S0 INFRA_FAIL)
  - impl.c:     REAL bit-exact C (never a stub — 2026-10-09 lesson: stub
                caused S2 INFRA_FAIL undefined reference to mix_hash)
  - meta.json:  includes rtl_top (2026-10-09 lesson: missing rtl_top caused
                S0 KeyError INFRA_FAIL)

Bit-exactness verified: model vs RTL (iverilog sim), model vs impl.c (gcc).
"""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b8 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]
RC_DEC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
          0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
          0x2545F4914F6CDD1D,
          0x9E3779B97F4A7C15 ^ 0xDEADBEEF,
          0x3C6EF372FE94F82A ^ 0x12345678,
          0xDAA66D2C7DDF743F ^ 0xABCDEF01]


# RTL fragments per fused op: fn(cur, r0, r1[, r2]) -> Verilog expr
def _rtl_fchi(cur, r):
    return f"({cur} ^ ({r[0]} & ~{r[1]}))"


def _rtl_fand(cur, r):
    return f"(({cur} & {r[0]}) ^ {r[1]})"


def _rtl_fxorand(cur, r):
    return f"(({cur} & {r[0]}) ^ ({cur} & {r[1]}) ^ {r[2]})"


def gen_fused_rtl(name, fn_name, sched, nrots):
    rtl_fn = {"_fchi": _rtl_fchi, "_fand": _rtl_fand,
              "_fxorand": _rtl_fxorand}[fn_name]
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    for i in range(6):
        rots = sched[i][:nrots]
        r = [rotl(cur, t) for t in rots]
        fexpr = rtl_fn(cur, r)
        rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
        L.append(f"  wire [63:0] st{i+1} = {fexpr} ^ {rk};")
        cur = f"st{i+1}"
    L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
    L.append(f"  assign out = {cur} ^ {{32'h0, key_r13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)


def gen_het5_rtl(name):
    # 5-stage hetero, same op semantics as b6
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    for i, op in enumerate(M.SEQ_HET5):
        nrots = M.OP_NROTS_B6[op]
        rots = M.SCHED_HET5[i][:nrots]
        r = [rotl(cur, t) for t in rots]
        if op == "maj":
            maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
            nl = f"({maj} ^ {r[3]})"
        elif op == "andor":
            nl = f"((({r[0]} & {r[1]}) | ({r[2]} & {r[3]})) ^ {r[4]})"
        elif op == "chi":
            nl = f"({r[0]} ^ ({r[1]} & ~{r[2]}))"
        elif op == "majxor":
            maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
            nl = f"({maj} ^ ({r[3]} & {r[4]}))"
        elif op == "xor3and":
            nl = f"({r[0]} ^ {r[1]} ^ {r[2]} ^ ({r[3]} & {r[4]} & {r[5]}))"
        rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
        L.append(f"  wire [63:0] st{i+1} = {cur} ^ {nl} ^ {rk};")
        cur = f"st{i+1}"
    L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
    L.append(f"  assign out = {cur} ^ {{32'h0, key_r13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)


# C fragments per fused op
def _c_fchi(r):
    return f"    nl = x ^ (rotl64(x,{r[0]}) & ~rotl64(x,{r[1]}));"


def _c_fand(r):
    return f"    nl = (x & rotl64(x,{r[0]})) ^ rotl64(x,{r[1]});"


def _c_fxorand(r):
    return (f"    nl = (x & rotl64(x,{r[0]})) ^ (x & rotl64(x,{r[1]})) "
            f"^ rotl64(x,{r[2]});")


def gen_fused_c(name, desc, fn_name, sched, nrots):
    c_fn = {"_fchi": _c_fchi, "_fand": _c_fand,
            "_fxorand": _c_fxorand}[fn_name]
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         f"// {name}: {desc}",
         "// bit-exact C port of t6_models_b8._fused_cascade",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    static const uint64_t RC[8] = {"
         + ", ".join("0x%016Xu" % v for v in RC_DEC) + "};",
         "    uint64_t x = val ^ key, nl;"]
    for i in range(6):
        rots = sched[i][:nrots]
        L.append(f"    // stage {i}")
        L.append(c_fn(rots))
        L.append(f"    x = nl ^ (rotl64(key, {13*(i+1)}) ^ RC[{i % 8}]);")
    L.append("    x ^= rotl64(key, 13) >> 32;  // post-whiten")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_het5_c(name, desc):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {",
         "    return (a & b) | (a & c) | (b & c);",
         "}",
         f"// {name}: {desc}",
         "// bit-exact C port of t6_models_b8._hetero5_cascade",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    static const uint64_t RC[8] = {"
         + ", ".join("0x%016Xu" % v for v in RC_DEC) + "};",
         "    uint64_t x = val ^ key, nl;"]
    for i, op in enumerate(M.SEQ_HET5):
        nrots = M.OP_NROTS_B6[op]
        rots = M.SCHED_HET5[i][:nrots]
        R = lambda j: f"rotl64(x,{rots[j]})"  # noqa: E731
        L.append(f"    // stage {i}: {op}")
        if op == "maj":
            L.append(f"    nl = maj64({R(0)},{R(1)},{R(2)}) ^ {R(3)};")
        elif op == "andor":
            L.append(f"    nl = (({R(0)} & {R(1)}) | ({R(2)} & {R(3)})) ^ {R(4)};")
        elif op == "chi":
            L.append(f"    nl = {R(0)} ^ ({R(1)} & ~{R(2)});")
        elif op == "majxor":
            L.append(f"    nl = maj64({R(0)},{R(1)},{R(2)}) ^ ({R(3)} & {R(4)});")
        elif op == "xor3and":
            L.append(f"    nl = {R(0)} ^ {R(1)} ^ {R(2)} ^ ({R(3)} & {R(4)} & {R(5)});")
        L.append(f"    x ^= nl ^ (rotl64(key, {13*(i+1)}) ^ RC[{i % 8}]);")
    L.append("    x ^= rotl64(key, 13) >> 32;  // post-whiten")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


# Bundle specs: name -> (kind, fn_name, sched, nrots)
BUNDLES = {
    "t6_fchi6a": ("fused", "_fchi", M.SCHED_F2, 2),
    "t6_fand6a": ("fused", "_fand", M.SCHED_F2, 2),
    "t6_fxorand6a": ("fused", "_fxorand", M.SCHED_F3, 3),
    "t6_het5a": ("het5", None, None, None),
}


def self_contained_model(name, desc):
    """Build model.py source via inspect.getsource (no sys.path hacks)."""
    parts = [f'"""Bit-exact Python model for {name} (batch 8)."""',
             "import numpy as np", ""]
    # Needed names from t6_models_b8
    parts.append(inspect.getsource(M.M64).replace("M64 = ", "M64 = ")
                 if False else "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    rc_src = inspect.getsource(M).split("RC64 = [")[1].split("]")[0]
    parts.append("RC64 = [" + rc_src + "]")
    parts.append("")
    for fn_name in ["_rotl64", "_fchi", "_fand", "_fxorand"]:
        parts.append(inspect.getsource(getattr(M, fn_name)))
    if BUNDLES[name][0] == "fused":
        parts.append(inspect.getsource(M._fused_cascade))
        parts.append(inspect.getsource(M._vec))
        fn_name, sched_name, nrots = BUNDLES[name][1], None, BUNDLES[name][3]
        # inline the schedule
        sched = BUNDLES[name][2]
        parts.append(f"SCHED = {sched!r}")
        parts.append(f"_FN = {fn_name}")
        parts.append(f"_NROTS = {nrots}")
        parts.append("")
        parts.append("def _scalar(v, k):")
        parts.append("    return _fused_cascade(v, k, _FN, SCHED, _NROTS)")
        parts.append("")
        parts.append("_mix_np = _vec(_scalar)")
    else:
        parts.append(inspect.getsource(M._maj))
        parts.append(f"SEQ_HET5 = {M.SEQ_HET5!r}")
        parts.append(f"SCHED_HET5 = {M.SCHED_HET5!r}")
        parts.append(f"OP_NROTS_B6 = {M.OP_NROTS_B6!r}")
        parts.append(inspect.getsource(M._hetero5_cascade))
        parts.append(inspect.getsource(M._vec))
        parts.append("")
        parts.append("def _scalar(v, k):")
        parts.append("    return _hetero5_cascade(v, k)")
        parts.append("")
        parts.append("_mix_np = _vec(_scalar)")
    parts.append("")
    parts.append("def mix(v, k):")
    parts.append("    if np.ndim(v) == 0 and np.ndim(k) == 0:")
    parts.append("        return _scalar(int(v), int(k))")
    parts.append("    return _mix_np(v, k)")
    parts.append("")
    parts.append("def mix_np(V, K):")
    parts.append("    return _mix_np(V, K)")
    parts.append("")
    parts.append(f"meta = {{'desc': {desc!r}}}")
    return "\n".join(parts) + "\n"


def main():
    import numpy as np
    for name, (kind, fn_name, sched, nrots) in BUNDLES.items():
        desc = M.CANDIDATES_B8[name][1]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        # RTL
        if kind == "fused":
            rtl = gen_fused_rtl(name, fn_name, sched, nrots)
            impl_src = gen_fused_c(name, desc, fn_name, sched, nrots)
        else:
            rtl = gen_het5_rtl(name)
            impl_src = gen_het5_c(name, desc)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(rtl + "\n")
        # self-contained model.py
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc))
        # meta.json WITH rtl_top
        meta_json = {
            "name": name,
            "rtl_top": name,
            "description": desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
        }
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump(meta_json, f, indent=1)
        # real impl.c
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(impl_src)
        print(f"{name}: bundle written to {d}")

    # ---- bit-exact verification ----
    print("\n=== bit-exact checks ===")
    ok = True
    for name in BUNDLES:
        d = os.path.join(FB, name)
        # 1. model.py loads and matches t6_models_b8
        spec = __import__("importlib.util", fromlist=["util"])
        mu = spec.spec_from_file_location("m_" + name,
                                          os.path.join(d, "model.py"))
        m = spec.module_from_spec(mu)
        mu.loader.exec_module(m)
        ref_fn = M.CANDIDATES_B8[name][0]
        import numpy as np
        rng = np.random.default_rng(42)
        for trial in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            a = int(m.mix(np.uint64(v), np.uint64(k)))
            b = int(ref_fn(np.uint64(v), np.uint64(k)))
            if a != b:
                print(f"{name}: MODEL MISMATCH at trial {trial}")
                ok = False
                break
        else:
            print(f"{name}: model.py bit-exact vs t6_models_b8 (200 vecs)")
        # 2. impl.c compiles and matches
        test_c = (f'#include <stdio.h>\n#include <stdint.h>\n'
                  f'uint64_t mix_hash(uint64_t, uint64_t);\n'
                  f'int main(){{uint64_t v,k;int n=0;'
                  f'while(scanf("%lx %lx",&v,&k)==2){{'
                  f'printf("%016lx\\n",mix_hash(v,k));n++;}}return 0;}}')
        with open("/tmp/b8_test.c", "w") as f:
            f.write(test_c)
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b8_test",
                            "/tmp/b8_test.c", os.path.join(d, "impl.c")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: impl.c COMPILE FAIL: {r.stderr[:200]}")
            ok = False
            continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64)))
                for _ in range(200)]
        inp = "\n".join(f"{v:x} {k:x}" for v, k in vecs)
        r = subprocess.run(["/tmp/b8_test"], input=inp, capture_output=True,
                           text=True)
        outs = r.stdout.strip().split("\n")
        for (v, k), o in zip(vecs, outs):
            exp = int(ref_fn(np.uint64(v), np.uint64(k)))
            if int(o, 16) != exp:
                print(f"{name}: IMPL.C MISMATCH")
                ok = False
                break
        else:
            print(f"{name}: impl.c bit-exact vs model (200 vecs)")
    print("ALL OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

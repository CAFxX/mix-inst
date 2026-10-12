#!/usr/bin/env python3
"""Generate a validation candidate from an explicit P-box list (round_wf 2D phase).

Usage: gen_from_P.py <name> <P_json_file>
  P_json_file: JSON list of 64 ints (the permutation).
Emits round_wf/validation/candidates/<name>/{impl.c,model.py,meta.json,rtl.v}
with the P-box replaced by the table-driven version. Then xcheck + S2 via
validation/run_s2_screen.py <name>.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = "/home/hatch/workspace/mix/exploration"
R22C = EXP + "/fast_battery/candidates/r22c_spn_mix4r_lp_nw"
CANDDIR = EXP + "/round_wf/validation/candidates"

def check_P(P):
    assert sorted(P) == list(range(64)), "not a permutation"
    seen = [False] * 64; cyc = 0
    for i in range(64):
        if not seen[i]:
            cyc += 1; j = i
            while not seen[j]:
                seen[j] = True; j = P[j]
    assert cyc == 1, f"not single-cycle: {cyc}"
    assert all(P[i] != i for i in range(64)), "fixed point"
    return True

def main():
    name, pfile = sys.argv[1], sys.argv[2]
    P = json.load(open(pfile))
    assert len(P) == 64
    check_P(P)
    W = sum(abs(P[i] - i) for i in range(64))
    S = sum(abs(P[i] // 4 - i // 4) for i in range(64))
    outdir = f"{CANDDIR}/{name}"
    os.makedirs(outdir, exist_ok=True)

    src = open(f"{R22C}/impl.c").read()
    ptab = "static const uint8_t PTAB[64] = {\n    " + ",\n    ".join(
        ", ".join(str(P[4 * r + k]) for k in range(4)) for r in range(16)) + "\n};"
    new_pbox = (ptab + "\nstatic uint64_t pbox64_o34(uint64_t x) {\n"
                "    /* round_wf 2D phase: out[PTAB[i]] = in[i]. Single 64-cycle,\n"
                "     * zero fixed points, Dmin=4 (O34-validated family). */\n"
                "    uint64_t y = 0;\n"
                "    for (int i = 0; i < 64; i++)\n"
                "        y |= ((x >> i) & 1u) << PTAB[i];\n"
                "    return y;\n}\n")
    pat = re.compile(r"static uint64_t pbox64_o34\(uint64_t x\) \{.*?\n\}\n", re.S)
    assert pat.search(src), "pbox fn not found"
    impl = pat.sub(new_pbox, src)
    impl = impl.replace("r22c_spn_mix4r_lp_nw: O38 V0",
                        f"{name}: round_wf 2D-phase P-box variant")
    open(f"{outdir}/impl.c", "w").write(impl)

    model = f'''"""Python model wrapper for {name} (round_wf 2D phase).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`. Bit-exact vs impl.c."""
import numpy as np
_PTAB = np.array({P}, dtype=np.int64)
_S1 = np.array([0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10], dtype=np.int64)
_GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)
_MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & _MASK64 if r else x & _MASK64
def _rk(k, i):
    with np.errstate(over="ignore"):
        return (_rotl64(k, 13 * (i + 1)) ^ (np.uint64(i + 1) * _GOLDEN64)) & _MASK64
def _sbox16(x):
    out = np.zeros_like(x); xv = x & _MASK64
    for i in range(16):
        nib = ((xv >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(_S1, nib).astype(np.uint64) << np.uint64(4*i)
    return out & _MASK64
def _pbox(x):
    out = np.zeros_like(x); xv = x & _MASK64
    for i, d in enumerate(_PTAB):
        out |= ((xv >> np.uint64(i)) & np.uint64(1)) << np.uint64(int(d))
    return out & _MASK64
def _lin(x):
    return (x ^ _rotl64(x, 3) ^ _rotl64(x, 11)) & _MASK64
def mix_np(v, k):
    x = np.asarray(v, dtype=np.uint64) & _MASK64
    kk = np.asarray(k, dtype=np.uint64) & _MASK64
    for i in range(4):
        x = _lin(_pbox(_sbox16(x ^ _rk(kk, i))))
    return x & _MASK64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
'''
    open(f"{outdir}/model.py", "w").write(model)

    rtl = open(f"{R22C}/rtl.v").read()
    def repl(m):
        src_bit = int(m.group(2))
        return f"t[{P[src_bit]}] = s[{src_bit}];"
    rtl2, n = re.subn(r"t\[(\d+)\] = s\[(\d+)\];", repl, rtl)
    assert n == 256, f"expected 256 pbox lines, got {n}"
    rtl2 = rtl2.replace("module r22c_spn_mix4r_lp_nw(", f"module {name}(")
    rtl2 = rtl2.replace("// r22c_spn_mix4r_lp_nw: O38 V0",
                        f"// {name}: round_wf 2D-phase P-box variant")
    open(f"{outdir}/rtl.v", "w").write(rtl2)

    meta = json.load(open(f"{R22C}/meta.json"))
    meta["name"] = name
    meta["description"] = (f"round_wf 2D-phase P-box variant of r22c "
                           f"(W1d={W}, S={S}); 4r keyed SPN")
    meta["composition"] = meta["description"]
    meta["rtl_top"] = name
    sys.path.insert(0, outdir)
    import model as wm
    g0 = meta["goldens"][0]
    out = wm.mix(int(g0["val"], 16), int(g0["key"], 16))
    g0["out"] = hex(out)
    json.dump(meta, open(f"{outdir}/meta.json", "w"), indent=1)
    print(f"generated {name}: W1d={W} S={S} golden={hex(out)}")

if __name__ == "__main__":
    main()

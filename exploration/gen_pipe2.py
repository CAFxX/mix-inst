"""2-stage pipeline for the round-3 winner (function-identical to spn4_xorlin_1137).

Stage 1 (combinational): (val,key) -> rounds 0,1 -> s2.
Registers: s2_q[63:0], key_q[63:0], valid_q.
Stage 2 (combinational): (s2_q,key_q) -> rounds 2,3 -> whitening -> out.

Uses the QM-minimal PRESENT S-box SOP (same as r3_xorlin_qm).
If levers include 'b', uses the L^{-1} whitening absorption.

Verification:
  1. tb_pipe2: functional - out after 2 cycles == numpy model; valid tracking.
  2. Throughput: new input every cycle -> valid_out every cycle after fill.
"""
import os, subprocess, sys

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
from gen_r3 import _QM, rk_expr, rotl, emit_k4p, LR, LS

def sbox_qm_layer(prefix, sx, rounds_tag):
    """Emit QM S-box layer: sy = SBOX(sx). Returns (verilog_lines, sy_name)."""
    L = []
    sbnames = []
    for b in range(16):
        sl = f"{prefix}_sl{b}"
        sb = f"{prefix}_sb{b}"
        L.append(f"  wire [3:0] {sl} = {sx}[{4*b+3}:{4*b}];")
        L.append(f"  wire [3:0] {sb};")
        for bit in range(4):
            terms = []
            for (mask, bits) in _QM[bit]:
                lits = []
                for j in range(4):
                    if not (mask >> j) & 1:
                        nm = f"{sl}[{j}]"
                        lits.append(nm if (bits >> j) & 1 else f"(~{nm})")
                terms.append("(" + "&".join(lits) + ")" if lits else "1'b1")
            rhs = " | ".join(terms) if terms else "1'b0"
            L.append(f"  assign {sb}[{bit}] = {rhs};")
        sbnames.append(sb)
    sy = f"{prefix}_sy"
    L.append(f"  wire [63:0] {sy} = {{{', '.join(sbnames[::-1])}}};")
    return L, sy

def two_rounds(tag, s_in, key_sig, rk_idx_base, levers):
    """Two full rounds: s_in -> xor rk -> S-box -> L -> xor rk -> S-box -> L -> s_out.
    Returns (lines, s_out_name, sy_last_name)."""
    L = []
    s_cur = s_in
    sy_last = None
    for r in range(2):
        rk_i = rk_idx_base + r
        # rk from key_sig: rk[i] = ROTL(key,13*(i+1)) ^ RC[i]
        rk = rk_expr(rk_i).replace("key", key_sig)
        sx = f"{tag}_sx{r}"
        L.append(f"  wire [63:0] {sx} = {s_cur} ^ {rk};")
        sl, sy = sbox_qm_layer(f"{tag}_r{r}", sx, tag)
        L.extend(sl)
        sy_last = sy
        s_nxt = f"{tag}_s{r+1}"
        L.append(f"  wire [63:0] {s_nxt} = {sy} ^ {rotl(sy, LR)} ^ {rotl(sy, LS)};")
        s_cur = s_nxt
    return L, s_cur, sy_last

def build_pipe2(name, levers):
    L = [f"// {name}: 2-stage pipeline, function-identical to spn4_xorlin_1137",
         f"// levers={levers}; QM S-box",
         f"module {name}(",
         "  input wire clk,",
         "  input wire [63:0] val,",
         "  input wire [63:0] key,",
         "  input wire valid_in,",
         "  output wire [63:0] out,",
         "  output wire valid_out",
         ");"]
    # ---- stage 1 combinational: (val,key) -> rounds 0,1 ----
    L.append("  // stage 1: input whitening + rounds 0,1")
    if "d" in levers:
        L.append(f"  wire [63:0] st1_sx0 = val ^ key ^ {rk_expr(0)};")
        # need s_in for two_rounds; handle specially
        s_in = None  # merged below
    else:
        L.append("  wire [63:0] st1_s0 = val ^ key;")
        s_in = "st1_s0"
    if "d" in levers:
        # manually do rounds with merged sx0
        L.append("  // (d lever: sx0 merged)")
        lr, s_cur = two_rounds_merged_sx0(levers)
        L.extend(lr)
    else:
        lr, s_cur, _ = two_rounds("st1", s_in, "key", 0, levers)
        L.extend(lr)
    # ---- pipeline registers ----
    L.append("  // pipeline registers")
    L.append("  reg [63:0] s2_q;")
    L.append("  reg [63:0] key_q;")
    L.append("  reg valid_q;")
    L.append("  always @(posedge clk) begin")
    L.append(f"    s2_q <= {s_cur};")
    L.append("    key_q <= key;")
    L.append("    valid_q <= valid_in;")
    L.append("  end")
    # ---- stage 2 combinational: (s2_q,key_q) -> rounds 2,3 -> whitening ----
    L.append("  // stage 2: rounds 2,3 + whitening")
    if "b" in levers:
        L.append("  wire [63:0] k4p;")
        # emit_k4p uses 'key'; replace with key_q
        for kl in emit_k4p():
            L.append(kl.replace("key[", "key_q[").replace("// lever b", "// lever b (stage2)"))
    lr2, s_cur2, sy_last2 = two_rounds("st2", "s2_q", "key_q", 2, levers)
    L.extend(lr2)
    # s_cur2 is s4 (after L of round 3); sy_last2 is sy3. Whitening:
    if "b" in levers:
        L.append(f"  wire [63:0] st2_z3 = {sy_last2} ^ k4p;")
        L.append("  assign out = st2_z3 ^ %s ^ %s;" % (rotl("st2_z3", LR), rotl("st2_z3", LS)))
    else:
        rk4 = rk_expr(4).replace("key", "key_q")
        L.append(f"  assign out = {s_cur2} ^ {rk4};")
    L.append("  assign valid_out = valid_q;")
    L.append("endmodule")
    path = EXP + f"/rtl/r3/{name}.v"
    open(path, "w").write("\n".join(L) + "\n")
    return path

def two_rounds_merged_sx0(levers):
    """Rounds 0,1 with sx0 = val^key^rk0 pre-merged (d lever)."""
    L = []
    sx0 = "st1_sx0"
    sl, sy = sbox_qm_layer("st1_r0", sx0, "st1")
    L.extend(sl)
    L.append(f"  wire [63:0] st1_s1 = {sy} ^ {rotl(sy, LR)} ^ {rotl(sy, LS)};")
    rk1 = rk_expr(1)
    L.append(f"  wire [63:0] st1_sx1 = st1_s1 ^ {rk1};")
    sl, sy = sbox_qm_layer("st1_r1", "st1_sx1", "st1")
    L.extend(sl)
    L.append(f"  wire [63:0] st1_s2 = {sy} ^ {rotl(sy, LR)} ^ {rotl(sy, LS)};")
    return L, "st1_s2"

if __name__ == "__main__":
    import sys
    levers = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] else set()
    name = "mix_pipe2_" + ("_".join(sorted(levers)) if levers else "base")
    p = build_pipe2(name, levers)
    print("built", p)

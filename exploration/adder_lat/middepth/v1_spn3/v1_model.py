"""V1: 3-stage SPN with 4-bit Midori Sb0 S-boxes (track-3 mid-depth, worker V1).

Structure:
    x ^= k
    for i in 1..3:
        x = sbox4_layer(x)        # 16x parallel Midori Sb0
        x = linear_layer(x, params_i)
    x ^= rotl(k, 13)

This module: Verilog generation (single stage and full 3-stage) + bit-exact
numpy Python model. Verilog and model are generated from the same parameters.
"""
import numpy as np

# Midori Sb0 (from sub10/measure_sbox.py, "midori0")
MIDORI_SB0 = [0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

SB0 = np.array(MIDORI_SB0, dtype=np.uint64)

def sbox4_layer(x):
    """16x parallel 4-bit S-box. x: uint64 array -> uint64 array."""
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4 * i)) & np.uint64(0xF)
        y |= SB0[nib] << np.uint64(4 * i)
    return y

def lin_4term(x, p, q, r, s):
    return (x ^ rotl(x, p) ^ rotl(x, q) ^ rotl(x, r) ^ rotl(x, s)) & M64

def present_p(i):
    return 63 if i == 63 else (16 * i) % 63

def lin_present(x):
    """PRESENT P-box (wiring only): y[P(i)] = x[i]."""
    y = np.zeros_like(x)
    for i in range(64):
        bit = (x >> np.uint64(i)) & np.uint64(1)
        y |= bit << np.uint64(present_p(i))
    return y

def lin_rotxor(x, p, q):
    return (x ^ rotl(x, p) ^ rotl(x, q)) & M64

def mix_spn3(x, k, stages, lin):
    """x,k: uint64 arrays. stages: list of per-stage linear params.
    lin: '4term' (params=(p,q,r,s)), 'present' (params ignored), 'rotxor' (params=(p,q))."""
    x = (x ^ k) & M64
    for prm in stages:
        x = sbox4_layer(x)
        if lin == '4term':
            x = lin_4term(x, *prm)
        elif lin == 'present':
            x = lin_present(x)
        elif lin == 'rotxor':
            x = lin_rotxor(x, *prm)
        else:
            raise ValueError(lin)
    return (x ^ rotl(k, 13)) & M64


# ---------------- Verilog generation ----------------

SBOX_CASES = "\n".join(
    f"            4'h{v:X}: sbox = 4'h{t:X};" for v, t in enumerate(MIDORI_SB0))

SBOX_FN = """    function [3:0] sbox(input [3:0] a);
        case (a)
%s
        endcase
    endfunction
""" % SBOX_CASES

def rotl_expr(sig, r):
    r %= 64
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)

def gen_stage(name, lin, pqrs=(7, 13, 29, 41)):
    """One stage: sbox layer + linear. Top module `name`, ports x->y."""
    body = []
    body.append("module %s(input [63:0] x, output [63:0] y);" % name)
    body.append(SBOX_FN)
    body.append("    wire [63:0] s;")
    body.append("    genvar i;")
    body.append("    generate")
    body.append("        for (i = 0; i < 16; i = i + 1) begin : sb")
    body.append("            assign s[i*4+3:i*4] = sbox(x[i*4+3:i*4]);")
    body.append("        end")
    body.append("    endgenerate")
    if lin == '4term':
        p, q, r, s = pqrs
        e = " ^ ".join([rotl_expr("s", rr) for rr in (0, p, q, r, s)])
        body.append("    assign y = %s;" % e)
    elif lin == 'present':
        wires = ["s[%d]" % i for i in range(64)]
        # y[P(i)] = s[i]
        out = [""] * 64
        for i in range(64):
            out[present_p(i)] = "s[%d]" % i
        body.append("    assign y = {%s};" % ", ".join(reversed(out)))
    elif lin == 'rotxor':
        p, q = pqrs
        e = " ^ ".join([rotl_expr("s", rr) for rr in (0, p, q)])
        body.append("    assign y = %s;" % e)
    else:
        raise ValueError(lin)
    body.append("endmodule")
    return "\n".join(body) + "\n"

def gen_full(top, lin, stages):
    """Full 3-stage keyed SPN. Ports: x[63:0], k[63:0] -> y[63:0]."""
    body = []
    body.append("module %s(input [63:0] x, input [63:0] k, output [63:0] y);" % top)
    body.append(SBOX_FN)
    body.append("    wire [63:0] w0 = x ^ k;")
    prev = "w0"
    for idx, prm in enumerate(stages):
        sb = "s%d" % idx
        ln = "l%d" % idx
        body.append("    wire [63:0] %s;" % sb)
        body.append("    genvar g%d;" % idx)
        body.append("    generate")
        body.append("        for (g%d = 0; g%d < 16; g%d = g%d + 1) begin : sb%d"
                    % (idx, idx, idx, idx, idx))
        body.append("            assign %s[g%d*4+3:g%d*4] = sbox(%s[g%d*4+3:g%d*4]);"
                    % (sb, idx, idx, prev, idx, idx))
        body.append("        end")
        body.append("    endgenerate")
        if lin == '4term':
            p, q, r, s = prm
            e = " ^ ".join([rotl_expr(sb, rr) for rr in (0, p, q, r, s)])
        elif lin == 'present':
            out = [""] * 64
            for i in range(64):
                out[present_p(i)] = "%s[%d]" % (sb, i)
            e = "{%s}" % ", ".join(reversed(out))
        elif lin == 'rotxor':
            p, q = prm
            e = " ^ ".join([rotl_expr(sb, rr) for rr in (0, p, q)])
        else:
            raise ValueError(lin)
        body.append("    wire [63:0] %s = %s;" % (ln, e))
        prev = ln
    body.append("    assign y = %s ^ %s;" % (prev, rotl_expr("k", 13)))
    body.append("endmodule")
    return "\n".join(body) + "\n"


if __name__ == "__main__":
    # self-test: model sanity (bijectivity of one stage is NOT required;
    # just check determinism + avalanche nonzero)
    xs = np.arange(256, dtype=np.uint64)
    k = np.uint64(0x123456789ABCDEF0)
    y = mix_spn3(xs, k, [(7, 13, 29, 41)] * 3, '4term')
    assert y.shape == (256,) and len(set(y.tolist())) > 200, "degenerate"
    yp = mix_spn3(xs, k, [None] * 3, 'present')
    assert len(set(yp.tolist())) > 200, "degenerate present"
    print("selftest OK: 4term distinct=%d/256 present distinct=%d/256"
          % (len(set(y.tolist())), len(set(yp.tolist()))))

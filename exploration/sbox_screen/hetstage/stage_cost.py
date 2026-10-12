#!/usr/bin/env python3
"""Per-stage unit-delay cost calibration for the hetstage pool (track-2).

Emits single-stage 64-bit verilog for each hetero stage type + anchors,
synthesizes through the PINNED flow (run_synth.synth_one: yosys 0.69,
abc -genlib mini.genlib, dual-analyzer XCHECK), prints crit ("u").

Anchors (must reproduce the het8 scale): MUXD ~3.86u, XOR4-5t ~4.0u.
New: CIRC1 (2-term), CIRC2 (3-term), GFM3 (sparse-constant GF mult),
ANDOR (4-input AND-OR mix).
"""
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from run_synth import synth_one

WORK = os.path.expanduser("~/workspace/mix/exploration/sbox_screen/hetstage/cost_work")


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return "{%s[%d:0], %s[%d:%d]}" % (x, 63 - r, x, 63, 64 - r)


# ---- GF(2^64) multiply-by-constant bit matrix (P = x^64+x^4+x^3+x+1) ----
# mask[j] = input-bit mask with parity(x & mask[j]) == bit j of (x*C mod P).
# colvec[i] = (z^i * C mod P) as output-bit vector; mask[j] selects the
# input positions i whose column has bit j set (transpose of colvec).
def gf_mat(C):
    """Return list of 64 int masks: outbit j = parity(x & mask[j])."""
    P = (1 << 64) | (1 << 4) | (1 << 3) | (1 << 1) | 1  # degree-64 poly bits
    colvec = []
    for i in range(64):
        prod = 0
        cc = C
        b = 0
        while cc:
            if cc & 1:
                prod ^= 1 << (i + b)
            cc >>= 1
            b += 1
        # reduce bits 127..64
        for k in range(127, 63, -1):
            if (prod >> k) & 1:
                prod ^= (P << (k - 64))
        colvec.append(prod & ((1 << 64) - 1))
    masks = []
    for j in range(64):
        m = 0
        for i in range(64):
            if (colvec[i] >> j) & 1:
                m |= 1 << i
        masks.append(m)
    return masks


def mod_v(name, body):
    return ("module %s (input  [63:0] x, output [63:0] y);\n%s\nendmodule\n"
            % (name, body))


def emit():
    os.makedirs(WORK, exist_ok=True)
    mods = {}
    # anchors
    s, a, b, d = rotl("x", 5), rotl("x", 17), rotl("x", 33), 41
    mods["muxd"] = mod_v("muxd",
        "  wire [63:0] m = (%s & %s) | (~%s & %s);\n  assign y = x ^ m ^ %s;"
        % (s, a, s, b, rotl("x", d)))
    mods["xor4"] = mod_v("xor4",
        "  assign y = x ^ %s ^ %s ^ %s ^ %s;"
        % (rotl("x", 5), rotl("x", 17), rotl("x", 33), rotl("x", 41)))
    # new hetero stages
    mods["circ1"] = mod_v("circ1", "  assign y = x ^ %s;" % rotl("x", 13))
    mods["circ2"] = mod_v("circ2",
        "  assign y = x ^ %s ^ %s;" % (rotl("x", 13), rotl("x", 37)))
    mods["andor"] = mod_v("andor",
        "  assign y = x ^ ((%s & %s) | (%s & %s));"
        % (rotl("x", 5), rotl("x", 17), rotl("x", 33), rotl("x", 41)))
    # sparse-constant GF mults: C popcount 3 and 7
    for cname, C in (("gfm3", (1 << 37) | (1 << 11) | 1),
                     ("gfm7", (1 << 60) | (1 << 47) | (1 << 33) | (1 << 21) | (1 << 9) | (1 << 4) | 1)):
        masks = gf_mat(C)
        lines = ["  assign y[%d] = ^(x & 64'h%016x);" % (j, m)
                 for j, m in enumerate(masks)]
        mods[cname] = mod_v(cname, "\n".join(lines))
        tot = sum(bin(m).count("1") for m in masks)
        print("%s: C=%#x matrix weight=%d (avg %.1f/col)" % (cname, C, tot, tot / 64.0),
              flush=True)
    for name, src in mods.items():
        p = os.path.join(WORK, name + ".v")
        with open(p, "w") as f:
            f.write(src)
    return mods


def main():
    mods = emit()
    print("== per-stage unit-delay cost (pinned yosys 0.69 flow) ==", flush=True)
    for name in ["muxd", "xor4", "circ1", "circ2", "andor", "gfm3", "gfm7"]:
        src = os.path.join(WORK, name + ".v")
        r = synth_one(src, name, os.path.join(WORK, "s_" + name))
        print("COST %-6s cells=%5d area=%7.0f crit=%5.2fu" %
              (name, r["cells"], r["area"], r["crit"]), flush=True)


if __name__ == "__main__":
    main()

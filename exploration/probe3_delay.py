"""Delay-decomposition probes for spn4_xorlin_1137 (round 3, priority 1).

Synthesizes isolated pieces through the IDENTICAL flow (run_synth.py) to find
where the 44.8 unit-delays go:
  probe_sbox  : 16x PRESENT S-box only (64 in -> 64 out)
  probe_L     : L(x)=x^ROTL(x,11)^ROTL(x,37) only
  probe_keyxor: sx = s ^ rotl(key,13) ^ RC (key schedule xor shape)
  probe_round1: one full round (keyxor + sbox + L)
Each probe's crit tells us the per-piece cost; the sum structure reveals
ABC's cross-boundary optimization.
"""
import os, subprocess, sys

EXP = "/home/hatch/workspace/mix/exploration"

PRESENT = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]

def sop_terms(sig, base, table, bit):
    terms = []
    for v in range(16):
        if (table[v] >> bit) & 1:
            lits = []
            for j in range(4):
                nm = "%s[%d]" % (sig, base + j)
                lits.append(nm if (v >> j) & 1 else "(~%s)" % nm)
            terms.append("(" + "&".join(lits) + ")")
    return terms

def sbox_layer(sig_in, prefix):
    L = []
    sbnames = []
    for b in range(16):
        sb = "%s_sb%d" % (prefix, b)
        sbnames.append(sb)
        L.append("  wire [3:0] %s;" % sb)
        for bit in range(4):
            terms = sop_terms(sig_in, 4*b, PRESENT, bit)
            rhs = " | ".join(terms) if terms else "1'b0"
            L.append("  assign %s[%d] = %s;" % (sb, bit, rhs))
    L.append("  wire [63:0] %s_sy = {%s};" % (prefix, ", ".join(sbnames[::-1])))
    return "\n".join(L), "%s_sy" % prefix

def rotl(sig, r):
    r %= 64
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63-r, sig, 64-r) if r else sig

def module(name, body):
    return ("module %s(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);\n%s\nendmodule\n"
            % (name, body))

def gen():
    os.makedirs(EXP + "/rtl/probe3", exist_ok=True)
    # sbox only
    sb, sy = sbox_layer("val", "p")
    open(EXP + "/rtl/probe3/probe_sbox.v", "w").write(
        module("probe_sbox", sb + "\n  assign out = %s;" % sy))
    # L only
    open(EXP + "/rtl/probe3/probe_L.v", "w").write(
        module("probe_L", "  assign out = val ^ %s ^ %s;" % (rotl("val", 11), rotl("val", 37))))
    # keyxor only: sx = s ^ rotl(key,13) ^ RC
    open(EXP + "/rtl/probe3/probe_keyxor.v", "w").write(
        module("probe_keyxor",
               "  assign out = val ^ %s ^ 64'h9e3779b97f4a7c15;" % rotl("key", 13)))
    # one full round
    kx = "  wire [63:0] sx = val ^ key ^ %s ^ 64'h9e3779b97f4a7c15;" % rotl("key", 13)
    sb, sy = sbox_layer("sx", "p")
    body = kx + "\n" + sb + "\n  assign out = %s ^ %s ^ %s;" % (sy, rotl(sy, 11), rotl(sy, 37))
    open(EXP + "/rtl/probe3/probe_round1.v", "w").write(module("probe_round1", body))
    print("probes written")

def synth(name):
    r = subprocess.run(
        [sys.executable, EXP + "/run_synth.py",
         EXP + "/rtl/probe3/%s.v" % name, name, EXP + "/results/probe3/_%s" % name],
        capture_output=True, text=True, timeout=900, cwd=EXP,
        env={**os.environ, "PATH": EXP + "/bin:" + os.environ["PATH"]})
    for line in r.stdout.splitlines():
        if line.startswith("RESULT") or line.startswith("REF"):
            print(line)
    if r.returncode != 0:
        print("FAILED", name, r.stdout[-1500:], r.stderr[-1500:])

if __name__ == "__main__":
    gen()
    for n in ["probe_sbox", "probe_L", "probe_keyxor", "probe_round1"]:
        synth(n)

"""Verilog for C1/C2 partitioned NAND4-Toffoli, 2 stages.
Stage1: controls C1={0..8} (frozen), targets T1={9..63}.
Stage2: controls C2={9..17} (frozen), targets T2={0..8}|{18..63}.
Gate: out[t] = in[t] ^ ~(in[c1]&in[c2]&in[c3]&in[c4]).
"""
C1 = list(range(0, 9))
T1 = list(range(9, 64))
C2 = list(range(9, 18))
T2 = list(range(0, 9)) + list(range(18, 64))

def controls(t, cpool, seed):
    import random
    r = random.Random(seed + t)
    return r.sample(cpool, 4)

lines = ["module toffoli_c1c2(input  [63:0] din, output [63:0] dout);",
         "  wire [63:0] s1;"]
for t in range(64):
    if t in T1:
        cs = controls(t, C1, 1000)
        lines.append(f"  assign s1[{t}] = din[{t}] ^ ~(&{{din[{cs[0]}], din[{cs[1]}], din[{cs[2]}], din[{cs[3]}]}});")
    else:
        lines.append(f"  assign s1[{t}] = din[{t}];")
for t in range(64):
    if t in T2:
        cs = controls(t, C2, 2000)
        lines.append(f"  assign dout[{t}] = s1[{t}] ^ ~(&{{s1[{cs[0]}], s1[{cs[1]}], s1[{cs[2]}], s1[{cs[3]}]}});")
    else:
        lines.append(f"  assign dout[{t}] = s1[{t}];")
lines.append("endmodule")
open("toffoli_c1c2.v", "w").write("\n".join(lines) + "\n")
print("wrote toffoli_c1c2.v")

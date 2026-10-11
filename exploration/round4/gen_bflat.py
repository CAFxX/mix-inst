"""Generate fully-flat, unrolled Verilog for the B family (Blink/Midori SPN)."""
import os

R4 = "/home/hatch/workspace/mix/exploration/round4"
OUT = os.path.join(R4, "rtl", "flat2")
os.makedirs(OUT, exist_ok=True)

_S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
       0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]
_MIDORI = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
           0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
_PERM = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
# shuffle concat (MSB first): out_nib[i] = in_nib[PERM[i]]
_SHUF = "{" + ", ".join(f"x[{4*_PERM[i]+3}:{4*_PERM[i]}]"
                        for i in range(15, -1, -1)) + "}"

CANDS = [("r4_blink2", 0, 2), ("r4_blink3", 0, 3),
         ("r4_blink4", 0, 4), ("r4_midori3", 1, 3)]


def gen(name, sb, rounds):
    L = []
    L.append(f"// Flat unrolled {name}: Blink/Midori SPN, sb={sb}, {rounds} rounds.")
    L.append(f"module {name}")
    L.append("    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
    # Minimized DNF S-box (Quine-McCluskey, verified 16/16). 4.6u vs 11.0u ternary.
    L.append("    function automatic [3:0] sbox(input [3:0] x);")
    L.append("        reg y0, y1, y2, y3;")
    L.append("        begin")
    if sb == 0:  # S1: 0,1,2,4,3,8,f,c,9,5,b,6,7,e,d,a
        L.append("            y0 = ( x[2] & ~x[0]) | (x[3] & ~x[0]) | (~x[2] & ~x[1] & x[0]);")
        L.append("            y1 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[2] & ~x[0]) | (x[3] & ~x[2] & x[1]) | (~x[3] & x[1] & ~x[0]) | (x[3] & x[2] & x[0]);")
        L.append("            y2 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[1] & x[0]) | (x[3] & ~x[2] & x[0]) | (x[2] & x[1] & ~x[0]);")
        L.append("            y3 = (x[2] & x[1]) | (x[2] & x[0]) | (x[3] & ~x[2] & ~x[0]);")
    else:  # Midori Sb0: c,5,6,b,9,0,a,d,3,e,f,8,4,7,1,2
        L.append("            y0 = (x[3] & x[1] & ~x[0]) | (~x[3] & ~x[2] & x[0]) | (~x[3] & x[2] & ~x[1] & ~x[0]) | (~x[3] & x[1] & x[0]) | (x[3] & x[2] & ~x[1] & x[0]) | (x[3] & ~x[2] & ~x[0]);")
        L.append("            y1 = (~x[3] & ~x[2] & x[1]) | (x[3] & ~x[1] & x[0]) | (x[3] & ~x[2] & ~x[0]) | (~x[3] & x[1] & ~x[0]) | (x[3] & x[2] & x[0]);")
        L.append("            y2 = (x[3] & x[2] & ~x[1]) | (~x[2] & ~x[1] & x[0]) | (~x[3] & ~x[2] & ~x[0]) | (~x[3] & x[2] & x[1] & x[0]) | (~x[2] & x[1] & ~x[0]);")
        L.append("            y3 = (~x[3] & x[2] & ~x[0]) | (~x[3] & x[1] & x[0]) | (x[3] & ~x[2] & x[0]) | (~x[3] & ~x[1] & ~x[0]) | (x[3] & ~x[2] & x[1]);")
    L.append("            sbox = {y3, y2, y1, y0};")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [63:0] sbox16(input [63:0] x);")
    L.append("        begin")
    terms = ", ".join(f"sbox(x[{4*s+3}:{4*s}])" for s in range(15, -1, -1))
    L.append(f"            sbox16 = {{{terms}}};")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [15:0] mixcol(input [15:0] c);")
    L.append("        reg [3:0] n0, n1, n2, n3;")
    L.append("        begin")
    L.append("            n0 = c[3:0]; n1 = c[7:4]; n2 = c[11:8]; n3 = c[15:12];")
    L.append("            mixcol = {(n0^n1^n2), (n0^n1^n3), (n0^n2^n3), (n1^n2^n3)};")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [63:0] midori_M(input [63:0] x);")
    L.append("        begin")
    L.append("            midori_M = {mixcol(x[63:48]), mixcol(x[47:32]),")
    L.append("                        mixcol(x[31:16]), mixcol(x[15:0])};")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [63:0] shuffle(input [63:0] x);")
    L.append("        begin")
    L.append(f"            shuffle = {_SHUF};")
    L.append("        end")
    L.append("    endfunction")
    # round keys: rk_i = rotl64(key, 13*(i+1)) ^ (i+1)*C ; i = 0..rounds
    for i in range(rounds + 1):
        rr = (13 * (i + 1)) % 64
        const = ((i + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        rot = "key" if rr == 0 else f"{{key[{63-rr}:0], key[63:{64-rr}]}}"
        L.append(f"    wire [63:0] rk{i} = {rot} ^ 64'h{const:016X};")
    L.append("    wire [63:0] s0 = val ^ key;")
    for i in range(rounds):
        L.append(f"    wire [63:0] s{i+1} = shuffle(midori_M(sbox16(s{i} ^ rk{i})));")
    L.append(f"    assign out = s{rounds} ^ rk{rounds};")
    L.append("endmodule")
    path = os.path.join(OUT, f"{name}.v")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {path}")


for name, sb, rounds in CANDS:
    gen(name, sb, rounds)

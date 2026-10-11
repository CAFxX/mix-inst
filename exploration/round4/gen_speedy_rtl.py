"""Generate r4_speedy.v (parameterized) with the S6 case statement emitted
from the verified table (eprint 2021/960 Table 3)."""
S6 = [0x08, 0x00, 0x09, 0x03, 0x38, 0x10, 0x29, 0x13,
      0x0c, 0x0d, 0x04, 0x07, 0x30, 0x01, 0x20, 0x23,
      0x1a, 0x12, 0x18, 0x32, 0x3e, 0x16, 0x2c, 0x36,
      0x1c, 0x1d, 0x14, 0x37, 0x34, 0x05, 0x24, 0x27,
      0x02, 0x06, 0x0b, 0x0f, 0x33, 0x17, 0x21, 0x15,
      0x0a, 0x1b, 0x0e, 0x1f, 0x31, 0x11, 0x25, 0x35,
      0x22, 0x26, 0x2a, 0x2e, 0x3a, 0x1e, 0x28, 0x3c,
      0x2b, 0x3b, 0x2f, 0x3f, 0x39, 0x19, 0x2d, 0x3d]
S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
      0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]

L = []
L.append("// Round 4, family S: SPEEDY 6-bit S-box SPN probe (survey-driven).")
L.append("// S6 = SPEEDY S-box (eprint 2021/960 Table 3, verified vs paper DNF).")
L.append("// S-box layer: 10x S6 on bits [59:0] + S1 on bits [63:60], then ROTL17.")
L.append("// Round: x ^= rk[i]; x = sbox_layer(x); x = ROTL64(x,17); + whitening.")
L.append("// rk[i] = ROTL64(key,13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15.")
L.append("module r4_speedy #(parameter ROUNDS = 3)")
L.append("    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
L.append("    function automatic [5:0] s6(input [5:0] x);")
L.append("        begin")
L.append("            case (x)")
for i, v in enumerate(S6):
    L.append(f"                6'h{i:02X}: s6 = 6'h{v:02X};")
L.append("            endcase")
L.append("        end")
L.append("    endfunction")
L.append("    function automatic [3:0] s1(input [3:0] x);")
L.append("        begin")
L.append("            case (x)")
for i, v in enumerate(S1):
    L.append(f"                4'h{i:X}: s1 = 4'h{v:X};")
L.append("            endcase")
L.append("        end")
L.append("    endfunction")
L.append("    function automatic [63:0] sbox_layer(input [63:0] x);")
L.append("        begin")
terms = [f"s6(x[{6*g+5}:{6*g}])" for g in range(9, -1, -1)]
L.append("            sbox_layer = {" + f"s1(x[63:60]), {', '.join(terms)}" + "};")
L.append("        end")
L.append("    endfunction")
L.append("    wire [63:0] x0 = val ^ key;")
L.append("    wire [63:0] xs [0:ROUNDS];")
L.append("    assign xs[0] = x0;")
L.append("    genvar i;")
L.append("    generate")
L.append("        for (i = 0; i < ROUNDS; i = i + 1) begin : rnd")
L.append("            localparam integer RR = (13 * (i + 1)) % 64;")
L.append("            wire [63:0] rk = {key[63-RR:0], key[63:64-RR]} ^ ((i + 1) * 64'h9E3779B97F4A7C15);")
L.append("            wire [63:0] sb = sbox_layer(xs[i] ^ rk);")
L.append("            assign xs[i+1] = {sb[46:0], sb[63:47]};")
L.append("        end")
L.append("    endgenerate")
L.append("    localparam integer RWR = (13 * (ROUNDS + 1)) % 64;")
L.append("    wire [63:0] rkW = {key[63-RWR:0], key[63:64-RWR]} ^ ((ROUNDS + 1) * 64'h9E3779B97F4A7C15);")
L.append("    assign out = xs[ROUNDS] ^ rkW;")
L.append("endmodule")
open("/home/hatch/workspace/mix/exploration/round4/rtl/r4_speedy.v", "w").write("\n".join(L) + "\n")
print("wrote r4_speedy.v")

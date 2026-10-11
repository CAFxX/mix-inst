"""Generate fully-flat, unrolled Verilog for the S family (SPEEDY S-box SPN)."""
import os

R4 = "/home/hatch/workspace/mix/exploration/round4"
OUT = os.path.join(R4, "rtl", "flat2")
os.makedirs(OUT, exist_ok=True)

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

CANDS = [("r4_speedy3", 3), ("r4_speedy4", 4)]


def gen(name, rounds):
    L = []
    L.append(f"// Flat unrolled {name}: SPEEDY 6-bit S-box SPN, {rounds} rounds.")
    L.append(f"module {name}")
    L.append("    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
    L.append("    function automatic [5:0] s6(input [5:0] x);")
    L.append("        begin")
    terms = " :\n".join(f"                       (x == 6'h{i:02X}) ? 6'h{v:02X}" for i, v in enumerate(S6))
    L.append("            s6 = " + terms + " :\n                       6'h00;")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [3:0] s1(input [3:0] x);")
    L.append("        begin")
    terms = " :\n".join(f"                       (x == 4'h{i:X}) ? 4'h{v:X}" for i, v in enumerate(S1))
    L.append("            s1 = " + terms + " :\n                       4'h0;")
    L.append("        end")
    L.append("    endfunction")
    L.append("    function automatic [63:0] sbox_layer(input [63:0] x);")
    L.append("        begin")
    terms = ", ".join(f"s6(x[{6*g+5}:{6*g}])" for g in range(9, -1, -1))
    L.append(f"            sbox_layer = {{s1(x[63:60]), {terms}}};")
    L.append("        end")
    L.append("    endfunction")
    for i in range(rounds + 1):
        rr = (13 * (i + 1)) % 64
        const = ((i + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        rot = "key" if rr == 0 else f"{{key[{63-rr}:0], key[63:{64-rr}]}}"
        L.append(f"    wire [63:0] rk{i} = {rot} ^ 64'h{const:016X};")
    L.append("    wire [63:0] st0 = val ^ key;")
    for i in range(rounds):
        L.append(f"    wire [63:0] sb{i} = sbox_layer(st{i} ^ rk{i});")
        L.append(f"    wire [63:0] st{i+1} = {{sb{i}[46:0], sb{i}[63:47]}};")
    L.append(f"    assign out = st{rounds} ^ rk{rounds};")
    L.append("endmodule")
    path = os.path.join(OUT, f"{name}.v")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {path}")


for name, rounds in CANDS:
    gen(name, rounds)

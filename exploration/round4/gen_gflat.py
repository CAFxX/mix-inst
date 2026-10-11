"""Generate fully-flat, unrolled Verilog for the G family (Goldreich 5-local F Feistel)."""
import os

R4 = "/home/hatch/workspace/mix/exploration/round4"
OUT = os.path.join(R4, "rtl", "flat2")
os.makedirs(OUT, exist_ok=True)

_TAPS = [[1, 11, 14, 20, 21], [0, 2, 3, 7, 28], [3, 15, 16, 19, 21],
         [1, 7, 10, 19, 25], [6, 11, 19, 28, 31], [4, 11, 17, 19, 21],
         [3, 6, 20, 21, 23], [0, 7, 8, 10, 11], [2, 8, 15, 29, 30],
         [4, 14, 20, 21, 26], [0, 2, 9, 12, 20], [2, 3, 4, 5, 23],
         [2, 3, 4, 5, 23], [2, 19, 23, 27, 29], [1, 5, 6, 8, 12],
         [13, 16, 17, 18, 27], [1, 13, 15, 21, 25], [12, 13, 16, 19, 20],
         [6, 9, 18, 21, 28], [3, 6, 11, 12, 29], [0, 9, 15, 20, 24],
         [12, 14, 19, 25, 29], [1, 23, 27, 28, 31], [5, 12, 17, 27, 31],
         [4, 5, 6, 17, 20], [0, 3, 14, 21, 23], [1, 7, 11, 22, 24],
         [5, 6, 7, 15, 26], [0, 7, 16, 22, 30], [1, 18, 22, 29, 31],
         [6, 7, 16, 19, 27], [0, 4, 6, 10, 23]]

CANDS = [("r4_gl5_f6", 6), ("r4_gl5_f8", 8)]


def gen(name, rounds):
    L = []
    L.append(f"// Flat unrolled {name}: Goldreich 5-local F Feistel, {rounds} rounds.")
    L.append(f"module {name}")
    L.append("    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
    L.append("    function automatic [31:0] F32(input [31:0] h);")
    L.append("        begin")
    for j, (a, b, c, d, e) in enumerate(_TAPS):
        L.append(f"            F32[{j}] = h[{a}] ^ h[{b}] ^ h[{c}] ^ (h[{d}] & h[{e}]);")
    L.append("        end")
    L.append("    endfunction")
    L.append("    wire [31:0] klo = key[31:0];")
    for i in range(rounds):
        rr = (7 * (i + 1)) % 32
        const = ((i + 1) * 0x9E3779B9) & 0xFFFFFFFF
        rot = "klo" if rr == 0 else f"{{klo[{31-rr}:0], klo[31:{32-rr}]}}"
        L.append(f"    wire [31:0] rk{i} = {rot} ^ 32'h{const:08X};")
    L.append("    wire [63:0] s0 = val ^ key;")
    for i in range(rounds):
        L.append(f"    wire [63:0] s{i+1} = {{s{i}[31:0], s{i}[63:32] ^ F32(s{i}[31:0] ^ rk{i})}}" + ";")
    L.append(f"    assign out = s{rounds};")
    L.append("endmodule")
    path = os.path.join(OUT, f"{name}.v")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {path}")


for name, rounds in CANDS:
    gen(name, rounds)

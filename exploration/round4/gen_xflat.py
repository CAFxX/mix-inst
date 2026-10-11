"""Generate fully-flat, unrolled Verilog for the X family (AND-Feistel).

No unpacked arrays, no generate blocks, no submodule instantiation -- so the
yosys-mapped netlist has plain (non-escaped) net names that analyze2.py can
parse. Round keys and rotation amounts are computed in Python and emitted as
explicit wires/constants.
"""
import os

R4 = "/home/hatch/workspace/mix/exploration/round4"
OUT = os.path.join(R4, "rtl", "flat2")
os.makedirs(OUT, exist_ok=True)

# (name, ftype, rounds)
CANDS = [
    ("r4_simeck_f10", 0, 10),
    ("r4_simon_f10", 1, 10),
    ("r4_simeck_f12", 0, 12),
    ("r4_dbland_f8", 2, 8),
]

F32_BODY = {
    0: """    function automatic [31:0] F32(input [31:0] h);
        reg [31:0] r1, r5, r2;
        begin
            r1 = {h[30:0], h[31]};
            r5 = {h[26:0], h[31:27]};
            r2 = {h[29:0], h[31:30]};
            F32 = (r1 & r5) ^ r2;
        end
    endfunction""",
    1: """    function automatic [31:0] F32(input [31:0] h);
        reg [31:0] r1, r8, r2;
        begin
            r1 = {h[30:0], h[31]};
            r8 = {h[23:0], h[31:24]};
            r2 = {h[29:0], h[31:30]};
            F32 = (r1 & r8) ^ r2;
        end
    endfunction""",
    2: """    function automatic [31:0] F32(input [31:0] h);
        reg [31:0] r1, r5, r2, r7, r13, r11;
        begin
            r1  = {h[30:0], h[31]};
            r5  = {h[26:0], h[31:27]};
            r2  = {h[29:0], h[31:30]};
            r7  = {h[24:0], h[31:25]};
            r13 = {h[18:0], h[31:19]};
            r11 = {h[20:0], h[31:21]};
            F32 = ((r1 & r5) ^ r2) ^ ((r7 & r13) ^ r11);
        end
    endfunction""",
}


def gen(name, ftype, rounds):
    L = []
    L.append(f"// Flat unrolled {name}: AND-Feistel ftype={ftype}, rounds={rounds}.")
    L.append(f"// No arrays/generate/hierarchy: plain net names for analyze2.py.")
    L.append(f"module {name}")
    L.append("    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
    L.append(F32_BODY[ftype])
    L.append("    wire [31:0] klo = key[31:0];")
    # round keys: rk_i = rotl32(klo, 13*(i+1) % 32) ^ (i+1)*0x9E3779B9
    for i in range(rounds):
        rr = (7 * (i + 1)) % 32
        const = ((i + 1) * 0x9E3779B9) & 0xFFFFFFFF
        if rr == 0:
            rot = "klo"
        else:
            rot = f"{{klo[{31-rr}:0], klo[31:{32-rr}]}}"
        L.append(f"    wire [31:0] rk{i} = {rot} ^ 32'h{const:08X};")
    # state chain: s[i+1] = {L_i, R_i ^ F(L_i) ^ rk_i} where s = {R,L}
    L.append("    wire [63:0] s0 = val ^ key;")
    for i in range(rounds):
        L.append(f"    wire [63:0] s{i+1} = {{s{i}[31:0], s{i}[63:32] ^ F32(s{i}[31:0]) ^ rk{i}}};")
    L.append(f"    assign out = s{rounds};")
    L.append("endmodule")
    path = os.path.join(OUT, f"{name}.v")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {path}")


for name, ftype, rounds in CANDS:
    gen(name, ftype, rounds)

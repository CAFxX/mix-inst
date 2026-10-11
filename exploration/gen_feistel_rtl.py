"""Generate function-free Batch-C Feistel RTL.

Why: yosys elaborates Verilog `function`s into dollar-func-hierarchical wires
and `case`-based S-boxes into $memrd ROMs; both emit mapped-netlist identifier
forms that exploration/analyze2.py cannot parse (regexes assume word-char
names, numeric-only selects). This generator emits fully-unrolled,
function-free, case-free RTL: S-boxes as 4x 16-bit LUT planes + 16:1 muxes
(ABC optimizes), P32/rotations as pure rewiring, rounds as flat wire assigns.
The mapped netlist then contains only ports and _NNNN_ auto names.

Tables are imported from models/_feistel_common (same source as the models).
"""
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from models._feistel_common import PRESENT_SBOX, GIFT_SBOX

RC32 = 0x9E3779B9


def planes(table):
    """ps[k] = 16-bit int; bit i of ps[k] = bit k of table[i]."""
    assert len(set(table)) == 16
    ps = []
    for k in range(4):
        v = 0
        for i in range(16):
            if (table[i] >> k) & 1:
                v |= 1 << i
        ps.append(v)
    return ps


P32 = [(8 * i) % 31 for i in range(31)] + [31]
assert len(set(P32)) == 32


def rotl_expr(x, r):
    r %= 32
    assert r != 0, "rotation by 0 needs a guard; not used here"
    return f"(({x} << {r}) | ({x} >> {32 - r}))"


def gen(name, rounds, ftype, constr_line):
    assert ftype in ("present", "gift", "xor")
    table = {"present": PRESENT_SBOX, "gift": GIFT_SBOX}.get(ftype)
    ps = planes(table) if table else None

    L = []
    A = L.append
    A(f"// {name}: {rounds}-round Feistel, 32-bit halves. (Batch C)")
    A(f"// {constr_line}")
    A("// S-box via 4x 16-bit LUT planes + 16:1 mux per output bit (function-free,")
    A("// case-free: ABC optimizes; mapped netlist has no $func$/ROM hierarchy).")
    A(f"module {name}(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);")
    if ps:
        sname = "PRESENT" if ftype == "present" else "GIFT"
        A(f"  // {sname} S-box bit planes: PLANEk[i] = bit k of SBOX[i]")
        for k in range(4):
            A(f"  localparam [15:0] PLANE{k} = 16'h{ps[k]:04X};")
    A("  wire [31:0] klo = key[31:0];")
    A("  wire [31:0] khi = key[63:32];")
    A("  wire [31:0] L0 = val[31:0] ^ klo;")
    A("  wire [31:0] R0 = val[63:32] ^ khi;")
    for i in range(rounds):
        j = i + 1
        rl, rh = (3 * j) % 32, (5 * j) % 32
        rc = (j * RC32) & 0xFFFFFFFF
        A(f"  // round {j}: rk = ROTL32(klo,{rl}) ^ ROTL32(khi,{rh}) ^ 0x{rc:08X}")
        A(f"  wire [31:0] rk{i} = {rotl_expr('klo', rl)} ^ {rotl_expr('khi', rh)} ^ 32'h{rc:08X};")
        if ftype == "xor":
            A(f"  wire [31:0] t{i} = R{i} ^ rk{i};")
            A(f"  wire [31:0] f{i} = t{i} ^ {rotl_expr(f't{i}', 7)} ^ {rotl_expr(f't{i}', 19)};")
        else:
            A(f"  wire [31:0] fx{i} = R{i} ^ rk{i};")
            for s in range(8):
                A(f"  wire [3:0] n{i}_{s} = fx{i}[{4*s+3}:{4*s}];")
            A(f"  wire [31:0] sb{i};")
            for s in range(8):
                for k in range(4):
                    A(f"  assign sb{i}[{4*s+k}] = PLANE{k}[n{i}_{s}];")
            A(f"  wire [31:0] f{i};  // P32: f[P32(b)] = sb[b]")
            for b in range(32):
                A(f"  assign f{i}[{P32[b]}] = sb{i}[{b}];")
        A(f"  wire [31:0] L{j} = R{i};")
        A(f"  wire [31:0] R{j} = L{i} ^ f{i};")
    A("  // no final swap; out = {Rn^ROTL32(khi,7), Ln^ROTL32(klo,7)}")
    A(f"  assign out = {{ R{rounds} ^ {rotl_expr('khi', 7)}, L{rounds} ^ {rotl_expr('klo', 7)} }};")
    A("endmodule")
    A("")
    return "\n".join(L)


CANDIDATES = {
    # name: (rounds, ftype, construction one-liner)
    "feistel6_sbox": (
        6, "present",
        "F(x,rk)=P32(SBOX8(x^rk)), 8x PRESENT S-box (table borrowed from PRESENT only, "
        "not the cipher), P32(i)=8*i mod 31 (i<31), P32(31)=31."),
    "feistel7_sbox": (
        7, "present",
        "F(x,rk)=P32(SBOX8(x^rk)), 8x PRESENT S-box (borrowed table only), "
        "P32(i)=8*i mod 31 (i<31), P32(31)=31; 7-round boundary probe."),
    "feistel8_xor": (
        8, "xor",
        "F(x,rk)=(x^rk)^ROTL32(x,7)^ROTL32(x,19): near-affine (linear-plus-keyxor) F, "
        "CRYPTOGRAPHICALLY WEAK BY CONSTRUCTION; boundary-mapping probe only."),
    "feistel6_giftsbox": (
        6, "gift",
        "F(x,rk)=P32(SBOX8(x^rk)), 8x GIFT S-box GS=1A4C6F392DB7508E (Table 3, Banik et "
        "al., CHES 2017 primary paper; borrowed table only), P32 as above."),
}

if __name__ == "__main__":
    for name, (rounds, ftype, cline) in CANDIDATES.items():
        path = f"/home/hatch/workspace/mix/exploration/rtl/{name}.v"
        with open(path, "w") as f:
            f.write(gen(name, rounds, ftype, cline))
        print(f"wrote {path}")

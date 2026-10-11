"""Generate fully-flat, unrolled Verilog for the HYBRID track (round 4)."""
import os

R4 = "/home/hatch/workspace/mix/exploration/round4"
OUT = os.path.join(R4, "rtl", "flat2")
os.makedirs(OUT, exist_ok=True)

PERM = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
C_MUL1 = 0x9E3779B97F4A7C15
C_MUL2 = 0xBF58476D1CE4E5B9
C_CLMUL = 0xA5A5A5A5A5A5A5A7
C_LM1 = 0x9E37
C_LM2 = 0x7F4B

S1_DNF = """    function automatic [3:0] sbox(input [3:0] x);
        reg y0, y1, y2, y3;
        begin
            y0 = ( x[2] & ~x[0]) | (x[3] & ~x[0]) | (~x[2] & ~x[1] & x[0]);
            y1 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[2] & ~x[0]) | (x[3] & ~x[2] & x[1]) | (~x[3] & x[1] & ~x[0]) | (x[3] & x[2] & x[0]);
            y2 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[1] & x[0]) | (x[3] & ~x[2] & x[0]) | (x[2] & x[1] & ~x[0]);
            y3 = (x[2] & x[1]) | (x[2] & x[0]) | (x[3] & ~x[2] & ~x[0]);
            sbox = {y3, y2, y1, y0};
        end
    endfunction"""


def sbox16_fn():
    L = [S1_DNF]
    L.append("    function automatic [63:0] sbox16(input [63:0] x);")
    L.append("        begin")
    terms = ", ".join(f"sbox(x[{4*s+3}:{4*s}])" for s in range(15, -1, -1))
    L.append(f"            sbox16 = {{{terms}}};")
    L.append("        end")
    L.append("    endfunction")
    return L


def sbox8_fn():
    L = [S1_DNF]
    L.append("    function automatic [31:0] sbox8(input [31:0] x);")
    L.append("        begin")
    terms = ", ".join(f"sbox(x[{4*s+3}:{4*s}])" for s in range(7, -1, -1))
    L.append(f"            sbox8 = {{{terms}}};")
    L.append("        end")
    L.append("    endfunction")
    return L


def midori_fns():
    L = []
    L.append("    function automatic [63:0] midori_M(input [63:0] x);")
    L.append("        reg [3:0] n0,n1,n2,n3;")
    L.append("        reg [63:0] y;")
    L.append("        begin")
    # fully unrolled per column (c=0..3), nibbles explicit
    for c in range(4):
        b = 16 * c
        L.append(f"            n0 = x[{b+3}:{b}]; n1 = x[{b+7}:{b+4}];")
        L.append(f"            n2 = x[{b+11}:{b+8}]; n3 = x[{b+15}:{b+12}];")
        L.append(f"            y[{b+3}:{b}]    = n1^n2^n3;")
        L.append(f"            y[{b+7}:{b+4}]   = n0^n2^n3;")
        L.append(f"            y[{b+11}:{b+8}]  = n0^n1^n3;")
        L.append(f"            y[{b+15}:{b+12}] = n0^n1^n2;")
    L.append("            midori_M = y;")
    L.append("        end")
    L.append("    endfunction")
    # shuffle as explicit concat (PERM: out_nib[i] = in_nib[PERM[i]])
    terms = ", ".join(f"x[{4*PERM[i]+3}:{4*PERM[i]}]" for i in range(15, -1, -1))
    L.append("    function automatic [63:0] shuffle(input [63:0] x);")
    L.append("        begin")
    L.append(f"            shuffle = {{{terms}}};")
    L.append("        end")
    L.append("    endfunction")
    return L


def tchi64_fn():
    # triangular chi, explicit unrolled
    L = ["    function automatic [63:0] tchi64(input [63:0] x);",
         "        begin"]
    terms = []
    for i in range(61, -1, -1):
        terms.append(f"(x[{i}] ^ ((~x[{i+1}]) & x[{i+2}]))")
    # build concat: {y63, y62, y61, ..., y0} = {x[63], x[62], (terms)}
    body = ", ".join(["x[63]", "x[62]"] + terms)
    L.append(f"            tchi64 = {{{body}}};")
    L.append("        end")
    L.append("    endfunction")
    return L


def cchi32_fn():
    L = ["    function automatic [31:0] cchi32(input [31:0] x);",
         "        reg [31:0] r1, r2;",
         "        begin",
         "            r1 = {x[30:0], x[31]};",
         "            r2 = {x[29:0], x[31:30]};",
         "            cchi32 = x ^ ((~r1) & r2);",
         "        end",
         "    endfunction"]
    return L


def clmul_wires(xname, C, yname):
    # y[k] = ^(x & MASK_k), MASK_k bit i set iff C[k-i]=1
    L = []
    for k in range(64):
        mask = 0
        for i in range(k + 1):
            if (C >> (k - i)) & 1:
                mask |= (1 << i)
        L.append(f"    wire [{k}:{k}] {yname}{k} = ^({xname} & 64'h{mask:016X});")
    # concat into yname
    terms = ", ".join(f"{yname}{k}" for k in range(63, -1, -1))
    L.append(f"    wire [63:0] {yname} = {{{terms}}};")
    return L


def rotl64(xname, r, yname):
    r %= 64
    if r == 0:
        return [f"    wire [63:0] {yname} = {xname};"]
    return [f"    wire [63:0] {yname} = {{{xname}[{63-r}:0], {xname}[63:{64-r}]}};"]


def rk_wires(keyname, idx, yname):
    # rk = ROTL64(key,13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15
    r = (13 * (idx + 1)) % 64
    c = ((idx + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    rot = f"{{{keyname}[{63-r}:0], {keyname}[63:{64-r}]}}" if r else keyname
    return [f"    wire [63:0] {yname} = {rot} ^ 64'h{c:016X};"]


def gen_header(name, fns):
    L = [f"// Hybrid {name}: see r4_hybrid.py", f"module {name}",
         "    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);"]
    L.extend(fns)
    return L


def write(name, lines):
    p = os.path.join(OUT, name + ".v")
    open(p, "w").write("\n".join(lines) + "\n")
    print("wrote", p)


# ---- H1: sandwich2 ----
def gen_sandwich2():
    name = "r4_h_sandwich2"
    L = gen_header(name, sbox16_fn() + tchi64_fn())
    L.append("    wire [63:0] x0 = val ^ key;")
    L += rk_wires("key", 0, "rk0")
    L += rk_wires("key", 1, "rk1")
    L += rk_wires("key", 2, "rk2")
    L.append("    wire [63:0] s0 = sbox16(x0 ^ rk0);")
    L.append("    wire [63:0] t0 = tchi64(s0);")
    L += rotl64("t0", 13, "r0")
    L.append("    wire [63:0] s1 = sbox16(r0 ^ rk1);")
    L.append("    wire [63:0] t1 = tchi64(s1);")
    L += rotl64("t1", 13, "r1")
    L.append("    assign out = r1 ^ rk2;")
    L.append("endmodule")
    write(name, L)


# ---- H2: chifeist6 ----
def gen_chifeist6():
    name = "r4_h_chifeist6"
    L = gen_header(name, cchi32_fn())
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [31:0] L0 = x0[63:32];")
    L.append("    wire [31:0] R0 = x0[31:0];")
    for i in range(7):
        L += rk_wires("key", i, f"rk{i}")
    # 6 rounds
    for i in range(6):
        Li, Ri = f"L{i}", f"R{i}"
        L.append(f"    wire [31:0] F{i} = cchi32({Ri} ^ rk{i}[31:0]);")
        L.append(f"    wire [31:0] L{i+1} = {Ri};")
        L.append(f"    wire [31:0] R{i+1} = {Li} ^ F{i};")
    L.append("    assign out = {L6 ^ rk6[63:32], R6 ^ rk6[31:0]};")
    L.append("endmodule")
    write(name, L)


# ---- H3: multspn ----
def gen_multspn():
    name = "r4_h_multspn"
    L = gen_header(name, sbox16_fn() + midori_fns())
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append(f"    wire [63:0] m0 = x0 * 64'h{C_MUL1:016X};")
    L += rk_wires("key", 0, "rk0")
    L += rk_wires("key", 1, "rk1")
    L += rk_wires("key", 2, "rk2")
    L.append("    wire [63:0] s0 = shuffle(midori_M(sbox16(m0 ^ rk0)));")
    L.append("    wire [63:0] s1 = shuffle(midori_M(sbox16(s0 ^ rk1)));")
    L.append("    assign out = s1 ^ rk2;")
    L.append("endmodule")
    write(name, L)


# ---- H4: spnmult ----
def gen_spnmult():
    name = "r4_h_spnmult"
    L = gen_header(name, sbox16_fn() + midori_fns())
    L.append("    wire [63:0] x0 = val ^ key;")
    L += rk_wires("key", 0, "rk0")
    L += rk_wires("key", 1, "rk1")
    L += rk_wires("key", 2, "rk2")
    L.append("    wire [63:0] s0 = shuffle(midori_M(sbox16(x0 ^ rk0)));")
    L.append("    wire [63:0] s1 = shuffle(midori_M(sbox16(s0 ^ rk1)));")
    L.append(f"    wire [63:0] m0 = s1 * 64'h{C_MUL2:016X};")
    L.append("    assign out = m0 ^ rk2;")
    L.append("endmodule")
    write(name, L)


# ---- H5: clmulspn ----
def gen_clmulspn():
    name = "r4_h_clmulspn"
    L = gen_header(name, sbox16_fn())
    L.append("    wire [63:0] x0 = val ^ key;")
    L += rk_wires("key", 0, "rk0")
    L += rk_wires("key", 1, "rk1")
    L += rk_wires("key", 2, "rk2")
    L.append("    wire [63:0] s0 = sbox16(x0 ^ rk0);")
    L += clmul_wires("s0", C_CLMUL, "c0")
    L += rotl64("c0", 17, "r0")
    L.append("    wire [63:0] s1 = sbox16(r0 ^ rk1);")
    L += clmul_wires("s1", C_CLMUL, "c1")
    L += rotl64("c1", 17, "r1")
    L.append("    assign out = r1 ^ rk2;")
    L.append("endmodule")
    write(name, L)


# ---- H6: laimassey ----
def gen_laimassey():
    name = "r4_h_laimassey"
    L = gen_header(name, [])
    L.append("    // F(z) = ((z_lo*C1)^(z_hi*C2)) ^ ROTL32(z,9)")
    L.append("    function automatic [31:0] lmf(input [31:0] z);")
    L.append("        reg [31:0] p;")
    L.append("        begin")
    L.append(f"            p = ((z[15:0] * 16'h{C_LM1:04X}) ^ (z[31:16] * 16'h{C_LM2:04X}));")
    L.append("            lmf = p ^ {z[22:0], z[31:23]};")
    L.append("        end")
    L.append("    endfunction")
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [31:0] L0 = x0[63:32];")
    L.append("    wire [31:0] R0 = x0[31:0];")
    for i in range(4):
        L += rk_wires("key", i, f"rk{i}")
    for i in range(3):
        L.append(f"    wire [31:0] T{i} = lmf((L{i} ^ R{i} ^ rk{i}[31:0]));")
        L.append(f"    wire [31:0] La{i} = L{i} ^ T{i};")
        L.append(f"    wire [31:0] Ra{i} = R{i} ^ T{i};")
        L.append(f"    wire [31:0] L{i+1} = Ra{i};")
        L.append(f"    wire [31:0] R{i+1} = La{i};")
    L.append("    assign out = {L3 ^ rk3[63:32], R3 ^ rk3[31:0]};")
    L.append("endmodule")
    write(name, L)


# ---- H7: xorspn ----
def gen_xorspn():
    name = "r4_h_xorspn"
    L = gen_header(name, sbox16_fn() + midori_fns())
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [63:0] xs1 = x0 ^ (x0 >> 12);")
    L.append("    wire [63:0] xs2 = xs1 ^ (xs1 << 25);")
    L.append("    wire [63:0] xs3 = xs2 ^ (xs2 >> 27);")
    L += rk_wires("key", 0, "rk0")
    L += rk_wires("key", 1, "rk1")
    L += rk_wires("key", 2, "rk2")
    L.append("    wire [63:0] s0 = shuffle(midori_M(sbox16(xs3 ^ rk0)));")
    L.append("    wire [63:0] s1 = shuffle(midori_M(sbox16(s0 ^ rk1)));")
    L.append("    assign out = s1 ^ rk2;")
    L.append("endmodule")
    write(name, L)


# ---- H8: heterofeist ----
def gen_heterofeist():
    name = "r4_h_heterofeist"
    L = gen_header(name, sbox8_fn() + cchi32_fn())
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [31:0] L0 = x0[63:32];")
    L.append("    wire [31:0] R0 = x0[31:0];")
    for i in range(7):
        L += rk_wires("key", i, f"rk{i}")
    for i in range(6):
        Li, Ri = f"L{i}", f"R{i}"
        if i % 2 == 0:
            L.append(f"    wire [31:0] F{i} = sbox8({Ri} ^ rk{i}[31:0]);")
        else:
            L.append(f"    wire [31:0] F{i} = cchi32({Ri} ^ rk{i}[31:0]);")
        L.append(f"    wire [31:0] L{i+1} = {Ri};")
        L.append(f"    wire [31:0] R{i+1} = {Li} ^ F{i};")
    L.append("    assign out = {L6 ^ rk6[63:32], R6 ^ rk6[31:0]};")
    L.append("endmodule")
    write(name, L)


def gen_sandwich3():
    name = "r4_h_sandwich3"
    L = gen_header(name, sbox16_fn() + tchi64_fn())
    L.append("    wire [63:0] x0 = val ^ key;")
    for i in range(4):
        L += rk_wires("key", i, f"rk{i}")
    L.append("    wire [63:0] s0 = sbox16(x0 ^ rk0);")
    L.append("    wire [63:0] t0 = tchi64(s0);")
    L += rotl64("t0", 13, "r0")
    L.append("    wire [63:0] s1 = sbox16(r0 ^ rk1);")
    L.append("    wire [63:0] t1 = tchi64(s1);")
    L += rotl64("t1", 13, "r1")
    L.append("    wire [63:0] s2 = sbox16(r1 ^ rk2);")
    L.append("    wire [63:0] t2 = tchi64(s2);")
    L += rotl64("t2", 13, "r2")
    L.append("    assign out = r2 ^ rk3;")
    L.append("endmodule")
    write(name, L)


def gen_xorspn3():
    name = "r4_h_xorspn3"
    L = gen_header(name, sbox16_fn() + midori_fns())
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [63:0] xs1 = x0 ^ (x0 >> 12);")
    L.append("    wire [63:0] xs2 = xs1 ^ (xs1 << 25);")
    L.append("    wire [63:0] xs3 = xs2 ^ (xs2 >> 27);")
    for i in range(4):
        L += rk_wires("key", i, f"rk{i}")
    L.append("    wire [63:0] s0 = shuffle(midori_M(sbox16(xs3 ^ rk0)));")
    L.append("    wire [63:0] s1 = shuffle(midori_M(sbox16(s0 ^ rk1)));")
    L.append("    wire [63:0] s2 = shuffle(midori_M(sbox16(s1 ^ rk2)));")
    L.append("    assign out = s2 ^ rk3;")
    L.append("endmodule")
    write(name, L)


if __name__ == "__main__":
    gen_sandwich2()
    gen_chifeist6()
    gen_multspn()
    gen_spnmult()
    gen_clmulspn()
    gen_laimassey()
    gen_xorspn()
    gen_heterofeist()
    gen_sandwich3()
    gen_xorspn3()

"""Round 6 Feistel RTL generator: flat, unrolled Verilog.

Feistel with SPN F-function (2-round SPN on 32 bits).
S-boxes as case statements (Yosys/ABC optimizes).
"""
import os, sys

R6 = "/home/hatch/workspace/mix/exploration/round6"
OUT = os.path.join(R6, "rtl")
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.join(R6, "models"))
from r6 import SBOXES

def sbox_case(name, table):
    lines = [f"function automatic [3:0] sbox_{name}(input [3:0] x);",
             "    begin",
             "        case (x)"]
    for i, v in enumerate(table):
        lines.append(f"            4'h{i:X}: sbox_{name} = 4'h{v:X};")
    lines += [f"            default: sbox_{name} = 4'h0;",
              "        endcase",
              "    end",
              "endfunction"]
    return "\n".join(lines)

def gen_feistel(name, nrounds, sbox_name):
    sb = SBOXES[sbox_name]
    lines = [
        f"// {name}: {nrounds}-round Feistel, F=2r SPN ({sbox_name})",
        f"module {name}(",
        "    input  [63:0] val,",
        "    input  [63:0] key,",
        "    output [63:0] out",
        ");",
        "",
        sbox_case(sbox_name, sb),
        "",
        "// Round key: rotl(k, 13*(i+1)) XOR ((i+1)*0x9E3779B97F4A7C15)",
        "function automatic [63:0] rk(input [63:0] k, input integer i);",
        "    integer r;",
        "    reg [63:0] rc;",
        "    begin",
        "        r = (13 * (i + 1)) % 64;",
        "        rc = (i + 1) * 64'h9E3779B97F4A7C15;",
        "        if (r == 0)",
        "            rk = k ^ rc;",
        "        else",
        "            rk = ((k << r) | (k >> (64 - r))) ^ rc;",
        "    end",
        "endfunction",
        "",
        "// F-function: 2-round SPN on 32 bits",
        "function automatic [31:0] F(input [31:0] R, input [31:0] rk32);",
        "    reg [31:0] t;",
        "    integer j;",
        "    begin",
        "        // S-box layer 1",
        "        for (j = 0; j < 8; j = j + 1)",
        f"            t[4*j+:4] = sbox_{sbox_name}(R[4*j+:4]);",
        "        // Diffusion: rotate-xor",
        "        t = t ^ {t[24:0], t[31:25]} ^ {t[18:0], t[31:19]};",
        "        // S-box layer 2",
        "        for (j = 0; j < 8; j = j + 1)",
        f"            t[4*j+:4] = sbox_{sbox_name}(t[4*j+:4]);",
        "        F = t ^ rk32;",
        "    end",
        "endfunction",
        "",
        "reg [31:0] L, R;",
        "reg [31:0] Lt, Rt;",
        "reg [63:0] rkv;",
        "integer i;",
        "always @(*) begin",
        "    // Initial whitening",
        "    L = val[63:32] ^ key[63:32];",
        "    R = val[31:0]  ^ key[31:0];",
        "    // Feistel rounds",
        f"    for (i = 0; i < {nrounds}; i = i + 1) begin",
        "        rkv = rk(key, i+1);",
        "        Lt = R;",
        "        Rt = L ^ F(R, rkv[31:0]);",
        "        L = Lt;",
        "        R = Rt;",
        "    end",
        "end",
        "",
        "assign out = {R, L};",
        "",
        "endmodule",
    ]
    path = os.path.join(OUT, f"r6_{name}.v")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {path}")

if __name__ == "__main__":
    gen_feistel("r6_feist8_spn", 8, "s1")
    gen_feistel("r6_feist12_spn", 12, "s1")
    gen_feistel("r6_feist8_present", 8, "present")

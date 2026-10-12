#!/usr/bin/env python3
"""Generate Verilog for R1 hierarchical 3-stage (a^b)^(c&d)."""

def gen_r1_hier():
    lines = []
    lines.append("module r1_hier (input [63:0] x, output [63:0] y);")
    lines.append("  wire [63:0] s1, s2;")
    lines.append("  // Stage 1: out[i] = (in[i]^in[i+1]) ^ (in[i+2]&in[i+3])")
    lines.append("  genvar i;")
    lines.append("  generate")
    lines.append("    for (i = 0; i < 64; i = i + 1) begin : st1")
    lines.append("      assign s1[i] = (x[i] ^ x[(i+1)%64]) ^ (x[(i+2)%64] & x[(i+3)%64]);")
    lines.append("    end")
    lines.append("    // Stage 2: out[i] = (s1[i]^s1[i+16]) ^ (s1[i+32]&s1[i+48])")
    lines.append("    for (i = 0; i < 64; i = i + 1) begin : st2")
    lines.append("      assign s2[i] = (s1[i] ^ s1[(i+16)%64]) ^ (s1[(i+32)%64] & s1[(i+48)%64]);")
    lines.append("    end")
    lines.append("    // Stage 3: out[i] = (s2[i]^s2[i+4]) ^ (s2[i+8]&s2[i+12])")
    lines.append("    for (i = 0; i < 64; i = i + 1) begin : st3")
    lines.append("      assign y[i] = (s2[i] ^ s2[(i+4)%64]) ^ (s2[(i+8)%64] & s2[(i+12)%64]);")
    lines.append("    end")
    lines.append("  endgenerate")
    lines.append("endmodule")
    return "\n".join(lines)

if __name__ == "__main__":
    verilog = gen_r1_hier()
    with open("/home/hatch/workspace/mix/exploration/adder_lat/recursive/r1_hier.v", "w") as f:
        f.write(verilog + "\n")
    print("Generated r1_hier.v")
    # Quick sanity: count assigns
    print(f"Lines: {len(verilog.splitlines())}")

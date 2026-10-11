// Wave-14 calibration: S0 delay of word-level primitives via run_synth.py.
// Each module is a bare combinational word-level op. The bare-add64 number
// (w_add64) is the "adder-like" north-star target.
module w_add64(input [63:0] a, b, output [63:0] o);
  assign o = a + b;
endmodule

module w_add32x2(input [63:0] a, b, output [63:0] o);
  wire [31:0] lo = a[31:0] + b[31:0];
  wire [31:0] hi = a[63:32] + b[63:32];
  assign o = {hi, lo};
endmodule

module w_add16x4(input [63:0] a, b, output [63:0] o);
  wire [15:0] l0 = a[15:0]  + b[15:0];
  wire [15:0] l1 = a[31:16] + b[31:16];
  wire [15:0] l2 = a[47:32] + b[47:32];
  wire [15:0] l3 = a[63:48] + b[63:48];
  assign o = {l3, l2, l1, l0};
endmodule

// CSA-inference probes: if Yosys fuses these, add3/add4 cost ~ add64 + ~2u/extra op.
module w_add3(input [63:0] a, b, c, output [63:0] o);
  assign o = a + b + c;
endmodule

module w_add4(input [63:0] a, b, c, d, output [63:0] o);
  assign o = a + b + c + d;
endmodule

module w_mul16(input [63:0] a, b, output [63:0] o);
  assign o = a[15:0] * b[15:0];
endmodule

module w_mul32(input [63:0] a, b, output [63:0] o);
  assign o = a[31:0] * b[31:0];
endmodule

// Multiply by odd constant = shift-add network, bijective on 64 bits.
module w_mulc64(input [63:0] a, output [63:0] o);
  assign o = a * 64'h9E3779B97F4A7C15;
endmodule

// GF(2^64) multiply by fixed const, reduction poly x^64+x^4+x^3+x+1.
// Linear over GF(2), bijective, full-word diffusion in one shot.
module w_gf64(input [63:0] a, output [63:0] o);
  parameter [63:0] C = 64'h9E3779B97F4A7C15;
  wire [63:0] acc [0:64];
  assign acc[0] = 64'd0;
  genvar i;
  generate
    for (i = 0; i < 64; i = i + 1) begin : gfm
      wire [63:0] xt = {acc[i][62:0], 1'b0} ^ (acc[i][63] ? 64'h1B : 64'b0);
      assign acc[i+1] = xt ^ (C[63-i] ? a : 64'b0);
    end
  endgenerate
  assign o = acc[64];
endmodule

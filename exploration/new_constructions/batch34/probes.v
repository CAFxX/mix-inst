// Batch-34 S0 cost probes (track 6, 2026-10-11).
// Single combinational stages, 64-bit in/out. Rotation = wiring (free).
// Goal: per-stage delay for dense nonlinear stage forms.
// Positive control: stg_and1 must reproduce ~3.3u (al_and6a/b33 per-stage).

function [63:0] rotl64;
  input [63:0] x;
  input integer r;
  begin
    rotl64 = (x << r) | (x >> (64 - r));
  end
endfunction

// (1) baseline: x ^= (ra&rb)^rc  -- expect ~3.3u
module stg_and1(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  assign y = x ^ (ra & rb) ^ rc;
endmodule

// (2) AND3+mask: x ^= (ra&rb&rc)^rd  -- expect ~4.0u (b30 wand3_5c class)
module stg_a3(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  wire [63:0] rd = rotl64(x, 41);
  assign y = x ^ (ra & rb & rc) ^ rd;
endmodule

// (3) dual-AND3+mask: x ^= (ra&rb&rc)^(rd&re&rf)^rg  -- 6 probes/stage, NEW
module stg_d2a3(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  wire [63:0] rd = rotl64(x, 41);
  wire [63:0] re = rotl64(x, 11);
  wire [63:0] rf = rotl64(x, 52);
  wire [63:0] rg = rotl64(x, 7);
  assign y = x ^ (ra & rb & rc) ^ (rd & re & rf) ^ rg;
endmodule

// (4) AOI21+mask: x ^= ~((ra&rb)|rc) ^ rd  -- complex-gate probe, NEW
module stg_aoi(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  wire [63:0] rd = rotl64(x, 41);
  assign y = x ^ ~((ra & rb) | rc) ^ rd;
endmodule

// (5) narrow-add control: 4x parallel 16-bit adds + rotation XOR.
// ARX re-test trigger probe: is ONE parallel narrow-add layer cost-viable?
module stg_add16(input [63:0] x, output [63:0] y);
  wire [15:0] s0 = x[15:0]   + 16'h9e37;
  wire [15:0] s1 = x[31:16]  + 16'h79b9;
  wire [15:0] s2 = x[47:32]  + 16'h7f4a;
  wire [15:0] s3 = x[63:48]  + 16'h7c15;
  wire [63:0] w = {s3, s2, s1, s0};
  assign y = w ^ rotl64(w, 13);
endmodule

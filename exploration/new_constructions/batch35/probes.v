// Batch-35 S0 cost probes (track 6, 2026-10-11).
// Single combinational stages, 64-bit in/out. Shifts/rotations = wiring (free).
// Goal: per-stage delay for the shift-AND stage form.
// Positive control: stg_and1 must reproduce ~3.3u (b33 per-stage).

function [63:0] rotl64;
  input [63:0] x;
  input integer r;
  begin
    rotl64 = (x << r) | (x >> (64 - r));
  end
endfunction

// (1) baseline: x ^= (ra&rb)^rc  -- expect ~3.3u (positive control)
module stg_and1(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  assign y = x ^ (ra & rb) ^ rc;
endmodule

// (2) shift-AND + rotation mask: x ^= ((x>>a)&(x<<b)) ^ rotl(x,c)
module stg_shand(input [63:0] x, output [63:0] y);
  wire [63:0] sa = x >> 5;
  wire [63:0] sb = x << 9;
  wire [63:0] rc = rotl64(x, 37);
  assign y = x ^ (sa & sb) ^ rc;
endmodule

// (3) shift-AND, no mask (arm D ablation): x ^= ((x>>a)&(x<<b))
module stg_shand_nm(input [63:0] x, output [63:0] y);
  wire [63:0] sa = x >> 5;
  wire [63:0] sb = x << 9;
  assign y = x ^ (sa & sb);
endmodule

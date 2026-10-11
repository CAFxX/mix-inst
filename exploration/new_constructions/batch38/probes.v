// Batch-38 S0 cost probes (track 6, 2026-10-11).
// Single combinational stages for the asymmetric/symmetric nested shift-AND
// forms. Gate count = b33c's (XOR2+AND2+XOR2); expect ~4.0u DUT-relative.

function [63:0] rotl64;
  input [63:0] x;
  input integer r;
  begin
    rotl64 = (x << r) | (x >> (64 - r));
  end
endfunction

// nestA: x ^= ((x>>a)^(x<<b)) & (x>>c)
module stg_nestA(input [63:0] x, output [63:0] y);
  wire [63:0] pa = x >> 5;
  wire [63:0] qb = x << 9;
  wire [63:0] rc = x >> 13;
  assign y = x ^ ((pa ^ qb) & rc);
endmodule

// nestB: x ^= (x>>a) & ((x<<b) ^ rotl(x,c))
module stg_nestB(input [63:0] x, output [63:0] y);
  wire [63:0] pa = x >> 5;
  wire [63:0] qb = x << 9;
  wire [63:0] rc = rotl64(x, 37);
  assign y = x ^ (pa & (qb ^ rc));
endmodule

// nestS: x ^= ((x>>a)^(x<<b)) & ((x>>c)^(x<<d))
module stg_nestS(input [63:0] x, output [63:0] y);
  wire [63:0] pa = x >> 5;
  wire [63:0] qb = x << 9;
  wire [63:0] rc = x >> 13;
  wire [63:0] sd = x << 3;
  assign y = x ^ ((pa ^ qb) & (rc ^ sd));
endmodule

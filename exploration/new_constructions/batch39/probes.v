// Batch-39 S0 cost probes (track 6, 2026-10-11).
// 2-term stages: ANDN (complemented-input AND) and unmasked OR.
// Hypothesis: 2 logic levels (vs b33c's 3) -> ~2.5-3.0u/stage.

function [63:0] rotl64;
  input [63:0] x;
  input integer r;
  begin
    rotl64 = (x << r) | (x >> (64 - r));
  end
endfunction

// andn: x ^= (ra & ~rb) -- expect ~2.5-3.0u (ANDN2+XOR2)
module stg_andn(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  assign y = x ^ (ra & ~rb);
endmodule

// orr: x ^= (ra | rb) -- expect ~2.5-3.0u (OR2+XOR2)
module stg_orr(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  assign y = x ^ (ra | rb);
endmodule

// andnM: x ^= (ra & ~rb) ^ rc -- masked control, expect ~3.3u
module stg_andnM(input [63:0] x, output [63:0] y);
  wire [63:0] ra = rotl64(x, 5);
  wire [63:0] rb = rotl64(x, 13);
  wire [63:0] rc = rotl64(x, 29);
  assign y = x ^ (ra & ~rb) ^ rc;
endmodule

// boolfunc_b.v — Design B: bipartite / alternating-parity thin Toffoli (Stage E then Stage O)
//
// 64-bit input -> 64-bit output, parameters A, B must be ODD.
// Stage E (even targets, odd controls frozen):
//   out[2i]   = in[2i]   XOR (in[(2i+A)%64] AND in[(2i+B)%64])   for i=0..31
//   out[2i+1] = in[2i+1]                                        (passthrough)
// Stage O (odd targets, even controls frozen):
//   out[2i+1] = in[2i+1] XOR (in[(2i+1+A)%64] AND in[(2i+1+B)%64]) for i=0..31
//   out[2i]   = in[2i]                                          (passthrough)
// Each stage is 32 disjoint Toffolis with frozen controls -> bijective (own inverse).
module boolfunc_b #(parameter A = 1, parameter B = 3) (
    input  [63:0] din,
    output [63:0] dout
);
    wire [63:0] e; // Stage E result
    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin : stage_e
            assign e[2*i]   = din[2*i] ^ (din[(2*i + A) % 64] & din[(2*i + B) % 64]);
            assign e[2*i+1] = din[2*i+1];
        end
        for (i = 0; i < 32; i = i + 1) begin : stage_o
            assign dout[2*i]   = e[2*i];
            assign dout[2*i+1] = e[2*i+1] ^ (e[(2*i + 1 + A) % 64] & e[(2*i + 1 + B) % 64]);
        end
    endgenerate
endmodule

// Concrete instantiations for the three offset candidates under test.
module boolfunc_b_13 (input [63:0] din, output [63:0] dout);
    boolfunc_b #(.A(1), .B(3)) u (.din(din), .dout(dout));
endmodule

module boolfunc_b_17 (input [63:0] din, output [63:0] dout);
    boolfunc_b #(.A(1), .B(7)) u (.din(din), .dout(dout));
endmodule

module boolfunc_b_311 (input [63:0] din, output [63:0] dout);
    boolfunc_b #(.A(3), .B(11)) u (.din(din), .dout(dout));
endmodule

// Large-offset variants (diffusion-aware: wrap-around taps for high targets).
// Added 2026-10-12 after the O151 sequential-input insight.
module boolfunc_b_133 (input [63:0] din, output [63:0] dout);
    boolfunc_b #(.A(1), .B(33)) u (.din(din), .dout(dout));
endmodule

module boolfunc_b_335 (input [63:0] din, output [63:0] dout);
    boolfunc_b #(.A(3), .B(35)) u (.din(din), .dout(dout));
endmodule

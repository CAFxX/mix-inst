// Round-4 delay probes (not candidates): raw primitive costs in the -fast flow.


module probe_clmul_sparse(input wire [63:0] x, output wire [63:0] p);
    // carry-less multiply by sparse constant 0x100000000000003F (7 nonzero bits)
    localparam [63:0] C = 64'h100000000000003F;
    wire [63:0] t0 = x;
    wire [63:0] t1 = x << 1;
    wire [63:0] t2 = x << 2;
    wire [63:0] t3 = x << 3;
    wire [63:0] t4 = x << 4;
    wire [63:0] t5 = x << 5;
    wire [63:0] t6 = x << 60;
    assign p = t0 ^ t1 ^ t2 ^ t3 ^ t4 ^ t5 ^ t6;
endmodule

module probe_mult16(input wire [15:0] x, output wire [15:0] p);
    localparam [15:0] C = 16'h9E37;
    assign p = x * C;
endmodule

module probe_mult32(input wire [31:0] x, output wire [31:0] p);
    localparam [31:0] C = 32'h85EBCA6B;
    assign p = x * C;
endmodule

module probe_sbox4(input wire [3:0] x, output wire [3:0] p);
    // single PRESENT S-box (per-bit cost reference)
    reg [3:0] q;
    always @(*) begin
        case (x)
            4'h0: q = 4'hC; 4'h1: q = 4'h5; 4'h2: q = 4'h6; 4'h3: q = 4'hB;
            4'h4: q = 4'h9; 4'h5: q = 4'h0; 4'h6: q = 4'hA; 4'h7: q = 4'hD;
            4'h8: q = 4'h3; 4'h9: q = 4'hE; 4'hA: q = 4'hF; 4'hB: q = 4'h8;
            4'hC: q = 4'h4; 4'hD: q = 4'h7; 4'hE: q = 4'h1; 4'hF: q = 4'h2;
        endcase
    end
    assign p = q;
endmodule

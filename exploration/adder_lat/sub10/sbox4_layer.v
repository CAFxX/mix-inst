// 16x PRESENT 4-bit S-box in parallel (one S-layer for 64-bit state)
// PRESENT S-box: C,5,6,B,9,0,A,D,3,E,F,8,4,7,1,2
module sbox4_layer(
    input  [63:0] x,
    output [63:0] y
);
    // PRESENT S-box as combinational logic (case form)
    function [3:0] sbox(input [3:0] a);
        case (a)
            4'h0: sbox = 4'hC;
            4'h1: sbox = 4'h5;
            4'h2: sbox = 4'h6;
            4'h3: sbox = 4'hB;
            4'h4: sbox = 4'h9;
            4'h5: sbox = 4'h0;
            4'h6: sbox = 4'hA;
            4'h7: sbox = 4'hD;
            4'h8: sbox = 4'h3;
            4'h9: sbox = 4'hE;
            4'hA: sbox = 4'hF;
            4'hB: sbox = 4'h8;
            4'hC: sbox = 4'h4;
            4'hD: sbox = 4'h7;
            4'hE: sbox = 4'h1;
            4'hF: sbox = 4'h2;
        endcase
    endfunction

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : sb
            assign y[i*4+3:i*4] = sbox(x[i*4+3:i*4]);
        end
    endgenerate
endmodule

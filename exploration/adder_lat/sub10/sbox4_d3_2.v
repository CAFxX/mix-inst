// 16x d3_2 4-bit S-box
module sbox4_d3_2(
    input  [63:0] x,
    output [63:0] y
);
    function [3:0] sbox(input [3:0] a);
        case (a)
            4'h0: sbox = 4'h0;
            4'h1: sbox = 4'h1;
            4'h2: sbox = 4'h2;
            4'h3: sbox = 4'h3;
            4'h4: sbox = 4'h4;
            4'h5: sbox = 4'h6;
            4'h6: sbox = 4'h8;
            4'h7: sbox = 4'hA;
            4'h8: sbox = 4'hC;
            4'h9: sbox = 4'h9;
            4'hA: sbox = 4'h5;
            4'hB: sbox = 4'hD;
            4'hC: sbox = 4'h7;
            4'hD: sbox = 4'hE;
            4'hE: sbox = 4'hF;
            4'hF: sbox = 4'hB;
        endcase
    endfunction
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : sb
            assign y[i*4+3:i*4] = sbox(x[i*4+3:i*4]);
        end
    endgenerate
endmodule

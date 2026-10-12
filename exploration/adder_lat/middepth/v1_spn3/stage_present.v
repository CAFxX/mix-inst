module spn3_stage_present(input [63:0] x, output [63:0] y);
    function [3:0] sbox(input [3:0] a);
        case (a)
            4'h0: sbox = 4'hC;
            4'h1: sbox = 4'hA;
            4'h2: sbox = 4'hD;
            4'h3: sbox = 4'h3;
            4'h4: sbox = 4'hE;
            4'h5: sbox = 4'hB;
            4'h6: sbox = 4'hF;
            4'h7: sbox = 4'h7;
            4'h8: sbox = 4'h8;
            4'h9: sbox = 4'h9;
            4'hA: sbox = 4'h1;
            4'hB: sbox = 4'h5;
            4'hC: sbox = 4'h0;
            4'hD: sbox = 4'h2;
            4'hE: sbox = 4'h4;
            4'hF: sbox = 4'h6;
        endcase
    endfunction

    wire [63:0] s;
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : sb
            assign s[i*4+3:i*4] = sbox(x[i*4+3:i*4]);
        end
    endgenerate
    assign y = {s[63], s[59], s[55], s[51], s[47], s[43], s[39], s[35], s[31], s[27], s[23], s[19], s[15], s[11], s[7], s[3], s[62], s[58], s[54], s[50], s[46], s[42], s[38], s[34], s[30], s[26], s[22], s[18], s[14], s[10], s[6], s[2], s[61], s[57], s[53], s[49], s[45], s[41], s[37], s[33], s[29], s[25], s[21], s[17], s[13], s[9], s[5], s[1], s[60], s[56], s[52], s[48], s[44], s[40], s[36], s[32], s[28], s[24], s[20], s[16], s[12], s[8], s[4], s[0]};
endmodule

// t6_chiS4b: batch-45 chiS4 schedule (triage z=5.38)
module t6_chiS4b(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    // chi_3 S-box: 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity.
    // y[3j+k] = x[3j+k] ^ (~x[3j+(k+1)%3] & x[3j+(k+2)%3])  (b42 geometry)
    function [63:0] chi3;
        input [63:0] x;
        integer j;
        reg [63:0] y;
        begin
            y[63] = x[63];
            for (j = 0; j < 21; j = j + 1) begin
                y[3*j]   = x[3*j]   ^ (~x[3*j+1] & x[3*j+2]);
                y[3*j+1] = x[3*j+1] ^ (~x[3*j+2] & x[3*j]);
                y[3*j+2] = x[3*j+2] ^ (~x[3*j]   & x[3*j+1]);
            end
            chi3 = y;
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] c1 = chi3(x0);
    wire [63:0] x1 = c1 ^ {c1[35:0], c1[63:28]} ^ {c1[24:0], c1[63:39]};
    wire [63:0] c2 = chi3(x1);
    wire [63:0] x2 = c2 ^ {c2[16:0], c2[63:47]} ^ {c2[20:0], c2[63:43]};
    wire [63:0] c3 = chi3(x2);
    wire [63:0] x3 = c3 ^ {c3[59:0], c3[63:4]} ^ {c3[9:0], c3[63:54]};
    wire [63:0] c4 = chi3(x3);
    wire [63:0] x4 = c4 ^ {c4[29:0], c4[63:34]} ^ {c4[7:0], c4[63:56]};
    assign out = x4 ^ {key[12:0], key[63:51]};
endmodule

// t6_chiS4c: batch-45 chiS4 schedule (triage z=7.96)
module t6_chiS4c(
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
    wire [63:0] x1 = c1 ^ {c1[37:0], c1[63:26]} ^ {c1[41:0], c1[63:22]};
    wire [63:0] c2 = chi3(x1);
    wire [63:0] x2 = c2 ^ {c2[56:0], c2[63:7]} ^ {c2[6:0], c2[63:57]};
    wire [63:0] c3 = chi3(x2);
    wire [63:0] x3 = c3 ^ {c3[5:0], c3[63:58]} ^ {c3[61:0], c3[63:2]};
    wire [63:0] c4 = chi3(x3);
    wire [63:0] x4 = c4 ^ {c4[24:0], c4[63:39]} ^ {c4[54:0], c4[63:9]};
    assign out = x4 ^ {key[12:0], key[63:51]};
endmodule

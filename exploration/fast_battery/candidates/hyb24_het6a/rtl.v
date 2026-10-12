// hyb24_het6a: batch-24b guided 6-stage heterogeneous AND schedule (triage z=7.16)
module hyb24_het6a(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ ({x0[46:0], x0[63:47]} & {x0[46:0], x0[63:47]}) ^ {x0[37:0], x0[63:38]};
    wire [63:0] x2 = x1 ^ ({x1[22:0], x1[63:23]} & {x1[7:0], x1[63:8]}) ^ {x1[23:0], x1[63:24]};
    wire [63:0] x3 = x2 ^ ({x2[8:0], x2[63:9]} & {x2[27:0], x2[63:28]}) ^ {x2[59:0], x2[63:60]};
    wire [63:0] x4 = x3 ^ ({x3[41:0], x3[63:42]} & {x3[59:0], x3[63:60]}) ^ {x3[26:0], x3[63:27]};
    wire [63:0] x5 = x4 ^ ({x4[11:0], x4[63:12]} & {x4[16:0], x4[63:17]});
    wire [63:0] x6 = x5 ^ ({x5[8:0], x5[63:9]} & {x5[8:0], x5[63:9]});
    assign out = x6 ^ {key[50:0], key[63:51]};
endmodule

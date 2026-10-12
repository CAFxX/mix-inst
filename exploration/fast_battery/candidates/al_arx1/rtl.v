// al_arx1: single-addition ARX (track-6 ARX axis; RTL written 2026-10-10 from model.py)
// x = val + key; x ^= rotl(x,13) ^ rotl(x,29); x = P(x); x ^= rotl(x,7); x ^= key
// PBOX[i] = (19*i + 1) % 64
module al_arx1(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] a0 = val + key;
    wire [63:0] b0 = a0 ^ {a0[50:0], a0[63:51]} ^ {a0[34:0], a0[63:35]};
    wire [63:0] p0;
    assign p0[1] = b0[0];
    assign p0[20] = b0[1];
    assign p0[39] = b0[2];
    assign p0[58] = b0[3];
    assign p0[13] = b0[4];
    assign p0[32] = b0[5];
    assign p0[51] = b0[6];
    assign p0[6] = b0[7];
    assign p0[25] = b0[8];
    assign p0[44] = b0[9];
    assign p0[63] = b0[10];
    assign p0[18] = b0[11];
    assign p0[37] = b0[12];
    assign p0[56] = b0[13];
    assign p0[11] = b0[14];
    assign p0[30] = b0[15];
    assign p0[49] = b0[16];
    assign p0[4] = b0[17];
    assign p0[23] = b0[18];
    assign p0[42] = b0[19];
    assign p0[61] = b0[20];
    assign p0[16] = b0[21];
    assign p0[35] = b0[22];
    assign p0[54] = b0[23];
    assign p0[9] = b0[24];
    assign p0[28] = b0[25];
    assign p0[47] = b0[26];
    assign p0[2] = b0[27];
    assign p0[21] = b0[28];
    assign p0[40] = b0[29];
    assign p0[59] = b0[30];
    assign p0[14] = b0[31];
    assign p0[33] = b0[32];
    assign p0[52] = b0[33];
    assign p0[7] = b0[34];
    assign p0[26] = b0[35];
    assign p0[45] = b0[36];
    assign p0[0] = b0[37];
    assign p0[19] = b0[38];
    assign p0[38] = b0[39];
    assign p0[57] = b0[40];
    assign p0[12] = b0[41];
    assign p0[31] = b0[42];
    assign p0[50] = b0[43];
    assign p0[5] = b0[44];
    assign p0[24] = b0[45];
    assign p0[43] = b0[46];
    assign p0[62] = b0[47];
    assign p0[17] = b0[48];
    assign p0[36] = b0[49];
    assign p0[55] = b0[50];
    assign p0[10] = b0[51];
    assign p0[29] = b0[52];
    assign p0[48] = b0[53];
    assign p0[3] = b0[54];
    assign p0[22] = b0[55];
    assign p0[41] = b0[56];
    assign p0[60] = b0[57];
    assign p0[15] = b0[58];
    assign p0[34] = b0[59];
    assign p0[53] = b0[60];
    assign p0[8] = b0[61];
    assign p0[27] = b0[62];
    assign p0[46] = b0[63];
    wire [63:0] c0 = p0 ^ {p0[56:0], p0[63:57]};
    assign out = c0 ^ key;
endmodule

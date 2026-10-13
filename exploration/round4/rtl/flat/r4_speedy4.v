// Flat single-module build of r4_speedy4 (from r4_speedy.v);
// parameters: {'ROUNDS': '4'}
module r4_speedy4
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [5:0] s6(input [5:0] x);
        begin
            case (x)
                6'h00: s6 = 6'h08;
                6'h01: s6 = 6'h00;
                6'h02: s6 = 6'h09;
                6'h03: s6 = 6'h03;
                6'h04: s6 = 6'h38;
                6'h05: s6 = 6'h10;
                6'h06: s6 = 6'h29;
                6'h07: s6 = 6'h13;
                6'h08: s6 = 6'h0C;
                6'h09: s6 = 6'h0D;
                6'h0A: s6 = 6'h04;
                6'h0B: s6 = 6'h07;
                6'h0C: s6 = 6'h30;
                6'h0D: s6 = 6'h01;
                6'h0E: s6 = 6'h20;
                6'h0F: s6 = 6'h23;
                6'h10: s6 = 6'h1A;
                6'h11: s6 = 6'h12;
                6'h12: s6 = 6'h18;
                6'h13: s6 = 6'h32;
                6'h14: s6 = 6'h3E;
                6'h15: s6 = 6'h16;
                6'h16: s6 = 6'h2C;
                6'h17: s6 = 6'h36;
                6'h18: s6 = 6'h1C;
                6'h19: s6 = 6'h1D;
                6'h1A: s6 = 6'h14;
                6'h1B: s6 = 6'h37;
                6'h1C: s6 = 6'h34;
                6'h1D: s6 = 6'h05;
                6'h1E: s6 = 6'h24;
                6'h1F: s6 = 6'h27;
                6'h20: s6 = 6'h02;
                6'h21: s6 = 6'h06;
                6'h22: s6 = 6'h0B;
                6'h23: s6 = 6'h0F;
                6'h24: s6 = 6'h33;
                6'h25: s6 = 6'h17;
                6'h26: s6 = 6'h21;
                6'h27: s6 = 6'h15;
                6'h28: s6 = 6'h0A;
                6'h29: s6 = 6'h1B;
                6'h2A: s6 = 6'h0E;
                6'h2B: s6 = 6'h1F;
                6'h2C: s6 = 6'h31;
                6'h2D: s6 = 6'h11;
                6'h2E: s6 = 6'h25;
                6'h2F: s6 = 6'h35;
                6'h30: s6 = 6'h22;
                6'h31: s6 = 6'h26;
                6'h32: s6 = 6'h2A;
                6'h33: s6 = 6'h2E;
                6'h34: s6 = 6'h3A;
                6'h35: s6 = 6'h1E;
                6'h36: s6 = 6'h28;
                6'h37: s6 = 6'h3C;
                6'h38: s6 = 6'h2B;
                6'h39: s6 = 6'h3B;
                6'h3A: s6 = 6'h2F;
                6'h3B: s6 = 6'h3F;
                6'h3C: s6 = 6'h39;
                6'h3D: s6 = 6'h19;
                6'h3E: s6 = 6'h2D;
                6'h3F: s6 = 6'h3D;
            endcase
        end
    endfunction
    function automatic [3:0] s1(input [3:0] x);
        begin
            case (x)
                4'h0: s1 = 4'h0;
                4'h1: s1 = 4'h1;
                4'h2: s1 = 4'h2;
                4'h3: s1 = 4'h4;
                4'h4: s1 = 4'h3;
                4'h5: s1 = 4'h8;
                4'h6: s1 = 4'hF;
                4'h7: s1 = 4'hC;
                4'h8: s1 = 4'h9;
                4'h9: s1 = 4'h5;
                4'hA: s1 = 4'hB;
                4'hB: s1 = 4'h6;
                4'hC: s1 = 4'h7;
                4'hD: s1 = 4'hE;
                4'hE: s1 = 4'hD;
                4'hF: s1 = 4'hA;
            endcase
        end
    endfunction
    function automatic [63:0] sbox_layer(input [63:0] x);
        begin
            sbox_layer = {s1(x[63:60]), s6(x[59:54]), s6(x[53:48]), s6(x[47:42]), s6(x[41:36]), s6(x[35:30]), s6(x[29:24]), s6(x[23:18]), s6(x[17:12]), s6(x[11:6]), s6(x[5:0])};
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] xs [0:4];
    assign xs[0] = x0;
    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin : rnd
            localparam integer RR = (13 * (i + 1)) % 64;
            wire [63:0] rk = {key[63-RR:0], key[63:64-RR]} ^ ((i + 1) * 64'h9E3779B97F4A7C15);
            wire [63:0] sb = sbox_layer(xs[i] ^ rk);
            assign xs[i+1] = {sb[46:0], sb[63:47]};
        end
    endgenerate
    localparam integer RWR = (13 * (4 + 1)) % 64;
    wire [63:0] rkW = {key[63-RWR:0], key[63:64-RWR]} ^ ((4 + 1) * 64'h9E3779B97F4A7C15);
    assign out = xs[4] ^ rkW;
endmodule

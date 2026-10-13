// Flat unrolled r4_speedy4: SPEEDY 6-bit S-box SPN, 4 rounds.
module r4_speedy4
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [5:0] s6(input [5:0] x);
        begin
            s6 =                        (x == 6'h00) ? 6'h08 :
                       (x == 6'h01) ? 6'h00 :
                       (x == 6'h02) ? 6'h09 :
                       (x == 6'h03) ? 6'h03 :
                       (x == 6'h04) ? 6'h38 :
                       (x == 6'h05) ? 6'h10 :
                       (x == 6'h06) ? 6'h29 :
                       (x == 6'h07) ? 6'h13 :
                       (x == 6'h08) ? 6'h0C :
                       (x == 6'h09) ? 6'h0D :
                       (x == 6'h0A) ? 6'h04 :
                       (x == 6'h0B) ? 6'h07 :
                       (x == 6'h0C) ? 6'h30 :
                       (x == 6'h0D) ? 6'h01 :
                       (x == 6'h0E) ? 6'h20 :
                       (x == 6'h0F) ? 6'h23 :
                       (x == 6'h10) ? 6'h1A :
                       (x == 6'h11) ? 6'h12 :
                       (x == 6'h12) ? 6'h18 :
                       (x == 6'h13) ? 6'h32 :
                       (x == 6'h14) ? 6'h3E :
                       (x == 6'h15) ? 6'h16 :
                       (x == 6'h16) ? 6'h2C :
                       (x == 6'h17) ? 6'h36 :
                       (x == 6'h18) ? 6'h1C :
                       (x == 6'h19) ? 6'h1D :
                       (x == 6'h1A) ? 6'h14 :
                       (x == 6'h1B) ? 6'h37 :
                       (x == 6'h1C) ? 6'h34 :
                       (x == 6'h1D) ? 6'h05 :
                       (x == 6'h1E) ? 6'h24 :
                       (x == 6'h1F) ? 6'h27 :
                       (x == 6'h20) ? 6'h02 :
                       (x == 6'h21) ? 6'h06 :
                       (x == 6'h22) ? 6'h0B :
                       (x == 6'h23) ? 6'h0F :
                       (x == 6'h24) ? 6'h33 :
                       (x == 6'h25) ? 6'h17 :
                       (x == 6'h26) ? 6'h21 :
                       (x == 6'h27) ? 6'h15 :
                       (x == 6'h28) ? 6'h0A :
                       (x == 6'h29) ? 6'h1B :
                       (x == 6'h2A) ? 6'h0E :
                       (x == 6'h2B) ? 6'h1F :
                       (x == 6'h2C) ? 6'h31 :
                       (x == 6'h2D) ? 6'h11 :
                       (x == 6'h2E) ? 6'h25 :
                       (x == 6'h2F) ? 6'h35 :
                       (x == 6'h30) ? 6'h22 :
                       (x == 6'h31) ? 6'h26 :
                       (x == 6'h32) ? 6'h2A :
                       (x == 6'h33) ? 6'h2E :
                       (x == 6'h34) ? 6'h3A :
                       (x == 6'h35) ? 6'h1E :
                       (x == 6'h36) ? 6'h28 :
                       (x == 6'h37) ? 6'h3C :
                       (x == 6'h38) ? 6'h2B :
                       (x == 6'h39) ? 6'h3B :
                       (x == 6'h3A) ? 6'h2F :
                       (x == 6'h3B) ? 6'h3F :
                       (x == 6'h3C) ? 6'h39 :
                       (x == 6'h3D) ? 6'h19 :
                       (x == 6'h3E) ? 6'h2D :
                       (x == 6'h3F) ? 6'h3D :
                       6'h00;
        end
    endfunction
    function automatic [3:0] s1(input [3:0] x);
        begin
            s1 =                        (x == 4'h0) ? 4'h0 :
                       (x == 4'h1) ? 4'h1 :
                       (x == 4'h2) ? 4'h2 :
                       (x == 4'h3) ? 4'h4 :
                       (x == 4'h4) ? 4'h3 :
                       (x == 4'h5) ? 4'h8 :
                       (x == 4'h6) ? 4'hF :
                       (x == 4'h7) ? 4'hC :
                       (x == 4'h8) ? 4'h9 :
                       (x == 4'h9) ? 4'h5 :
                       (x == 4'hA) ? 4'hB :
                       (x == 4'hB) ? 4'h6 :
                       (x == 4'hC) ? 4'h7 :
                       (x == 4'hD) ? 4'hE :
                       (x == 4'hE) ? 4'hD :
                       (x == 4'hF) ? 4'hA :
                       4'h0;
        end
    endfunction
    function automatic [63:0] sbox_layer(input [63:0] x);
        begin
            sbox_layer = {s1(x[63:60]), s6(x[59:54]), s6(x[53:48]), s6(x[47:42]), s6(x[41:36]), s6(x[35:30]), s6(x[29:24]), s6(x[23:18]), s6(x[17:12]), s6(x[11:6]), s6(x[5:0])};
        end
    endfunction
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] rk3 = {key[11:0], key[63:12]} ^ 64'h78DDE6E5FD29F054;
    wire [63:0] rk4 = {key[62:0], key[63:63]} ^ 64'h1715609F7C746C69;
    wire [63:0] st0 = val ^ key;
    wire [63:0] sb0 = sbox_layer(st0 ^ rk0);
    wire [63:0] st1 = {sb0[46:0], sb0[63:47]};
    wire [63:0] sb1 = sbox_layer(st1 ^ rk1);
    wire [63:0] st2 = {sb1[46:0], sb1[63:47]};
    wire [63:0] sb2 = sbox_layer(st2 ^ rk2);
    wire [63:0] st3 = {sb2[46:0], sb2[63:47]};
    wire [63:0] sb3 = sbox_layer(st3 ^ rk3);
    wire [63:0] st4 = {sb3[46:0], sb3[63:47]};
    assign out = st4 ^ rk4;
endmodule

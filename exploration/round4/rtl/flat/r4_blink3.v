// Flat single-module build of r4_blink3 (from r4_blink.v);
// parameters: {'SB': '0', 'ROUNDS': '3'}
module r4_blink3
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [3:0] sbox(input [3:0] x);
        begin
            if (0 == 0) begin
                // S1: 0 1 2 4 3 8 f c 9 5 b 6 7 e d a
                case (x)
                    4'h0: sbox = 4'h0; 4'h1: sbox = 4'h1;
                    4'h2: sbox = 4'h2; 4'h3: sbox = 4'h4;
                    4'h4: sbox = 4'h3; 4'h5: sbox = 4'h8;
                    4'h6: sbox = 4'hF; 4'h7: sbox = 4'hC;
                    4'h8: sbox = 4'h9; 4'h9: sbox = 4'h5;
                    4'hA: sbox = 4'hB; 4'hB: sbox = 4'h6;
                    4'hC: sbox = 4'h7; 4'hD: sbox = 4'hE;
                    4'hE: sbox = 4'hD; 4'hF: sbox = 4'hA;
                endcase
            end else begin
                // Midori Sb0: c a d 3 e b f 7 8 9 1 5 0 2 4 6
                case (x)
                    4'h0: sbox = 4'hC; 4'h1: sbox = 4'hA;
                    4'h2: sbox = 4'hD; 4'h3: sbox = 4'h3;
                    4'h4: sbox = 4'hE; 4'h5: sbox = 4'hB;
                    4'h6: sbox = 4'hF; 4'h7: sbox = 4'h7;
                    4'h8: sbox = 4'h8; 4'h9: sbox = 4'h9;
                    4'hA: sbox = 4'h1; 4'hB: sbox = 4'h5;
                    4'hC: sbox = 4'h0; 4'hD: sbox = 4'h2;
                    4'hE: sbox = 4'h4; 4'hF: sbox = 4'h6;
                endcase
            end
        end
    endfunction
    function automatic [63:0] sbox16(input [63:0] x);
        begin
            sbox16 = {sbox(x[63:60]), sbox(x[59:56]), sbox(x[55:52]), sbox(x[51:48]),
                      sbox(x[47:44]), sbox(x[43:40]), sbox(x[39:36]), sbox(x[35:32]),
                      sbox(x[31:28]), sbox(x[27:24]), sbox(x[23:20]), sbox(x[19:16]),
                      sbox(x[15:12]), sbox(x[11:8]),  sbox(x[7:4]),   sbox(x[3:0])};
        end
    endfunction
    function automatic [15:0] mixcol(input [15:0] c);
        reg [3:0] n0, n1, n2, n3;
        begin
            n0 = c[3:0]; n1 = c[7:4]; n2 = c[11:8]; n3 = c[15:12];
            mixcol = {(n0^n1^n2), (n0^n1^n3), (n0^n2^n3), (n1^n2^n3)};
        end
    endfunction
    function automatic [63:0] midori_M(input [63:0] x);
        begin
            midori_M = {mixcol(x[63:48]), mixcol(x[47:32]),
                        mixcol(x[31:16]), mixcol(x[15:0])};
        end
    endfunction
    function automatic [63:0] shuffle(input [63:0] x);
        begin
            // Midori ShuffleCell: out_nib[i] = in_nib[PERM[i]]
            shuffle = {x[35:32], x[11:8], x[55:52], x[31:28],
                       x[27:24], x[51:48], x[15:12], x[39:36],
                       x[7:4], x[47:44], x[19:16], x[59:56],
                       x[63:60], x[23:20], x[43:40], x[3:0]};
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] xs [0:3];
    assign xs[0] = x0;
    genvar i;
    generate
        for (i = 0; i < 3; i = i + 1) begin : rnd
            // RR = 13*(i+1) % 64; nonzero for 3 <= 4 (13,26,39,52)
            localparam integer RR = (13 * (i + 1)) % 64;
            wire [63:0] rk = {key[63-RR:0], key[63:64-RR]} ^ ((i + 1) * 64'h9E3779B97F4A7C15);
            assign xs[i+1] = shuffle(midori_M(sbox16(xs[i] ^ rk)));
        end
    endgenerate
    wire [63:0] rkW = {key[63-((13*(3+1))%64):0], key[63:64-((13*(3+1))%64)]}
                      ^ ((3 + 1) * 64'h9E3779B97F4A7C15);
    assign out = xs[3] ^ rkW;
endmodule

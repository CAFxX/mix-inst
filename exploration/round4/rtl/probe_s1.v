// Probe: S1 S-box (ternary) delay in isolation
module s1_probe(input wire [3:0] x, output wire [3:0] y);
    function automatic [3:0] sbox(input [3:0] x);
        begin
            sbox = (x == 4'h0) ? 4'h0 :
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
    assign y = sbox(x);
endmodule

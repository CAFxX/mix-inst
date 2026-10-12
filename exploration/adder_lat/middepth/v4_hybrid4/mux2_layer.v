// MUX2 layer: 64 parallel 2:1 MUX gates (tt=0xac, O138).
// y[i] = s[i] ? b[i] : a[i], where s=rotl(x,RS), a=rotl(x,RA), b=rotl(x,RB).
// Pure substitution (no feed-forward XOR) so the stage is a single MUX2 = 2.0u.
module mux2_layer #(
    parameter RS = 7,
    parameter RA = 23,
    parameter RB = 41
)(
    input  [63:0] x,
    output [63:0] y
);
    function [63:0] rotl(input [63:0] v, input integer n);
        begin
            if (n == 0)
                rotl = v;
            else
                rotl = (v << n) | (v >> (64 - n));
        end
    endfunction

    wire [63:0] s = rotl(x, RS);
    wire [63:0] a = rotl(x, RA);
    wire [63:0] b = rotl(x, RB);

    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1) begin : mx
            assign y[i] = s[i] ? b[i] : a[i];
        end
    endgenerate
endmodule

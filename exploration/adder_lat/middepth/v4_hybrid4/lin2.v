// 2-term rotl-xor linear: y = x ^ rotl(x,P) ^ rotl(x,Q). 2 XOR levels.
module lin2 #(
    parameter P = 7,
    parameter Q = 23
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
    wire [63:0] rp = rotl(x, P);
    wire [63:0] rq = rotl(x, Q);
    assign y = x ^ rp ^ rq;
endmodule

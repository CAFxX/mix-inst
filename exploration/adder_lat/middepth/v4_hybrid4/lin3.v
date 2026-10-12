// 3-term rotl-xor linear: y = x ^ rotl(x,P) ^ rotl(x,Q) ^ rotl(x,R). 2 XOR levels.
module lin3 #(
    parameter P = 7,
    parameter Q = 23,
    parameter R = 41
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
    wire [63:0] rr = rotl(x, R);
    wire [63:0] t1 = rp ^ rq;
    assign y = x ^ t1 ^ rr;
endmodule
